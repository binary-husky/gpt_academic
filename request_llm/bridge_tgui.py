'''
Contributed by SagsMug. Modified by binary-husky
https://github.com/oobabooga/text-generation-webui/pull/175
'''

import asyncio
import json
import random
import string
import websockets
import logging
import time
import threading
import importlib
from toolbox import get_conf
LLM_MODEL, = get_conf('LLM_MODEL')

# "TGUI:galactica-1.3b@localhost:7860"
model_name, addr_port = LLM_MODEL.split('@')
assert ':' in addr_port, "LLM_MODEL 格式不正确！" + LLM_MODEL
addr, port = addr_port.split(':')

def random_hash():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(9))

async def run(context, max_token=512):
    params = {
        'max_new_tokens': max_token,
        'do_sample': True,
        'temperature': 0.5,
        'top_p': 0.9,
        'typical_p': 1,
        'repetition_penalty': 1.05,
        'encoder_repetition_penalty': 1.0,
        'top_k': 0,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': True,
        'seed': -1,
    }
    session = random_hash()

    async with websockets.connect(f"ws://{addr}:{port}/queue/join") as websocket:
        while content := json.loads(await websocket.recv()):
            #Python3.10 syntax, replace with if elif on older
            if content["msg"] ==  "send_hash":
                await websocket.send(json.dumps({
                    "session_hash": session,
                    "fn_index": 12
                }))
            elif content["msg"] ==  "estimation":
                pass
            elif content["msg"] ==  "send_data":
                await websocket.send(json.dumps({
                    "session_hash": session,
                    "fn_index": 12,
                    "data": [
                        context,
                        params['max_new_tokens'],
                        params['do_sample'],
                        params['temperature'],
                        params['top_p'],
                        params['typical_p'],
                        params['repetition_penalty'],
                        params['encoder_repetition_penalty'],
                        params['top_k'],
                        params['min_length'],
                        params['no_repeat_ngram_size'],
                        params['num_beams'],
                        params['penalty_alpha'],
                        params['length_penalty'],
                        params['early_stopping'],
                        params['seed'],
                    ]
                }))
            elif content["msg"] ==  "process_starts":
                pass
            elif content["msg"] in ["process_generating", "process_completed"]:
                yield content["output"]["data"][0]
                # You can search for your desired end indicator and 
                #  stop generation by closing the websocket here
                if (content["msg"] == "process_completed"):
                    break





def predict_tgui(inputs, top_p, temperature, chatbot=[], history=[], system_prompt='', stream = True, additional_fn=None):
    """
        发送至chatGPT，流式获取输出。
        用于基础的对话功能。
        inputs 是本次问询的输入
        top_p, temperature是chatGPT的内部调优参数
        history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
        chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
        additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)    # 热更新prompt
        core_functional = core_functional.get_functions()
        if "PreProcess" in core_functional[additional_fn]: inputs = core_functional[additional_fn]["PreProcess"](inputs)  # 获取预处理函数（如果有的话）
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]

    raw_input = "What I would like to say is the following: " + inputs
    logging.info(f'[raw_input] {raw_input}')
    history.extend([inputs, ""])
    chatbot.append([inputs, ""])
    yield chatbot, history, "等待响应"

    prompt = inputs
    tgui_say = ""

    mutable = ["", time.time()]
    def run_coorotine(mutable):
        async def get_result(mutable):
            async for response in run(prompt):
                print(response[len(mutable[0]):])
                mutable[0] = response
                if (time.time() - mutable[1]) > 3: 
                    print('exit when no listener')
                    break
        asyncio.run(get_result(mutable))

    thread_listen = threading.Thread(target=run_coorotine, args=(mutable,), daemon=True)
    thread_listen.start()

    while thread_listen.is_alive():
        time.sleep(1)
        mutable[1] = time.time()
        # Print intermediate steps
        if tgui_say != mutable[0]:
            tgui_say = mutable[0]
            history[-1] = tgui_say
            chatbot[-1] = (history[-2], history[-1])
            yield chatbot, history, "status_text"

    logging.info(f'[response] {tgui_say}')



def predict_tgui_no_ui(inputs, top_p, temperature, history=[], sys_prompt=""):
    raw_input = "What I would like to say is the following: " + inputs
    prompt = inputs
    tgui_say = ""
    mutable = ["", time.time()]
    def run_coorotine(mutable):
        async def get_result(mutable):
            async for response in run(prompt, max_token=20):
                print(response[len(mutable[0]):])
                mutable[0] = response
                if (time.time() - mutable[1]) > 3: 
                    print('exit when no listener')
                    break
        asyncio.run(get_result(mutable))
    thread_listen = threading.Thread(target=run_coorotine, args=(mutable,))
    thread_listen.start()
    while thread_listen.is_alive():
        time.sleep(1)
        mutable[1] = time.time()
    tgui_say = mutable[0]
    return tgui_say
