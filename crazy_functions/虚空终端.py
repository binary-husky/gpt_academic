from comm_tools.toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from pydantic import BaseModel, Field
from typing import List
from comm_tools.toolbox import CatchException, update_ui, gen_time_str
from comm_tools.toolbox import update_ui_lastest_msg
from request_llm.bridge_all import predict_no_ui_long_connection
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.json_fns.pydantic_io import GptJsonIO
from crazy_functions.vt_fns.vt_modify_config import modify_configuration_hot
from crazy_functions.vt_fns.vt_modify_config import modify_configuration_reboot
from enum import Enum
import copy, json, pickle, os, sys

class IntentionEnum(str, Enum):
    ModifyConfiguration = 'ModifyConfiguration'
    ExecutePlugin = 'ExecutePlugin'
    Chat = 'Chat'

class UserIntention(BaseModel):
    user_prompt: str = Field(description="the content of user input", default="")
    intention_type: IntentionEnum = Field(description="the type of user intention", default=IntentionEnum.Chat)
    user_provide_file: bool = Field(description="whether the user provides a path to a file", default=False)
    user_provide_url: bool = Field(description="whether the user provides a url", default=False)

def execute_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention):
    # 没写完
    pass


"""
def get_fn_lib():
    return {
        "BatchTranslatePDFDocuments_MultiThreaded": ("crazy_functions.批量翻译PDF文档_多线程",  "批量翻译PDF文档"),
        "SummarizingWordDocuments": ("crazy_functions.总结word文档",  "总结word文档"),
        "ImageGeneration": ("crazy_functions.图片生成",  "图片生成"),
        "TranslateMarkdownFromEnglishToChinese": ("crazy_functions.批量Markdown翻译",  "Markdown中译英"),
        "SummaryAudioVideo": ("crazy_functions.总结音视频",  "总结音视频"),
    }

def inspect_dependency(chatbot, history):
    return True

def eval_code(code, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import importlib

    with open('gpt_log/void_terminal_runtime.py', 'w', encoding='utf8') as f:
        f.write(code)

    try:
        AutoAcademic = getattr(importlib.import_module('gpt_log.void_terminal_runtime', 'AutoAcademic'), 'AutoAcademic')
        # importlib.reload(AutoAcademic)
        auto_dict = AutoAcademic()
        selected_function = auto_dict.selected_function
        txt = auto_dict.txt
        fp, fn = get_fn_lib()[selected_function]
        fn_plugin = getattr(importlib.import_module(fp, fn), fn)
        yield from fn_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    except:
        from comm_tools.toolbox import trimmed_format_exc
        chatbot.append(["执行错误", f"\n```\n{trimmed_format_exc()}\n```\n"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

def get_code_block(reply):
    import re
    pattern = r"```([\s\S]*?)```" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    if len(matches) != 1: 
        raise RuntimeError("GPT is not generating proper code.")
    return matches[0].strip('python') #  code block
=======
def chat(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention):
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=txt, inputs_show_user=txt,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=system_prompt
    )
    chatbot[-1] = [txt, gpt_say]
    history.extend([txt, gpt_say])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    pass
>>>>>>> master

@CatchException
def 自动终端(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数, 如温度和top_p等, 一般原样传递下去就行
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("自动终端状态: ", f"正在执行任务: {txt}"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 初始化插件状态
    state = chatbot._cookies.get('plugin_state', None)
    if state is not None:   state = pickle.loads(state)
    else:                   state = {}

    def update_vt_state():
        # 赋予插件锁定 锁定插件回调路径，当下一次用户提交时，会直接转到该函数
        chatbot._cookies['lock_plugin'] = 'crazy_functions.虚空终端->自动终端'
        chatbot._cookies['vt_state'] = pickle.dumps(state)

    # ⭐ ⭐ ⭐ 分析用户意图
    yield from update_ui_lastest_msg(lastmsg=f"正在执行任务: {txt}\n\n分析用户意图中", chatbot=chatbot, history=history, delay=0)
    gpt_json_io = GptJsonIO(UserIntention)
    inputs = "Analyze the intention of the user according to following user input: \n\n" + txt + '\n\n' + gpt_json_io.format_instructions
    run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(
        inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
    user_intention = gpt_json_io.generate_output_auto_repair(run_gpt_fn(inputs, ""), run_gpt_fn)

    # 用户意图: 修改本项目的配置
    if user_intention.intention_type == IntentionEnum.ModifyConfiguration:
        yield from modify_configuration_reboot(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

    # 用户意图: 调度插件
    if user_intention.intention_type == IntentionEnum.ExecutePlugin:
        yield from execute_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

    # 用户意图: 聊天
    if user_intention.intention_type == IntentionEnum.Chat:
        yield from chat(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

    # update_vt_state()

    return





    # # if state == 'wait_user_keyword':
    # #     chatbot._cookies['lock_plugin'] = None          # 解除插件锁定，避免遗忘导致死锁
    # #     chatbot._cookies['plugin_state_0001'] = None    # 解除插件状态，避免遗忘导致死锁

    # #     # 解除插件锁定
    # #     chatbot.append((f"获取关键词：{txt}", ""))
    # #     yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    # #     inputs=inputs_show_user=f"Extract all image urls in this html page, pick the first 5 images and show them with markdown format: \n\n {page_return}"
    # #     gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
    # #         inputs=inputs, inputs_show_user=inputs_show_user,
    # #         llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
    # #         sys_prompt="When you want to show an image, use markdown format. e.g. ![image_description](image_url). If there are no image url provided, answer 'no image url provided'"
    # #     )
    # #     chatbot[-1] = [chatbot[-1][0], gpt_say]
    # yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    # return
"""