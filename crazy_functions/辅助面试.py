from toolbox import update_ui
from toolbox import CatchException, get_conf, write_results_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from request_llm.bridge_all import predict_no_ui_long_connection
import threading, time
import numpy as np
from .live_audio.aliyunASR import AliyunASR
import json



class AsyncGptTask():
    def __init__(self) -> None:
        self.observe_future = []
        self.observe_future_chatbot_index = []

    def gpt_thread_worker(self, i_say, llm_kwargs, history, sys_prompt, observe_window, index):
        try:
            gpt_say_partial = predict_no_ui_long_connection(inputs=i_say, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=observe_window[index])
        except ConnectionAbortedError as token_exceed_err:
            print('至少一个线程任务Token溢出而失败', e)
        except Exception as e:
            print('至少一个线程任务意外失败', e)

    def add_async_gpt_task(self, i_say, chatbot_index, llm_kwargs, history, system_prompt):
        self.observe_future.append([""])
        self.observe_future_chatbot_index.append(chatbot_index)
        cur_index = len(self.observe_future)-1
        th_new = threading.Thread(target=self.gpt_thread_worker, args=(i_say, llm_kwargs, history, system_prompt, self.observe_future, cur_index))
        th_new.daemon = True
        th_new.start()

    def update_chatbot(self, chatbot):
        for of, ofci in zip(self.observe_future, self.observe_future_chatbot_index):
            try:
                chatbot[ofci] = list(chatbot[ofci])
                chatbot[ofci][1] = of[0]
            except:
                self.observe_future = []
                self.observe_future_chatbot_index = []
        return chatbot

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
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        self.agt = AsyncGptTask()

        while True:
            self.event_on_result_chg.wait(timeout=0.25)  # run once every 0.25 second
            chatbot = self.agt.update_chatbot(chatbot)   # 将子线程的gpt结果写入chatbot
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

            if self.event_on_result_chg.is_set(): 
                # update audio decode result
                self.event_on_result_chg.clear()
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1][0] = self.parsed_text
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

            if self.event_on_entence_end.is_set():
                # called when a sentence has ended
                self.event_on_entence_end.clear()
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1] = [self.parsed_sentence, "[waiting gpt reply]"]
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
                # add gpt task 创建子线程请求gpt，避免线程阻塞
                self.agt.add_async_gpt_task(self.parsed_sentence, len(chatbot)-1, llm_kwargs, history, system_prompt)
                chatbot.append(["", ""])
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


@CatchException
def 辅助面试(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # pip install -U openai-whisper
    chatbot.append(["函数插件功能：辅助面试", "辅助面试助手, 正在监听音频 ..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import nls
        from scipy import io
    except:
        chatbot.append(["导入依赖失败", "使用该模块需要额外依赖, 安装方法:```pip install scipy git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git```"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    TOKEN, APPKEY = get_conf('ALIYUN_TOKEN', 'ALIYUN_APPKEY')
    if TOKEN == "" or APPKEY == "":
        chatbot.append(["导入依赖失败", "没有阿里云语音识别APPKEY和TOKEN, 详情见https://help.aliyun.com/document_detail/450255.html"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    ia = InterviewAssistant()
    yield from ia.begin(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

