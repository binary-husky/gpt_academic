# encoding: utf-8
# @Time   : 2024/2/27
# @Author : Spike
# @Descr   :
import json
import random
import time
from common.logger_handler import logger
import requests

from common.func_box import extract_link_pf, valid_img_extensions, batch_encode_image
from common.toolbox import get_conf, select_api_key, is_any_api_key, trimmed_format_exc, update_ui, clip_history, read_one_api_model_name
from request_llms.bridge_chatgpt import verify_endpoint

proxies, TIMEOUT_SECONDS, MAX_RETRY, API_ORG, AZURE_CFG_ARRAY, API_URL_REDIRECT = \
    get_conf('proxies', 'TIMEOUT_SECONDS', 'MAX_RETRY', 'API_ORG', 'AZURE_CFG_ARRAY',
             'API_URL_REDIRECT')


class GPTChatInit:

    def __init__(self):
        self.llm_model = ''
        self.retry_sum = 0

    def __conversation_user(self, user_input):
        if 'vision' in self.llm_model:
            what_i_ask_now = {
                "role": "user",
                "content": []
            }
            img_mapping = extract_link_pf(user_input, valid_img_extensions)
            encode_img_map = batch_encode_image(img_mapping)
            for i in encode_img_map:  # 替换图片链接
                user_input = user_input.replace(img_mapping[i], '')
            what_i_ask_now['content'].append({"type": "text",
                                              "text": user_input})
            for fp in encode_img_map:
                what_i_ask_now['content'].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_img_map[fp]['data']}"
                    }
                })
            return what_i_ask_now
        what_i_ask_now = {"role": "user", "content": user_input}
        return what_i_ask_now

    def __conversation_history(self, history):
        conversation_cnt = len(history) // 2
        messages = []
        if conversation_cnt:
            for index in range(0, 2 * conversation_cnt, 2):
                what_i_have_asked = {
                    "role": "user",
                    "content": str(history[index])
                }
                what_gpt_answer = {
                    "role": "assistant",
                    "content": str(history[index + 1])
                }
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "": continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        return messages

    def generate_payload(self, inputs, llm_kwargs, history, system_prompt, stream):
        """
        整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
        """

        if not is_any_api_key(llm_kwargs['api_key']):
            raise AssertionError(
                "你提供了错误的API_KEY。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。")

        self.llm_model = llm_kwargs['llm_model']
        api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
        llm_kwargs.update({'use-key': api_key})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        if API_ORG.startswith('org-'):
            headers.update({"OpenAI-Organization": API_ORG})
        if self.llm_model.startswith('azure-'):
            headers.update({"api-key": api_key})
            if self.llm_model in AZURE_CFG_ARRAY.keys():
                azure_api_key_unshared = AZURE_CFG_ARRAY[self.llm_model]["AZURE_API_KEY"]
                headers.update({"api-key": azure_api_key_unshared})

        messages = [{"role": "system", "content": system_prompt}]
        if 'vision' not in self.llm_model:
            messages.extend(self.__conversation_history(history))
        what_i_ask_now = self.__conversation_user(user_input=inputs)
        messages.append(what_i_ask_now)
        if self.llm_model.startswith('api2d-'):
            self.llm_model = self.llm_model.replace('api2d-', '')
        if self.llm_model == "gpt-3.5-random":  # 随机选择, 绕过openai访问频率限制
            self.llm_model = random.choice([
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
                "gpt-3.5-turbo-0301",
            ])
        if llm_kwargs['llm_model'].startswith('one-api-'):
            model = llm_kwargs['llm_model'][len('one-api-'):]
            model, _ = read_one_api_model_name(model)
        if llm_kwargs['llm_model'].startswith('vllm-'):
            model = llm_kwargs['llm_model'][len('vllm-'):]
            model, _ = read_one_api_model_name(model)
        payload = {
            "model": self.llm_model,
            "messages": messages,
            "temperature": llm_kwargs.get('temperature', 1.0),  # 1.0,
            "top_p": llm_kwargs.get('top_p', 1.0),  # 1.0,
            "n": llm_kwargs.get('n_choices', 1),
            "presence_penalty": llm_kwargs.get('presence_penalty', 2.0),
            "frequency_penalty": llm_kwargs.get('frequency_penalty', 0),
            # "max_context": llm_kwargs['max_context'],  用了会报错，不知道咋回事
            # "max_generation": llm_kwargs['max_generation'],
            # "logit_bias": llm_kwargs['logit_bias'],
            "user": llm_kwargs.get('user_identifier', ''),
            "stream": stream,
            "max_tokens": llm_kwargs.get('max_generation', 4096)
        }
        if 'gpt' in llm_kwargs['llm_model']:
            payload.update({"stop": llm_kwargs.get('stop', '')})
        if '1106' in self.llm_model:
            payload.update({"response_format": {"type": llm_kwargs.get('response_format', "text")}})
        return headers, payload

    @staticmethod
    def _check_endpoint(llm_kwargs):
        # 检查endpoint是否合法
        from request_llms.bridge_all import model_info
        return verify_endpoint(model_info[llm_kwargs['llm_model']]['endpoint'])

    def _analysis_content(self, chuck):
        chunk_decoded = chuck.decode("utf-8")
        chunk_json = {}
        content = ""
        try:
            chunk_json = json.loads(chunk_decoded[6:])
            content = chunk_json['choices'][0]["delta"].get("content", "")
        except:
            pass
        return chunk_decoded, chunk_json, content

    def generate_messages(self, inputs, llm_kwargs, history, system_prompt, stream):
        # make a POST request to the API endpoint, stream=True
        gpt_bro_result = ""
        chunk_content = ''
        endpoint = self._check_endpoint(llm_kwargs)
        if not endpoint:
            raise RuntimeError("你提供了错误的API_ENDPOINT。")
        headers, payload = self.generate_payload(inputs, llm_kwargs, history, system_prompt, stream)
        try:
            if API_URL_REDIRECT:
                proxies = None
            response = requests.post(endpoint, headers=headers, proxies=proxies,
                                     json=payload, stream=stream, timeout=TIMEOUT_SECONDS)
        except Exception as e:
            self.retry_sum += 1
            error = trimmed_format_exc()
            if self.retry_sum > 3:
                logger.error(f'请求失败， {error}')
                return error, error, error
            logger.warning(f'请求失败， {error}')
            return self.generate_messages(inputs, llm_kwargs, history, system_prompt, stream)
        for chuck in response.iter_lines():
            chunk_decoded, check_json, content = self._analysis_content(chuck)
            chunk_content += chunk_decoded + '\n'
            if content:
                gpt_bro_result += content
                yield content, gpt_bro_result, ''
            else:
                error_meg = msg_handle_error(llm_kwargs, chunk_decoded)
                if error_meg:
                    history, retry = msg_handler_history(inputs, history, llm_kwargs, chunk_decoded)
                    if retry and self.retry_sum == 0:
                        self.retry_sum += 1
                        yield content, retry, retry
                        return self.generate_messages(inputs, llm_kwargs, history, system_prompt, stream)
                    yield error_meg, error_meg, error_meg
                    break
        if not gpt_bro_result:
            yield '', chunk_content, chunk_content
            print(chunk_content)


def msg_handler_history(inputs, history, llm_kwargs, chunk_decoded):
    from request_llms.bridge_all import model_info
    retry = False
    if "reduce the length" in chunk_decoded:
        # 清除当前溢出的输入：history[-2] 是本次输入, history[-1] 是本次输出
        if len(history) >= 2: history[-1] = ""; history[-2] = ""
        history = clip_history(inputs=inputs, history=history,
                               tokenizer=model_info[llm_kwargs['llm_model']]['tokenizer'],  # history至少释放二分之一
                               max_token_limit=(model_info[llm_kwargs['llm_model']]['max_token']))
        retry = "[Local Message] Reduce the length. 本次输入过长, 或历史数据过长. 历史缓存数据已部分释放, 重新提交一次"
    return history, retry


def msg_handle_error(llm_kwargs, chunk_decoded):
    use_ket = llm_kwargs.get('use-key', '')
    api_key_encryption = use_ket[:8] + '****' + use_ket[-5:]
    openai_website = f' 请登录OpenAI查看详情 https://platform.openai.com/signup  api-key: `{api_key_encryption}`'
    error_msg = ''
    if "does not exist" in chunk_decoded:
        error_msg = f"[Local Message] Model {llm_kwargs['llm_model']} does not exist. 模型不存在, 或者您没有获得体验资格."
    elif "Incorrect API key" in chunk_decoded:
        error_msg = f"[Local Message] Incorrect API key. OpenAI以提供了不正确的API_KEY为由, 拒绝服务." + openai_website
    elif "exceeded your current quota" in chunk_decoded:
        error_msg = "[Local Message] You exceeded your current quota. OpenAI以账户额度不足为由, 拒绝服务." + openai_website
    elif "account is not active" in chunk_decoded:
        error_msg = "[Local Message] Your account is not active. OpenAI以账户失效为由, 拒绝服务." + openai_website
    elif "associated with a deactivated account" in chunk_decoded:
        error_msg = "[Local Message] You are associated with a deactivated account. OpenAI以账户失效为由, 拒绝服务." + openai_website
    elif "API key has been deactivated" in chunk_decoded:
        error_msg = "[Local Message] API key has been deactivated. OpenAI以账户失效为由, 拒绝服务." + openai_website
    elif "bad forward key" in chunk_decoded:
        error_msg = "[Local Message] Bad forward key. API2D账户额度不足."
    elif "Not enough point" in chunk_decoded:
        error_msg = "[Local Message] Not enough point. API2D账户点数不足."
    elif 'error' in str(chunk_decoded).lower():
        try:
            error_msg = json.dumps(json.loads(chunk_decoded[:6]), indent=4, ensure_ascii=False)
        except:
            error_msg = chunk_decoded
    return error_msg


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history, msg=f"初始化{llm_kwargs.get('llm_model')}模型")  # 刷新界面
    gpt_bro_init = GPTChatInit()
    history.extend([inputs, ''])
    stream_response = gpt_bro_init.generate_messages(inputs, llm_kwargs, history, system_prompt, stream)
    yield from update_ui(chatbot=chatbot, history=history, msg=f"等待`{llm_kwargs.get('llm_model')}`模型响应")  # 刷新界面
    for content, gpt_bro_result, error_bro_meg in stream_response:
        chatbot[-1] = [inputs, gpt_bro_result]
        history[-1] = gpt_bro_result
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        if error_bro_meg:
            chatbot[-1] = [inputs, error_bro_meg]
            history = history[:-2]
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            break


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None,
                                  console_slience=False):
    gpt_bro_init = GPTChatInit()
    watch_dog_patience = 60  # 看门狗的耐心, 设置10秒即可
    stream_response = gpt_bro_init.generate_messages(inputs, llm_kwargs, history, sys_prompt, True)
    gpt_bro_result = ''
    for content, gpt_bro_result, error_bro_meg in stream_response:
        gpt_bro_result = gpt_bro_result
        if error_bro_meg:
            if len(observe_window) >= 3:
                observe_window[2] = error_bro_meg
            return f'{gpt_bro_result} 对话错误'
            # 观测窗
        if len(observe_window) >= 1:
            observe_window[0] = gpt_bro_result
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                observe_window[2] = "请求超时，程序终止。"
                raise RuntimeError(f"{gpt_bro_result} 程序终止。")
    return gpt_bro_result


if __name__ == '__main__':
    test = GPTChatInit()