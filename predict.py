# 借鉴了 https://github.com/GaiZhenbiao/ChuanhuChatGPT 项目

import json
import gradio as gr
import logging
import traceback
import requests
import importlib

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
try: from config_private import proxies, API_URL, API_KEY, TIMEOUT_SECONDS 
except: from config import proxies, API_URL, API_KEY, TIMEOUT_SECONDS

timeout_bot_msg = 'Request timeout, network error. please check proxy settings in config.py.'

def predict(inputs, top_p, temperature, chatbot=[], history=[], system_prompt='', retry=False, 
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

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    chat_counter = len(history) // 2

    print(f"chat_counter - {chat_counter}")

    messages = [{"role": "system", "content": system_prompt}]
    if chat_counter:
        for index in range(0, 2*chat_counter, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index+1]
            if what_i_have_asked["content"] != "":
                if not (what_gpt_answer["content"] != "" or retry): continue
                if what_gpt_answer["content"] == timeout_bot_msg: continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']

    if retry and chat_counter:
        messages.pop()
    else:
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = inputs
        messages.append(what_i_ask_now)
        chat_counter += 1

    # messages
    payload = {
        "model": "gpt-3.5-turbo",
        # "model": "gpt-4",
        "messages": messages, 
        "temperature": temperature,  # 1.0,
        "top_p": top_p,  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    history.append(inputs)

    try:
        # make a POST request to the API endpoint using the requests.post method, passing in stream=True
        response = requests.post(API_URL, headers=headers, proxies=proxies,
                                json=payload, stream=True, timeout=TIMEOUT_SECONDS)
    except:
        chatbot[-1] = ((chatbot[-1][0], timeout_bot_msg))
        yield chatbot, history, "请求超时"
        raise TimeoutError

    token_counter = 0
    partial_words = ""

    counter = 0
    if stream:
        stream_response =  response.iter_lines()
        while True:
            chunk = next(stream_response)
            if chunk == b'data: [DONE]':
                break

            if counter == 0:
                counter += 1
                continue
            counter += 1
            # check whether each line is non-empty
            if chunk:
                # decode each line as response data is in bytes
                try:
                    if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
                        logging.info(f'[response] {chatbot[-1][-1]}')
                        break
                except Exception as e:
                    traceback.print_exc()
                    print(chunk.decode())

                try:
                    chunkjson = json.loads(chunk.decode()[6:])
                    status_text = f"finish_reason: {chunkjson['choices'][0]['finish_reason']}"
                    partial_words = partial_words + json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"]
                    if token_counter == 0:
                        history.append(" " + partial_words)
                    else:
                        history[-1] = partial_words
                    chatbot[-1] = (history[-2], history[-1])
                    token_counter += 1
                    yield chatbot, history, status_text

                except Exception as e:
                    traceback.print_exc()
                    print(chunk.decode())
                    yield chatbot, history, "Json解析不合常规"
