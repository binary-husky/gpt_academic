from http import HTTPStatus
from toolbox import get_conf
import threading

timeout_bot_msg = '[Local Message] Request timeout. Network error.'

class QwenRequestInstance():
    def __init__(self):
        import dashscope
        self.time_to_yield_event = threading.Event()
        self.time_to_exit_event = threading.Event()
        self.result_buf = ""

        def validate_key():
            DASHSCOPE_API_KEY = get_conf("DASHSCOPE_API_KEY")
            if DASHSCOPE_API_KEY == '': return False
            return True

        if not validate_key():
            raise RuntimeError('请配置 DASHSCOPE_API_KEY')
        dashscope.api_key = get_conf("DASHSCOPE_API_KEY")


    def generate(self, inputs, llm_kwargs, history, system_prompt):
        # import _thread as thread
        from dashscope import Generation
        QWEN_MODEL = {
            'qwen-turbo': Generation.Models.qwen_turbo,
            'qwen-plus': Generation.Models.qwen_plus,
            'qwen-max': Generation.Models.qwen_max,
        }[llm_kwargs['llm_model']]
        top_p = llm_kwargs.get('top_p', 0.8)
        if top_p == 0: top_p += 1e-5
        if top_p == 1: top_p -= 1e-5

        self.result_buf = ""
        responses = Generation.call(
            model=QWEN_MODEL,
            messages=generate_message_payload(inputs, llm_kwargs, history, system_prompt),
            top_p=top_p,
            temperature=llm_kwargs.get('temperature', 1.0),
            result_format='message',
            stream=True,
            incremental_output=True
        )

        for response in responses:
            if response.status_code == HTTPStatus.OK:
                if response.output.choices[0].finish_reason == 'stop':
                    try:
                        self.result_buf += response.output.choices[0].message.content
                    except:
                        pass
                    yield self.result_buf
                    break
                elif response.output.choices[0].finish_reason == 'length':
                    self.result_buf += "[Local Message] 生成长度过长，后续输出被截断"
                    yield self.result_buf
                    break
                else:
                    self.result_buf += response.output.choices[0].message.content
                    yield self.result_buf
            else:
                self.result_buf += f"[Local Message] 请求错误：状态码：{response.status_code}，错误码:{response.code}，消息：{response.message}"
                yield self.result_buf
                break

        # 耗尽generator避免报错
        while True:
            try: next(responses)
            except: break

        return self.result_buf


def generate_message_payload(inputs, llm_kwargs, history, system_prompt):
    conversation_cnt = len(history) // 2
    if system_prompt == '': system_prompt = 'Hello!'
    messages = [{"role": "user", "content": system_prompt}, {"role": "assistant", "content": "Certainly!"}]
    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index+1]
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
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)
    return messages
