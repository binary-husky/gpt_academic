from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import threading

class InterviewAssistent():

    def __init__(self):
        pass

    
    # def audio_capture_thread(self):

        # 第7步：所有线程同时开始执行任务函数
        # handles = [ for index, fp in enumerate(file_manifest)]




    def init(self):
        self.captured_words = ""
        # threading.Thread(target=self.audio_capture_thread, args=(self, 1))


    def begin(self, llm_kwargs, plugin_kwargs, chatbot, history):
        while True:
            break
            # yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面







@CatchException
def 辅助面试(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    pass
    # pip install -U openai-whisper
    # while True:
    #     time.sleep(4)
    #     print(plugin_kwargs)
    # ia = InterviewAssistent()
    # yield from ia.begin(llm_kwargs, plugin_kwargs, chatbot, history)

