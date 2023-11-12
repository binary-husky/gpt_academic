from comm_tools.toolbox import get_conf
import threading
import logging

timeout_bot_msg = '[Local Message] Request timeout. Network error.'

class ZhipuRequestInstance():
    def __init__(self):

        self.time_to_yield_event = threading.Event()
        self.time_to_exit_event = threading.Event()

        self.result_buf = ""

    def generate(self, inputs, llm_kwargs, history, system_prompt):
        # import _thread as thread
        import zhipuai
        ZHIPUAI_API_KEY, ZHIPUAI_MODEL = get_conf("ZHIPUAI_API_KEY", "ZHIPUAI_MODEL")
        zhipuai.api_key = ZHIPUAI_API_KEY
        self.result_buf = ""
        response = zhipuai.model_api.sse_invoke(
            model=ZHIPUAI_MODEL,
            prompt=generate_message_payload(inputs, llm_kwargs, history, system_prompt),
            top_p=llm_kwargs['top_p'],
            temperature=llm_kwargs['temperature'],
        )
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
        return self.result_buf

def generate_message_payload(inputs, llm_kwargs, history, system_prompt):
    conversation_cnt = len(history) // 2
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
