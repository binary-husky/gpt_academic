import os
import threading
from toolbox import get_conf
from loguru import logger as logging

timeout_bot_msg = '[Local Message] Request timeout. Network error.'
#os.environ['VOLC_ACCESSKEY'] = ''
#os.environ['VOLC_SECRETKEY'] = ''

class YUNQUERequestInstance():
    def __init__(self):

        self.time_to_yield_event = threading.Event()
        self.time_to_exit_event = threading.Event()

        self.result_buf = ""

    def generate(self, inputs, llm_kwargs, history, system_prompt):
        # import _thread as thread
        from volcengine.maas import MaasService, MaasException

        maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')

        YUNQUE_SECRET_KEY, YUNQUE_ACCESS_KEY,YUNQUE_MODEL = get_conf("YUNQUE_SECRET_KEY", "YUNQUE_ACCESS_KEY","YUNQUE_MODEL")
        maas.set_ak(YUNQUE_ACCESS_KEY) #填写 VOLC_ACCESSKEY
        maas.set_sk(YUNQUE_SECRET_KEY) #填写 'VOLC_SECRETKEY'

        self.result_buf = ""

        req = {
        "model": {
            "name": YUNQUE_MODEL,
            "version": "1.0", # use default version if not specified.
        },
        "parameters": {
            "max_new_tokens": 4000,  # 输出文本的最大tokens限制
            "min_new_tokens": 1,  # 输出文本的最小tokens限制
            "temperature": llm_kwargs['temperature'],  # 用于控制生成文本的随机性和创造性，Temperature值越大随机性越大，取值范围0~1
            "top_p": llm_kwargs['top_p'],  # 用于控制输出tokens的多样性，TopP值越大输出的tokens类型越丰富，取值范围0~1
            "top_k": 0,  # 选择预测值最大的k个token进行采样，取值范围0-1000，0表示不生效
            "max_prompt_tokens": 4000,  # 最大输入 token 数，如果给出的 prompt 的 token 长度超过此限制，取最后 max_prompt_tokens 个 token 输入模型。
        },
            "messages": self.generate_message_payload(inputs, llm_kwargs, history, system_prompt)
        }

        response = maas.stream_chat(req)

        for resp in response:
            self.result_buf += resp.choice.message.content
            yield self.result_buf
        '''
        for event in response.events():
            if event.event == "add":
                self.result_buf += event.data
                yield self.result_buf
            elif event.event == "error" or event.event == "interrupted":
                raise RuntimeError("Unknown error:" + event.data)
            elif event.event == "finish":
                yield self.result_buf
                break
            else:
                raise RuntimeError("Unknown error:" + str(event))

        logging.info(f'[raw_input] {inputs}')
        logging.info(f'[response] {self.result_buf}')
        '''
        return self.result_buf

    def generate_message_payload(inputs, llm_kwargs, history, system_prompt):
        from volcengine.maas import ChatRole
        conversation_cnt = len(history) // 2
        messages = [{"role": ChatRole.USER, "content": system_prompt},
                    {"role": ChatRole.ASSISTANT, "content": "Certainly!"}]
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                what_i_have_asked = {}
                what_i_have_asked["role"] = ChatRole.USER
                what_i_have_asked["content"] = history[index]
                what_gpt_answer = {}
                what_gpt_answer["role"] = ChatRole.ASSISTANT
                what_gpt_answer["content"] = history[index + 1]
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "":
                        continue
                    if what_gpt_answer["content"] == timeout_bot_msg:
                        continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        what_i_ask_now = {}
        what_i_ask_now["role"] = ChatRole.USER
        what_i_ask_now["content"] = inputs
        messages.append(what_i_ask_now)
        return messages