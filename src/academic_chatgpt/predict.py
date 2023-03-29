# Referenced https://github.com/GaiZhenbiao/ChuanhuChatGPT project

import importlib
import json
import traceback

import requests
from loguru import logger
from .config import load_config

timeout_bot_msg = (
    "[local] Request timeout, network error. please check proxy settings in config.py."
)


CONFIGS = load_config()


def get_full_error(chunk, stream_response):
    """Get the complete error message returned from Openai."""
    while True:
        try:
            chunk += next(stream_response)
        except StopIteration:
            break
    return chunk


def predict_no_ui(inputs, top_p, temperature, history=[]):
    """Send to chatGPT, wait for reply, complete in one go, and do not display intermediate process.

    A simplified version of the predict function.
    Used for cases where the payload is relatively large, or for implementing complex functions with multiple threads and nesting.

    inputs is the input for this inquiry
    top_p, temperature are internal tuning parameters of chatGPT
    history is the previous conversation list
    (Note that if either inputs or history is too long, it will trigger a token count overflow error, and then raise ConnectionAbortedError.)
    """
    headers, payload = generate_payload(
        inputs, top_p, temperature, history, system_prompt="", stream=False
    )

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            response = requests.post(
                CONFIGS.API_URL,
                headers=headers,
                proxies=CONFIGS.proxies,
                json=payload,
                stream=False,
                timeout=CONFIGS.TIMEOUT_SECONDS * 2,
            )
            break

        except requests.exceptions.ReadTimeout:
            retry += 1
            traceback.print_exc()
            if CONFIGS.MAX_RETRY != 0:
                logger.info(
                    f"Request timed out, retrying ({retry}/{CONFIGS.MAX_RETRY}) ……"
                )

            if retry > CONFIGS.MAX_RETRY:
                raise TimeoutError

    try:
        result = json.loads(response.text)["choices"][0]["message"]["content"]
        return result
    except Exception:
        if "choices" not in response.text:
            logger.info(response.text)
        raise ConnectionAbortedError("Json parsing is not normal" + response.text)


def predict(
    inputs,
    top_p,
    temperature,
    chatbot=[],
    history=[],
    system_prompt="",
    stream=True,
    additional_fn=None,
):
    """Send to chatGPT, and get output in a streaming manner.
    Used for basic conversation functions.
    inputs is the input for this inquiry
    top_p, temperature are internal tuning parameters of chatGPT
    history is the previous conversation list (Note that if either inputs or history is too long, it will trigger a token count overflow error.)
    chatbot is the conversation list displayed in the WebUI. Modify it, then yeild it out, and you can directly modify the content of the conversation interface.
    additional_fn represents which button was clicked. The buttons are in functional.py.
    """
    if additional_fn is not None:
        from . import functional

        importlib.reload(functional)
        functional = functional.get_functionals()
        inputs = (
            functional[additional_fn]["Prefix"]
            + inputs
            + functional[additional_fn]["Suffix"]
        )

    if stream:
        raw_input = inputs
        logger.info(f"[raw_input] {raw_input}")
        chatbot.append((inputs, ""))
        yield chatbot, history, "Waiting for response"

    headers, payload = generate_payload(
        inputs, top_p, temperature, history, system_prompt, stream
    )
    history.append(inputs)
    history.append(" ")

    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=True
            response = requests.post(
                CONFIGS.API_URL,
                headers=headers,
                proxies=CONFIGS.proxies,
                json=payload,
                stream=True,
                timeout=CONFIGS.TIMEOUT_SECONDS,
            )
            break
        except Exception:
            retry += 1
            chatbot[-1] = (chatbot[-1][0], timeout_bot_msg)
            retry_msg = (
                f", retrying ({retry}/{CONFIGS.MAX_RETRY}) ……"
                if CONFIGS.MAX_RETRY > 0
                else ""
            )
            yield chatbot, history, "Request timed out" + retry_msg
            if retry > CONFIGS.MAX_RETRY:
                raise TimeoutError

    gpt_replying_buffer = ""

    is_head_of_the_stream = True
    if stream:
        stream_response = response.iter_lines()
        while True:
            chunk = next(stream_response)
            if is_head_of_the_stream:
                # The first frame of the data stream does not carry content
                is_head_of_the_stream = False
                continue

            if chunk:
                try:
                    if len(json.loads(chunk.decode()[6:])["choices"][0]["delta"]) == 0:
                        # Determine the end of the data stream, and gpt_replying_buffer is also written
                        logger.info(f"[response] {gpt_replying_buffer}")
                        break
                    # Process the body of the data stream
                    chunkjson = json.loads(chunk.decode()[6:])
                    status_text = (
                        f"finish_reason: {chunkjson['choices'][0]['finish_reason']}"
                    )
                    # If an exception is thrown here, it is generally because the text is too long. See the output of get_full_error for details.
                    gpt_replying_buffer = (
                        gpt_replying_buffer
                        + json.loads(chunk.decode()[6:])["choices"][0]["delta"][
                            "content"
                        ]
                    )
                    history[-1] = gpt_replying_buffer
                    chatbot[-1] = (history[-2], history[-1])
                    yield chatbot, history, status_text

                except Exception:
                    traceback.print_exc()
                    yield chatbot, history, "Json parsing is not normal."

                    chunk = get_full_error(chunk, stream_response)
                    error_msg = chunk.decode()
                    if "reduce the length" in error_msg:
                        chatbot[-1] = (
                            chatbot[-1][0],
                            "[Local Message] Input (or history) is too long, please reduce input or clear history by refreshing this page.",
                        )
                        history = []
                    elif "Incorrect API key" in error_msg:
                        chatbot[-1] = (
                            chatbot[-1][0],
                            "[Local Message] Incorrect API key provided.",
                        )

                    else:
                        from .utils import regular_txt_to_markdown

                        tb_str = regular_txt_to_markdown(traceback.format_exc())
                        chatbot[-1] = (
                            chatbot[-1][0],
                            f"[Local Message] Json Error \n\n {tb_str} \n\n {regular_txt_to_markdown(chunk.decode()[4:])}",
                        )

                    yield chatbot, history, "Json parsing is not normal" + error_msg
                    return


def generate_payload(inputs, top_p, temperature, history, system_prompt, stream):
    """Integrate all information, select LLM model, generate http request, and prepare for sending requests."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIGS.API_KEY}",
    }

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
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)

    payload = {
        "model": CONFIGS.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,  # 1.0,
        "top_p": top_p,  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    logger.info(f" {CONFIGS.LLM_MODEL} : {conversation_cnt} : {inputs}")
    return headers, payload
