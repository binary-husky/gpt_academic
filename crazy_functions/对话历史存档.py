from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive

def write_chat_to_file(chatbot, file_name=None):
    """
    将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os
    import time
    if file_name is None:
        file_name = 'chatGPT对话历史' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.html'
    os.makedirs('./gpt_log/', exist_ok=True)
    with open(f'./gpt_log/{file_name}', 'w', encoding='utf8') as f:
        for i, contents in enumerate(chatbot):
            for content in contents:
                try:    # 这个bug没找到触发条件，暂时先这样顶一下
                    if type(content) != str: content = str(content)
                except:
                    continue
                f.write(content)
                f.write('\n\n')
            f.write('<hr color="red"> \n\n')

    res = '对话历史写入：' + os.path.abspath(f'./gpt_log/{file_name}')
    print(res)
    return res

@CatchException
def 对话历史存档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """

    chatbot.append(("保存当前对话", f"[Local Message] {write_chat_to_file(chatbot)}"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

