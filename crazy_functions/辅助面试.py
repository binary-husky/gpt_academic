from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import threading, time
import numpy as np
from .live_audio.aliyunASR import AliyunASR


class InterviewAssistant(AliyunASR):
    def __init__(self):
        super(InterviewAssistant, self).__init__()
        self.capture_interval = 0.5 # second
        self.stop = False
        self.parsed_text = ""

    def init(self, chatbot):
        # 初始化音频采集线程
        self.captured_audio = np.array([])
        self.keep_latest_n_second = 10
        self.ready_audio_flagment = None
        self.stop = False
        th1 = threading.Thread(target=self.audio_convertion_thread, args=(chatbot._cookies['uuid'],))
        th1.daemon = True
        th1.start()

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
        chatbot.append(["", ""])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        while True:
            self.event_on_result_chg.wait()
            chatbot[-1][0] = self.parsed_text
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
            # if self.event_on_entence_end

            # yield from self.gpt_answer(text, chatbot, history, llm_kwargs)
            # self.ready_audio_flagment = None

@CatchException
def 辅助面试(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # pip install -U openai-whisper
    chatbot.append(["函数插件功能：辅助面试", "辅助面试助手, 正在监听音频 ..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    ia = InterviewAssistant()
    yield from ia.begin(llm_kwargs, plugin_kwargs, chatbot, history)

