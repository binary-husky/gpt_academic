# encoding: utf-8
# @Time   : 2024/1/22
# @Author : Kilig947 & binary husky
# @Descr   : 兼容最新的智谱Ai
from toolbox import get_conf
from toolbox import get_conf, encode_image, get_pictures_list
import requests
import json
class TaichuChatInit:
    def __init__(self): ...

    def __conversation_user(self, user_input: str, llm_kwargs:dict):
        return {"role": "user", "content": user_input}

    def __conversation_history(self, history:list, llm_kwargs:dict):
        messages = []
        conversation_cnt = len(history) // 2
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                what_i_have_asked = self.__conversation_user(history[index], llm_kwargs)
                what_gpt_answer = {
                    "role": "assistant",
                    "content": history[index + 1]
                }
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
        return messages

    def generate_chat(self, inputs:str, llm_kwargs:dict, history:list, system_prompt:str):
        TAICHU_API_KEY = get_conf("TAICHU_API_KEY")
        params = {
            'api_key': TAICHU_API_KEY,
            'model_code': 'taichu_llm',
            'question': '\n\n'.join(history) + inputs,
            'prefix': system_prompt,
            'temperature': llm_kwargs.get('temperature', 0.95),
            'stream_format': 'json'
        }

        api = 'https://ai-maas.wair.ac.cn/maas/v1/model_api/invoke'
        response = requests.post(api, json=params, stream=True)
        results = ""
        if response.status_code == 200:
            response.encoding = 'utf-8'
            for line in response.iter_lines(decode_unicode=True):
                try: delta = json.loads(line)['data']['content']
                except: delta = json.loads(line)['choices'][0]['text']
                results += delta
                yield delta, results
        else:
            raise ValueError


if __name__ == '__main__':
    zhipu = TaichuChatInit()
    zhipu.generate_chat('你好', {'llm_model': 'glm-4'}, [], '你是WPSAi')
