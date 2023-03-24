import markdown, mdtex2html, threading
from show_math import convert as convert_math
from functools import wraps

def predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature, history=[]):
    """
        调用简单的predict_no_ui接口，但是依然保留了些许界面心跳功能
    """
    import time
    try: from config_private import TIMEOUT_SECONDS
    except: from config import TIMEOUT_SECONDS
    from predict import predict_no_ui
    mutable = [None]
    def mt(): mutable[0] = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history)
    thread_name = threading.Thread(target=mt); thread_name.start()
    cnt = 0
    while thread_name.is_alive():
        cnt += 1
        chatbot[-1] = (i_say_show_user, f"[Local Message] waiting gpt response {cnt}/{TIMEOUT_SECONDS*2}"+''.join(['.']*(cnt%4)))
        yield chatbot, history, '正常'
        time.sleep(1)
    gpt_say = mutable[0]
    return gpt_say

def write_results_to_file(history, file_name=None):
    """
        将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os, time
    if file_name is None:
        file_name = time.strftime("chatGPT分析报告%Y-%m-%d-%H-%M-%S", time.localtime()) + '.md'
    os.makedirs('./gpt_log/', exist_ok=True)
    with open(f'./gpt_log/{file_name}', 'w') as f:
        f.write('# chatGPT 分析报告\n')
        for i, content in enumerate(history):
            if i%2==0: f.write('## ')
            f.write(content)
            f.write('\n\n')
    res = '以上材料已经被写入' + os.path.abspath(f'./gpt_log/{file_name}')
    print(res)
    return res

def regular_txt_to_markdown(text):
    """
        将普通文本转换为Markdown格式的文本。
    """
    text = text.replace('\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    return text

def CatchException(f):
    """
        装饰器函数，捕捉函数f中的异常并封装到一个生成器中返回，并显示到聊天当中。
    """
    @wraps(f)
    def decorated(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
        try:
            yield from f(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)
        except Exception as e:
            import traceback
            from check_proxy import check_proxy
            try: from config_private import proxies
            except: from config import proxies
            tb_str = regular_txt_to_markdown(traceback.format_exc())
            chatbot[-1] = (chatbot[-1][0], f"[Local Message] 实验性函数调用出错: \n\n {tb_str} \n\n 当前代理可用性: \n\n {check_proxy(proxies)}")
            yield chatbot, history, f'异常 {e}'
    return decorated

def report_execption(chatbot, history, a, b):
    """
        向chatbot中添加错误信息
    """
    chatbot.append((a, b))
    history.append(a); history.append(b)

def text_divide_paragraph(text):
    """
        将文本按照段落分隔符分割开，生成带有段落标签的HTML代码。
    """
    if '```' in text:
        # careful input
        return text
    else:
        # wtf input
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if i!=0: lines[i] = "<p>"+lines[i].replace(" ", "&nbsp;")+"</p>"
        text = "".join(lines)
        return text

def markdown_convertion(txt):
    """
        将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    if ('$' in txt) and ('```' not in txt):
        return markdown.markdown(txt,extensions=['fenced_code','tables']) + '<br><br>' + \
            markdown.markdown(convert_math(txt, splitParagraphs=False),extensions=['fenced_code','tables'])
    else:
        return markdown.markdown(txt,extensions=['fenced_code','tables'])


def format_io(self, y):
    """
        将输入和输出解析为HTML格式。将y中最后一项的输入部分段落化，并将输出部分的Markdown和数学公式转换为HTML格式。
    """
    if y is None: return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask) # 输入部分太自由，预处理一波
    y[-1] = (
        None if i_ask is None else markdown.markdown(i_ask, extensions=['fenced_code','tables']),
        None if gpt_reply is None else markdown_convertion(gpt_reply)
    )
    return y


def find_free_port():
    """
        返回当前系统中可用的未使用端口。
    """
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]