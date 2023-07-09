from toolbox import update_ui
from toolbox import CatchException, get_conf, markdown_convertion
from crazy_functions.crazy_utils import input_clipping
from request_llm.bridge_all import predict_no_ui_long_connection
import threading, time
import numpy as np
from .live_audio.aliyunASR import AliyunASR
import json

class WatchDog():
    def __init__(self, timeout, bark_fn, interval=3, msg="") -> None:
        self.last_feed = None
        self.timeout = timeout
        self.bark_fn = bark_fn
        self.interval = interval
        self.msg = msg
    
    def watch(self):
        while True:
            if time.time() - self.last_feed > self.timeout:
                if len(self.msg) > 0: print(self.msg)
                self.bark_fn()
                break
            time.sleep(self.interval)

    def begin_watch(self):
        self.last_feed = time.time()
        th = threading.Thread(target=self.watch)
        th.daemon = True
        th.start()

    def feed(self):
        self.last_feed = time.time()

def chatbot2history(chatbot):
    history = []
    for c in chatbot:
        for q in c:
            if q not in ["[请讲话]", "[等待GPT响应]"]:
                history.append(q.strip('<div class="markdown-body">').strip('</div>').strip('<p>').strip('</p>'))
    return history

class AsyncGptTask():
    def __init__(self) -> None:
        self.observe_future = []
        self.observe_future_chatbot_index = []

    def gpt_thread_worker(self, i_say, llm_kwargs, history, sys_prompt, observe_window, index):
        try:
            MAX_TOKEN_ALLO = 2560
            i_say, history = input_clipping(i_say, history, max_token_limit=MAX_TOKEN_ALLO)
            gpt_say_partial = predict_no_ui_long_connection(inputs=i_say, llm_kwargs=llm_kwargs, history=history, sys_prompt=sys_prompt, 
                                                            observe_window=observe_window[index], console_slience=True)
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
                chatbot[ofci][1] = markdown_convertion(of[0])
            except:
                self.observe_future = []
                self.observe_future_chatbot_index = []
        return chatbot

class InterviewAssistant(AliyunASR):
    def __init__(self):
        self.capture_interval = 0.5 # second
        self.stop = False
        self.parsed_text = ""
        self.parsed_sentence = ""
        self.buffered_sentence = ""
        self.event_on_result_chg = threading.Event()
        self.event_on_entence_end = threading.Event()
        self.event_on_commit_question = threading.Event()

    def __del__(self):
        self.stop = True

    def init(self, chatbot):
        # 初始化音频采集线程
        self.captured_audio = np.array([])
        self.keep_latest_n_second = 10
        self.commit_after_pause_n_second = 1.5
        self.ready_audio_flagment = None
        self.stop = False
        self.plugin_wd = WatchDog(timeout=5, bark_fn=self.__del__, msg="程序终止")
        self.aut = threading.Thread(target=self.audio_convertion_thread, args=(chatbot._cookies['uuid'],))
        self.aut.daemon = True
        self.aut.start()
        # th2 = threading.Thread(target=self.audio2txt_thread, args=(chatbot._cookies['uuid'],))
        # th2.daemon = True
        # th2.start()

    def no_audio_for_a_while(self):
        if len(self.buffered_sentence) < 7: # 如果一句话小于7个字，暂不提交
            self.commit_wd.begin_watch()
        else:
            self.event_on_commit_question.set()

    def begin(self, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
        # main plugin function
        self.init(chatbot)
        chatbot.append(["[请讲话]", "[等待GPT响应]"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        self.plugin_wd.begin_watch()
        self.agt = AsyncGptTask()
        self.commit_wd = WatchDog(timeout=self.commit_after_pause_n_second, bark_fn=self.no_audio_for_a_while, interval=0.2)
        self.commit_wd.begin_watch()

        while True:
            self.event_on_result_chg.wait(timeout=0.25)  # run once every 0.25 second
            chatbot = self.agt.update_chatbot(chatbot)   # 将子线程的gpt结果写入chatbot
            history = chatbot2history(chatbot)
            yield from update_ui(chatbot=chatbot, history=history)      # 刷新界面
            self.plugin_wd.feed()

            if self.event_on_result_chg.is_set(): 
                # update audio decode result
                self.event_on_result_chg.clear()
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1][0] = self.buffered_sentence + self.parsed_text
                history = chatbot2history(chatbot)
                yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
                self.commit_wd.feed()

            if self.event_on_entence_end.is_set():
                # called when a sentence has ended
                self.event_on_entence_end.clear()
                self.parsed_text = self.parsed_sentence
                self.buffered_sentence += self.parsed_sentence

            if self.event_on_commit_question.is_set():
                # called when a question should be commited
                self.event_on_commit_question.clear()
                if len(self.buffered_sentence) == 0: raise RuntimeError

                self.commit_wd.begin_watch()
                chatbot[-1] = list(chatbot[-1])
                chatbot[-1] = [self.buffered_sentence, "[等待GPT响应]"]
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
                # add gpt task 创建子线程请求gpt，避免线程阻塞
                history = chatbot2history(chatbot)
                self.agt.add_async_gpt_task(self.buffered_sentence, len(chatbot)-1, llm_kwargs, history, system_prompt)
                
                self.buffered_sentence = ""
                chatbot.append(["[请讲话]", "[等待GPT响应]"])
                yield from update_ui(chatbot=chatbot, history=history) # 刷新界面




@CatchException
def 语音助手(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # pip install -U openai-whisper
    chatbot.append(["对话助手函数插件：使用时，双手离开鼠标键盘吧", "音频助手, 正在听您讲话（点击“停止”键可终止程序）..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import nls
        from scipy import io
    except:
        chatbot.append(["导入依赖失败", "使用该模块需要额外依赖, 安装方法:```pip install --upgrade pyOpenSSL scipy git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git```"])
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

