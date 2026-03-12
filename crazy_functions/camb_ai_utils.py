import time
import struct
from toolbox import get_conf


def get_camb_client():
    """Creates a CambAI client using the configured API key."""
    from camb.client import CambAI
    api_key = get_conf("CAMB_API_KEY")
    if not api_key:
        raise ValueError("CAMB_API_KEY is not configured. Please set it in config_private.py.")
    return CambAI(api_key=api_key)


def poll_task(status_fn, task_id, max_attempts=60, interval=2.0):
    """Polls an async CAMB task until completion or failure."""
    success_states = {"completed", "SUCCESS"}
    failure_states = {"failed", "FAILED", "error", "ERROR"}
    for _ in range(max_attempts):
        status = status_fn(task_id)
        if status.status in success_states:
            return status
        if status.status in failure_states:
            error_msg = getattr(status, 'error', 'Unknown error')
            raise RuntimeError(f"CAMB AI task failed: {error_msg}")
        time.sleep(interval)
    raise TimeoutError(f"CAMB AI task timed out after {max_attempts * interval}s")


def detect_audio_format(data):
    """Detects audio format from magic bytes."""
    if data[:4] == b'RIFF':
        return 'wav'
    if data[:3] == b'ID3' or data[:2] == b'\xff\xfb' or data[:2] == b'\xff\xf3':
        return 'mp3'
    if data[:4] == b'fLaC':
        return 'flac'
    if data[:4] == b'OggS':
        return 'ogg'
    return 'pcm'


def add_wav_header(pcm_data, sample_rate=24000, channels=1, bits_per_sample=16):
    """Adds a WAV header to raw PCM data."""
    data_size = len(pcm_data)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,
        1,  # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size,
    )
    return header + pcm_data


def map_language_to_bcp47(lang):
    """Maps frontend language codes to BCP-47 codes for CAMB AI TTS."""
    mapping = {
        'zh': 'zh-cn',
        'en': 'en-us',
        'ja': 'ja-jp',
        'ko': 'ko-kr',
        'fr': 'fr-fr',
        'de': 'de-de',
        'es': 'es-es',
        'pt': 'pt-br',
        'ru': 'ru-ru',
        'ar': 'ar-sa',
        'it': 'it-it',
    }
    if lang is None:
        return get_conf("CAMB_TTS_LANGUAGE")
    lang = lang.lower().strip()
    return mapping.get(lang, lang)


def camb_tts_generate(text, language=None, voice_id=None, model=None, speed=None):
    """High-level TTS function that returns WAV bytes."""
    from camb import StreamTtsOutputConfiguration, StreamTtsVoiceSettings

    client = get_camb_client()
    if language is None:
        language = get_conf("CAMB_TTS_LANGUAGE")
    if voice_id is None:
        voice_id = get_conf("CAMB_TTS_VOICE_ID")
    if model is None:
        model = get_conf("CAMB_TTS_MODEL")
    if speed is None:
        speed = get_conf("CAMB_TTS_SPEED")

    chunks = client.text_to_speech.tts(
        text=text,
        language=language,
        voice_id=voice_id,
        speech_model=model,
        output_configuration=StreamTtsOutputConfiguration(format="wav"),
        voice_settings=StreamTtsVoiceSettings(speed=speed),
    )
    audio_data = b''.join(chunks)

    fmt = detect_audio_format(audio_data)
    if fmt == 'pcm':
        audio_data = add_wav_header(audio_data)
    return audio_data
