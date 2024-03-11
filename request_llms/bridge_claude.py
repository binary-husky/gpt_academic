# 借鉴了 https://github.com/GaiZhenbiao/ChuanhuChatGPT 项目

"""
    该文件中主要包含2个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui_long_connection：支持多线程
"""

import os
import time
import traceback
from toolbox import get_conf, update_ui, trimmed_format_exc, encode_image, every_image_file_in_path

picture_system_prompt = "\n当回复图像时,必须说明正在回复哪张图像。所有图像仅在最后一个问题中提供,即使它们在历史记录中被提及。请使用'这是第X张图像:'的格式来指明您正在描述的是哪张图像。"
Claude_3_Models = ["claude-3-sonnet-20240229", "claude-3-opus-20240229"]

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import get_conf, update_ui, trimmed_format_exc, ProxyNetworkActivate
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
    if inputs == "":     inputs = "空空如也的输入栏"
    message = generate_payload(inputs, llm_kwargs, history, stream=True, image_paths=None)
    retry = 0
    if len(ANTHROPIC_API_KEY) == 0:
        raise RuntimeError("没有设置ANTHROPIC_API_KEY选项")

    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            from .bridge_all import model_info
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=model_info[llm_kwargs['llm_model']]['endpoint'])
            # endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
            # with ProxyNetworkActivate()
            stream = anthropic.messages.create(
                messages=message,
                max_tokens=4096,       # The maximum number of tokens to generate before stopping.
                model=llm_kwargs['llm_model'],
                stream=True,
                temperature = llm_kwargs['temperature'],
                system=sys_prompt
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
            if completion.type == "message_start" or completion.type == "content_block_start":
                continue
            elif completion.type == "message_stop" or completion.type == "content_block_stop" or completion.type == "message_delta":
                break
            result += completion.delta.text
            if not console_slience: print(completion.delta.text, end='')
            if observe_window is not None:
                # 观测窗，把已经获取的数据显示出去
                if len(observe_window) >= 1: observe_window[0] += completion.delta.text
                # 看门狗，如果超过期限没有喂狗，则终止
                if len(observe_window) >= 2:
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
    except Exception as e:
        traceback.print_exc()

    return result

def make_media_input(history,inputs,image_paths):
    for image_path in image_paths:
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
    return inputs

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
    if inputs == "":     inputs = "空空如也的输入栏"
    from anthropic import Anthropic
    if len(ANTHROPIC_API_KEY) == 0:
        chatbot.append((inputs, "没有设置ANTHROPIC_API_KEY"))
        yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    have_recent_file, image_paths = every_image_file_in_path(chatbot)
    if len(image_paths) > 20:
        chatbot.append((inputs, "图片数量超过api上限(20张)"))
        yield from update_ui(chatbot=chatbot, history=history, msg="等待响应")
        return

    if any([llm_kwargs['llm_model'] == model for model in Claude_3_Models]) and have_recent_file:
        if inputs == "" or inputs == "空空如也的输入栏":     inputs = "请描述给出的图片"
        system_prompt += picture_system_prompt  # 由于没有单独的参数保存包含图片的历史，所以只能通过提示词对第几张图片进行定位
        chatbot.append((make_media_input(history,inputs, image_paths), ""))
        yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面
    else:
        chatbot.append((inputs, ""))
        yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    try:
        message = generate_payload(inputs, llm_kwargs, history, stream, image_paths)
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
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=model_info[llm_kwargs['llm_model']]['endpoint'])
            # endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
            # with ProxyNetworkActivate()
            stream = anthropic.messages.create(
                messages=message,
                max_tokens=4096,       # The maximum number of tokens to generate before stopping.
                model=llm_kwargs['llm_model'],
                stream=True,
                temperature = llm_kwargs['temperature'],
                system=system_prompt
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
        if completion.type == "message_start" or completion.type == "content_block_start":
            continue
        elif completion.type == "message_stop" or completion.type == "content_block_stop" or completion.type == "message_delta":
            break
        try:
            gpt_replying_buffer = gpt_replying_buffer + completion.delta.text
            history[-1] = gpt_replying_buffer
            chatbot[-1] = (history[-2], history[-1])
            yield from update_ui(chatbot=chatbot, history=history, msg='正常') # 刷新界面

        except Exception as e:
            from toolbox import regular_txt_to_markdown
            tb_str = '```\n' + trimmed_format_exc() + '```'
            chatbot[-1] = (chatbot[-1][0], f"[Local Message] 异常 \n\n{tb_str}")
            yield from update_ui(chatbot=chatbot, history=history, msg="Json异常" + tb_str) # 刷新界面
            return

def generate_payload(inputs, llm_kwargs, history, stream, image_paths):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """

    conversation_cnt = len(history) // 2

    messages = []

    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = [{"type": "text", "text": history[index]}]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = [{"type": "text", "text": history[index+1]}]
            if what_i_have_asked["content"][0]["text"] != "":
                if what_i_have_asked["content"][0]["text"] == "": continue
                if what_i_have_asked["content"][0]["text"] == timeout_bot_msg: continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'][0]['text'] = what_gpt_answer['content'][0]['text']

    if any([llm_kwargs['llm_model'] == model for model in Claude_3_Models]) and image_paths:
        base64_images = []
        for image_path in image_paths:
            base64_images.append(encode_image(image_path))
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = []
        for base64_image in base64_images:
            what_i_ask_now["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image,
                }
            })
        what_i_ask_now["content"].append({"type": "text", "text": inputs})
    else:
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = [{"type": "text", "text": inputs}]
    messages.append(what_i_ask_now)
    return messages