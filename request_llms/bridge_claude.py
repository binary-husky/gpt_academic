# 借鉴了 https://github.com/GaiZhenbiao/ChuanhuChatGPT 项目

"""
    该文件中主要包含2个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui_long_connection：支持多线程
"""

import os
import json
import time
import gradio as gr
import logging
import traceback
import requests
import importlib

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from comm_tools.toolbox import get_conf, update_ui, trimmed_format_exc, ProxyNetworkActivate
proxies, TIMEOUT_SECONDS, MAX_RETRY, ANTHROPIC_API_KEY = \
    get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY', 'ANTHROPIC_API_KEY')

timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'

def get_full_error(chunk, stream_response):
    """
        获取完整的从Openai返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None, console_slience=False):
    """
    发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        chatGPT的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    from anthropic import Anthropic
    watch_dog_patience = 5 # 看门狗的耐心, 设置5秒即可
    prompt = generate_payload(inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=True)
    retry = 0
    if len(ANTHROPIC_API_KEY) == 0:
        raise RuntimeError("没有设置ANTHROPIC_API_KEY选项")

    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            from .bridge_all import model_info
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            # endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
            # with ProxyNetworkActivate()
            stream = anthropic.completions.create(
                prompt=prompt,
                max_tokens_to_sample=4096,       # The maximum number of tokens to generate before stopping.
                model=llm_kwargs['llm_model'],
                stream=True,
                temperature = llm_kwargs['temperature']
            )
            break
        except Exception as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY: raise TimeoutError
            if MAX_RETRY!=0: print(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')
    result = ''
    try: 
        for completion in stream:
            result += completion.completion
            if not console_slience: print(completion.completion, end='')
            if observe_window is not None: 
                # 观测窗，把已经获取的数据显示出去
                if len(observe_window) >= 1: observe_window[0] += completion.completion
                # 看门狗，如果超过期限没有喂狗，则终止
                if len(observe_window) >= 2:  
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
    except Exception as e:
        traceback.print_exc()

    return result


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
    发送至chatGPT，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是chatGPT的内部调优参数
    history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
    chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    from anthropic import Anthropic
    if len(ANTHROPIC_API_KEY) == 0:
        chatbot.append((inputs, "没有设置ANTHROPIC_API_KEY"))
        yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面
        return
    
    if additional_fn is not None:
        from comm_tools.core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    raw_input = inputs
    logging.info(f'[raw_input] {raw_input}')
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    try:
        prompt = generate_payload(inputs, llm_kwargs, history, system_prompt, stream)
    except RuntimeError as e:
        chatbot[-1] = (inputs, f"您提供的api-key不满足要求，不包含任何可用于{llm_kwargs['llm_model']}的api-key。您可能选择了错误的模型或请求源。")
        yield from update_ui(chatbot=chatbot, history=history, msg="api-key不满足要求") # 刷新界面
        return

    history.append(inputs); history.append("")

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=True
            from .bridge_all import model_info
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            # endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
            # with ProxyNetworkActivate()
            stream = anthropic.completions.create(
                prompt=prompt,
                max_tokens_to_sample=4096,       # The maximum number of tokens to generate before stopping.
                model=llm_kwargs['llm_model'],
                stream=True,
                temperature = llm_kwargs['temperature']
            )
            
            break
        except:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], timeout_bot_msg))
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时"+retry_msg) # 刷新界面
            if retry > MAX_RETRY: raise TimeoutError

    gpt_replying_buffer = ""
    
    for completion in stream:
        try:
            gpt_replying_buffer = gpt_replying_buffer + completion.completion
            history[-1] = gpt_replying_buffer
            chatbot[-1] = (history[-2], history[-1])
            yield from update_ui(chatbot=chatbot, history=history, msg='正常') # 刷新界面

        except Exception as e:
            from comm_tools.toolbox import regular_txt_to_markdown
            tb_str = '```\n' + trimmed_format_exc() + '```'
            chatbot[-1] = (chatbot[-1][0], f"[Local Message] 异常 \n\n{tb_str}")
            yield from update_ui(chatbot=chatbot, history=history, msg="Json异常" + tb_str) # 刷新界面
            return
        



# https://github.com/jtsang4/claude-to-chatgpt/blob/main/claude_to_chatgpt/adapter.py
def convert_messages_to_prompt(messages):
    prompt = ""
    role_map = {
        "system": "Human",
        "user": "Human",
        "assistant": "Assistant",
    }
    for message in messages:
        role = message["role"]
        content = message["content"]
        transformed_role = role_map[role]
        prompt += f"\n\n{transformed_role.capitalize()}: {content}"
    prompt += "\n\nAssistant: "
    return prompt

def generate_payload(inputs, llm_kwargs, history, system_prompt, stream):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index+1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "": continue
                if what_gpt_answer["content"] == timeout_bot_msg: continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']

    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)
    prompt = convert_messages_to_prompt(messages)

    return prompt


