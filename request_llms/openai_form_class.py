import json
import time
import gradio as gr
import logging
import traceback
import requests
import importlib
import random

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import (
    get_conf,
    update_ui,
    trimmed_format_exc,
    is_the_upload_folder,
    read_one_api_model_name,
)

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf(
    "proxies", "TIMEOUT_SECONDS", "MAX_RETRY"
)

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)


def get_full_error(chunk, stream_response):
    """
    尝试获取完整的错误信息
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def decode_chunk(chunk):
    """
    用于解读"content"和"finish_reason"的内容
    """
    chunk = chunk.decode()
    respose = ""
    finish_reason = "False"
    try:
        chunk = json.loads(chunk)
    except:
        pass
    try:
        respose = chunk["choices"][0]["delta"]["content"]
        finish_reason = chunk["choices"][0]["finish_reason"]
    except:
        pass
    return respose, finish_reason


def generate_message(input, model, key, history, token, system_prompt, temperature):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    api_key = f"Bearer {key}"

    headers = {"Content-Type": "application/json", "Authorization": api_key}

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2 * conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index + 1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]["content"] = what_gpt_answer["content"]
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = input
    messages.append(what_i_ask_now)
    playload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
        "max_tokens": token,
    }
    try:
        print(f" {model} : {conversation_cnt} : {input[:100]} ..........")
    except:
        print("输入中可能存在乱码。")
    return headers, playload
