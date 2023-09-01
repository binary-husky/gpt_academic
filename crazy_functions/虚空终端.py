from pydantic import BaseModel, Field
from typing import List
from toolbox import CatchException, update_ui, gen_time_str
from toolbox import update_ui_lastest_msg
from request_llm.bridge_all import predict_no_ui_long_connection
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.json_fns.pydantic_io import GptJsonIO
from crazy_functions.vt_fns.vt_modify_config import modify_configuration_hot
from crazy_functions.vt_fns.vt_modify_config import modify_configuration_reboot
from crazy_functions.vt_fns.vt_call_plugin import execute_plugin
from enum import Enum
import copy, json, pickle, os, sys


class UserIntention(BaseModel):
    user_prompt: str = Field(description="the content of user input", default="")
    intention_type: str = Field(description="the type of user intention, choose from ['ModifyConfiguration', 'ExecutePlugin', 'Chat']", default="Chat")
    user_provide_file: bool = Field(description="whether the user provides a path to a file", default=False)
    user_provide_url: bool = Field(description="whether the user provides a url", default=False)

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

def analyze_with_rule(txt):
    user_intention = UserIntention()
    user_intention.user_prompt = txt
    is_certain = False

    if '调用插件' in txt:
        is_certain = True
        user_intention.intention_type = 'ExecutePlugin'

    if '修改配置' in txt:
        is_certain = True
        user_intention.intention_type = 'ModifyConfiguration'

    return is_certain, user_intention

@CatchException
def 自动终端(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数, 如温度和top_p等, 一般原样传递下去就行
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
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
    is_certain, user_intention = analyze_with_rule(txt)
    if not is_certain:
        yield from update_ui_lastest_msg(lastmsg=f"正在执行任务: {txt}\n\n分析用户意图中", chatbot=chatbot, history=history, delay=0)
        gpt_json_io = GptJsonIO(UserIntention)
        inputs = "Analyze the intention of the user according to following user input: \n\n" + txt + '\n\n' + gpt_json_io.format_instructions
        run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(
            inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
        user_intention = gpt_json_io.generate_output_auto_repair(run_gpt_fn(inputs, ""), run_gpt_fn)
    else:
        pass

    # 用户意图: 修改本项目的配置
    if user_intention.intention_type == 'ModifyConfiguration':
        yield from modify_configuration_reboot(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

    # 用户意图: 调度插件
    if user_intention.intention_type == 'ExecutePlugin':
        yield from execute_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

    # 用户意图: 聊天
    if user_intention.intention_type == 'Chat':
        yield from chat(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention)

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
