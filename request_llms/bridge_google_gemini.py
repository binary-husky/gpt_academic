# encoding: utf-8
# @Time   : 2023/12/21
# @Author : Spike
# @Descr   :
import json
import re
import time
from request_llms.com_google import GoogleChatInit
from common.toolbox import get_conf, update_ui, update_ui_lastest_msg

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY')
timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None,
                                  console_slience=False):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        raise ValueError(f"请配置 GEMINI_API_KEY。")

    genai = GoogleChatInit()
    watch_dog_patience = 30  # 看门狗的耐心, 设置10秒即可
    gpt_replying_buffer = ''
    stream_response = genai.generate_chat(inputs, llm_kwargs, history, sys_prompt)
    for text_match, error_match, results in stream_response:
        if text_match:
            gpt_replying_buffer += text_match
        elif error_match:
            if len(observe_window) >= 3:
                observe_window[2] = error_match
            return f'{results} 对话错误'
        # 观测窗
        if len(observe_window) >= 1:
            observe_window[0] = gpt_replying_buffer
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")

    return gpt_replying_buffer


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        yield from update_ui_lastest_msg(f"请配置 GEMINI_API_KEY。", chatbot=chatbot, history=history, delay=0)
        return

    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history)
    genai = GoogleChatInit()
    retry = 0
    while True:
        try:
            stream_response = genai.generate_chat(inputs, llm_kwargs, history, system_prompt)
            break
        except Exception as e:
            retry += 1
            chatbot[-1] = [(chatbot[-1][0], timeout_bot_msg)]
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时" + retry_msg)  # 刷新界面
            if retry > MAX_RETRY:
                return Exception('对话错误')
    gpt_replying_buffer = ""
    gpt_replying_result = ""
    history.extend([inputs, ''])
    for text_match, error_match, results in stream_response:
        gpt_replying_result += results
        if text_match:
            gpt_replying_buffer += text_match
            chatbot[-1] = [inputs, gpt_replying_buffer]
            history[-1] = gpt_replying_buffer
            yield from update_ui(chatbot=chatbot, history=history)
        if error_match:
            history = history[-2]  # 错误的不纳入对话
            chatbot[-1] = [inputs, gpt_replying_buffer + f"对话错误，请查看message\n\n```\n{error_match}\n```"]
            yield from update_ui(chatbot=chatbot, history=history)
            return RuntimeError('对话错误')
    if not gpt_replying_buffer:
        history = history[-2]  # 错误的不纳入对话
        chatbot[-1] = [inputs, gpt_replying_buffer + f"详细返回\n\n```\n{json.loads(gpt_replying_result)}\n```"]
        yield from update_ui(chatbot=chatbot, history=history)
        return Exception('对话错误')


if __name__ == '__main__':
    import sys
    llm_kwargs = {'llm_model': 'gemini-pro'}
    result = predict('Write long a story about a magic backpack.', llm_kwargs, llm_kwargs, [])
    for i in result:
        print(i)
