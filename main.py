import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
import gradio as gr 
from predict import predict
from toolbox import format_io, find_free_port

# 建议您复制一个config_private.py放自己的秘密，如API和代理网址，避免不小心传github被别人看到
try: from config_private import proxies, WEB_PORT 
except: from config import proxies, WEB_PORT

# 如果WEB_PORT是-1，则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT

initial_prompt = "Serve me as a writing and programming assistant."
title_html = """<h1 align="center">ChatGPT 学术优化</h1>"""

import logging
os.makedirs('gpt_log', exist_ok=True)
logging.basicConfig(filename='gpt_log/chat_secrets.log', level=logging.INFO, encoding='utf-8') # python 版本建议3.9+（越新越好）
print('所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log，请注意自我隐私保护哦！')

# 一些普通功能模块
from functional import get_functionals
functional = get_functionals()

# 对一些丧心病狂的实验性功能模块进行测试
from functional_crazy import get_crazy_functionals
crazy_functional = get_crazy_functionals()

# 处理markdown文本格式的转变
gr.Chatbot.postprocess = format_io

with gr.Blocks() as demo:   # 借助gradio框架，实现webUI
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
    for k in functional:
        functional[k]["Button"].click(predict, 
            [txt, top_p, temperature, chatbot, history, systemPromptTxt, TRUE, gr.State(k)], [chatbot, history, statusDisplay], show_progress=True)
    for k in crazy_functional:
        crazy_functional[k]["Button"].click(crazy_functional[k]["Function"], 
            [txt, top_p, temperature, chatbot, history, systemPromptTxt, gr.State(PORT)], [chatbot, history, statusDisplay])

# 延迟函数，做一些准备工作，最后尝试打开浏览器
def auto_opentab_delay():
    import threading, webbrowser, time
    print(f"URL http://localhost:{PORT}")
    def open(): time.sleep(2)
    webbrowser.open_new_tab(f'http://localhost:{PORT}')
    t = threading.Thread(target=open)
    t.daemon = True; t.start()

auto_opentab_delay()
demo.title = "ChatGPT 学术优化"
demo.queue().launch(server_name="0.0.0.0", share=True, server_port=PORT)
