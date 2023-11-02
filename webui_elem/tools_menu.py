#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :

import gradio as gr
from comm_tools import webui_local, func_box, toolbox
from comm_tools.crazy_functional import crazy_fns_role, crazy_classification, crazy_fns

default_plugin, = toolbox.get_conf('default_plugin')
i18n = webui_local.I18nAuto()
get_html = func_box.get_html


class RightElem:

    def __init__(self):
        self.initial_prompt = ''

    def _draw_tools_head(self):
        with gr.Row():
            gr.Markdown("## " + i18n("工具箱"))
            gr.HTML(get_html("close_btn.html").format(
                obj="toolbox"), elem_classes="close-btn")

    def _draw_function_chat(self):
        preset_prompt, = toolbox.get_conf('preset_prompt')
        with gr.TabItem('基础', id='func_tab', elem_id='chuanhu-toolbox-tabs'):
            self.system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=f"System Prompt",
                                            label="System prompt", value=self.initial_prompt)

            func_box.md_division_line()
            self.sm_upload = gr.Files(label='Upload file', type='file', elem_id='upload-index-file',
                                      visible=True, interactive=True, container=False)
            func_box.md_division_line()
            with gr.Row():
                self.pro_search_txt = gr.Textbox(placeholder='搜索提示词/Masks', show_label=False, elem_classes='pm_search',)
                self.multiplexing_edit_check = gr.Checkbox(value=True, label='复用', show_label=True, elem_id='pm_check',
                                                     interactive=True, container=False)
            self.pro_func_prompt = gr.Dataset(components=[gr.HTML()], label="提示词列表", visible=False,
                                              samples=[['...', ""] for i in range(20)], type='index',
                                              elem_id='prompt_list', samples_per_page=10, )
            self.pro_fp_state = gr.State({'samples': None})

    def _draw_plugin_chat(self):
        with gr.TabItem('插件', id='plug_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Accordion("上传本地文件可供高亮函数插件调用", open=False, visible=False) as self.area_file_up:
                self.file_upload = gr.Files(label="任何文件, 但推荐上传压缩文件(zip, tar)",
                                            file_count="multiple").style()
            self.plugin_dropdown = gr.Dropdown(choices=crazy_classification, label='选择插件分类', value=default_plugin,
                                               multiselect=True, interactive=True, elem_classes='normal_mut_select'
                                               ).style(container=False)
            with gr.Accordion("函数插件区/高亮插件需要输入框支持", open=True) as self.area_crazy_fn:
                with gr.Row():
                    for role in crazy_fns_role:
                        for k in crazy_fns_role[role]:
                            if not crazy_fns_role[role][k].get("AsButton", True): continue
                            if role not in default_plugin:
                                variant = crazy_fns_role[role][k]["Color"] if "Color" in crazy_fns_role[role][k] else "secondary"
                                crazy_fns_role[role][k]['Button'] = gr.Button(k, variant=variant, visible=False).style(size="sm")
                            else:
                                variant = crazy_fns[k]["Color"] if "Color" in crazy_fns_role[role][k] else "secondary"
                                crazy_fns_role[role][k]['Button'] = gr.Button(k, variant=variant, visible=True).style(size="sm")
            func_box.md_division_line()
            with gr.Accordion("更多函数插件/自定义插件参数", open=True, ):
                dropdown_fn_list = []
                for role in crazy_fns_role:
                    if role in default_plugin:
                        for k in crazy_fns_role[role]:
                            if not crazy_fns_role[role][k].get("AsButton", True):
                                dropdown_fn_list.append(k)
                            elif crazy_fns_role[role][k].get('AdvancedArgs', False):
                                dropdown_fn_list.append(k)
                self.dropdown_fn = gr.Dropdown(dropdown_fn_list, value=r"打开插件列表", interactive=True, show_label=False, label="").style(
                    container=False)
                self.plugin_advanced_arg = gr.Textbox(show_label=True, label="高级参数输入区", visible=False, elem_classes='no_padding_input',
                                                 placeholder="这里是特殊函数插件的高级参数输入区").style()
                self.switchy_bt = gr.Button(r"请先从插件列表中选择", variant="secondary", visible=False)

    def _draw_langchain_base(self):
        spl, = toolbox.get_conf('spl')
        with gr.TabItem('知识库', id='langchain_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Box():
                with gr.Row():
                    self.langchain_classifi = gr.Dropdown(choices=[], value="公共知识库", interactive=True, label="选择知识库分类",
                                                        elem_classes='normal_select').style(container=False)
                with gr.Row():
                    self.langchain_class_name = gr.Textbox(show_label=False, placeholder='*必填，构建知识库同时创建分类', elem_classes='no_padding_input',
                                                          visible=False, interactive=True).style()
            with gr.Box():
                self.langchain_upload = gr.Files(label="解析支持多类型文档，多文件建议使用zip上传", file_count="multiple", file_types=spl)
                self.langchain_links = gr.Textbox(show_label=False, placeholder='网络文件,多个链接使用换行间隔',
                                                  elem_classes='no_padding_input').style()
                self.langchain_know_kwargs = gr.State({'file_path': '', 'know_name': '', 'know_obj': {}, 'file_list': []})
                #  file_path 是上传文件存储的地址，know_name，know_obj是ql向量化后的对象
            func_box.md_division_line()
            with gr.Box():
                with gr.Row():
                    self.langchain_select = gr.Dropdown(choices=[], value=r"新建知识库",
                                                        interactive=True, label="新建or增量重构", elem_classes='normal_select').style(container=False)
                with gr.Row():
                    self.langchain_name = gr.Textbox(show_label=False, placeholder='知识库名称or重命名').style(container=False)
            with gr.Row():
                self.langchain_submit = gr.Button(value='构建/更新知识库', variant='primary').style(size='sm')
                self.langchain_stop = gr.Button(value='停止构建').style(size='sm')
            self.langchain_status = gr.Markdown(value='')
            self.langchain_error = gr.Markdown(value='')

    def _draw_setting_chat(self):
        worker_num, = toolbox.get_conf('DEFAULT_WORKER_NUM')
        with gr.TabItem('调优', id='sett_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Box():
                # gr.Markdown(func_box.get_html('what_news.html').replace('{%v}', 'LLMs调优参数'))
                default_params, = toolbox.get_conf('LLMS_DEFAULT_PARAMETER')
                with gr.Accordion(label='LLMs调优参数', open=False):
                    self.top_p = gr.Slider(minimum=-0, maximum=1.0, value=default_params['top_p'], step=0.01, interactive=True,
                                           label="Top-p", ).style(container=False)
                    self.temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True,
                                                 label="Temperature",).style(container=False)
                    self.n_choices_slider = gr.Slider(minimum=1, maximum=10, value=default_params['n_choices'], step=1,
                                                      interactive=True, label="n choices",
                                                      ).style(container=False)
                    self.stop_sequence_txt = gr.Textbox(show_label=True, placeholder=i18n("停止符，用英文逗号隔开..."),
                                                        label="stop", value=default_params['stop'], lines=1,
                                                        ).style(container=False)
                    self.presence_penalty_slider = gr.Slider(minimum=-2.0, mmaximum=default_params['presence_penalty'], value=0.0,
                                                             step=0.01, interactive=True, label="presence penalty",
                                                             ).style(container=False)
                    self.frequency_penalty_slider = gr.Slider(minimum=-2.0, maximum=2, value=default_params['frequency_penalty'], step=0.01,
                                                              interactive=True, label="frequency penalty",
                                                              ).style(container=False)

                    self.user_identifier_txt = gr.Textbox(show_label=True, placeholder=i18n("用于定位滥用行为"),
                                                          label=i18n("用户名"), value=default_params['user'], lines=1,
                                                          ).style(container=False)
                    func_box.md_division_line()
                    self.max_context_length_slider = gr.Slider(minimum=1, maximum=32768, value=default_params['max_context'],
                                                               step=1, interactive=True, label="max context",
                                                               ).style(container=False)
                    self.max_generation_slider = gr.Slider(minimum=1, maximum=32768, value=default_params['max_generation'],
                                                           step=1, interactive=True, label="max generations",
                                                           ).style(container=False)
                    self.logit_bias_txt = gr.Textbox(show_label=True, placeholder=f"word:likelihood",
                                                     label="logit bias", value=default_params['logit_bias'], lines=1,
                                                     ).style(container=False)
                    self.max_length_sl = gr.Slider(minimum=256, maximum=4096, value=4096, step=1, interactive=True,
                                                   label="MaxLength", visible=False
                                                   ).style(container=False)
                    self.default_worker_num = gr.Slider(minimum=1, maximum=30, value=worker_num, step=1, interactive=True,
                                                   label="多线程最大并行数"
                                                        ).style(container=False)
                func_box.md_division_line()
                with gr.Accordion(label='Langchain调优参数'):
                    self.vector_search_score = gr.Slider(minimum=0, maximum=1100, value=500, step=1, interactive=True,
                                           label="SCORE-THRESHOLD", ).style(container=False)
                    self.vector_search_top_k = gr.Slider(minimum=1, maximum=10, value=4, step=1, interactive=True,
                                                 label="TOP-K",).style(container=False)
                    self.vector_chunk_size = gr.Slider(minimum=100, maximum=1000, value=521, step=1, interactive=True,
                                           label="CHUNK-SIZE", ).style(container=False)
                func_box.md_division_line()
                with gr.Accordion(label='工具调试参数', open=True):
                    self.pro_tf_slider = gr.Slider(minimum=0.01, maximum=1.0, value=0.70, step=0.01, interactive=True,
                                                   label="搜索匹配系数").style(container=False)
                    self.ocr_identifying_trust = gr.Slider(minimum=0.01, maximum=1.0, value=0.60, step=0.01, interactive=True,
                                                   label="OCR 识别信任指数").style(container=False)
            # temp = gr.Markdown(self.description)

    def draw_tools_area(self):
        with gr.Column(elem_id="toolbox-area", scale=1):
            with gr.Box(elem_id="chuanhu-toolbox"):
                self._draw_tools_head()
                with gr.Tabs(elem_id=""):
                    self._draw_function_chat()
                    self._draw_plugin_chat()
                    self._draw_langchain_base()
                    self._draw_setting_chat()