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

    def __conversation_user(self, user_input):
        what_i_have_asked = {"role": "user", "parts": []}
        if 'vision' not in self.url_gemini:
            input_ = user_input
            encode_img = []
        else:
            input_, encode_img = func_box.input_encode_handler(user_input)
        what_i_have_asked['parts'].append({'text': input_})
        if encode_img:
            for data in encode_img:
                what_i_have_asked['parts'].append(
                    {'inline_data': {
                        "mime_type": f"image/{data['type']}",
                        "data": data['data']
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
        return response.iter_lines()

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
    # print(gootle.generate_message_payload('你好呀', {},
    #                                                 ['123123', '3123123'], ''))
    # gootle.input_encode_handle('123123[123123](./123123), ![53425](./asfafa/fff.jpg)')

    test = '1234124125412412'

    def testfff(t: str):
        ff = t.replace('1', '   hhh')
        print(ff)
    testfff(test)
    print(test)