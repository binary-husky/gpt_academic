# encoding: utf-8
# @Time   : 2024/1/22
# @Author : Kilig947 & binary husky
# @Descr   : 兼容最新的智谱Ai
from toolbox import get_conf
from zhipuai import ZhipuAI
from toolbox import get_conf, encode_image, get_pictures_list
from loguru import logger
import os


def input_encode_handler(inputs:str, llm_kwargs:dict):
    if llm_kwargs["most_recent_uploaded"].get("path"):
        image_paths = get_pictures_list(llm_kwargs["most_recent_uploaded"]["path"])
    md_encode = []
    for md_path in image_paths:
        type_ = os.path.splitext(md_path)[1].replace(".", "")
        type_ = "jpeg" if type_ == "jpg" else type_
        md_encode.append({"data": encode_image(md_path), "type": type_})
    return inputs, md_encode


class ZhipuChatInit:

    def __init__(self):
        ZHIPUAI_API_KEY, ZHIPUAI_MODEL = get_conf("ZHIPUAI_API_KEY", "ZHIPUAI_MODEL")
        if len(ZHIPUAI_MODEL) > 0:
            logger.error('ZHIPUAI_MODEL 配置项选项已经弃用，请在LLM_MODEL中配置')
        self.zhipu_bro = ZhipuAI(api_key=ZHIPUAI_API_KEY)
        self.model = ''

    def __conversation_user(self, user_input: str, llm_kwargs:dict):
        if self.model not in ["glm-4v"]:
            return {"role": "user", "content": user_input}
        else:
            input_, encode_img = input_encode_handler(user_input, llm_kwargs=llm_kwargs)
            what_i_have_asked = {"role": "user", "content": []}
            what_i_have_asked['content'].append({"type": 'text', "text": user_input})
            if encode_img:
                if len(encode_img) > 1:
                    logger.warning("glm-4v只支持一张图片,将只取第一张图片进行处理")
                img_d = {"type": "image_url",
                            "image_url": {
                                "url": encode_img[0]['data']
                            }
                        }
                what_i_have_asked['content'].append(img_d)
            return what_i_have_asked

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

    @staticmethod
    def preprocess_param(param, default=0.95, min_val=0.01, max_val=0.99):
        """预处理参数，保证其在允许范围内，并处理精度问题"""
        try:
            param = float(param)
        except ValueError:
            return default

        if param <= min_val:
            return min_val
        elif param >= max_val:
            return max_val
        else:
            return round(param, 2)  # 可挑选精度，目前是两位小数

    def __conversation_message_payload(self, inputs:str, llm_kwargs:dict, history:list, system_prompt:str):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        self.model = llm_kwargs['llm_model']
        messages.extend(self.__conversation_history(history, llm_kwargs))  # 处理 history
        if inputs.strip() == "": # 处理空输入导致报错的问题 https://github.com/binary-husky/gpt_academic/issues/1640 提示 {"error":{"code":"1214","message":"messages[1]:content和tool_calls 字段不能同时为空"}
            inputs = "."    # 空格、换行、空字符串都会报错，所以用最没有意义的一个点代替
        messages.append(self.__conversation_user(inputs, llm_kwargs))  # 处理用户对话
        """
        采样温度，控制输出的随机性，必须为正数
        取值范围是：(0.0, 1.0)，不能等于 0，默认值为 0.95，
        值越大，会使输出更随机，更具创造性；
        值越小，输出会更加稳定或确定
        建议您根据应用场景调整 top_p 或 temperature 参数，但不要同时调整两个参数
        """
        temperature = self.preprocess_param(
            param=llm_kwargs.get('temperature', 0.95),
            default=0.95,
            min_val=0.01,
            max_val=0.99
        )
        """
        用温度取样的另一种方法，称为核取样
        取值范围是：(0.0, 1.0) 开区间，
        不能等于 0 或 1，默认值为 0.7
        模型考虑具有 top_p 概率质量 tokens 的结果
        例如：0.1 意味着模型解码器只考虑从前 10% 的概率的候选集中取 tokens
        建议您根据应用场景调整 top_p 或 temperature 参数，
        但不要同时调整两个参数
        """
        top_p = self.preprocess_param(
            param=llm_kwargs.get('top_p', 0.70),
            default=0.70,
            min_val=0.01,
            max_val=0.99
        )
        response = self.zhipu_bro.chat.completions.create(
            model=self.model, messages=messages, stream=True,
            temperature=temperature,
            top_p=top_p,
            max_tokens=llm_kwargs.get('max_tokens', 1024 * 4),
        )
        return response

    def generate_chat(self, inputs:str, llm_kwargs:dict, history:list, system_prompt:str):
        self.model = llm_kwargs['llm_model']
        response = self.__conversation_message_payload(inputs, llm_kwargs, history, system_prompt)
        bro_results = ''
        for chunk in response:
            bro_results += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content, bro_results


if __name__ == '__main__':
    zhipu = ZhipuChatInit()
    zhipu.generate_chat('你好', {'llm_model': 'glm-4'}, [], '你是WPSAi')
