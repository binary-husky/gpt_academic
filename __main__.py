import os
import gradio as gr
from request_llm.bridge_all import predict
from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_user_upload, \
    get_user_download, get_conf, ArgsGeneralWrapper, DummyWith

# 问询记录, python 版本建议3.9+（越新越好）
import logging

# 一些普通功能模块
from core_functional import get_core_functions

functional = get_core_functions()

# 高级函数插件
from crazy_functional import get_crazy_functions

crazy_fns = get_crazy_functions()

# 处理markdown文本格式的转变
gr.Chatbot.postprocess = format_io

# 做一些外观色彩上的调整
from theme import adjust_theme, advanced_css

set_theme = adjust_theme()

# 代理与自动更新
from check_proxy import check_proxy, auto_update, warm_up_modules

import func_box

from check_proxy import get_current_version

os.makedirs("gpt_log", exist_ok=True)
try:
    logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO, encoding="utf-8")
except:
    logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO)
print("所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log, 请注意自我隐私保护哦！")

# 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY, AVAIL_LLM_MODELS = \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT',
             'API_KEY', 'AVAIL_LLM_MODELS')

proxy_info = check_proxy(proxies)
# 如果WEB_PORT是-1, 则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
if not AUTHENTICATION: AUTHENTICATION = None
os.environ['no_proxy'] = '*'  # 避免代理网络产生意外污染


class ChatBotFrame:

    def __init__(self):
        self.cancel_handles = []
        self.initial_prompt = "In answer to my question, Think about what are some alternative perspectives"
        self.title_html = f"<h1 align=\"center\">ksoGPT  {get_current_version()}</h1>"
        self.description = """代码开源和更新[地址🚀](https://github.com/binary-husky/chatgpt_academic)，感谢热情的[开发者们❤️](https://github.com/binary-husky/chatgpt_academic/graphs/contributors)"""


class ChatBot(ChatBotFrame):

    def __init__(self):
        super().__init__()
        self.__url = f'http://{func_box.ipaddr()}:{PORT}'
        # self.__gr_url = gr.State(self.__url)

    def draw_title(self):
        self.title = gr.HTML(self.title_html)
        self.cookies = gr.State({'api_key': API_KEY, 'llm_model': LLM_MODEL, 'local': self.__url})

    def draw_chatbot(self):
        with gr.Box():
            self.chatbot = gr.Chatbot(label=f"当前模型：{LLM_MODEL}")
            self.chatbot.style(height=CHATBOT_HEIGHT)
            self.history = gr.State([])
            with gr.Row():
                self.status = gr.Markdown(f"Tip: 按Enter提交, 按Shift+Enter换行。当前模型: {LLM_MODEL} \n {proxy_info}")

    def draw_input_chat(self):
        with gr.Accordion("输入区", open=True) as self.area_input_primary:
            with gr.Row():
                self.txt = gr.Textbox(show_label=False, placeholder="Input question here.").style(container=False)
            with gr.Row():
                self.submitBtn = gr.Button("提交", variant="primary")
            with gr.Row():
                self.resetBtn = gr.Button("重置", variant="secondary");
                self.stopBtn = gr.Button("停止", variant="secondary");
                self.resetBtn.style(size="sm")
                self.stopBtn.style(size="sm")

    def draw_function_chat(self):
        with gr.Tab('Function'):
            with gr.Accordion("基础功能区", open=True) as self.area_basic_fn:
                with gr.Row():
                    for k in functional:
                        variant = functional[k]["Color"] if "Color" in functional[k] else "secondary"
                        functional[k]["Button"] = gr.Button(k, variant=variant)

    def draw_public_chat(self):
        with gr.Tab('Public'):
            with gr.Accordion("上传本地文件可供高亮函数插件调用", open=False) as self.area_file_up:
                self.file_upload = gr.Files(label="任何文件, 但推荐上传压缩文件(zip, tar)",
                                            file_count="multiple")
                self.file_upload.style()
                with gr.Row():
                    self.upload_history = gr.Button("Get Upload History", variant="secondary")
                    self.get_download = gr.Button('Get Download Link', variant='stop')
                    self.upload_history.style(size='sm')
                    self.get_download.style(size='sm')
            with gr.Accordion("函数插件区", open=True) as self.area_crazy_fn:
                with gr.Row():
                    for k in crazy_fns:
                        if not crazy_fns[k].get("AsButton", True): continue
                        self.variant = crazy_fns[k]["Color"] if "Color" in crazy_fns[k] else "secondary"
                        crazy_fns[k]["Button"] = gr.Button(k, variant=self.variant)
                        crazy_fns[k]["Button"].style(size="sm")
                with gr.Accordion("更多函数插件", open=False):
                    dropdown_fn_list = [k for k in crazy_fns.keys() if
                                        not crazy_fns[k].get("AsButton", True)]
                    self.dropdown = gr.Dropdown(dropdown_fn_list, value=r"打开插件列表", label="").style(
                            container=False)
                    self.switchy_bt = gr.Button(r"请先从插件列表中选择", variant="secondary")

    def draw_setting_chat(self):
        with gr.Tab('Setting'):
            self.top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01, interactive=True, label="Top-p (nucleus sampling)", )
            self.temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True, label="Temperature", )
            self.max_length_sl = gr.Slider(minimum=256, maximum=4096, value=4096, step=1, interactive=True, label="MaxLength", )
            self.models_box = gr.CheckboxGroup(["input加密"], value=["input加密"], label="对话模式")
            self.system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=f"System Prompt", label="System prompt", value=self.initial_prompt)
            self.md_dropdown = gr.Dropdown(AVAIL_LLM_MODELS, value=LLM_MODEL, label="更换LLM模型/请求源").style(container=False)


            # temp = gr.Markdown(self.description)

    def draw_goals_auto(self):
        with gr.Tab('Ai Prompt'):
            with gr.Row():
                self.ai_name = gr.Textbox(show_label=False, placeholder="给Ai一个名字").style(container=False)
            with gr.Row():
                self.ai_role = gr.Textbox(lines=5, show_label=False, placeholder="请输入你的需求").style(container=False)
            with gr.Row():
                self.ai_goal_list = gr.Dataframe(headers=['Goals'], interactive=True, row_count=4, col_count=(1, 'fixed'),  type='array')
            with gr.Row():
                self.ai_budget = gr.Number(show_label=False, value=0.0, info="关于本次项目的预算，超过预算自动停止，默认无限").style(container=False)
                # self.ai_goal_list.style()

        with gr.Tab('Ai Settings'):
            pass

    def draw_next_auto(self):
        with gr.Row():
            self.text_continue = gr.Textbox(visible=False, show_label=False, placeholder="请根据提示输入执行命令").style(container=False)
        with gr.Row():
            self.submit_start = gr.Button("Start", variant='primary')
            self.submit_next = gr.Button("Next", visible=False, variant='primary')
            self.submit_stop = gr.Button("Stop", variant="stop")
            self.agent_obj = gr.State({'obj': None, "start": self.submit_start,
                                       "next": self.submit_next, "text": self.text_continue})

    def signals_input_setting(self):
        # 注册input
        self.input_combo = [self.cookies, self.max_length_sl, self.md_dropdown,
                       self.txt, self.top_p, self.temperature, self.chatbot, self.history,
                       self.system_prompt, self.models_box]
        self.output_combo = [self.cookies, self.chatbot, self.history, self.status, self.txt]
        self.predict_args = dict(fn=ArgsGeneralWrapper(predict), inputs=self.input_combo, outputs=self.output_combo)
        # 提交按钮、重置按钮
        self.cancel_handles.append(self.txt.submit(**self.predict_args))
        self.cancel_handles.append(self.submitBtn.click(**self.predict_args))
        self.resetBtn.click(lambda: ([], [], "已重置"), None, [self.chatbot, self.history, self.status])

    def signals_function(self):
        # 基础功能区的回调函数注册
        for k in functional:
            self.click_handle = functional[k]["Button"].click(fn=ArgsGeneralWrapper(predict),
                                                         inputs=[*self.input_combo, gr.State(True), gr.State(k)],
                                                         outputs=self.output_combo)
            self.cancel_handles.append(self.click_handle)

    def signals_public(self):
        # 文件上传区，接收文件后与chatbot的互动
        self.file_upload.upload(on_file_uploaded, [self.file_upload, self.chatbot, self.txt], [self.chatbot, self.txt])
        self.upload_history.click(get_user_upload, [self.chatbot], outputs=[self.chatbot])
        self.get_download.click(get_user_download, [self.chatbot, self.cookies, self.txt], outputs=[self.chatbot, self.txt])
        # 函数插件-固定按钮区
        for k in crazy_fns:
            if not crazy_fns[k].get("AsButton", True): continue
            self.click_handle = crazy_fns[k]["Button"].click(
                ArgsGeneralWrapper(crazy_fns[k]["Function"]), [*self.input_combo, gr.State(PORT)], self.output_combo)
            self.click_handle.then(on_report_generated, [self.file_upload, self.chatbot], [self.file_upload, self.chatbot])
            self.cancel_handles.append(self.click_handle)

        # 函数插件-下拉菜单与随变按钮的互动
        def on_dropdown_changed(k):
            variant = crazy_fns[k]["Color"] if "Color" in crazy_fns[k] else "secondary"
            return {self.switchy_bt: gr.update(value=k, variant=variant)}
        self.dropdown.select(on_dropdown_changed, [self.dropdown], [self.switchy_bt])
        
        # 随变按钮的回调函数注册
        def route(k, *args, **kwargs):
            if k in [r"打开插件列表", r"请先从插件列表中选择"]: return
            yield from ArgsGeneralWrapper(crazy_fns[k]["Function"])(*args , **kwargs)
        self.click_handle = self.switchy_bt.click(route, [self.switchy_bt, *self.input_combo], self.output_combo)
        self.click_handle.then(on_report_generated, [self.file_upload, self.chatbot], [self.file_upload, self.chatbot])
        self.cancel_handles.append(self.click_handle)
        # 终止按钮的回调函数注册
        self.stopBtn.click(fn=None, inputs=None, outputs=None, cancels=self.cancel_handles)
        def on_md_dropdown_changed(k):
            return {self.chatbot: gr.update(label="当前模型："+k)}
        self.md_dropdown.select(on_md_dropdown_changed, [self.md_dropdown], [self.chatbot])


    def signals_auto_input(self):
        from autogpt.cli import agent_main
        self.auto_input_combo = [self.ai_name, self.ai_role, self.ai_goal_list, self.ai_budget,
                                self.cookies, self.chatbot, self.history,
                                self.agent_obj]
        self.auto_output_combo = [self.cookies, self.chatbot, self.history, self.status,
                                  self.agent_obj, self.submit_start, self.submit_next, self.text_continue]
        self.submit_start.click(fn=agent_main, inputs=self.auto_input_combo, outputs=self.auto_output_combo)


    # gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
    def auto_opentab_delay(self):
        import threading, webbrowser, time

        print(f"如果浏览器没有自动打开，请复制并转到以下URL：")
        print(f"\t（亮色主题）: http://localhost:{PORT}")
        print(f"\t（暗色主题）: {self.__url}/?__dark-theme=true")
    
        def open():
            time.sleep(2)  # 打开浏览器
            webbrowser.open_new_tab(f"http://localhost:{PORT}/?__dark-theme=true")
        threading.Thread(target=open, name="open-browser", daemon=True).start()
        threading.Thread(target=auto_update, name="self-upgrade", daemon=True).start()
        # threading.Thread(target=warm_up_modules, name="warm-up", daemon=True).start()


    def main(self):
        with gr.Blocks(title="ChatGPT For Tester", theme=set_theme, analytics_enabled=False, css=advanced_css) as demo:
            # 绘制页面title
            self.draw_title()
            # 绘制一个ROW，row会让底下的元素自动排部
            with gr.Row():
                # 绘制列1
                with gr.Column(scale=100) as chat:
                    pass
                # 绘制列2
                with gr.Column(scale=51):
                    # 绘制对话模组
                    with gr.Tab('对话模式'):
                        self.draw_input_chat()
                        self.draw_function_chat()
                        self.draw_public_chat()
                        self.draw_setting_chat()
                    # 绘制autogpt模组
                    with gr.Tab('Auto-GPT'):
                        self.draw_next_auto()
                        self.draw_goals_auto()
                with chat:
                    self.draw_chatbot()
            # 函数注册，需要在Blocks下进行
            self.signals_input_setting()
            self.signals_function()
            self.signals_public()
            self.signals_auto_input()
        # Start
        self.auto_opentab_delay()
        demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION)

if __name__ == '__main__':
    ChatBot().main()

