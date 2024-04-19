# encoding: utf-8
# @Time   : 2024/1/16
# @Author : Spike
# @Descr   : ...
import os
from moviepy.editor import AudioFileClip


class AudioHandler:

    def __init__(self, audio_path, output_dir=None):
        if output_dir:
            self.output_dir = os.path.join(output_dir, 'markdown')
            os.makedirs(self.output_dir, exist_ok=True)
        self.audio_path = audio_path
        self.file_name = os.path.basename(audio_path).split('.')[0]
        self.content_text = ''

    @staticmethod
    def audio_extraction_text(file):
        import speech_recognition as sr
        # 打开音频文件
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            # 读取音频文件的内容
            audio_content = r.record(source)
            # 使用Google的文字转话服务将音频转换为文字
            text = r.recognize_google(audio_content, language='zh-CN')
        return text

    def video_converters(self):
        temp_path = os.path.join(self.output_dir, f"{self.file_name}")
        videoclip = AudioFileClip(self.audio_path)
        videoclip.write_audiofile(temp_path)
        self.content_text = self.audio_extraction_text(temp_path)
        return
