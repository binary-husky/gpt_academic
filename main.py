import os; os.environ['no_proxy'] = '*' 
import gradio as gr 
import markdown, mdtex2html
from predict import predict
from show_math import convert as convert_math

try: from config_private import proxies, WEB_PORT # 放自己的秘密如API和代理网址 os.path.exists('config_private.py')
except: from config import proxies, WEB_PORT

def find_free_port():
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT

initial_prompt = "Serve me as a writing and programming assistant."
title_html = """<h1 align="center">ChatGPT 学术优化</h1>"""

import logging
os.makedirs('gpt_log', exist_ok=True)
logging.basicConfig(filename='gpt_log/chat_secrets.log', level=logging.INFO, encoding='utf-8')
print('所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log，请注意自我隐私保护哦！')

# 一些普通功能
from functional import get_functionals
functional = get_functionals()

# 对一些丧心病狂的实验性功能进行测试
from functional_crazy import get_crazy_functionals
crazy_functional = get_crazy_functionals()

def reset_textbox(): return gr.update(value='')

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
        math_config = {'mdx_math': {'enable_dollar_delimiter': True}}
        return markdown.markdown(txt,extensions=['fenced_code','tables']) + '<br><br>' + \
            markdown.markdown(convert_math(txt, splitParagraphs=False),extensions=['fenced_code','tables'])
    else:
        return markdown.markdown(txt,extensions=['fenced_code','tables'])


def format_io(self,y):
    if y is None:
        return []
    i_ask, gpt_reply = y[-1]
    
    i_ask = text_divide_paragraph(i_ask) # 输入部分太自由，预处理一波
    
    y[-1] = (
        None if i_ask is None else markdown.markdown(i_ask, extensions=['fenced_code','tables']),
        None if gpt_reply is None else markdown_convertion(gpt_reply)
    )
    return y
gr.Chatbot.postprocess = format_io

with gr.Blocks() as demo:
    gr.HTML(title_html)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot()
            chatbot.style(height=1000)
            chatbot.style()
            history = gr.State([])
            TRUE = gr.State(True)
            FALSE = gr.State(False)
        with gr.Column(scale=1):
            with gr.Row():
                with gr.Column(scale=12):
                    txt = gr.Textbox(show_label=False, placeholder="Input question here.").style(container=False)
                with gr.Column(scale=1):
                    submitBtn = gr.Button("Ask", variant="primary")
            with gr.Row():
                for k in functional:
                    variant = functional[k]["Color"] if "Color" in functional[k] else "secondary"
                    functional[k]["Button"] = gr.Button(k, variant=variant)
                for k in crazy_functional:
                    variant = crazy_functional[k]["Color"] if "Color" in crazy_functional[k] else "secondary"
                    crazy_functional[k]["Button"] = gr.Button(k, variant=variant)
            from check_proxy import check_proxy
            statusDisplay = gr.Markdown(f"{check_proxy(proxies)}")
            systemPromptTxt = gr.Textbox(show_label=True, placeholder=f"System Prompt", label="System prompt", value=initial_prompt).style(container=True)
            #inputs, top_p, temperature, top_k, repetition_penalty
            with gr.Accordion("arguments", open=False):
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01,interactive=True, label="Top-p (nucleus sampling)",)
                temperature = gr.Slider(minimum=-0, maximum=5.0, value=1.0, step=0.01, interactive=True, label="Temperature",)

    txt.submit(predict, [txt, top_p, temperature, chatbot, history, systemPromptTxt], [chatbot, history, statusDisplay])
    submitBtn.click(predict, [txt, top_p, temperature, chatbot, history, systemPromptTxt], [chatbot, history, statusDisplay], show_progress=True)
    # submitBtn.click(reset_textbox, [], [txt])
    for k in functional:
        functional[k]["Button"].click(predict, 
            [txt, top_p, temperature, chatbot, history, systemPromptTxt, TRUE, gr.State(k)], [chatbot, history, statusDisplay], show_progress=True)
    for k in crazy_functional:
        crazy_functional[k]["Button"].click(crazy_functional[k]["Function"], 
            [txt, top_p, temperature, chatbot, history, systemPromptTxt, gr.State(PORT)], [chatbot, history, statusDisplay])

print(f"URL http://localhost:{PORT}")
demo.title = "ChatGPT 学术优化"

def auto_opentab_delay():
    import threading, webbrowser, time
    def open(): time.sleep(2)
    webbrowser.open_new_tab(f'http://localhost:{PORT}')
    t = threading.Thread(target=open)
    t.daemon = True; t.start()

auto_opentab_delay()
demo.queue().launch(server_name="0.0.0.0", share=True, server_port=PORT)
