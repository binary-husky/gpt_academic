#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :
import gradio as gr
from common import func_box
from webui_elem import webui_local

i18n = webui_local.I18nAuto()
get_html = func_box.get_html


class LeftElem:

    def __init__(self):
        pass

    def _draw_history_head(self):
        with gr.Row(elem_id="chuanhu-history-header"):
            with gr.Row(elem_id="chuanhu-history-search-row"):
                with gr.Column(min_width=150, scale=2):
                    self.historySearchTextbox = gr.Textbox(show_label=False, container=False,
                                                           placeholder=i18n("搜索对话详情..."), lines=1,
                                                           elem_id="history-search-tb")
                with gr.Column(min_width=52, scale=1, elem_id="gr-history-header-btns"):
                    self.uploadFileBtn = gr.UploadButton(
                        interactive=True, label="", file_types=[".json"],
                        elem_id="gr-history-upload-btn")
                    self.historyRefreshBtn = gr.Button("", elem_id="gr-history-refresh-btn")

    def _draw_history_body(self):
        with gr.Row(elem_id="chuanhu-history-body"):
            with gr.Column(scale=6, elem_id="history-select-wrap"):
                self.historySelectList = gr.Radio(
                    label=i18n("从列表中加载对话"),
                    choices=['123', '213'],
                    value='123',
                    # multiselect=False,
                    container=False,
                    elem_id="history-select-dropdown"
                )
            with gr.Row(visible=False):
                self.historyDeleteBtn = gr.Button(i18n("🗑️"), elem_id="gr-history-delete-btn")
                self.historyDownloadBtn = gr.Button(i18n("⏬"), elem_id="gr-history-download-btn")
                self.historyMarkdownDownloadBtn = gr.Button(i18n("⤵️"), elem_id="gr-history-markdown-download-btn")
                self.historyMasksConverterBtn = gr.Button('mask', elem_id='gr-history-masks-converter-btn')

    def _draw_history_edit(self):
        with gr.Row(visible=False):
            with gr.Column(scale=6):
                self.saveFileName = gr.Textbox(
                    show_label=True,
                    placeholder=i18n("设置文件名: 默认为.json，可选为.md"),
                    label=i18n("设置保存文件名"),
                    value=i18n("对话历史记录"),
                    elem_classes="no-container"
                    # container=False,
                )
            with gr.Column(scale=1):
                self.renameHistoryBtn = gr.Button(i18n("💾 Rename Chat"),
                                                  elem_id="gr-history-save-btn")
                self.exportMarkdownBtn = gr.Button(i18n("📝 Export as Markdown"),
                                                   elem_id="gr-markdown-export-btn")

    def draw_history_area(self):
        with gr.Column(elem_id="menu-area"):
            with gr.Column(elem_id="chuanhu-history"):
                with gr.Box():
                    self._draw_history_head()
                    self._draw_history_body()
                    self._draw_history_edit()

            with gr.Column(elem_id="chuanhu-menu-footer"):
                with gr.Row(elem_id="chuanhu-func-nav"):
                    gr.HTML(get_html("func_nav.html"))
                # gr.HTML(get_html("footer.html").format(versions=versions_html()), elem_id="footer")
                # gr.Markdown(CHUANHU_DESCRIPTION, elem_id="chuanhu-author")
