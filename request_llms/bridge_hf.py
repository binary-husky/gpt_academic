import time
import os
from toolbox import update_ui, get_conf, update_ui_lastest_msg, log_chat
from toolbox import check_packages, report_exception, have_any_recent_upload_image_files
from toolbox import ChatBotWithCookies

model_name = 'Hugging Face Playground'
default_model = 'Qwen/Qwen2.5-72B-Instruct'

def validate_key():
    HUGGINGFACE_ACCESS_TOKEN = get_conf("HUGGINGFACE_ACCESS_TOKEN")
    if HUGGINGFACE_ACCESS_TOKEN == '': return False
    return True

def make_media_input(inputs, image_paths):
    for image_path in image_paths:
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
    return inputs

def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list=[], sys_prompt:str="",
                                  observe_window:list=[], console_slience:bool=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    if llm_kwargs["llm_model"] == "HFPlayground":
        llm_kwargs["llm_model"] = default_model

    if validate_key() is False:
        raise RuntimeError('请配置HUGGINGFACE_ACCESS_TOKEN')

    # 开始接收回复
    from .com_hfplayground import HFPlaygroundInit
    hfp_init = HFPlaygroundInit()
    for chunk, response in hfp_init.generate_chat(inputs, llm_kwargs, history, sys_prompt):
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
    return response


def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot:ChatBotWithCookies,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history)

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        check_packages(["openai"])
    except:
        yield from update_ui_lastest_msg(f"导入软件依赖失败。使用该模型需要额外依赖，安装方法```pip install --upgrade openai```。",
            chatbot=chatbot, history=history, delay=0)
        return

    if validate_key() is False:
        yield from update_ui_lastest_msg(lastmsg="[Local Message] 请配置HUGGINGFACE_ACCESS_TOKEN", chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)
        chatbot[-1] = [inputs, ""]
        yield from update_ui(chatbot=chatbot, history=history)

    if llm_kwargs["llm_model"] == "HFPlayground":
        llm_kwargs["llm_model"] = default_model

    # 开始接收回复
    from .com_hfplayground import HFPlaygroundInit
    hfp_init = HFPlaygroundInit()
    for chunk, response in hfp_init.generate_chat(inputs, llm_kwargs, history, system_prompt):
        chatbot[-1] = [inputs, response]
        yield from update_ui(chatbot=chatbot, history=history)
    history.extend([inputs, response])
    log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=response)
    yield from update_ui(chatbot=chatbot, history=history)