#! .\venv\
# encoding: utf-8
# @Time   : 2023/7/23
# @Author : Spike
# @Descr   :
from comm_tools import toolbox
from comm_tools import func_box
from crazy_functions import crazy_box
import os


@toolbox.CatchException
def 批量分析流程图或图片(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    chatbot_with_cookie = toolbox.ChatBotWithCookies(chatbot)
    chatbot_with_cookie.write_list(chatbot)
    file_handle = crazy_box.Utils()
    task_info, kdocs_manifest_tmp, proj_dir = crazy_box.get_kdocs_from_everything(txt, type='', ipaddr=llm_kwargs['ipaddr'])
    if txt:
        if os.path.exists(txt):
            file_manifest = file_handle.global_search_for_files(txt, matching=file_handle.picture_format)
            yield from crazy_box.ocr_batch_processing(file_manifest, chatbot, history, llm_kwargs=llm_kwargs)
        elif kdocs_manifest_tmp != []:
            yield from crazy_box.ocr_batch_processing(kdocs_manifest_tmp, chatbot, history, llm_kwargs=llm_kwargs)
        else:
            chatbot.append([crazy_box.previously_on_plugins, None])
            yield from toolbox.update_ui(chatbot, history)
    else:
        chatbot.append([f'空空如也的输入框，{crazy_box.previously_on_plugins}', None])
        yield from toolbox.update_ui(chatbot, history)