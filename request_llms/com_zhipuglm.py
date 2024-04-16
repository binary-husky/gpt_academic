# encoding: utf-8
# @Time   : 2024/1/22
# @Author : Spike
# @Descr   : 兼容最新的智谱Ai
import requests
import time
import jwt
import json
from common.toolbox import get_conf
from common import func_box, toolbox

proxies, TIMEOUT_SECONDS = toolbox.get_conf('proxies', 'TIMEOUT_SECONDS')


def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


class ZhipuChatInit:

    def __init__(self):
        self.ZHIPUAI_API_KEY = get_conf("ZHIPUAI_API_KEY")
        # self.zhipu_bro = ZhipuAI(api_key=self.ZHIPUAI_API_KEY, timeout=60)
        self.model = 'glm-4'
        self.zhipu_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'

    def __conversation_user(self, user_input: str):
        if '4v' not in self.model:
            return {"role": "user", "content": user_input}
        else:
            img_mapping = func_box.extract_link_pf(user_input, func_box.valid_img_extensions)
            encode_img_map = func_box.batch_encode_image(img_mapping)
            for i in encode_img_map:  # 替换图片链接    st.dataframe(online_handler.set_date_style(df))

                user_input = user_input.replace(img_mapping[i], '')
            what_i_have_asked = {"role": "user", "content": []}
            what_i_have_asked['content'].append({"type": 'text', "text": user_input})
            for fp in encode_img_map:
                img_d = {"type": "image_url",
                         "image_url": {'url': encode_img_map[fp]['data']}}
                what_i_have_asked['content'].append(img_d)
            return what_i_have_asked

    def __conversation_history(self, history):
        messages = []
        conversation_cnt = len(history) // 2
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                what_i_have_asked = self.__conversation_user(history[index])
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
        messages.extend(self.__conversation_history(history))  # 处理 history
        messages.append(self.__conversation_user(inputs))  # 处理用户对话
        # response = self.zhipu_bro.chat.completions.create(
        #     model=self.model, messages=messages, stream=True,
        #     temperature=llm_kwargs.get('temperature', 0.95)*0.95,  # 石乐志，只能传默认的temperature 和 top_p
        #     top_p=llm_kwargs.get('top_p', 0.7)*0.7,
        #     max_tokens=llm_kwargs.get('max_tokens', 1024 * 4),  # 最大输出模型的一半
        # )     pydantic 版本太高、不使用SDK调用
        zhipu_token = generate_token(self.ZHIPUAI_API_KEY, 60)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {zhipu_token}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": llm_kwargs.get('temperature', 1) * 0.95,
            "top_p": llm_kwargs.get('top_p', 1) * 0.7,
            "max_tokens": llm_kwargs.get('max_tokens', 1024 * 4),
            "stream": True
        }
        if llm_kwargs.get('stop'):
            # 目前仅支持单个单词，并且不能传空
            payload.update({"stop": llm_kwargs.get('stop', '').split(' ')[:1]})
        return headers, payload
        messages.extend(self.__conversation_history(history, llm_kwargs))  # 处理 history
        if inputs.strip() == "":  # 处理空输入导致报错的问题 https://github.com/binary-husky/gpt_academic/issues/1640 提示 {"error":{"code":"1214","message":"messages[1]:content和tool_calls 字段不能同时为空"}
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

    def generate_chat(self, inputs, llm_kwargs, history, system_prompt):
        headers, payload = self.__conversation_message_payload(inputs, llm_kwargs, history, system_prompt)
        response = requests.post(url=self.zhipu_url, headers=headers, data=json.dumps(payload).encode('utf-8'),
                                 stream=True, proxies=proxies, timeout=TIMEOUT_SECONDS)
        bro_results = ''
        for resp in response.iter_lines():
            chunk = resp.decode("utf-8")
            chunk_index = chunk.find('{')
            if chunk_index != -1:
                bro_loads = json.loads(chunk[chunk_index:])
                if bro_loads.get('error'):
                    bro_chunk = json.dumps(bro_loads, indent=4, ensure_ascii=False)
                    bro_results += f"\n```json\n{bro_chunk}\n"
                    yield bro_chunk, bro_results
                    continue
                bro_chunk = bro_loads['choices'][0]['delta']['content']
                bro_results += bro_chunk
                yield bro_chunk, bro_results
            else:
                # print(chunk)
                pass


if __name__ == '__main__':
    zhipu = ZhipuChatInit()
    zhipu.generate_chat('你好', {'llm_model': 'glm-4'}, [], '你是WPSAi')
