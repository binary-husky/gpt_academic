
import time
from comm_tools.toolbox import update_ui, get_conf, update_ui_lastest_msg

model_name = '智谱AI大模型'

def validate_key():
    ZHIPUAI_API_KEY = get_conf("ZHIPUAI_API_KEY")
    if ZHIPUAI_API_KEY == '': return False
    return True

def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=[], console_slience=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    if validate_key() is False:
        raise RuntimeError('请配置ZHIPUAI_API_KEY')

    from .com_zhipuapi import ZhipuRequestInstance
    sri = ZhipuRequestInstance()
    for response in sri.generate(inputs, llm_kwargs, history, sys_prompt):
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time()-observe_window[1]) > watch_dog_patience: raise RuntimeError("程序终止。")
    return response

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history)

    if validate_key() is False:
        yield from update_ui_lastest_msg(lastmsg="[Local Message] 请配置ZHIPUAI_API_KEY", chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    # 开始接收回复    
    from .com_zhipuapi import ZhipuRequestInstance
    sri = ZhipuRequestInstance()
    for response in sri.generate(inputs, llm_kwargs, history, system_prompt):
        chatbot[-1] = (inputs, response)
        yield from update_ui(chatbot=chatbot, history=history)

    # 总结输出
    if response == f"[Local Message] 等待{model_name}响应中 ...":
        response = f"[Local Message] {model_name}响应异常 ..."
    history.extend([inputs, response])
    yield from update_ui(chatbot=chatbot, history=history)