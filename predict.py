# 借鉴了 https://github.com/GaiZhenbiao/ChuanhuChatGPT 项目

import json
import gradio as gr
import logging
import traceback
import requests
import importlib
from colorful import *

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
try: from config_private import proxies, API_URL, API_KEY, TIMEOUT_SECONDS, MAX_RETRY, LLM_MODEL
except: from config import proxies, API_URL, API_KEY, TIMEOUT_SECONDS, MAX_RETRY, LLM_MODEL

timeout_bot_msg = '[local] Request timeout, network error. please check proxy settings in config.py.'

def get_full_error(chunk, stream_response):
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def predict_no_ui(inputs, top_p, temperature, history=[]):
    headers, payload = generate_payload(inputs, top_p, temperature, history, system_prompt="", stream=False)

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            response = requests.post(API_URL, headers=headers, proxies=proxies,
                                    json=payload, stream=False, timeout=TIMEOUT_SECONDS*2); break
        except TimeoutError as e:
            retry += 1
            traceback.print_exc()
            if MAX_RETRY!=0: print(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')
            if retry > MAX_RETRY: raise TimeoutError

    try:
        result = json.loads(response.text)["choices"][0]["message"]["content"]
        return result
    except Exception as e:
        if "choices" not in response.text: print(response.text)
        raise ConnectionAbortedError("Json解析不合常规，可能是文本过长" + response.text)


def predict(inputs, top_p, temperature, chatbot=[], history=[], system_prompt='', 
            stream = True, additional_fn=None):

    if additional_fn is not None:
        import functional
        importlib.reload(functional)
        functional = functional.get_functionals()
        inputs = functional[additional_fn]["Prefix"] + inputs + functional[additional_fn]["Suffix"]

    if stream:
        raw_input = inputs
        logging.info(f'[raw_input] {raw_input}')
        chatbot.append((inputs, ""))
        yield chatbot, history, "等待响应"

    headers, payload = generate_payload(inputs, top_p, temperature, history, system_prompt, stream)
    history.append(inputs); history.append(" ")

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=True
            response = requests.post(API_URL, headers=headers, proxies=proxies,
                                    json=payload, stream=True, timeout=TIMEOUT_SECONDS);break
        except:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], timeout_bot_msg))
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield chatbot, history, "请求超时"+retry_msg
            if retry > MAX_RETRY: raise TimeoutError

    gpt_replying_buffer = ""
    
    is_head_of_the_stream = True
    if stream:
        stream_response =  response.iter_lines()
        while True:
            chunk = next(stream_response)
            # print(chunk.decode()[6:])
            if is_head_of_the_stream:
                # 数据流的第一帧不携带content
                is_head_of_the_stream = False; continue
            
            if chunk:
                try:
                    if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
                        # 判定为数据流的结束，gpt_replying_buffer也写完了
                        logging.info(f'[response] {gpt_replying_buffer}')
                        break
                    # 处理数据流的主体
                    chunkjson = json.loads(chunk.decode()[6:])
                    status_text = f"finish_reason: {chunkjson['choices'][0]['finish_reason']}"
                    # 如果这里抛出异常，一般是文本过长，详情见get_full_error的输出
                    gpt_replying_buffer = gpt_replying_buffer + json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"]
                    history[-1] = gpt_replying_buffer
                    chatbot[-1] = (history[-2], history[-1])
                    yield chatbot, history, status_text

                except Exception as e:
                    traceback.print_exc()
                    yield chatbot, history, "Json解析不合常规，很可能是文本过长"
                    chunk = get_full_error(chunk, stream_response)
                    error_msg = chunk.decode()
                    if "reduce the length" in error_msg:
                        chatbot[-1] = (history[-1], "[local] input is too long, reduce input or clear history.")
                    yield chatbot, history, "Json解析不合常规，很可能是文本过长" + error_msg
                    return

def generate_payload(inputs, top_p, temperature, history, system_prompt, stream):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

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

    payload = {
        "model": LLM_MODEL,
        "messages": messages, 
        "temperature": temperature,  # 1.0,
        "top_p": top_p,  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    
    print(f" {LLM_MODEL} : {conversation_cnt} : {inputs}")
    return headers,payload


