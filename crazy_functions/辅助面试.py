from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import threading, time
import numpy as np

def take_audio_sentence_flagment(captured_audio):
    """
    判断音频是否到达句尾，如果到了，截取片段
    """
    ready_part = None
    other_part = captured_audio
    return ready_part, other_part

class InterviewAssistent():
    def __init__(self):
        self.capture_interval = 1.0 # second
        self.stop = False
        pass

    def init(self, chatbot):
        # 初始化音频采集线程
        self.captured_audio = np.array([])
        self.keep_latest_n_second = 10
        self.ready_audio_flagment = None
        self.stop = False
        th1 = threading.Thread(target=self.audio_capture_thread, args=(chatbot._cookies['uuid'],))
        th1.daemon = True
        th1.start()
        th2 = threading.Thread(target=self.audio2txt_thread, args=(chatbot._cookies['uuid'],))
        th2.daemon = True
        th2.start()

    def audio_capture_thread(self, uuid):
        # 在一个异步线程中采集音频
        from .live_audio.audio_io import RealtimeAudioDistribution
        rad = RealtimeAudioDistribution()
        while not self.stop:
            time.sleep(self.capture_interval)
            self.captured_audio = np.concatenate((self.captured_audio, rad.read(uuid.hex)))
            if len(self.captured_audio) > self.keep_latest_n_second * rad.rate:
                self.captured_audio = self.captured_audio[-self.keep_latest_n_second * rad.rate:]

    def audio2txt_thread(self, llm_kwargs):
        import whisper
        # 在一个异步线程中音频转文字
        while not self.stop:
            time.sleep(1)
            if len(self.captured_audio) > 0:
                model = whisper.load_model("base")
                result = model.transcribe("audio.mp3", language='Chinese')

    def gpt_answer(self, text, chatbot, history, llm_kwargs):
        i_say = inputs_show_user = text
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=inputs_show_user,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
            sys_prompt="你是求职者，正在参加面试，请回答问题。"
        )
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        history.extend([i_say, gpt_say])

    def begin(self, llm_kwargs, plugin_kwargs, chatbot, history):
        # 面试插件主函数
        self.init(chatbot)
        while True:
            time.sleep(self.capture_interval)
            if self.ready_audio_flagment:
                audio_for_whisper = self.ready_audio_flagment
                text = self.audio2txt(audio_for_whisper, llm_kwargs)
                yield from self.gpt_answer(text, chatbot, history, llm_kwargs)
                self.ready_audio_flagment = None

@CatchException
def 辅助面试(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # pip install -U openai-whisper
    chatbot.append(["函数插件功能：辅助面试", "正在预热本地音频转文字模型 ..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    import whisper
    whisper.load_model("base")
    chatbot.append(["预热本地音频转文字模型完成", "辅助面试助手, 正在监听音频 ..."])

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    ia = InterviewAssistent()
    yield from ia.begin(llm_kwargs, plugin_kwargs, chatbot, history)

