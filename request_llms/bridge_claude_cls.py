# encoding: utf-8
# @Time   : 2024/3/6
# @Author : Spike
# @Descr   :
import json
import random
import time
import requests
from common.logger_handler import logger
from common.toolbox import get_conf, update_ui
from common.func_box import extract_link_pf, valid_img_extensions, batch_encode_image

proxies, TIMEOUT_SECONDS, MAX_RETRY, ANTHROPIC_API_KEY = get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY',
                                                                  "ANTHROPIC_API_KEY")


class ClaudeBroInit:

    def __init__(self):
        self.url = 'https://api.anthropic.com/v1/messages'
        self.x_api_key = ANTHROPIC_API_KEY
        self.llm_model = ''
        self.retry = 0

    def __conversation_user(self, user_input):
        what_i_ask_now = {
            "role": "user",
            "content": []
        }
        img_mapping = extract_link_pf(user_input, valid_img_extensions)
        encode_img_map = batch_encode_image(img_mapping)
        for i in encode_img_map:  # 替换图片链接
            user_input = user_input.replace(img_mapping[i], '')
        what_i_ask_now['content'].append({"type": "text",
                                          "text": user_input})
        for fp in encode_img_map:
            what_i_ask_now['content'].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{encode_img_map[fp]['type']}",
                    "data": encode_img_map[fp]['data']
                }
            })
        return what_i_ask_now

    def __conversation_history(self, history):
        conversation_cnt = len(history) // 2
        messages = []
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                # claude 支持上下文
                what_i_have_asked = self.__conversation_user(history[index])
                what_gpt_answer = {
                    "role": "assistant",
                    "content": str(history[index + 1])
                }
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "": continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        return messages

    def generate_payload(self, inputs, llm_kwargs, history, system_prompt, stream):
        self.llm_model = llm_kwargs['llm_model']
        headers = {
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": f"{self.x_api_key}"
        }
        messages = self.__conversation_history(history)
        messages.append(self.__conversation_user(inputs))
        stop = llm_kwargs.get('stop', '').split(',')
        payload = {
            "model": self.llm_model,
            "messages": messages,
            "stream": stream,
            "max_tokens": 4096,
            "stop_sequences": stop if not stop else None,  # 要么列表要么None
            "temperature": llm_kwargs.get('temperature', 1.0),  # 1.0,
            "top_p": llm_kwargs.get('top_p', 1.0),  # 1.0,
            "system": system_prompt
        }
        llm_kwargs.update({'use-key': self.x_api_key})
        return headers, payload

    def _analysis_content(self, chuck):
        chunk_decoded = chuck.decode("utf-8")
        chunk_json = {}
        content = ""
        try:
            chunk_json = json.loads(chunk_decoded[6:])
            content = chunk_json['delta']['text']
        except:
            pass
        return chunk_decoded, chunk_json, content

    def generate_messages(self, inputs, llm_kwargs, history, system_prompt, stream):
        headers, payload = self.generate_payload(inputs, llm_kwargs, history, system_prompt, stream)
        response = requests.post(self.url, headers=headers, proxies=proxies,
                                 json=payload, stream=stream, timeout=TIMEOUT_SECONDS)

        claude_bro_result = ""
        chunk_content = ''
        for chuck in response.iter_lines():
            chunk_decoded, check_json, content = self._analysis_content(chuck)
            chunk_content += chunk_decoded
            if content:
                claude_bro_result += content
                yield content, claude_bro_result, ''
            else:
                error_meg = msg_handle_error(llm_kwargs, chunk_decoded)
                yield content, claude_bro_result, error_meg
        if claude_bro_result:
            logger.error("对话错误\n"+chunk_content)


def msg_handle_error(llm_kwargs, chunk_decoded):
    use_ket = llm_kwargs.get('use-key', '')
    api_key_encryption = use_ket[:8] + '****' + use_ket[-5:]
    if 'invalid_request_error' in chunk_decoded:
        return f"错误的请求格式\n```\n{chunk_decoded}```\n"
    elif 'authentication_error' in chunk_decoded:
        return f"提供了错误的key 或 {api_key_encryption} 失效过期 \n```\n{chunk_decoded}```\n"
    elif 'permission_error' in chunk_decoded:
        return f"你没有权限使用这个模型\n```\n{chunk_decoded}```\n"
    elif 'rate_limit_error' in chunk_decoded:
        return f"{api_key_encryption} 钱钱用完咯\n```\n{chunk_decoded}```\n"
    elif 'api_error' in chunk_decoded:
        return f"阿欧，这个错误很难遇到呢\n```\n{chunk_decoded}```\n"
    elif 'overloaded_error' in chunk_decoded:
        return f"不堪重负中\n```\n{chunk_decoded}```\n"
    elif 'error' in chunk_decoded.lower():
        return f"未知错误\n```\n{chunk_decoded}```\n"
    return ''


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应")  # 刷新界面
    gpt_bro_init = ClaudeBroInit()
    history.extend([inputs, ''])
    stream_response = gpt_bro_init.generate_messages(inputs, llm_kwargs, history, system_prompt, stream)
    for content, gpt_bro_result, error_bro_meg in stream_response:
        chatbot[-1] = [inputs, gpt_bro_result]
        history[-1] = gpt_bro_result
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        if error_bro_meg:
            chatbot[-1] = [inputs, error_bro_meg]
            history = history[:-2]
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            break


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None,
                                  console_slience=False):
    gpt_bro_init = ClaudeBroInit()
    watch_dog_patience = 30  # 看门狗的耐心, 设置10秒即可
    stream_response = gpt_bro_init.generate_messages(inputs, llm_kwargs, history, sys_prompt, True)
    gpt_bro_result = ''
    for content, gpt_bro_result, error_bro_meg in stream_response:
        gpt_bro_result = gpt_bro_result
        if error_bro_meg:
            if len(observe_window) >= 3:
                observe_window[2] = error_bro_meg
            return f'{gpt_bro_result} 对话错误'
            # 观测窗
        if len(observe_window) >= 1:
            observe_window[0] = gpt_bro_result
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                observe_window[2] = "请求超时，程序终止。"
                raise RuntimeError(f"{gpt_bro_result} 程序终止。")
    return gpt_bro_result


if __name__ == '__main__':
    claude = ClaudeBroInit()
    claude.generate_messages('hello ', {'llm_model': 'claude-3-opus-20240229'},
                             [], 'test', True)
