from toolbox import CatchException, update_ui, gen_time_str
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.crazy_utils import input_clipping
import copy, json

@CatchException
def 命令行助手(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本, 例如需要翻译的一段话, 再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数, 暂时没有用武之地
    chatbot         聊天显示框的句柄, 用于显示给用户
    history         聊天历史, 前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    # 清空历史, 以免输入溢出
    history = []

    # 输入
    i_say = "请写bash命令实现以下功能：" + txt
    # 开始
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=txt,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[],
        sys_prompt="你是一个Linux大师级用户。注意，当我要求你写bash命令时，尽可能地仅用一行命令解决我的要求。"
    )
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新



