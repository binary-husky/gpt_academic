# encoding: utf-8
# @Time   : 2023/12/21
# @Author : Spike
# @Descr   :
import json
import re
import os
import time
from request_llms.com_google import GoogleChatInit
from toolbox import get_conf, update_ui, update_ui_lastest_msg, have_any_recent_upload_image_files, trimmed_format_exc

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY')
timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None,
                                  console_slience=False):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        raise ValueError(f"请配置 GEMINI_API_KEY。")

    genai = GoogleChatInit()
    watch_dog_patience = 5  # 看门狗的耐心, 设置5秒即可
    gpt_replying_buffer = ''
    stream_response = genai.generate_chat(inputs, llm_kwargs, history, sys_prompt)
    for response in stream_response:
        results = response.decode()
        match = re.search(r'"text":\s*"((?:[^"\\]|\\.)*)"', results, flags=re.DOTALL)
        error_match = re.search(r'\"message\":\s*\"(.*?)\"', results, flags=re.DOTALL)
        if match:
            try:
                paraphrase = json.loads('{"text": "%s"}' % match.group(1))
            except:
                raise ValueError(f"解析GEMINI消息出错。")
            buffer = paraphrase['text']
            gpt_replying_buffer += buffer
            if len(observe_window) >= 1:
                observe_window[0] = gpt_replying_buffer
            if len(observe_window) >= 2:
                if (time.time() - observe_window[1]) > watch_dog_patience: raise RuntimeError("程序终止。")
        if error_match:
            raise RuntimeError(f'{gpt_replying_buffer} 对话错误')
    return gpt_replying_buffer


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        yield from update_ui_lastest_msg(f"请配置 GEMINI_API_KEY。", chatbot=chatbot, history=history, delay=0)
        return

    # 适配润色区域
    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    if "vision" in llm_kwargs["llm_model"]:
        have_recent_file, image_paths = have_any_recent_upload_image_files(chatbot)
        if not have_recent_file:
            chatbot.append((inputs, "没有检测到任何近期上传的图像文件，请上传jpg格式的图片，此外，请注意拓展名需要小写"))
            yield from update_ui(chatbot=chatbot, history=history, msg="等待图片") # 刷新界面
            return
        def make_media_input(inputs, image_paths): 
            for image_path in image_paths:
                inputs = inputs + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
            return inputs
        if have_recent_file:
            inputs = make_media_input(inputs, image_paths)

    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history)
    genai = GoogleChatInit()
    retry = 0
    while True:
        try:
            stream_response = genai.generate_chat(inputs, llm_kwargs, history, system_prompt)
            break
        except Exception as e:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], trimmed_format_exc()))
            yield from update_ui(chatbot=chatbot, history=history, msg="请求失败")  # 刷新界面
            return
    gpt_replying_buffer = ""
    gpt_security_policy = ""
    history.extend([inputs, ''])
    for response in stream_response:
        results = response.decode("utf-8")    # 被这个解码给耍了。。
        gpt_security_policy += results
        match = re.search(r'"text":\s*"((?:[^"\\]|\\.)*)"', results, flags=re.DOTALL)
        error_match = re.search(r'\"message\":\s*\"(.*)\"', results, flags=re.DOTALL)
        if match:
            try:
                paraphrase = json.loads('{"text": "%s"}' % match.group(1))
            except:
                raise ValueError(f"解析GEMINI消息出错。")
            gpt_replying_buffer += paraphrase['text']    # 使用 json 解析库进行处理
            chatbot[-1] = (inputs, gpt_replying_buffer)
            history[-1] = gpt_replying_buffer
            yield from update_ui(chatbot=chatbot, history=history)
        if error_match:
            history = history[-2]  # 错误的不纳入对话
            chatbot[-1] = (inputs, gpt_replying_buffer + f"对话错误，请查看message\n\n```\n{error_match.group(1)}\n```")
            yield from update_ui(chatbot=chatbot, history=history)
            raise RuntimeError('对话错误')
    if not gpt_replying_buffer:
        history = history[-2]  # 错误的不纳入对话
        chatbot[-1] = (inputs, gpt_replying_buffer + f"触发了Google的安全访问策略，没有回答\n\n```\n{gpt_security_policy}\n```")
        yield from update_ui(chatbot=chatbot, history=history)



if __name__ == '__main__':
    import sys
    llm_kwargs = {'llm_model': 'gemini-pro'}
    result = predict('Write long a story about a magic backpack.', llm_kwargs, llm_kwargs, [])
    for i in result:
        print(i)
