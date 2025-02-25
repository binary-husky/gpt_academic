import time
import os
from openai import OpenAI  # 新增OpenAI SDK
from toolbox import update_ui, get_conf, update_ui_lastest_msg, log_chat
from toolbox import check_packages, report_exception, have_any_recent_upload_image_files
from toolbox import ChatBotWithCookies

model_name = '火山引擎大模型API'
volcengine_default_model = get_conf("ARK_API_ID") # 获取实际模型ID

def validate_key():
    ARK_API_KEY = get_conf("ARK_API_KEY")
    if ARK_API_KEY == '': return False
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

    if llm_kwargs["llm_model"] == "volcengine":
        llm_kwargs["llm_model"] = volcengine_default_model

    if validate_key() is False:
        raise RuntimeError('请配置ARK_API_KEY')

    # 开始接收回复
    try:
        client = OpenAI(
            api_key=get_conf("ARK_API_KEY"),
            base_url=get_conf("ARK_API_URL") #"https://ark.cn-beijing.volces.com/api/v3",
        )
        
        messages = [{"role": "system", "content": sys_prompt}]
        for q, a in zip(history[::2], history[1::2]):
            messages.extend([{"role": "user", "content": q}, {"role": "assistant", "content": a}])
        messages.append({"role": "user", "content": inputs})

        response = client.chat.completions.create(
            model=llm_kwargs.get("llm_model", volcengine_default_model),
            messages=messages,
            stream=False,
            max_tokens=llm_kwargs.get("max_tokens", 2048),
            temperature=llm_kwargs.get("temperature", 0.7)
        )
        
        full_response = response.choices[0].message.content
        if len(observe_window) >= 1: observe_window[0] = full_response
        return full_response
    except Exception as e:
        report_exception(f"[VolcEngine] API错误: {str(e)}")
        return f"请求失败: {str(e)}"
    


def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot:ChatBotWithCookies,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    """
    发送至火山引擎LLM，流式获取输出。
    完整参数说明：
        inputs: 本次用户输入内容
        llm_kwargs: 模型参数（温度、最大token等）
        plugin_kwargs: 插件参数（保留）
        chatbot: 对话实例，用于前端展示
        history: 历史对话列表
        system_prompt: 系统级提示词
        stream: 流式输出开关（强制启用）
        additional_fn: 附加功能标识
    """
    # 初始化对话状态
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history)

    # 依赖检查（OpenAI SDK）
    try:
        check_packages(["openai"])
    except:
        error_msg = "缺少依赖：pip install openai"
        yield from update_ui_lastest_msg(error_msg, chatbot=chatbot)
        return

    # API密钥验证
    if not validate_key():
        error_msg = "[Local Message] 请配置ARK_API_KEY"
        yield from update_ui_lastest_msg(error_msg, chatbot=chatbot)
        return

    # 处理附加功能（如翻译、总结等）
    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)
        chatbot[-1] = [inputs, ""]
        yield from update_ui(chatbot=chatbot, history=history)

    # 模型参数处理
    llm_model = llm_kwargs.get("llm_model", volcengine_default_model)
    if llm_model == "volcengine": 
        llm_model = volcengine_default_model

    # 构建消息历史（适配OpenAI格式）
    messages = [{"role": "system", "content": system_prompt}]
    for pair in history:
        if len(pair) >= 2:
            messages.append({"role": "user", "content": pair[0]})
            messages.append({"role": "assistant", "content": pair[1]})
    messages.append({"role": "user", "content": inputs})

    # 初始化火山引擎客户端
    client = OpenAI(
        api_key=get_conf("ARK_API_KEY"),
        base_url= get_conf("ARK_API_URL") # "https://ark.cn-beijing.volces.com/api/v3",
    )

    # 流式请求处理
    full_response = ""
    try:
        stream_response = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            stream=True,
            temperature=llm_kwargs.get('temperature', 0.7),
            max_tokens=llm_kwargs.get('max_tokens', 2048)
        )
        
        # 处理流式响应
        for chunk in stream_response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                # 实时更新对话内容
                chatbot[-1] = [inputs, full_response]
                yield from update_ui(chatbot=chatbot, history=history)

    except Exception as e:
        # 异常处理
        error_info = f"API请求异常：{str(e)}"
        report_exception(error_info)
        full_response = f"【错误】{error_info}"
        chatbot[-1] = [inputs, full_response]
        yield from update_ui(chatbot=chatbot, history=history)

    # 记录最终结果
    history.extend([inputs, full_response])
    log_chat(
        llm_model=llm_model,
        input_str=inputs,
        output_str=full_response
    )
    yield from update_ui(chatbot=chatbot, history=history)