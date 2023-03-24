import markdown, mdtex2html
from show_math import convert as convert_math
from functools import wraps


def regular_txt_to_markdown(text):
    text = text.replace('\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    return text

def CatchException(f):
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
    chatbot.append((a, b))
    history.append(a); history.append(b)

def text_divide_paragraph(text):
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
    if ('$' in txt) and ('```' not in txt):
        return markdown.markdown(txt,extensions=['fenced_code','tables']) + '<br><br>' + \
            markdown.markdown(convert_math(txt, splitParagraphs=False),extensions=['fenced_code','tables'])
    else:
        return markdown.markdown(txt,extensions=['fenced_code','tables'])


def format_io(self, y):
    if y is None: return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask) # 输入部分太自由，预处理一波
    y[-1] = (
        None if i_ask is None else markdown.markdown(i_ask, extensions=['fenced_code','tables']),
        None if gpt_reply is None else markdown_convertion(gpt_reply)
    )
    return y


def find_free_port():
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]