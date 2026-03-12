"""
Tests for CAMB AI integration: utility functions, plugins, TTS endpoint.

Run unit tests only (no API key needed):
    pytest tests/test_camb_ai.py -k "not live"

Run all tests including integration (needs CAMB_API_KEY):
    CAMB_API_KEY=your-key pytest tests/test_camb_ai.py
"""

import os
import sys
import struct
import types
import pytest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Bootstrap: inject mock toolbox so that `from toolbox import ...` doesn't
# pull in gradio. The real camb SDK is used (installed from cambai-python-sdk).
# ---------------------------------------------------------------------------

_mock_get_conf = MagicMock(return_value="")

# Mock toolbox module (gradio dependency)
_toolbox = types.ModuleType("toolbox")
_toolbox.get_conf = _mock_get_conf
_toolbox.CatchException = lambda f: f  # passthrough decorator
_toolbox.report_exception = MagicMock()
_toolbox.update_ui = MagicMock(return_value=iter([None]))
_toolbox.get_log_folder = MagicMock(return_value="/tmp/test_camb_logs")
_toolbox.promote_file_to_downloadzone = MagicMock()
_toolbox.write_history_to_file = MagicMock(return_value="/tmp/test_history.md")
sys.modules.setdefault("toolbox", _toolbox)

# Now safe to import the modules under test
from crazy_functions.camb_ai_utils import (
    detect_audio_format,
    add_wav_header,
    map_language_to_bcp47,
    get_camb_client,
    poll_task,
    camb_tts_generate,
)


# ---------------------------------------------------------------------------
# Section 1: Utility tests (no SDK needed)
# ---------------------------------------------------------------------------

class TestDetectAudioFormat:

    def test_wav(self):
        assert detect_audio_format(b'RIFF\x00\x00\x00\x00WAVEfmt ') == 'wav'

    def test_mp3_id3(self):
        assert detect_audio_format(b'ID3\x04\x00\x00\x00\x00') == 'mp3'

    def test_mp3_sync_fb(self):
        assert detect_audio_format(b'\xff\xfb\x90\x00') == 'mp3'

    def test_mp3_sync_f3(self):
        assert detect_audio_format(b'\xff\xf3\x90\x00') == 'mp3'

    def test_flac(self):
        assert detect_audio_format(b'fLaC\x00\x00\x00') == 'flac'

    def test_ogg(self):
        assert detect_audio_format(b'OggS\x00\x02\x00\x00') == 'ogg'

    def test_pcm_fallback(self):
        assert detect_audio_format(b'\x00\x01\x02\x03\x04\x05') == 'pcm'


class TestAddWavHeader:

    def test_valid_riff_header(self):
        pcm = b'\x00' * 100
        wav = add_wav_header(pcm, sample_rate=16000, channels=1, bits_per_sample=16)
        assert wav[:4] == b'RIFF'
        assert wav[8:12] == b'WAVE'
        assert wav[12:16] == b'fmt '
        assert wav[36:40] == b'data'

    def test_correct_sizes(self):
        pcm = b'\xab' * 256
        wav = add_wav_header(pcm, sample_rate=24000, channels=1, bits_per_sample=16)
        riff_size = struct.unpack_from('<I', wav, 4)[0]
        assert riff_size == 36 + 256
        data_size = struct.unpack_from('<I', wav, 40)[0]
        assert data_size == 256
        assert len(wav) == 44 + 256

    def test_pcm_data_preserved(self):
        pcm = b'\x01\x02\x03\x04'
        wav = add_wav_header(pcm)
        assert wav[44:] == pcm


class TestMapLanguageToBcp47:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='en-us')
    def test_known_mappings(self, _mock_conf):
        assert map_language_to_bcp47('zh') == 'zh-cn'
        assert map_language_to_bcp47('en') == 'en-us'
        assert map_language_to_bcp47('ja') == 'ja-jp'
        assert map_language_to_bcp47('ko') == 'ko-kr'
        assert map_language_to_bcp47('fr') == 'fr-fr'

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='en-us')
    def test_passthrough_unknown(self, _mock_conf):
        assert map_language_to_bcp47('sv-se') == 'sv-se'

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='en-us')
    def test_case_insensitive(self, _mock_conf):
        assert map_language_to_bcp47('ZH') == 'zh-cn'
        assert map_language_to_bcp47(' En ') == 'en-us'

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='fr-fr')
    def test_none_returns_config(self, _mock_conf):
        assert map_language_to_bcp47(None) == 'fr-fr'


# ---------------------------------------------------------------------------
# Section 2: Unit tests (mocked SDK)
# ---------------------------------------------------------------------------

class TestGetCambClient:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='test-api-key-123')
    def test_creates_client(self, _mock_conf):
        mock_cls = MagicMock()
        with patch('camb.client.CambAI', mock_cls):
            client = get_camb_client()
        mock_cls.assert_called_once_with(api_key='test-api-key-123')

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='')
    def test_no_key_raises(self, _mock_conf):
        with pytest.raises(ValueError, match="CAMB_API_KEY"):
            get_camb_client()

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value=None)
    def test_none_key_raises(self, _mock_conf):
        with pytest.raises(ValueError, match="CAMB_API_KEY"):
            get_camb_client()


class TestPollTask:

    def _make_status(self, status_str, error=None):
        s = MagicMock()
        s.status = status_str
        if error:
            s.error = error
        return s

    def test_success_completed(self):
        status_fn = MagicMock(return_value=self._make_status("completed"))
        result = poll_task(status_fn, "task-1", max_attempts=5, interval=0)
        assert result.status == "completed"
        status_fn.assert_called_once_with("task-1")

    def test_success_after_pending(self):
        statuses = [
            self._make_status("processing"),
            self._make_status("processing"),
            self._make_status("completed"),
        ]
        status_fn = MagicMock(side_effect=statuses)
        result = poll_task(status_fn, "task-2", max_attempts=5, interval=0)
        assert result.status == "completed"
        assert status_fn.call_count == 3

    def test_success_state(self):
        status_fn = MagicMock(return_value=self._make_status("SUCCESS"))
        result = poll_task(status_fn, "task-5", max_attempts=5, interval=0)
        assert result.status == "SUCCESS"

    def test_failure_raises_runtime_error(self):
        status_fn = MagicMock(return_value=self._make_status("failed", error="bad input"))
        with pytest.raises(RuntimeError, match="bad input"):
            poll_task(status_fn, "task-3", max_attempts=5, interval=0)

    def test_failure_states(self):
        for state in ("FAILED", "error", "ERROR"):
            status_fn = MagicMock(return_value=self._make_status(state))
            with pytest.raises(RuntimeError):
                poll_task(status_fn, "task-f", max_attempts=5, interval=0)

    def test_timeout_raises(self):
        status_fn = MagicMock(return_value=self._make_status("processing"))
        with pytest.raises(TimeoutError, match="timed out"):
            poll_task(status_fn, "task-4", max_attempts=3, interval=0)
        assert status_fn.call_count == 3


class TestCambTtsGenerate:

    def _conf_side_effect(self, key):
        defaults = {
            "CAMB_API_KEY": "test-key",
            "CAMB_TTS_LANGUAGE": "en-us",
            "CAMB_TTS_VOICE_ID": 147320,
            "CAMB_TTS_MODEL": "mars-flash",
            "CAMB_TTS_SPEED": 1.0,
        }
        return defaults.get(key, "")

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_returns_wav_bytes(self, mock_conf):
        mock_conf.side_effect = self._conf_side_effect
        wav_chunk = b'RIFF' + b'\x00' * 100
        mock_client = MagicMock()
        mock_client.text_to_speech.tts.return_value = [wav_chunk]

        with patch('camb.client.CambAI', return_value=mock_client):
            result = camb_tts_generate("Hello world")

        assert result[:4] == b'RIFF'
        mock_client.text_to_speech.tts.assert_called_once()

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_pcm_gets_wav_header(self, mock_conf):
        mock_conf.side_effect = self._conf_side_effect
        pcm_data = b'\x01\x02' * 50
        mock_client = MagicMock()
        mock_client.text_to_speech.tts.return_value = [pcm_data]

        with patch('camb.client.CambAI', return_value=mock_client):
            result = camb_tts_generate("Hello")

        assert result[:4] == b'RIFF'
        assert result[44:] == pcm_data


# ---------------------------------------------------------------------------
# Section 3: Plugin tests (mocked SDK, verifying plugin generators)
# ---------------------------------------------------------------------------

def _consume_generator(gen):
    """Consume a plugin generator and return the final yielded tuple."""
    last = None
    for item in gen:
        last = item
    return last


def _make_update_ui(**kwargs):
    """Return an update_ui replacement that yields once so `yield from` works."""
    def _update_ui(*a, **kw):
        yield (kw.get('chatbot', []), [], [], "")
    return _update_ui


class TestTranslationPlugin:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='test-key')
    def test_text_input(self, _mock_conf):
        mock_result = MagicMock()
        mock_result.text = "Translated text here"
        mock_client = MagicMock()
        mock_client.translation.translation_stream.return_value = mock_result

        with patch('camb.client.CambAI', return_value=mock_client):
            # Patch toolbox functions used by the plugin module
            _toolbox.update_ui = MagicMock(side_effect=_make_update_ui())
            _toolbox.get_log_folder = MagicMock(return_value="/tmp/test_camb_translation")
            _toolbox.write_history_to_file = MagicMock(return_value="/tmp/hist.md")

            from crazy_functions.CambAI_Translation import CambAI_Translation
            chatbot = []
            plugin_kwargs = {"advanced_arg": "1,75"}
            gen = CambAI_Translation(
                "Hello world", {}, plugin_kwargs, chatbot, [], "", 0
            )
            _consume_generator(gen)

        mock_client.translation.translation_stream.assert_called_once()
        call_kw = mock_client.translation.translation_stream.call_args
        assert call_kw.kwargs.get('source_language') == 1


class TestTranscriptionPlugin:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='test-key')
    @patch('crazy_functions.camb_ai_utils.time')
    def test_audio_file(self, _mock_time, _mock_conf):
        mock_create_result = MagicMock(task_id="task-123")
        mock_status = MagicMock(status="completed", run_id="run-456")
        mock_transcript = MagicMock()
        mock_transcript.text = "Hello world transcript"
        # Remove segments so hasattr returns False
        del mock_transcript.segments

        mock_client = MagicMock()
        mock_client.transcription.create_transcription.return_value = mock_create_result
        mock_client.transcription.get_transcription_task_status.return_value = mock_status
        mock_client.transcription.get_transcription_result.return_value = mock_transcript

        import tempfile
        audio_file = os.path.join(tempfile.gettempdir(), 'test_transcribe.wav')
        with open(audio_file, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 100)

        try:
            with patch('camb.client.CambAI', return_value=mock_client):
                _toolbox.update_ui = MagicMock(side_effect=_make_update_ui())
                _toolbox.get_log_folder = MagicMock(return_value="/tmp/test_camb_transcription")
                _toolbox.write_history_to_file = MagicMock(return_value="/tmp/hist.md")

                from crazy_functions.CambAI_Transcription import CambAI_Transcription
                chatbot = []
                gen = CambAI_Transcription(
                    audio_file, {}, {"advanced_arg": "1"}, chatbot, [], "", 0
                )
                _consume_generator(gen)

            mock_client.transcription.create_transcription.assert_called_once()
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)


class TestAudioSeparationPlugin:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='test-key')
    @patch('crazy_functions.camb_ai_utils.time')
    def test_audio_file(self, _mock_time, _mock_conf):
        mock_create_result = MagicMock(task_id="task-sep-1")
        mock_status = MagicMock(status="completed", run_id="run-sep-1")
        mock_sep_info = MagicMock()
        mock_sep_info.vocals_url = "https://example.com/vocals.wav"
        mock_sep_info.background_url = "https://example.com/background.wav"

        mock_client = MagicMock()
        mock_client.audio_separation.create_audio_separation.return_value = mock_create_result
        mock_client.audio_separation.get_audio_separation_status.return_value = mock_status
        mock_client.audio_separation.get_audio_separation_run_info.return_value = mock_sep_info

        mock_response = MagicMock()
        mock_response.content = b'RIFF' + b'\x00' * 100
        mock_response.raise_for_status = MagicMock()

        import tempfile
        audio_file = os.path.join(tempfile.gettempdir(), 'test_sep.wav')
        with open(audio_file, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 100)

        try:
            mock_requests = MagicMock()
            mock_requests.get.return_value = mock_response
            with patch('camb.client.CambAI', return_value=mock_client), \
                 patch.dict(sys.modules, {'requests': mock_requests}):
                _toolbox.update_ui = MagicMock(side_effect=_make_update_ui())
                _toolbox.get_log_folder = MagicMock(return_value="/tmp/test_camb_separation")
                _toolbox.write_history_to_file = MagicMock(return_value="/tmp/hist.md")

                from crazy_functions.CambAI_AudioSeparation import CambAI_AudioSeparation
                chatbot = []
                gen = CambAI_AudioSeparation(
                    audio_file, {}, {}, chatbot, [], "", 0
                )
                _consume_generator(gen)

            mock_client.audio_separation.create_audio_separation.assert_called_once()
            assert mock_response.raise_for_status.call_count == 2
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)


class TestVoiceClonePlugin:

    @patch('crazy_functions.camb_ai_utils.get_conf', return_value='test-key')
    def test_voice_clone(self, _mock_conf):
        mock_result = MagicMock(voice_id=99999)
        mock_client = MagicMock()
        mock_client.voice_cloning.create_custom_voice.return_value = mock_result

        import tempfile
        audio_file = os.path.join(tempfile.gettempdir(), 'test_clone.wav')
        with open(audio_file, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 100)

        try:
            with patch('camb.client.CambAI', return_value=mock_client):
                _toolbox.update_ui = MagicMock(side_effect=_make_update_ui())
                _toolbox.get_log_folder = MagicMock(return_value="/tmp/test_camb_clone")
                _toolbox.write_history_to_file = MagicMock(return_value="/tmp/hist.md")

                from crazy_functions.CambAI_VoiceClone import CambAI_VoiceClone
                chatbot = []
                gen = CambAI_VoiceClone(
                    audio_file, {}, {"advanced_arg": "TestVoice,2"}, chatbot, [], "", 0
                )
                _consume_generator(gen)

            mock_client.voice_cloning.create_custom_voice.assert_called_once()
            call_kw = mock_client.voice_cloning.create_custom_voice.call_args
            assert call_kw.kwargs.get('voice_name') == 'TestVoice'
            assert '99999' in str(chatbot)
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)


# ---------------------------------------------------------------------------
# Section 4: TTS endpoint test (mocked)
# ---------------------------------------------------------------------------

class TestFastapiCambTtsBranch:

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_camb_tts_generate_called(self, mock_conf):
        """Verify camb_tts_generate produces WAV bytes for the endpoint path."""
        def conf_side_effect(key):
            defaults = {
                "CAMB_API_KEY": "test-key",
                "CAMB_TTS_LANGUAGE": "en-us",
                "CAMB_TTS_VOICE_ID": 147320,
                "CAMB_TTS_MODEL": "mars-flash",
                "CAMB_TTS_SPEED": 1.0,
            }
            return defaults.get(key, "")

        mock_conf.side_effect = conf_side_effect
        wav_data = b'RIFF' + b'\x00' * 200
        mock_client = MagicMock()
        mock_client.text_to_speech.tts.return_value = [wav_data]

        with patch('camb.client.CambAI', return_value=mock_client):
            language = map_language_to_bcp47("en")
            audio_bytes = camb_tts_generate("Test text", language=language)

        assert audio_bytes[:4] == b'RIFF'
        assert len(audio_bytes) > 0


# ---------------------------------------------------------------------------
# Section 5: Integration tests (live API, skipped without CAMB_API_KEY)
#   Audio playback via macOS `afplay`. Pass --playback to hear output.
# ---------------------------------------------------------------------------

PLAYBACK = os.environ.get("CAMB_TEST_PLAYBACK", "0") == "1"


def _play_wav(wav_bytes, label="audio"):
    """Save WAV bytes to a temp file and play via afplay (macOS)."""
    import tempfile
    import subprocess
    path = os.path.join(tempfile.gettempdir(), f"camb_test_{label}.wav")
    with open(path, 'wb') as f:
        f.write(wav_bytes)
    print(f"\n  [playback] {label}: {path} ({len(wav_bytes)} bytes)")
    try:
        subprocess.run(["afplay", path], check=True, timeout=30)
    except FileNotFoundError:
        print("  [playback] afplay not found — skipping playback (macOS only)")
    except subprocess.TimeoutExpired:
        print("  [playback] afplay timed out")


def _live_conf(api_key):
    """Return a get_conf side_effect that uses a real API key."""
    defaults = {
        "CAMB_API_KEY": api_key,
        "CAMB_TTS_LANGUAGE": "en-us",
        "CAMB_TTS_VOICE_ID": 147320,
        "CAMB_TTS_MODEL": "mars-flash",
        "CAMB_TTS_SPEED": 1.0,
    }
    def _side_effect(key):
        return defaults.get(key, "")
    return _side_effect


@pytest.mark.skipif(
    not os.environ.get("CAMB_API_KEY"),
    reason="CAMB_API_KEY not set — skipping live integration tests"
)
class TestLiveIntegration:

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_live_tts(self, mock_conf):
        """Live TTS call — verifies WAV output from real API and plays audio."""
        api_key = os.environ["CAMB_API_KEY"]
        mock_conf.side_effect = _live_conf(api_key)

        audio = camb_tts_generate("Hello! This is a live test of CAMB AI text to speech.")
        assert len(audio) > 44  # header + data
        assert audio[:4] == b'RIFF'
        print(f"\n  TTS returned {len(audio)} bytes of WAV audio")

        if PLAYBACK:
            _play_wav(audio, label="live_tts")

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_live_tts_chinese(self, mock_conf):
        """Live TTS in Chinese — verifies non-English voice works."""
        api_key = os.environ["CAMB_API_KEY"]
        mock_conf.side_effect = _live_conf(api_key)

        audio = camb_tts_generate("你好，这是一个语音合成测试。", language="zh-cn")
        assert len(audio) > 44
        assert audio[:4] == b'RIFF'
        print(f"\n  TTS (zh-cn) returned {len(audio)} bytes of WAV audio")

        if PLAYBACK:
            _play_wav(audio, label="live_tts_chinese")

    @patch('crazy_functions.camb_ai_utils.get_conf')
    def test_live_translation(self, mock_conf):
        """Live translation call — verifies text returned."""
        api_key = os.environ["CAMB_API_KEY"]
        mock_conf.return_value = api_key

        client = get_camb_client()
        try:
            result = client.translation.translation_stream(
                text="Hello world, this is a translation test.",
                source_language=1,   # English
                target_language=75,  # Chinese
            )
            # SDK may return HttpResponse wrapper or raw object
            if hasattr(result, 'data') and result.data is not None:
                translated = str(result.data)
            elif hasattr(result, 'text'):
                translated = result.text
            elif hasattr(result, '__iter__'):
                translated = ''.join(
                    chunk if isinstance(chunk, str) else chunk.text for chunk in result
                )
            else:
                translated = str(result)
        except Exception as e:
            # translation_stream returns plain text which SDK may fail to parse as JSON;
            # extract the translated text from the error body if present
            body = getattr(e, 'body', None)
            if body and isinstance(body, str) and len(body) > 0:
                translated = body
            else:
                raise

        assert len(translated) > 0
        print(f"\n  Translation result: {translated}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
