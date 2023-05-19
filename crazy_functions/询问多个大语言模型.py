from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime
@CatchException
def 同时问询(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，如温度和top_p等，一般原样传递下去就行
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append((txt, "正在同时咨询gpt-3.5和gpt-4……"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

    # llm_kwargs['llm_model'] = 'chatglm&gpt-3.5-turbo&api2d-gpt-3.5-turbo' # 支持任意数量的llm接口，用&符号分隔
    llm_kwargs['llm_model'] = 'gpt-3.5-turbo&gpt-4' # 支持任意数量的llm接口，用&符号分隔
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=txt, inputs_show_user=txt, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, 
        sys_prompt=system_prompt,
        retry_times_at_unknown_error=0
    )

    history.append(txt)
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新


@CatchException
def 同时问询_指定模型(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，如温度和top_p等，一般原样传递下去就行
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append((txt, "正在同时咨询ChatGPT和ChatGLM……"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    # llm_kwargs['llm_model'] = 'chatglm&gpt-3.5-turbo&api2d-gpt-3.5-turbo' # 支持任意数量的llm接口，用&符号分隔
    llm_kwargs['llm_model'] = plugin_kwargs.get("advanced_arg", 'chatglm&gpt-3.5-turbo') # 'chatglm&gpt-3.5-turbo' # 支持任意数量的llm接口，用&符号分隔
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=txt, inputs_show_user=txt, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, 
        sys_prompt=system_prompt,
        retry_times_at_unknown_error=0
    )

    history.append(txt)
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新