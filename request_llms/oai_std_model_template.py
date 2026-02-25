import json
import time
import traceback
import requests

from loguru import logger
from toolbox import get_conf, is_the_upload_folder, update_ui, update_ui_latest_msg

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf(
    "proxies", "TIMEOUT_SECONDS", "MAX_RETRY"
)

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)


def get_full_error(chunk, stream_response):
    """
    尝试获取完整的错误信息
    """
    while True:
        try:
            chunk += next(stream_response)
        except Exception:
            break
    return chunk


def decode_chunk(chunk):
    """
    用于解读"content"和"finish_reason"的内容（如果支持思维链也会返回"reasoning_content"内容）
    """
    chunk = chunk.decode()
    response = ""
    reasoning_content = ""
    finish_reason = "False"

    # 考虑返回类型是 text/json 和 text/event-stream 两种
    if chunk.startswith("data: "):
        chunk = chunk[6:]
    else:
        chunk = chunk

    try:
        chunk = json.loads(chunk)
    except Exception:
        response = ""
        finish_reason = chunk

    # 错误处理部分
    if "error" in chunk:
        response = "API_ERROR"
        try:
            chunk = json.loads(chunk)
            finish_reason = chunk["error"]["code"]
        except Exception:
            finish_reason = "API_ERROR"
        return response, reasoning_content, finish_reason, str(chunk)

    try:
        if chunk["choices"][0]["delta"]["content"] is not None:
            response = chunk["choices"][0]["delta"]["content"]
    except Exception:
        pass
    try:
        if chunk["choices"][0]["delta"]["reasoning_content"] is not None:
            reasoning_content = chunk["choices"][0]["delta"]["reasoning_content"]
    except Exception:
        pass
    try:
        finish_reason = chunk["choices"][0]["finish_reason"]
    except Exception:
        pass
    return response, reasoning_content, finish_reason, str(chunk)


def generate_message(input, model, key, history, max_output_token, system_prompt, temperature):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    api_key = f"Bearer {key}"

    headers = {"Content-Type": "application/json", "Authorization": api_key}

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2 * conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index + 1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]["content"] = what_gpt_answer["content"]
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = input
    messages.append(what_i_ask_now)
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
        "max_tokens": max_output_token,
    }

    return headers, payload


def get_predict_function(
        api_key_conf_name,
        max_output_token,
        disable_proxy = False,
        model_remove_prefix = [],
    ):
    """
    为openai格式的API生成响应函数，其中传入参数：
    api_key_conf_name：
        `config.py`中此模型的APIKEY的名字，例如"YIMODEL_API_KEY"
    max_output_token：
        每次请求的最大token数量，例如对于01万物的yi-34b-chat-200k，其最大请求数为4096
        ⚠️请不要与模型的最大token数量相混淆。
    disable_proxy：
        是否使用代理，True为不使用，False为使用。
    """

    APIKEY = get_conf(api_key_conf_name)

    def remove_prefix(model_name):
        # 去除模型名字的前缀，输入 volcengine-deepseek-r1-250120 会返回 deepseek-r1-250120
        if not model_remove_prefix:
            return model_name
        model_without_prefix = model_name
        for prefix in model_remove_prefix:
            if model_without_prefix.startswith(prefix):
                model_without_prefix = model_without_prefix[len(prefix):]
        return model_without_prefix

    def predict_no_ui_long_connection(
        inputs,
        llm_kwargs,
        history=[],
        sys_prompt="",
        observe_window=None,
        console_silence=False,
    ):
        """
        发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
        inputs：
            是本次问询的输入
        sys_prompt:
            系统静默prompt
        llm_kwargs：
            chatGPT的内部调优参数
        history：
            是之前的对话列表
        observe_window = None：
            用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
        """
        from .bridge_all import model_info
        watch_dog_patience = 5  # 看门狗的耐心，设置5秒不准咬人 (咬的也不是人)
        if len(APIKEY) == 0:
            raise RuntimeError(f"APIKEY为空,请检查配置文件的{APIKEY}")
        if inputs == "":
            inputs = "你好👋"


        headers, payload = generate_message(
            input=inputs,
            model=remove_prefix(llm_kwargs["llm_model"]),
            key=APIKEY,
            history=history,
            max_output_token=max_output_token,
            system_prompt=sys_prompt,
            temperature=llm_kwargs["temperature"],
        )

        reasoning = model_info[llm_kwargs['llm_model']].get('enable_reasoning', False)

        retry = 0
        while True:
            try:
                endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
                response = requests.post(
                    endpoint,
                    headers=headers,
                    proxies=None if disable_proxy else proxies,
                    json=payload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
                break
            except Exception:
                retry += 1
                traceback.print_exc()
                if retry > MAX_RETRY:
                    raise TimeoutError
                if MAX_RETRY != 0:
                    logger.error(f"请求超时，正在重试 ({retry}/{MAX_RETRY}) ……")

        result = ""
        finish_reason = ""
        if reasoning:
            reasoning_buffer = ""

        stream_response = response.iter_lines()
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                if result == "":
                    raise RuntimeError(f"获得空的回复，可能原因:{finish_reason}")
                break
            except requests.exceptions.ConnectionError:
                chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
            response_text, reasoning_content, finish_reason, decoded_chunk = decode_chunk(chunk)
            # 返回的数据流第一次为空，继续等待
            if response_text == "" and (reasoning == False or reasoning_content == "") and finish_reason != "False":
                continue
            if response_text == "API_ERROR" and (
                finish_reason != "False" or finish_reason != "stop"
            ):
                chunk = get_full_error(chunk, stream_response)
                chunk_decoded = chunk.decode()
                logger.error(chunk_decoded)
                raise RuntimeError(
                    f"API异常,请检测终端输出。可能的原因是:{finish_reason}"
                )
            if chunk:
                try:
                    if finish_reason == "stop":
                        if not console_silence:
                            print(f"[response] {result}")
                        break
                    result += response_text
                    if reasoning:
                        reasoning_buffer += reasoning_content
                    if observe_window is not None:
                        # 观测窗，把已经获取的数据显示出去
                        if len(observe_window) >= 1:
                            observe_window[0] += response_text
                        # 看门狗，如果超过期限没有喂狗，则终止
                        if len(observe_window) >= 2:
                            if (time.time() - observe_window[1]) > watch_dog_patience:
                                raise RuntimeError("用户取消了程序。")
                except Exception as e:
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    error_msg = chunk_decoded
                    logger.error(error_msg)
                    raise RuntimeError("Json解析不合常规")
        if reasoning:
            paragraphs = ''.join([f'<p style="margin: 1.25em 0;">{line}</p>' for line in reasoning_buffer.split('\n')])
            return f'''<div class="reasoning_process" >{paragraphs}</div>\n\n''' + result
        return result

    def predict(
        inputs,
        llm_kwargs,
        plugin_kwargs,
        chatbot,
        history=[],
        system_prompt="",
        stream=True,
        additional_fn=None,
    ):
        """
        发送至chatGPT，流式获取输出。
        用于基础的对话功能。
        inputs 是本次问询的输入
        top_p, temperature是chatGPT的内部调优参数
        history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
        chatbot 为WebUI中显示的对话列表，修改它，然后yield出去，可以直接修改对话界面内容
        additional_fn代表点击的哪个按钮，按钮见functional.py
        """
        from .bridge_all import model_info
        if len(APIKEY) == 0:
            raise RuntimeError(f"APIKEY为空,请检查配置文件的{APIKEY}")
        if inputs == "":
            inputs = "你好👋"
        if additional_fn is not None:
            from core_functional import handle_core_functionality

            inputs, history = handle_core_functionality(
                additional_fn, inputs, history, chatbot
            )
        logger.info(f"[raw_input] {inputs}")
        chatbot.append((inputs, ""))
        yield from update_ui(
            chatbot=chatbot, history=history, msg="等待响应"
        )  # 刷新界面

        # check mis-behavior
        if is_the_upload_folder(inputs):
            chatbot[-1] = (
                inputs,
                f"[Local Message] 检测到操作错误！当您上传文档之后，需点击“**函数插件区**”按钮进行处理，请勿点击“提交”按钮或者“基础功能区”按钮。",
            )
            yield from update_ui(
                chatbot=chatbot, history=history, msg="正常"
            )  # 刷新界面
            time.sleep(2)

        headers, payload = generate_message(
            input=inputs,
            model=remove_prefix(llm_kwargs["llm_model"]),
            key=APIKEY,
            history=history,
            max_output_token=max_output_token,
            system_prompt=system_prompt,
            temperature=llm_kwargs["temperature"],
        )

        reasoning = model_info[llm_kwargs['llm_model']].get('enable_reasoning', False)

        history.append(inputs)
        history.append("")
        retry = 0
        while True:
            try:
                endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
                response = requests.post(
                    endpoint,
                    headers=headers,
                    proxies=None if disable_proxy else proxies,
                    json=payload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
                break
            except Exception:
                retry += 1
                chatbot[-1] = (chatbot[-1][0], timeout_bot_msg)
                retry_msg = (
                    f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
                )
                yield from update_ui(
                    chatbot=chatbot, history=history, msg="请求超时" + retry_msg
                )  # 刷新界面
                if retry > MAX_RETRY:
                    raise TimeoutError

        gpt_replying_buffer = ""
        if reasoning:
            gpt_reasoning_buffer = ""

        stream_response = response.iter_lines()
        wait_counter = 0
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                if wait_counter != 0 and gpt_replying_buffer == "":
                    yield from update_ui_latest_msg(lastmsg="模型调用失败 ...", chatbot=chatbot, history=history, msg="failed")
                break
            except requests.exceptions.ConnectionError:
                chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
            response_text, reasoning_content, finish_reason, decoded_chunk = decode_chunk(chunk)
            if decoded_chunk == ': keep-alive':
                wait_counter += 1
                yield from update_ui_latest_msg(lastmsg="等待中 " + "".join(["."] * (wait_counter%10)), chatbot=chatbot, history=history, msg="waiting ...")
                continue
            # 返回的数据流第一次为空，继续等待
            if response_text == "" and (reasoning == False or reasoning_content == "") and finish_reason != "False":
                status_text = f"finish_reason: {finish_reason}"
                yield from update_ui(
                    chatbot=chatbot, history=history, msg=status_text
                )
                continue
            if chunk:
                try:
                    if response_text == "API_ERROR" and (
                        finish_reason != "False" or finish_reason != "stop"
                    ):
                        chunk = get_full_error(chunk, stream_response)
                        chunk_decoded = chunk.decode()
                        chatbot[-1] = (
                            chatbot[-1][0],
                            f"[Local Message] {finish_reason}, 获得以下报错信息：\n"
                            + chunk_decoded,
                        )
                        yield from update_ui(
                            chatbot=chatbot,
                            history=history,
                            msg="API异常:" + chunk_decoded,
                        )  # 刷新界面
                        logger.error(chunk_decoded)
                        return

                    if finish_reason == "stop":
                        logger.info(f"[response] {gpt_replying_buffer}")
                        break
                    status_text = f"finish_reason: {finish_reason}"
                    if reasoning:
                        gpt_replying_buffer += response_text
                        gpt_reasoning_buffer += reasoning_content
                        paragraphs = ''.join([f'<p style="margin: 1.25em 0;">{line}</p>' for line in gpt_reasoning_buffer.split('\n')])
                        history[-1] = f'<div class="reasoning_process">{paragraphs}</div>\n\n---\n\n' + gpt_replying_buffer
                    else:
                        gpt_replying_buffer += response_text
                        # 如果这里抛出异常，一般是文本过长，详情见get_full_error的输出
                        history[-1] = gpt_replying_buffer
                    chatbot[-1] = (history[-2], history[-1])
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg=status_text
                    )  # 刷新界面
                except Exception as e:
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg="Json解析不合常规"
                    )  # 刷新界面
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    chatbot[-1] = (
                        chatbot[-1][0],
                        "[Local Message] 解析错误,获得以下报错信息：\n" + chunk_decoded,
                    )
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg="Json异常" + chunk_decoded
                    )  # 刷新界面
                    logger.error(chunk_decoded)
                    return

    return predict_no_ui_long_connection, predict
