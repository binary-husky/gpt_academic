from toolbox import CatchException, update_ui, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import re

def write_chat_to_file(chatbot, history=None, file_name=None):
    """
    将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os
    import time
    if file_name is None:
        file_name = 'chatGPT对话历史' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.html'
    os.makedirs('./gpt_log/', exist_ok=True)
    with open(f'./gpt_log/{file_name}', 'w', encoding='utf8') as f:
        from theme.theme import advanced_css
        f.write(f'<!DOCTYPE html><head><meta charset="utf-8"><title>对话历史</title><style>{advanced_css}</style></head>')
        for i, contents in enumerate(chatbot):
            for j, content in enumerate(contents):
                try:    # 这个bug没找到触发条件，暂时先这样顶一下
                    if type(content) != str: content = str(content)
                except:
                    continue
                f.write(content)
                if j == 0:
                    f.write('<hr style="border-top: dotted 3px #ccc;">')
            f.write('<hr color="red"> \n\n')
        f.write('<hr color="blue"> \n\n raw chat context:\n')
        f.write('<code>')
        for h in history:
            f.write("\n>>>" + h)
        f.write('</code>')
    promote_file_to_downloadzone(f'./gpt_log/{file_name}', rename_file=file_name, chatbot=chatbot)
    return '对话历史写入：' + os.path.abspath(f'./gpt_log/{file_name}')

def gen_file_preview(file_name):
    try:
        with open(file_name, 'r', encoding='utf8') as f:
            file_content = f.read()
        # pattern to match the text between <head> and </head>
        pattern = re.compile(r'<head>.*?</head>', flags=re.DOTALL)
        file_content = re.sub(pattern, '', file_content)
        html, history = file_content.split('<hr color="blue"> \n\n raw chat context:\n')
        history = history.strip('<code>')
        history = history.strip('</code>')
        history = history.split("\n>>>")
        return list(filter(lambda x:x!="", history))[0][:100]
    except:
        return ""

def read_file_to_chat(chatbot, history, file_name):
    with open(file_name, 'r', encoding='utf8') as f:
        file_content = f.read()
    # pattern to match the text between <head> and </head>
    pattern = re.compile(r'<head>.*?</head>', flags=re.DOTALL)
    file_content = re.sub(pattern, '', file_content)
    html, history = file_content.split('<hr color="blue"> \n\n raw chat context:\n')
    history = history.strip('<code>')
    history = history.strip('</code>')
    history = history.split("\n>>>")
    history = list(filter(lambda x:x!="", history))
    html = html.split('<hr color="red"> \n\n')
    html = list(filter(lambda x:x!="", html))
    chatbot.clear()
    for i, h in enumerate(html):
        i_say, gpt_say = h.split('<hr style="border-top: dotted 3px #ccc;">')
        chatbot.append([i_say, gpt_say])
    chatbot.append([f"存档文件详情？", f"[Local Message] 载入对话{len(html)}条，上下文{len(history)}条。"])
    return chatbot, history    

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

    chatbot.append(("保存当前对话", 
        f"[Local Message] {write_chat_to_file(chatbot, history)}，您可以调用“载入对话历史存档”还原当下的对话。\n警告！被保存的对话历史可以被使用该系统的任何人查阅。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

def hide_cwd(str):
    import os
    current_path = os.getcwd()
    replace_path = "."
    return str.replace(current_path, replace_path)

@CatchException
def 载入对话历史存档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    from .crazy_utils import get_files_from_everything
    success, file_manifest, _ = get_files_from_everything(txt, type='.html')

    if not success:
        if txt == "": txt = '空空如也的输入栏'
        import glob
        local_history = "<br/>".join(["`"+hide_cwd(f)+f" ({gen_file_preview(f)})"+"`" for f in glob.glob(f'gpt_log/**/chatGPT对话历史*.html', recursive=True)])
        chatbot.append([f"正在查找对话历史文件（html格式）: {txt}", f"找不到任何html文件: {txt}。但本地存储了以下历史文件，您可以将任意一个文件路径粘贴到输入区，然后重试：<br/>{local_history}"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    try:
        chatbot, history = read_file_to_chat(chatbot, history, file_manifest[0])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    except:
        chatbot.append([f"载入对话历史文件", f"对话历史文件损坏！"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

@CatchException
def 删除所有本地对话历史记录(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """

    import glob, os
    local_history = "<br/>".join(["`"+hide_cwd(f)+"`" for f in glob.glob(f'gpt_log/**/chatGPT对话历史*.html', recursive=True)])
    for f in glob.glob(f'gpt_log/**/chatGPT对话历史*.html', recursive=True):
        os.remove(f)
    chatbot.append([f"删除所有历史对话文件", f"已删除<br/>{local_history}"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    return


