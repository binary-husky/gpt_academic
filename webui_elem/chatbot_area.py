#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :
import gradio as gr
from comm_tools import webui_local, func_box, toolbox
from webui_elem import func_signals

i18n = webui_local.I18nAuto()
get_html = func_box.get_html
LLM_MODEL, AVAIL_LLM_MODELS = toolbox.get_conf('LLM_MODEL', 'AVAIL_LLM_MODELS')


class ChatbotElem:

    def __init__(self):
        pass

    def _draw_chatbot_head(self):
        with gr.Row(elem_id="chatbot-header"):
            self.model_select_dropdown = gr.Dropdown(
                label=i18n("选择模型"), choices=AVAIL_LLM_MODELS, multiselect=False, value=LLM_MODEL, interactive=True,
                show_label=False, container=False, elem_id="model-select-dropdown"
            )
            self.lora_select_dropdown = gr.Dropdown(
                label=i18n("选择LoRA模型"), choices=[], multiselect=False, interactive=True,
                visible=False, container=False,
            )
            gr.HTML(get_html("chatbot_header_btn.html").format(
                json_label=i18n("历史记录（JSON）"), md_label=i18n("导出为 Markdown")),
                elem_id="chatbot-header-btn-bar")

    def _draw_chatbot_body(self):
        avatar_images, latex_option = toolbox.get_conf('avatar_images', 'latex_option')
        with gr.Row():
            latex_format = func_signals.latex_delimiters_dict[latex_option[0]]
            self.chatbot = gr.Chatbot(
                label="Chuanhu Chat",
                elem_id="chuanhu-chatbot",
                latex_delimiters=latex_format,
                # height=700,
                show_label=False,
                avatar_images=avatar_images,
                show_share_button=False,
            )

    def _draw_chatbot_input(self):
        with gr.Row(elem_id="chatbot-footer"):
            with gr.Box(elem_id="chatbot-input-box"):
                with gr.Row(elem_id="chatbot-input-row"):
                    with gr.Row(elem_id='gr-more-sm-row'):
                        self.sm_upload = gr.Files(label='上传文件编辑', type='file',
                                                  elem_id='upload-index-file',
                                                  visible=True, interactive=True)
                        with gr.Column(scale=1, elem_id='gr-more-sm-column'):
                            gr.HTML(get_html("chatbot_more.html").format(
                                single_turn_label=i18n("无记忆"), plugin_agent_label=i18n("插件代理"),
                                upload_file_label=i18n("上传文件"), uploaded_files_label=i18n("预提交文件"),
                                uploaded_files_tip=i18n("点击高亮插件，这些文件会被插件解析一起提交"),
                                plugin_agent_tip=i18n('对话自动选择插件'),
                                single_turn_tip=i18n('对话不参考上下文')
                            ))
                            self.use_websearch_checkbox = gr.Checkbox(label=i18n(
                                "使用插件代理"), value=False, elem_classes="switch-checkbox", elem_id="gr-websearch-cb",
                                visible=False)
                        with gr.Column(scale=1, elem_id='gr-chat-sm-column', elem_classes='') as self.sm_btn_column:
                                self.sm_code_block = gr.Button(value='< > 代码块', elem_id='sm_code_btn')
                                self.sm_upload_history = gr.Button("🥷 我的文件", elem_id='sm_file_btn')

                        with gr.Column(scale=1, elem_classes='gr-know-sm-column') as self.sm_know_select:
                            self.langchain_dropdown = gr.Dropdown(choices=[], value=[],
                                                                  show_label=True, interactive=True, label='知识库',
                                                                  multiselect=True, container=False,
                                                                  elem_classes='sm_select', elem_id='')

                    with gr.Row(elem_id="chatbot-input-tb-row"):
                        with gr.Column(min_width=225, scale=12):
                            self.user_input = gr.Textbox(
                                elem_id="user-input-tb", show_label=False,
                                placeholder=i18n("在这里输入，支持粘贴上传文件"), elem_classes="no-container",
                                max_lines=5,
                                # container=False
                            )
                        with gr.Column(min_width=42, scale=1, elem_id="chatbot-ctrl-btns"):
                            self.submitBtn = gr.Button(value="", variant="primary", elem_id="submit-btn")
                            self.input_copy = gr.State('')
                            self.cancelBtn = gr.Button(value="", variant="secondary", visible=False, elem_id="cancel-btn")
                # Note: Buttons below are set invisible in UI. But they are used in JS.
                with gr.Row(elem_id="chatbot-buttons", visible=False):
                    with gr.Column(min_width=120, scale=1):
                        self.emptyBtn = gr.Button(i18n("🧹 新的对话"), elem_id="empty-btn")
                    with gr.Column(min_width=120, scale=1):
                        self.retryBtn = gr.Button(i18n("🔄 重新生成"), elem_id="gr-retry-btn")
                    with gr.Column(min_width=120, scale=1):
                        self.delFirstBtn = gr.Button(i18n("🗑️ 删除最旧对话"))
                    with gr.Column(min_width=120, scale=1):
                        self.delLastBtn = gr.Button(i18n("🗑️ 删除最新对话"), elem_id="gr-dellast-btn")
                    with gr.Row(visible=False) as like_dislike_area:
                        with gr.Column(min_width=20, scale=1):
                            self.likeBtn = gr.Button(i18n("👍"), elem_id="gr-like-btn")
                        with gr.Column(min_width=20, scale=1):
                            self.dislikeBtn = gr.Button(i18n("👎"), elem_id="gr-dislike-btn")

    def draw_chatbot_area(self):
        with gr.Column(elem_id="chuanhu-area", scale=5):
            with gr.Column(elem_id="chatbot-area"):
                self._draw_chatbot_head()
                self._draw_chatbot_body()
                self._draw_chatbot_input()

