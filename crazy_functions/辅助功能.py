# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
from comm_tools.toolbox import update_ui, get_conf
from comm_tools.toolbox import CatchException

from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive


@CatchException
def 猜你想问(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
def 清除缓存(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    chatbot.append(['清除本地缓存数据', '执行中. 删除数据'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    import shutil, os
    PATH_PRIVATE_UPLOAD, PATH_LOGGING = get_conf('PATH_PRIVATE_UPLOAD', 'PATH_LOGGING')
    shutil.rmtree(PATH_LOGGING, ignore_errors=True)
    shutil.rmtree(PATH_PRIVATE_UPLOAD, ignore_errors=True)

    chatbot.append(['清除本地缓存数据', '执行完成'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面