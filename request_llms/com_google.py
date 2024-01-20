# encoding: utf-8
# @Time   : 2023/12/25
# @Author : Spike
# @Descr   :
import os.path
import re
import json
import requests
from typing import List, Dict, Tuple
from common import func_box
from common import toolbox

proxies, TIMEOUT_SECONDS = toolbox.get_conf('proxies', 'TIMEOUT_SECONDS')


class GoogleChatInit:

    def __init__(self):
        self.url_gemini = 'https://generativelanguage.googleapis.com/v1beta/models/%m:streamGenerateContent?key=%k'

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
        response = requests.post(url=self.url_gemini, headers=headers, data=json.dumps(payload),
                                 stream=True, proxies=proxies, timeout=TIMEOUT_SECONDS)
        bro_results = ''
        for resp in response.iter_lines():
            results = resp.decode("utf-8")
            bro_results += results
            text_pattern = re.compile(r'"text":\s*"((?:[^"\\]|\\.)*)"', flags=re.DOTALL)
            error_pattern = re.compile(r'"message":\s*"((?:[^"\\]|\\.)*)"', flags=re.DOTALL)
            text_match = re.search(text_pattern, results)
            error_match = re.search(error_pattern, results)
            # 预处理
            if text_match:
                text_match = json.loads('{"text": "%s"}' % text_match.group(1))['text']
            if error_match:
                error_match = json.loads('{"message": "%s"}' % text_match.group(1))['message']
            yield text_match, error_match, bro_results

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


if __name__ == '__main__':
    gootle = GoogleChatInit()
