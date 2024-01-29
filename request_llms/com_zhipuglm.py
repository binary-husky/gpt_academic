# encoding: utf-8
# @Time   : 2024/1/22
# @Author : Kilig947 & binary husky
# @Descr   : 兼容最新的智谱Ai
from toolbox import get_conf, have_any_recent_upload_image_files
from zhipuai import ZhipuAI
from .com_google import input_encode_handler
import logging


class ZhipuChatInit:

    def __init__(self):
        ZHIPUAI_API_KEY, ZHIPUAI_MODEL = get_conf("ZHIPUAI_API_KEY", "ZHIPUAI_MODEL")
        if len(ZHIPUAI_MODEL) > 0:
            logging.error('ZHIPUAI_MODEL 配置项选项已经弃用，请在LLM_MODEL中配置')
        self.zhipu_bro = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        self.model = 'glm-4'

    def __conversation_user(self, user_input: str, llm_kwargs):
        if '4v' not in self.model:
            return {"role": "user", "content": user_input}
        else:
            input_, encode_img = input_encode_handler(user_input, llm_kwargs=llm_kwargs)
            what_i_have_asked = {"role": "user", "content": []}
            what_i_have_asked['content'].append({"type": 'text', "text": user_input})
            if encode_img:
                img_d = {"type": "image_url",
                         "image_url": {'url': encode_img}}
                what_i_have_asked['content'].append(img_d)
            return what_i_have_asked

    def __conversation_history(self, history, llm_kwargs):
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

    def __conversation_message_payload(self, inputs, llm_kwargs, history, system_prompt):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        self.model = llm_kwargs['llm_model']
        messages.extend(self.__conversation_history(history))  # 处理 history
        messages.append(self.__conversation_user(inputs))  # 处理用户对话
        response = self.zhipu_bro.chat.completions.create(
            model=self.model, messages=messages, stream=True,
            temperature=llm_kwargs.get('temperature', 0.95)*0.95,  # 石乐志，只能传默认的temperature 和 top_p
            top_p=llm_kwargs.get('top_p', 0.7)*0.7,
            max_tokens=llm_kwargs.get('max_tokens', 1024 * 4),  # 最大输出模型的一半
        )
        return response

    def generate_chat(self, inputs, llm_kwargs, history, system_prompt):
        response = self.__conversation_message_payload(inputs, llm_kwargs, history, system_prompt)
        bro_results = ''
        for chunk in response:
            bro_results += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content, bro_results


if __name__ == '__main__':
    zhipu = ZhipuChatInit()
    zhipu.generate_chat('你好', {'llm_model': 'glm-4'}, [], '你是WPSAi')
