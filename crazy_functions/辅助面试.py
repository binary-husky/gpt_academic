from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from request_llm.bridge_all import predict_no_ui_long_connection
import threading, time
import numpy as np
from .live_audio.aliyunASR import AliyunASR
import json

def gpt_thread_worker(i_say, llm_kwargs, history, sys_prompt, observe_window, index):
    try:
        gpt_say_partial = predict_no_ui_long_connection(inputs=i_say, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=observe_window[index])
    except ConnectionAbortedError as token_exceed_err:
        print('至少一个线程任务Token溢出而失败', e)
    except Exception as e:
        print('至少一个线程任务意外失败', e)



class InterviewAssistant(AliyunASR):
    def __init__(self):
        self.capture_interval = 0.5 # second
        self.stop = False
        self.parsed_text = ""
        self.event_on_result_chg = threading.Event()
        self.event_on_entence_end = threading.Event()

    def init(self, chatbot):
        # 初始化音频采集线程
        self.captured_audio = np.array([])
        self.keep_latest_n_second = 10
        self.ready_audio_flagment = None
        self.stop = False
        th1 = threading.Thread(target=self.audio_convertion_thread, args=(chatbot._cookies['uuid'],))
        th1.daemon = True
        th1.start()
        # th2 = threading.Thread(target=self.audio2txt_thread, args=(chatbot._cookies['uuid'],))
        # th2.daemon = True
        # th2.start()

    def test_on_sentence_begin(self, message, *args):
        print("test_on_sentence_begin:{}".format(message))

    def test_on_sentence_end(self, message, *args):
        print("test_on_sentence_end:{}".format(message))
        message = json.loads(message)
        self.parsed_sentence = message['payload']['result']
        self.event_on_entence_end.set()

    def test_on_start(self, message, *args):
        print("test_on_start:{}".format(message))

    def test_on_error(self, message, *args):
        print("on_error args=>{}".format(args))

    def test_on_close(self, *args):
        print("on_close: args=>{}".format(args))

    def test_on_result_chg(self, message, *args):
        print("test_on_chg:{}".format(message))
        message = json.loads(message)
        self.parsed_text = message['payload']['result']
        self.event_on_result_chg.set()

    def test_on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))

    def gpt_answer(self, text, chatbot, history, llm_kwargs):
        i_say = inputs_show_user = text
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=inputs_show_user,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
            sys_prompt="请回答问题。"   # 你是求职者，正在参加面试，
        )
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        history.extend([i_say, gpt_say])

    def begin(self, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
        # main plugin function
        self.init(chatbot)
        chatbot.append(["", ""])
        observe_future = []
        observe_future_chatbot_index = []
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        while True:

            self.event_on_result_chg.wait(timeout=0.5)
            for of, ofci in zip(observe_future, observe_future_chatbot_index):
                try:
                    chatbot[ofci] = list(chatbot[ofci])
                    chatbot[ofci][1] = of[0]
                    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
                except:
                    observe_future = []
                    observe_future_chatbot_index = []

            if self.event_on_result_chg.is_set():
                self.event_on_result_chg.clear()

                # update audio decode result
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1][0] = self.parsed_text
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

            if self.event_on_entence_end.is_set():
                # called when a sentence is done
                self.event_on_entence_end.clear()
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1][0] = self.parsed_sentence
                chatbot[-1][1] = "[waiting gpt reply]"
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
                # add gpt task
                observe_future.append([""])
                observe_future_chatbot_index.append(len(chatbot)-1)
                cur_index = len(observe_future)-1
                th_new = threading.Thread(target=gpt_thread_worker, args=(self.parsed_sentence, llm_kwargs, history, system_prompt, observe_future, cur_index))
                th_new.daemon = True
                th_new.start()
                chatbot.append(["", ""])
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


@CatchException
def 辅助面试(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # pip install -U openai-whisper
    chatbot.append(["函数插件功能：辅助面试", "辅助面试助手, 正在监听音频 ..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    ia = InterviewAssistant()
    yield from ia.begin(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

