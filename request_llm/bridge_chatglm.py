
from transformers import AutoModel, AutoTokenizer
import time
import importlib
from toolbox import update_ui, get_conf


global chatglm_model, chatglm_tokenizer

chatglm_model = None
chatglm_tokenizer = None

def model_loader():
    global chatglm_model, chatglm_tokenizer
    if chatglm_tokenizer is None:
        chatglm_tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    if chatglm_model is None: # 尚未加载
        device, = get_conf('LOCAL_MODEL_DEVICE')
        if device=='cpu':
            chatglm_model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).float()
        else:
            chatglm_model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()
        chatglm_model = chatglm_model.eval()
    chatglm_model = chatglm_model.eval()

def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None, console_slience=False):
    """
        函数的说明请见 request_llm/bridge_all.py
    """
    global chatglm_model, chatglm_tokenizer
    if chatglm_model is None:
        observe_window[0] = "ChatGLM尚未加载，加载需要一段时间 ……"

    model_loader()
    # chatglm 没有 sys_prompt 接口，因此把prompt加入 history
    history_feedin = []
    for i in range(len(history)//2):
        history_feedin.append(["What can I do?", sys_prompt] )
        history_feedin.append([history[2*i], history[2*i+1]] )

    watch_dog_patience = 5 # 看门狗 (watchdog) 的耐心, 设置5秒即可
    response = ""
    for response, history in chatglm_model.stream_chat(chatglm_tokenizer, inputs, history=history_feedin, max_length=llm_kwargs['max_length'],
                                                       top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        # 观测窗，把已经获取的数据显示出去
        observe_window[0] = response
        # 看门狗 (watchdog)，如果超过期限没有喂狗，则终止
        if len(observe_window) >= 2:  
            if (time.time()-observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
        # if not console_slience:
        #     print(response)
    return response


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        函数的说明请见 request_llm/bridge_all.py
    """
    global chatglm_model, chatglm_tokenizer
    chatbot.append((inputs, ""))
    if chatglm_model is None:
        chatbot[-1] = (inputs, "ChatGLM尚未加载，加载需要一段时间 ……")
        yield from update_ui(chatbot=chatbot, history=[])
    model_loader()

    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)    # 热更新prompt
        core_functional = core_functional.get_core_functions()
        if "PreProcess" in core_functional[additional_fn]: inputs = core_functional[additional_fn]["PreProcess"](inputs)  # 获取预处理函数（如果有的话）
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]


    history_feedin = []
    for i in range(len(history)//2):
        history_feedin.append(["What can I do?", system_prompt] )
        history_feedin.append([history[2*i], history[2*i+1]] )

    for response, history in chatglm_model.stream_chat(chatglm_tokenizer, inputs, history=history_feedin, max_length=llm_kwargs['max_length'],
                                                       top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        chatbot[-1] = (inputs, response)
        yield from update_ui(chatbot=chatbot, history=history)