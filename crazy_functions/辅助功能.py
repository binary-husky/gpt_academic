# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
from toolbox import update_ui, get_conf, get_user
from toolbox import CatchException
from toolbox import default_user_name
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import shutil
import os


@CatchException
def 猜你想问(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    if txt:
        show_say = txt
        prompt = txt+'\n回答完问题后，再列出用户可能提出的三个问题。'
    else:
        prompt = history[-1]+"\n分析上述回答，再列出用户可能提出的三个问题。"
        show_say = '分析上述回答，再列出用户可能提出的三个问题。'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=prompt,
        inputs_show_user=show_say,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=history,
        sys_prompt=system_prompt
    )
    chatbot[-1] = (show_say, gpt_say)
    history.extend([show_say, gpt_say])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面


@CatchException
def 清除缓存(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    chatbot.append(['清除本地缓存数据', '执行中. 删除数据'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    def _get_log_folder(user=default_user_name):
        PATH_LOGGING = get_conf('PATH_LOGGING')
        _dir = os.path.join(PATH_LOGGING, user)
        if not os.path.exists(_dir): os.makedirs(_dir)
        return _dir

    def _get_upload_folder(user=default_user_name):
        PATH_PRIVATE_UPLOAD = get_conf('PATH_PRIVATE_UPLOAD')
        _dir = os.path.join(PATH_PRIVATE_UPLOAD, user)
        return _dir

    shutil.rmtree(_get_log_folder(get_user(chatbot)), ignore_errors=True)
    shutil.rmtree(_get_upload_folder(get_user(chatbot)), ignore_errors=True)

    chatbot.append(['清除本地缓存数据', '执行完成'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面