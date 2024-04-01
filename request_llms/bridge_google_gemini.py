# encoding: utf-8
# @Time   : 2023/12/21
# @Author : Spike
# @Descr   :
import json
import re
import time
from common.toolbox import get_conf, update_ui, update_ui_lastest_msg
import re
import json
import requests
from common.logger_handler import logger
from typing import Dict, Tuple
from common import func_box
from common import toolbox

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY')
timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'


class GoogleChatInit:
    def __init__(self, llm_kwargs):
        from .bridge_all import model_info
        endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
        self.url_gemini = endpoint + "/%m:streamGenerateContent?key=%k"
        self.retry = 0

    def __conversation_user(self, user_input: str):
        what_i_have_asked = {"role": "user", "parts": []}
        if 'vision' not in self.url_gemini:
            encode_img_map = {}
        else:
            img_mapping = func_box.extract_link_pf(user_input, func_box.valid_img_extensions)
            encode_img_map = func_box.batch_encode_image(img_mapping)
            for i in encode_img_map:  # 替换图片链接
                user_input = user_input.replace(img_mapping[i], '')
        what_i_have_asked['parts'].append({'text': user_input})
        for fp in encode_img_map:
            what_i_have_asked['parts'].append(
                {'inline_data': {
                    "mime_type": f"image/{encode_img_map[fp]['type']}",
                    "data": encode_img_map[fp]['data']
                }})
        return what_i_have_asked

    def __conversation_history(self, history):
        messages = []
        conversation_cnt = len(history) // 2
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                what_i_have_asked = self.__conversation_user(history[index])
                what_gpt_answer = {
                    "role": "model",
                    "parts": [{"text": history[index + 1]}]
                }
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
        return messages

    def generate_chat(self, inputs, llm_kwargs, history, system_prompt):
        headers, payload = self.generate_message_payload(inputs, llm_kwargs, history, system_prompt)
        try:
            response = requests.post(url=self.url_gemini, headers=headers, data=json.dumps(payload).encode('utf-8'),
                                     stream=True, proxies=proxies, timeout=TIMEOUT_SECONDS)
        except Exception as e:
            self.retry += 1
            if self.retry > 3:
                error = toolbox.trimmed_format_exc()
                return error, error, error
            return self.generate_chat(inputs, llm_kwargs, history, system_prompt)
        bro_results = ''
        chunk_all = ''
        for resp in response.iter_lines():
            results = resp.decode("utf-8")
            chunk_all += results
            text_pattern = re.compile(r'"text":\s?"(.*)"', flags=re.DOTALL)
            error_pattern = re.compile(r'"message":\s*"((?:[^"\\]|\\.)*)"', flags=re.DOTALL)
            text_match = re.search(text_pattern, results)
            error_match = re.search(error_pattern, results)
            # 预处理
            if text_match:
                text_match = json.loads('{"text": "%s"}' % text_match.group(1))['text']
                bro_results += text_match
            if error_match:
                error_match = json.loads('{"message": "%s"}' % error_match.group(1))['message']
            yield text_match, bro_results, error_match
        if not chunk_all:
            logger.warning('对话错误', chunk_all)

    def generate_message_payload(self, inputs, llm_kwargs, history, system_prompt) -> Tuple[Dict, Dict]:
        messages = [
            # {"role": "system", "parts": [{"text": system_prompt}]},  # gemini 不允许对话轮次为偶数，所以这个没有用，看后续支持吧。。。
            # {"role": "user", "parts": [{"text": ""}]},
            # {"role": "model", "parts": [{"text": ""}]}
        ]
        self.url_gemini = self.url_gemini.replace(
            '%m', llm_kwargs['llm_model']).replace(
            '%k', toolbox.get_conf('GEMINI_API_KEY')
        )
        header = {'Content-Type': 'application/json'}
        if 'vision' not in self.url_gemini:  # 不是vision 才处理history
            messages.extend(self.__conversation_history(history))  # 处理 history
        messages.append(self.__conversation_user(inputs))  # 处理用户对话
        payload = {
            "contents": messages,
            "generationConfig": {
                "stopSequences": str(llm_kwargs.get('stop', '')).split(' '),
                "temperature": llm_kwargs.get('temperature', 1),
                # "maxOutputTokens": 800,
                "topP": llm_kwargs.get('top_p', 0.8),
                "topK": 10
            }
        }
        return header, payload


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None,
                                  console_slience=False):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        raise ValueError(f"请配置 GEMINI_API_KEY。")

    genai = GoogleChatInit(llm_kwargs)
    watch_dog_patience = 5  # 看门狗的耐心, 设置5秒即可
    gpt_replying_buffer = ''
    stream_response = genai.generate_chat(inputs, llm_kwargs, history, sys_prompt)
    for text_match, results, error_match in stream_response:
        gpt_replying_buffer = results
        if error_match:
            if len(observe_window) >= 3:
                observe_window[2] = error_match
            return f'{results} 对话错误'
        # 观测窗
        if len(observe_window) >= 1:
            observe_window[0] = gpt_replying_buffer
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                observe_window[2] = "请求超时，程序终止。"
                raise RuntimeError("程序终止。")

    return gpt_replying_buffer


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    # 检查API_KEY
    if get_conf("GEMINI_API_KEY") == "":
        yield from update_ui_lastest_msg(f"请配置 GEMINI_API_KEY。", chatbot=chatbot, history=history, delay=0)
        return

    # 适配润色区域
    if additional_fn is not None:
        from common.core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history)
    genai = GoogleChatInit(llm_kwargs)
    retry = 0
    while True:
        try:
            stream_response = genai.generate_chat(inputs, llm_kwargs, history, system_prompt)
            break
        except Exception as e:
            retry += 1
            chatbot[-1] = [chatbot[-1][0], timeout_bot_msg]
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时" + retry_msg)  # 刷新界面
            if retry > MAX_RETRY:
                return Exception('对话错误')
    history.extend([inputs, ''])
    for text_match, results, error_match in stream_response:
        chatbot[-1] = [inputs, results]
        history[-1] = results
        yield from update_ui(chatbot=chatbot, history=history)
        if error_match:
            history = history[-2]  # 错误的不纳入对话
            chatbot[-1] = [inputs, results + f"对话错误，请查看message\n\n```\n{error_match}\n```"]
            yield from update_ui(chatbot=chatbot, history=history)
            return RuntimeError('对话错误')


if __name__ == '__main__':
    import sys

    llm_kwargs = {'llm_model': 'gemini-pro'}
    result = predict('Write long a story about a magic backpack.', llm_kwargs, llm_kwargs, [])
    for i in result:
        print(i)
