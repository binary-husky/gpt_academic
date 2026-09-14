"""
    该文件中主要包含三个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui_long_connection：支持多线程
"""

import json
import os
import re
import time
import traceback
import requests
import random
from loguru import logger

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import get_conf, update_ui, is_any_api_key, select_api_key, what_keys, clip_history
from toolbox import trimmed_format_exc, is_the_upload_folder, read_one_api_model_name, log_chat
from toolbox import ChatBotWithCookies, have_any_recent_upload_image_files, encode_image
proxies, TIMEOUT_SECONDS, MAX_RETRY, API_ORG = \
    get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY', 'API_ORG')

timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'

def get_full_error(chunk, stream_response):
    """
        获取完整的从API返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def make_multimodal_input(inputs, image_paths):
    image_base64_array = []
    for image_path in image_paths:
        path = os.path.abspath(image_path)
        base64 = encode_image(path)
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={path}" base64="{base64}"></div>'
        image_base64_array.append(base64)
    return inputs, image_base64_array

def reverse_base64_from_input(inputs):
    pattern = re.compile(r'<br/><br/><div align="center"><img[^<>]+base64="([^"]+)"></div>')
    base64_strings = pattern.findall(inputs)
    return base64_strings

def contain_base64(inputs):
    base64_strings = reverse_base64_from_input(inputs)
    return len(base64_strings) > 0

def append_image_if_contain_base64(inputs):
    if not contain_base64(inputs):
        return inputs
    else:
        image_base64_array = reverse_base64_from_input(inputs)
        pattern = re.compile(r'<br/><br/><div align="center"><img[^><]+></div>')
        inputs = re.sub(pattern, '', inputs)
        res = []
        res.append({
            "type": "text",
            "text": inputs
        })
        for image_base64 in image_base64_array:
            res.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        return res

def remove_image_if_contain_base64(inputs):
    if not contain_base64(inputs):
        return inputs
    else:
        pattern = re.compile(r'<br/><br/><div align="center"><img[^><]+></div>')
        inputs = re.sub(pattern, '', inputs)
        return inputs

def decode_chunk(chunk):
    # 提前读取一些信息 （用于判断异常）
    chunk_decoded = chunk.decode()
    chunkjson = None
    has_choices = False
    choice_valid = False
    has_content = False
    has_reasoning = False
    has_role = False
    try:
        chunkjson = json.loads(chunk_decoded[6:])
        has_choices = 'choices' in chunkjson
        if has_choices: choice_valid = (len(chunkjson['choices']) > 0)
        if has_choices and choice_valid:
            delta = chunkjson['choices'][0].get("delta", {})
            has_content = ("content" in delta and delta["content"] is not None)
            has_reasoning = ("reasoning_content" in delta and delta["reasoning_content"] is not None)
            has_role = ("role" in delta)
    except:
        pass
    return chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_reasoning, has_role

from functools import lru_cache
@lru_cache(maxsize=32)
def verify_endpoint(endpoint):
    """
        检查endpoint是否可用
    """
    if "你亲手写的api名称" in endpoint:
        raise ValueError("Endpoint不正确, 请检查API Route的Endpoint配置! 当前的Endpoint为:" + endpoint)
    return endpoint

def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list=[], sys_prompt:str="", observe_window:list=None, console_silence:bool=False):
    """
    发送至API Route，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        大模型的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    try:
        from request_llms.bridge_all import model_info, apiroute_endpoint
    except:
        model_info = {}
        apiroute_endpoint = "https://www.api-route.com/v1/chat/completions"

    watch_dog_patience = 5 # 看门狗的耐心, 设置5秒即可

    if model_info.get(llm_kwargs['llm_model'], {}).get('openai_disable_stream', False): stream = False
    else: stream = True

    headers, payload = generate_payload(inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=stream)
    retry = 0
    while True:
        try:
            endpoint = verify_endpoint(model_info.get(llm_kwargs['llm_model'], {}).get('endpoint', apiroute_endpoint))
            response = requests.post(endpoint, headers=headers, proxies=proxies,
                                    json=payload, stream=stream, timeout=TIMEOUT_SECONDS); break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY: raise TimeoutError
            if MAX_RETRY!=0: logger.error(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')

    if not stream:
        chunkjson = json.loads(response.content.decode())
        gpt_replying_buffer = chunkjson['choices'][0]["message"]["content"]
        return gpt_replying_buffer

    stream_response = response.iter_lines()
    result = ''
    reasoning_result = ''
    json_data = None
    while True:
        try: chunk = next(stream_response)
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response)
        chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_reasoning, has_role = decode_chunk(chunk)
        if len(chunk_decoded)==0 or chunk_decoded.startswith(':'): continue
        if not chunk_decoded.startswith('data:'):
            error_msg = get_full_error(chunk, stream_response).decode()
            if "reduce the length" in error_msg:
                raise ConnectionAbortedError("API Route拒绝了请求:" + error_msg)
            elif """type":"upstream_error","param":"307""" in error_msg:
                raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
            else:
                raise RuntimeError("API Route拒绝了请求：" + error_msg)
        if ('data: [DONE]' in chunk_decoded): break
        json_data = chunkjson['choices'][0]
        delta = json_data.get("delta", {})
        if len(delta) == 0: break
        if has_reasoning:
            reasoning_result += delta.get("reasoning_content", "")
        if (not has_content) and has_role: continue
        if (not has_content) and (not has_role) and (not has_reasoning): continue
        if has_content:
            result += delta["content"]
            if not console_silence: print(delta["content"], end='')
            if observe_window is not None:
                if len(observe_window) >= 1:
                    observe_window[0] += delta["content"]
                if len(observe_window) >= 2:
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
    if json_data and json_data.get('finish_reason') == 'length':
        raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
    return result


def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot:ChatBotWithCookies,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
    发送至API Route，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是内部调优参数
    history 是之前的对话列表
    chatbot 为WebUI中显示的对话列表，修改它，然后yield出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    try:
        from request_llms.bridge_all import model_info, apiroute_endpoint
    except:
        model_info = {}
        apiroute_endpoint = "https://www.api-route.com/v1/chat/completions"

    if is_any_api_key(inputs):
        chatbot._cookies['api_key'] = inputs
        chatbot.append(("输入已识别为API-Key", what_keys(inputs)))
        yield from update_ui(chatbot=chatbot, history=history, msg="api_key已导入") # 刷新界面
        return
    elif not is_any_api_key(chatbot._cookies['api_key']):
        chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。"))
        yield from update_ui(chatbot=chatbot, history=history, msg="缺少api_key") # 刷新界面
        return

    user_input = inputs
    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    # 多模态模型
    has_multimodal_capacity = model_info.get(llm_kwargs['llm_model'], {}).get('has_multimodal_capacity', False)
    if has_multimodal_capacity:
        has_recent_image_upload, image_paths = have_any_recent_upload_image_files(chatbot, pop=True)
    else:
        has_recent_image_upload, image_paths = False, []
    if has_recent_image_upload:
        _inputs, image_base64_array = make_multimodal_input(inputs, image_paths)
    else:
        _inputs, image_base64_array = inputs, []
    chatbot.append((_inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    # 禁用stream的特殊模型处理
    if model_info.get(llm_kwargs['llm_model'], {}).get('openai_disable_stream', False): stream = False
    else: stream = True

    # check mis-behavior
    if is_the_upload_folder(user_input):
        chatbot[-1] = (inputs, f"[Local Message] 检测到操作错误！当您上传文档之后，需点击“**函数插件区**”按钮进行处理，请勿点击“提交”按钮或者“基础功能区”按钮。")
        yield from update_ui(chatbot=chatbot, history=history, msg="正常") # 刷新界面
        time.sleep(2)

    try:
        headers, payload = generate_payload(inputs, llm_kwargs, history, system_prompt, image_base64_array, has_multimodal_capacity, stream)
    except RuntimeError as e:
        chatbot[-1] = (inputs, f"您提供的api-key不满足要求，不包含任何可用于{llm_kwargs['llm_model']}的api-key。您可能选择了错误的模型或请求源。")
        yield from update_ui(chatbot=chatbot, history=history, msg="api-key不满足要求") # 刷新界面
        return

    # 检查endpoint是否合法
    try:
        endpoint = verify_endpoint(model_info.get(llm_kwargs['llm_model'], {}).get('endpoint', apiroute_endpoint))
    except:
        tb_str = '```\n' + trimmed_format_exc() + '```'
        chatbot[-1] = (inputs, tb_str)
        yield from update_ui(chatbot=chatbot, history=history, msg="Endpoint不满足要求") # 刷新界面
        return

    # 加入历史
    if has_recent_image_upload:
        history.extend([_inputs, ""])
    else:
        history.extend([inputs, ""])

    retry = 0
    while True:
        try:
            response = requests.post(endpoint, headers=headers, proxies=proxies,
                                    json=payload, stream=stream, timeout=TIMEOUT_SECONDS);break
        except:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], timeout_bot_msg))
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时"+retry_msg) # 刷新界面
            if retry > MAX_RETRY: raise TimeoutError

    if not stream:
        try:
            chunkjson = json.loads(response.content.decode())
            gpt_replying_buffer = chunkjson['choices'][0]["message"]["content"]
            log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=gpt_replying_buffer)
            history[-1] = gpt_replying_buffer
            chatbot[-1] = (history[-2], history[-1])
            yield from update_ui(chatbot=chatbot, history=history)
        except Exception as e:
            yield from update_ui(chatbot=chatbot, history=history, msg="Json解析异常" + response.text)
        return

    if stream:
        gpt_replying_buffer = ""
        gpt_reasoning_buffer = ""
        is_head_of_the_stream = True
        stream_response = response.iter_lines()
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                chunk_decoded = chunk.decode()
                error_msg = chunk_decoded
                if len(gpt_replying_buffer.strip()) > 0 and len(error_msg) == 0:
                    break
                chatbot, history = handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg)
                yield from update_ui(chatbot=chatbot, history=history, msg="API Route返回了错误:" + chunk.decode())
                return

            chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_reasoning, has_role = decode_chunk(chunk)

            if is_head_of_the_stream and (r'"object":"error"' not in chunk_decoded) and (r"content" not in chunk_decoded):
                is_head_of_the_stream = False; continue

            if chunk:
                try:
                    if (has_choices and not choice_valid) or chunk_decoded.startswith(':'):
                        continue
                    if ('data: [DONE]' not in chunk_decoded) and len(chunk_decoded) > 0 and (chunkjson is None):
                        raise ValueError(f'无法读取以下数据，请检查配置。\n\n{chunk_decoded}')
                    if ('data: [DONE]' in chunk_decoded) or (len(chunkjson['choices'][0].get("delta", {})) == 0):
                        log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=gpt_replying_buffer)
                        break
                    status_text = f"finish_reason: {chunkjson['choices'][0].get('finish_reason', 'null')}"
                    delta = chunkjson['choices'][0]["delta"]
                    if has_reasoning:
                        gpt_reasoning_buffer += delta.get("reasoning_content", "")
                    if has_content:
                        gpt_replying_buffer += delta["content"]
                    elif has_role or has_reasoning:
                        pass
                    else:
                        if delta.get("content") is None and not has_reasoning:
                            continue

                    if gpt_reasoning_buffer:
                        paragraphs = ''.join([f'<p style="margin: 1.25em 0;">{line}</p>' for line in gpt_reasoning_buffer.split('\n')])
                        display_text = f'<div class="reasoning_process">{paragraphs}</div>\n\n---\n\n' + gpt_replying_buffer
                    else:
                        display_text = gpt_replying_buffer

                    history[-1] = display_text
                    chatbot[-1] = (history[-2], history[-1])
                    yield from update_ui(chatbot=chatbot, history=history, msg=status_text)
                except Exception as e:
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析不合常规")
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    error_msg = chunk_decoded
                    chatbot, history = handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg)
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析异常" + error_msg)
                    logger.error(error_msg)
                    return
        return


def handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg):
    try:
        from request_llms.bridge_all import model_info
    except:
        model_info = {}
    apiroute_website = ' 请访问 API Route 官网查看详情 https://www.api-route.com'
    if "reduce the length" in error_msg:
        if len(history) >= 2: history[-1] = ""; history[-2] = ""
        tokenizer = model_info.get(llm_kwargs['llm_model'], {}).get('tokenizer', None)
        max_token = model_info.get(llm_kwargs['llm_model'], {}).get('max_token', 128000)
        history = clip_history(inputs=inputs, history=history, tokenizer=tokenizer,
                                               max_token_limit=max_token)
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Reduce the length. 本次输入过长, 或历史数据过长. 历史缓存数据已部分释放, 您可以再次尝试.")
    elif "does not exist" in error_msg or "model_not_found" in error_msg:
        chatbot[-1] = (chatbot[-1][0], f"[Local Message] Model {llm_kwargs['llm_model']} does not exist. 模型在平台中不存在，或未上架。" + apiroute_website)
    elif "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Incorrect API key. API Route以提供了不正确的API_KEY为由拒绝服务。" + apiroute_website)
    elif "exceeded your current quota" in error_msg or "insufficient_quota" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Insufficient quota. API Route账户余额或额度不足。" + apiroute_website)
    else:
        from toolbox import regular_txt_to_markdown
        tb_str = '```\n' + trimmed_format_exc() + '```'
        chatbot[-1] = (chatbot[-1][0], f"[Local Message] 异常 \n\n{tb_str} \n\n{regular_txt_to_markdown(chunk_decoded)}")
    return chatbot, history

def generate_payload(inputs:str, llm_kwargs:dict, history:list, system_prompt:str, image_base64_array:list=[], has_multimodal_capacity:bool=False, stream:bool=True):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    try:
        from request_llms.bridge_all import model_info
    except:
        model_info = {}

    if not is_any_api_key(llm_kwargs['api_key']):
        raise AssertionError("你提供了错误的API_KEY。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。")

    api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    if API_ORG.startswith('org-'): headers.update({"OpenAI-Organization": API_ORG})

    if has_multimodal_capacity:
        enable_multimodal_capacity = (len(image_base64_array) > 0) or any([contain_base64(h) for h in history])
    else:
        enable_multimodal_capacity = False

    conversation_cnt = len(history) // 2
    openai_disable_system_prompt = model_info.get(llm_kwargs['llm_model'], {}).get('openai_disable_system_prompt', False)

    if openai_disable_system_prompt:
        messages = [{"role": "user", "content": system_prompt}]
    else:
        messages = [{"role": "system", "content": system_prompt}]

    if not enable_multimodal_capacity:
        if conversation_cnt:
            for index in range(0, 2*conversation_cnt, 2):
                what_i_have_asked = {}
                what_i_have_asked["role"] = "user"
                what_i_have_asked["content"] = remove_image_if_contain_base64(history[index])
                what_gpt_answer = {}
                what_gpt_answer["role"] = "assistant"
                what_gpt_answer["content"] = remove_image_if_contain_base64(history[index+1])
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
    else:
        if conversation_cnt:
            for index in range(0, 2*conversation_cnt, 2):
                what_i_have_asked = {}
                what_i_have_asked["role"] = "user"
                what_i_have_asked["content"] = append_image_if_contain_base64(history[index])
                what_gpt_answer = {}
                what_gpt_answer["role"] = "assistant"
                what_gpt_answer["content"] = append_image_if_contain_base64(history[index+1])
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "": continue
                    if what_gpt_answer["content"] == timeout_bot_msg: continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = []
        what_i_ask_now["content"].append({
            "type": "text",
            "text": inputs
        })
        for image_base64 in image_base64_array:
            what_i_ask_now["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        messages.append(what_i_ask_now)

    model = llm_kwargs['llm_model']
    if llm_kwargs['llm_model'].startswith('api-route-'):
        model = llm_kwargs['llm_model'][len('api-route-'):]
        model, _ = read_one_api_model_name(model)
    elif llm_kwargs['llm_model'].startswith('apiroute-'):
        model = llm_kwargs['llm_model'][len('apiroute-'):]
        model, _ = read_one_api_model_name(model)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": llm_kwargs.get('temperature', 1.0),
        "top_p": llm_kwargs.get('top_p', 1.0),
        "n": 1,
        "stream": stream,
    }

    return headers, payload
