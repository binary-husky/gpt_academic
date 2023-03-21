import json
import gradio as gr
import logging
import traceback
import requests
import importlib
import os

if os.path.exists('config_private.py'):
    # 放自己的秘密如API和代理网址
    from config_private import proxies, API_URL, API_KEY
else:
    from config import proxies, API_URL, API_KEY



def compose_system(system_prompt):
    return {"role": "system", "content": system_prompt}


def compose_user(user_input):
    return {"role": "user", "content": user_input}


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
        yield chatbot, history, "Waiting"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    chat_counter = len(history) // 2

    print(f"chat_counter - {chat_counter}")

    messages = [compose_system(system_prompt)]
    if chat_counter:
        for index in range(0, 2*chat_counter, 2):
            d1 = {}
            d1["role"] = "user"
            d1["content"] = history[index]
            d2 = {}
            d2["role"] = "assistant"
            d2["content"] = history[index+1]
            if d1["content"] != "":
                if d2["content"] != "" or retry:
                    messages.append(d1)
                    messages.append(d2)
            else:
                messages[-1]['content'] = d2['content']
    if retry and chat_counter:
        messages.pop()
    else:
        temp3 = {}
        temp3["role"] = "user"
        temp3["content"] = inputs
        messages.append(temp3)
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
                                json=payload, stream=True, timeout=15)
    except:
        chatbot[-1] = ((chatbot[-1][0], 'Request timeout, network error. please check proxy settings in config.py.'))
        yield chatbot, history, "Requests Timeout"
        raise TimeoutError

    token_counter = 0
    partial_words = ""

    counter = 0
    if stream:
        stream_response =  response.iter_lines()
        while True:
            chunk = next(stream_response)
            # print(chunk)
            
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

                chunkjson = json.loads(chunk.decode()[6:])
                status_text = f"id: {chunkjson['id']}, finish_reason: {chunkjson['choices'][0]['finish_reason']}"
                partial_words = partial_words + \
                    json.loads(chunk.decode()[6:])[
                        'choices'][0]["delta"]["content"]
                if token_counter == 0:
                    history.append(" " + partial_words)
                else:
                    history[-1] = partial_words
                chatbot[-1] = (history[-2], history[-1])
                token_counter += 1
                yield chatbot, history, status_text
