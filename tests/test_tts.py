import edge_tts
import os
import httpx
from toolbox import get_conf


async def test_tts():    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request to the target service
            import tempfile
            import edge_tts
            import wave
            import uuid
            from pydub import AudioSegment
            voice = get_conf("EDGE_TTS_VOICE")
            tts = edge_tts.Communicate(text="测试", voice=voice)
            temp_folder = tempfile.gettempdir()
            temp_file_name = str(uuid.uuid4().hex)
            temp_file = os.path.join(temp_folder, f'{temp_file_name}.mp3')
            await tts.save(temp_file)
            try:
                mp3_audio = AudioSegment.from_file(temp_file, format="mp3")
                mp3_audio.export(temp_file, format="wav")
                with open(temp_file, 'rb') as wav_file: t = wav_file.read()
            except:
                raise RuntimeError("ffmpeg未安装，无法处理EdgeTTS音频。安装方法见`https://github.com/jiaaro/pydub#getting-ffmpeg-set-up`")
        except httpx.RequestError as e:
            raise RuntimeError(f"请求失败: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tts())