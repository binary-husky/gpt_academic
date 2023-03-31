import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
import gradio as gr
from predict import predict
from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf

# 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION = \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION')


# 如果WEB_PORT是-1, 则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
if not AUTHENTICATION: AUTHENTICATION = None

initial_prompt = "Serve me as a writing and programming assistant."
title_html = """<h1 align="center">ChatGPT 学术优化</h1>"""

# 问询记录, python 版本建议3.9+（越新越好）
import logging
os.makedirs('gpt_log', exist_ok=True)
try:logging.basicConfig(filename='gpt_log/chat_secrets.log', level=logging.INFO, encoding='utf-8')
except:logging.basicConfig(filename='gpt_log/chat_secrets.log', level=logging.INFO)
print('所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log, 请注意自我隐私保护哦！')

# 一些普通功能模块
from functional import get_functionals
functional = get_functionals()

# 对一些丧心病狂的实验性功能模块进行测试
from functional_crazy import get_crazy_functionals
crazy_functional = get_crazy_functionals()

# 处理markdown文本格式的转变
gr.Chatbot.postprocess = format_io

# 做一些外观色彩上的调整
from theme import adjust_theme
set_theme = adjust_theme()

cancel_handles = []
with gr.Blocks(theme=set_theme, analytics_enabled=False) as demo:
    gr.HTML(title_html)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot()
            chatbot.style(height=1150)
            chatbot.style()
            history = gr.State([])
        with gr.Column(scale=1):
            with gr.Row():
                txt = gr.Textbox(show_label=False, placeholder="Input question here.").style(container=False)
            with gr.Row():
                submitBtn = gr.Button("提交", variant="primary")
            with gr.Row():
                resetBtn = gr.Button("重置", variant="secondary"); resetBtn.style(size="sm")
                stopBtn = gr.Button("停止", variant="secondary"); stopBtn.style(size="sm")
            with gr.Row():
                from check_proxy import check_proxy
                statusDisplay = gr.Markdown(f"Tip: 按Enter提交, 按Shift+Enter换行。当前模型: {LLM_MODEL} \n {check_proxy(proxies)}")
            with gr.Accordion("基础功能区", open=True):
                with gr.Row():
                    for k in functional:
                        variant = functional[k]["Color"] if "Color" in functional[k] else "secondary"
                        functional[k]["Button"] = gr.Button(k, variant=variant)
            with gr.Accordion("函数插件区", open=True):
                with gr.Row():
                    gr.Markdown("注意：以下“红颜色”标识的函数插件需从input区读取路径作为参数.")
                with gr.Row():
                    for k in crazy_functional:
                        variant = crazy_functional[k]["Color"] if "Color" in crazy_functional[k] else "secondary"
                        crazy_functional[k]["Button"] = gr.Button(k, variant=variant)
                with gr.Row():
                    with gr.Accordion("展开“文件上传区”。上传本地文件供“红颜色”的函数插件调用。", open=False):
                        file_upload = gr.Files(label='任何文件, 但推荐上传压缩文件(zip, tar)', file_count="multiple")
            with gr.Accordion("展开SysPrompt & GPT参数 & 交互界面布局", open=False):
                system_prompt = gr.Textbox(show_label=True, placeholder=f"System Prompt", label="System prompt", value=initial_prompt)
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01,interactive=True, label="Top-p (nucleus sampling)",)
                temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True, label="Temperature",)
                checkboxes = gr.CheckboxGroup(["基础功能区", "函数插件区", "文件上传区"], value=["USA", "Japan", "Pakistan"], 
                                                label="显示功能区")
    predict_args = dict(fn=predict, inputs=[txt, top_p, temperature, chatbot, history, system_prompt], outputs=[chatbot, history, statusDisplay], show_progress=True)
    empty_txt_args = dict(fn=lambda: "", inputs=[], outputs=[txt]) # 用于在提交后清空输入栏

    cancel_handles.append(txt.submit(**predict_args))
    # txt.submit(**empty_txt_args) 在提交后清空输入栏
    cancel_handles.append(submitBtn.click(**predict_args))
    # submitBtn.click(**empty_txt_args) 在提交后清空输入栏
    resetBtn.click(lambda: ([], [], "已重置"), None, [chatbot, history, statusDisplay])
    for k in functional:
        click_handle = functional[k]["Button"].click(predict,
            [txt, top_p, temperature, chatbot, history, system_prompt, gr.State(True), gr.State(k)], [chatbot, history, statusDisplay], show_progress=True)
        cancel_handles.append(click_handle)
    file_upload.upload(on_file_uploaded, [file_upload, chatbot, txt], [chatbot, txt])
    for k in crazy_functional:
        click_handle = crazy_functional[k]["Button"].click(crazy_functional[k]["Function"],
            [txt, top_p, temperature, chatbot, history, system_prompt, gr.State(PORT)], [chatbot, history, statusDisplay]
        )
        try: click_handle.then(on_report_generated, [file_upload, chatbot], [file_upload, chatbot])
        except: pass
        cancel_handles.append(click_handle)
    stopBtn.click(fn=None, inputs=None, outputs=None, cancels=cancel_handles)

# gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
def auto_opentab_delay():
    import threading, webbrowser, time
    print(f"如果浏览器没有自动打开，请复制并转到以下URL: http://localhost:{PORT}")
    def open(): 
        time.sleep(2)
        webbrowser.open_new_tab(f'http://localhost:{PORT}')
    threading.Thread(target=open, name="open-browser", daemon=True).start()

auto_opentab_delay()
demo.title = "ChatGPT 学术优化"
demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", share=True, server_port=PORT, auth=AUTHENTICATION)
