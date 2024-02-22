model_name = "YSHS GPT35"
cmd_to_install = "`pip install yshs damei easydict`"


import time
from toolbox import update_ui, get_conf, update_ui_lastest_msg
from yshs import Client
import yshs
__client = None
def get_client():
    global __client
    if __client is None:
        __client = Client()
    return __client
def validate_key():
    YSHS_API_KEY = get_conf("YSHS_API_KEY")
    if YSHS_API_KEY == '': return False
    yshs.api_key = YSHS_API_KEY
    return True

def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=[], console_slience=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    if validate_key() is False:
        raise RuntimeError('请配置YSHS_API_KEY')
    messages = [
        {"role": "system", "content": sys_prompt},  # 系统提示
    ]
    for i, msg in enumerate(history):
        if i % 2 == 0:
            # 偶数索引是问题
            messages.append({"role": "user", "content": msg})
        else:
            # 奇数索引是答案
            messages.append({"role": "assistant", "content": msg})
    messages.append({"role": "user", "content": inputs})
    print(messages)
    responese = yshs.LLM.chat(
        model="openai/gpt-3.5-turbo",  # 选择模型
        
        messages=messages
    )
    output= []
    for x in responese:
        output.append(x)
        if len(observe_window) >= 1:
            observe_window[0] = "".join(output)
        if len(observe_window) >= 2:
            if (time.time()-observe_window[1]) > watch_dog_patience: raise RuntimeError("程序终止。")
    return "".join(output)

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history)

    if validate_key() is False:
        yield from update_ui_lastest_msg(lastmsg="[Local Message] 请配置YSHS_API_KEY", chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    # 开始接收回复    
    messages = [
        {"role": "system", "content": system_prompt},  # 系统提示
    ]
    for i, msg in enumerate(history):
        if i % 2 == 0:
            # 偶数索引是问题
            messages.append({"role": "user", "content": msg})
        else:
            # 奇数索引是答案
            messages.append({"role": "assistant", "content": msg})
    messages.append({"role": "user", "content": inputs})
    responese = yshs.LLM.chat(
        model="openai/gpt-3.5-turbo",  # 选择模型
        
        messages=messages
    )
    output = []
    for x in responese:
        output.append(x)
        chatbot[-1] = (inputs, "".join(output))
        yield from update_ui(chatbot=chatbot, history=history)

    # 总结输出
    if output == f"[Local Message] 等待{model_name}响应中 ...":
        output = f"[Local Message] {model_name}响应异常 ..."
    history.extend([inputs, "".join(output)])
    yield from update_ui(chatbot=chatbot, history=history)

    
    