import json

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)

def decode_chunk(chunk):
    """
    用于解读"content"和"finish_reason"的内容
    """
    chunk = chunk.decode()
    respose = ""
    finish_reason = "False"
    try:
        chunk = json.loads(chunk[6:])
    except:
        finish_reason = "JSON_ERROR"
    # 错误处理部分
    if "error" in chunk:
        respose = "API_ERROR"
        try:
            chunk = json.loads(chunk)
            finish_reason = chunk["error"]["code"]
        except:
            finish_reason = "API_ERROR"
        return respose, finish_reason

    try:
        respose = chunk["choices"][0]["delta"]["content"]
    except:
        pass
    try:
        finish_reason = chunk["choices"][0]["finish_reason"]
    except:
        pass
    return respose, finish_reason


def generate_message(chatbot, input, model, key, history, max_output_token, system_prompt, temperature):
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
    if temperature == 2: temperature -= 1e-5
    playload = {
        "model": model,
        "input": messages,
        "parameters":{
            "result_format": "message",
            "temperature": temperature,
            "incremental_output": True,
            "max_tokens": max_output_token,
        }
    }
    try:
        print(f" {model} : {conversation_cnt} : {input[:100]} ..........")
    except:
        print("输入中可能存在乱码。")
    return headers, playload