"""
    该文件中主要包含三个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui：高级实验性功能模块调用，不会实时显示在界面上，参数简单，可以多线程并行，方便实现复杂的功能逻辑
    3. predict_no_ui_long_connection：在实验过程中发现调用predict_no_ui处理长文档时，和openai的连接容易断掉，这个函数用stream的方式解决这个问题，同样支持多线程
"""

import logging
import traceback
import importlib
import openai
import time


# 读取config.py文件中关于AZURE OPENAI API的信息
from toolbox import get_conf, update_ui, clip_history, trimmed_format_exc
TIMEOUT_SECONDS, MAX_RETRY, AZURE_ENGINE, AZURE_ENDPOINT, AZURE_API_VERSION, AZURE_API_KEY = \
    get_conf('TIMEOUT_SECONDS', 'MAX_RETRY',"AZURE_ENGINE","AZURE_ENDPOINT", "AZURE_API_VERSION", "AZURE_API_KEY")


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

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
    发送至azure openai api，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是chatGPT的内部调优参数
    history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
    chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    print(llm_kwargs["llm_model"])    

    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)    # 热更新prompt
        core_functional = core_functional.get_core_functions()
        if "PreProcess" in core_functional[additional_fn]: inputs = core_functional[additional_fn]["PreProcess"](inputs)  # 获取预处理函数（如果有的话）
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]

    raw_input = inputs
    logging.info(f'[raw_input] {raw_input}')
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    
    payload = generate_azure_payload(inputs, llm_kwargs, history, system_prompt, stream)    
        
    history.append(inputs); history.append("")

    retry = 0
    while True:
        try:            
                
            openai.api_type = "azure"            
            openai.api_version = AZURE_API_VERSION
            openai.api_base = AZURE_ENDPOINT
            openai.api_key = AZURE_API_KEY
            response = openai.ChatCompletion.create(timeout=TIMEOUT_SECONDS, **payload);break
        
        except:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], "获取response失败，重试中。。。"))
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时"+retry_msg) # 刷新界面
            if retry > MAX_RETRY: raise TimeoutError
            
    gpt_replying_buffer = ""    
    is_head_of_the_stream = True
    if stream:

        stream_response = response

        while True:
            try:
                chunk = next(stream_response)
                    
            except StopIteration:                
                from toolbox import regular_txt_to_markdown; tb_str = '```\n' + trimmed_format_exc() + '```'
                chatbot[-1] = (chatbot[-1][0], f"[Local Message] 远程返回错误: \n\n{tb_str} \n\n{regular_txt_to_markdown(chunk)}")
                yield from update_ui(chatbot=chatbot, history=history, msg="远程返回错误:" + chunk) # 刷新界面
                return            
            
            if is_head_of_the_stream and (r'"object":"error"' not in chunk):
                # 数据流的第一帧不携带content
                is_head_of_the_stream = False; continue
            
            if chunk:
                #print(chunk)
                try:                     
                    if "delta" in chunk["choices"][0]:
                        if chunk["choices"][0]["finish_reason"] == "stop":
                            logging.info(f'[response] {gpt_replying_buffer}')
                            break
                    status_text = f"finish_reason: {chunk['choices'][0]['finish_reason']}"    
                    gpt_replying_buffer = gpt_replying_buffer + chunk["choices"][0]["delta"]["content"]                               
                       
                    history[-1] = gpt_replying_buffer
                    chatbot[-1] = (history[-2], history[-1])
                    yield from update_ui(chatbot=chatbot, history=history, msg=status_text) # 刷新界面

                except Exception as e:
                    traceback.print_exc()
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析不合常规") # 刷新界面
                    chunk = get_full_error(chunk, stream_response)
                    
                    error_msg = chunk                    
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json异常" + error_msg) # 刷新界面
                    return


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None, console_slience=False):
    """
    发送至AZURE OPENAI API，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
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
    watch_dog_patience = 5 # 看门狗的耐心, 设置5秒即可
    payload = generate_azure_payload(inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=True)
    retry = 0
    while True:

        try:
            openai.api_type = "azure"            
            openai.api_version = AZURE_API_VERSION
            openai.api_base = AZURE_ENDPOINT
            openai.api_key = AZURE_API_KEY
            response = openai.ChatCompletion.create(timeout=TIMEOUT_SECONDS, **payload);break
        
        except:  
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY: raise TimeoutError
            if MAX_RETRY!=0: print(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')     
        

    stream_response =  response
    result = ''
    while True:
        try: chunk = next(stream_response)
        except StopIteration: 
            break
        except:
            chunk = next(stream_response) # 失败了，重试一次？再失败就没办法了。

        if len(chunk)==0: continue
        if not chunk.startswith('data:'): 
            error_msg = get_full_error(chunk, stream_response)
            if "reduce the length" in error_msg:
                raise ConnectionAbortedError("AZURE OPENAI API拒绝了请求:" + error_msg)
            else:
                raise RuntimeError("AZURE OPENAI API拒绝了请求：" + error_msg)
        if ('data: [DONE]' in chunk): break 
        
        delta = chunk["delta"]
        if len(delta) == 0: break
        if "role" in delta: continue
        if "content" in delta: 
            result += delta["content"]
            if not console_slience: print(delta["content"], end='')
            if observe_window is not None: 
                # 观测窗，把已经获取的数据显示出去
                if len(observe_window) >= 1: observe_window[0] += delta["content"]
                # 看门狗，如果超过期限没有喂狗，则终止
                if len(observe_window) >= 2:  
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
        else: raise RuntimeError("意外Json结构："+delta)
    if chunk['finish_reason'] == 'length':
        raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
    return result


def generate_azure_payload(inputs, llm_kwargs, history, system_prompt, stream):
    """
    整合所有信息，选择LLM模型，生成 azure openai api请求，为发送请求做准备
    """    

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
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']

    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)

    payload = {
        "model": llm_kwargs['llm_model'],
        "messages": messages, 
        "temperature": llm_kwargs['temperature'],  # 1.0,
        "top_p": llm_kwargs['top_p'],  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "engine": AZURE_ENGINE
    }
    try:
        print(f" {llm_kwargs['llm_model']} : {conversation_cnt} : {inputs[:100]} ..........")
    except:
        print('输入中可能存在乱码。')
    return payload


