# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file, get_log_folder
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
    chatbot.append(['清除本地缓存数据', '执行中. 删除 gpt_log & private_upload'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    import shutil, os
    gpt_log_dir = os.path.join(os.path.dirname(__file__), '..', 'gpt_log')
    private_upload_dir = os.path.join(os.path.dirname(__file__), '..', 'private_upload')
    shutil.rmtree(gpt_log_dir, ignore_errors=True)
    shutil.rmtree(private_upload_dir, ignore_errors=True)

    chatbot.append(['清除本地缓存数据', '执行完成'])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面