# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :

import gradio as gr
from common import func_box, toolbox
from webui_elem import webui_local
from common.crazy_functional import crazy_fns_role, crazy_classification, crazy_fns

default_plugin = toolbox.get_conf('DEFAULT_FN_GROUPS')
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
        preset_prompt = toolbox.get_conf('preset_prompt')
        with gr.TabItem('基础', id='func_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Row():
                self.preset_prompt = toolbox.get_conf('preset_prompt')
                self.pro_private_check = gr.Dropdown(choices=[], value=self.preset_prompt['value'],
                                                     label='提示词分类', elem_classes='normal_select',
                                                     allow_custom_value=True)
            with gr.Row():
                self.prompt_search_txt = gr.Textbox(placeholder='搜索提示词', show_label=False,
                                                    elem_classes='pm_search', )
                self.multiplexing_edit_check = gr.Checkbox(value=True, show_label=True, elem_id='pm_check',
                                                           container=False, elem_classes='switch-checkbox',
                                                           interactive=True, label='')
            self.pro_func_prompt = gr.Dataset(components=[gr.HTML()], label="Prompt - 复用", visible=False,
                                              samples=[['...', ""] for i in range(20)], type='index',
                                              elem_id='prompt_list', samples_per_page=10, )
            self.pro_fp_state = gr.State({'samples': None})
            func_box.md_division_line()
            self.system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=f"System Prompt",
                                            label="System prompt", value=self.initial_prompt)

    def _draw_plugin_chat(self):
        with gr.TabItem('插件', id='plug_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Accordion("上传本地文件可供高亮函数插件调用", open=False, visible=False) as self.area_file_up:
                self.file_upload = gr.Files(label="任何文件, 但推荐上传压缩文件(zip, tar)",
                                            file_count="multiple")
            self.plugin_dropdown = gr.Dropdown(choices=crazy_classification, label='选择插件分类', value=default_plugin,
                                               multiselect=True, interactive=True, elem_classes='normal_mut_select',
                                               container=False, show_label=True
                                               )
            with gr.Accordion("函数插件区/高亮插件需要输入框支持", open=True) as self.area_crazy_fn:
                with gr.Row():
                    for role in crazy_fns_role:
                        for k in crazy_fns_role[role]:
                            if not crazy_fns_role[role][k].get("AsButton", True): continue
                            if role not in default_plugin:
                                variant = crazy_fns_role[role][k]["Color"] if "Color" in crazy_fns_role[role][
                                    k] else "secondary"
                                crazy_fns_role[role][k]['Button'] = gr.Button(k, variant=variant, visible=False,
                                                                              size="sm")
                            else:
                                variant = crazy_fns[k]["Color"] if "Color" in crazy_fns_role[role][k] else "secondary"
                                crazy_fns_role[role][k]['Button'] = gr.Button(k, variant=variant,
                                                                              visible=True, size="sm")
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
                self.dropdown_fn = gr.Dropdown(dropdown_fn_list, value=r"打开插件列表", interactive=True,
                                               show_label=False, label="", container=False)
                self.plugin_advanced_arg = gr.Textbox(show_label=True, label="高级参数输入区", visible=False,
                                                      elem_classes='no_padding_input',
                                                      placeholder="这里是特殊函数插件的高级参数输入区")
                self.switchy_bt = gr.Button(r"请先从插件列表中选择", variant="secondary", visible=False)

    def _draw_setting_chat(self):
        with gr.TabItem('调优', id='sett_tab', elem_id='chuanhu-toolbox-tabs'):
            with gr.Box():
                # gr.Markdown(func_box.get_html('what_news.html').replace('{%v}', 'LLMs调优参数'))
                with gr.Accordion('提交文本预处理'):
                    self.input_models = gr.CheckboxGroup(
                        choices=['input加密', '网络链接RAG', '提取知识库摘要', 'Vision-Img'],
                        value=['input加密', '网络链接RAG', 'Vision-Img'],
                        container=False)
                with gr.Accordion('提交图片预处理', open=False):
                    self.vision_models = gr.CheckboxGroup(choices=['OCR缓存', 'gpt4-v自动识图', 'gemini-v自动识图',
                                                                   'glm-v自动识图'],
                                                          value=['OCR缓存', 'gpt4-v自动识图',
                                                                 'gemini-v自动识图', 'glm-v自动识图'],
                                                          container=False)
                with gr.Accordion('提交飞书项目展示信息'):
                    self.project_models = gr.CheckboxGroup(choices=['关联缺陷', '关联用例', '关联任务'],
                                                           value=['关联任务'],
                                                           container=False)

                func_box.md_division_line()
                with gr.Accordion(label='知识库调优参数'):
                    self.vector_search_to_history = gr.CheckboxGroup(choices=['专注力转移'],
                                                                     value=['专注力转移'],
                                                                     container=False)
                    self.vector_search_score = gr.Slider(minimum=0, maximum=1100, value=500, step=1, interactive=True,
                                                         label="SCORE-THRESHOLD", show_label=True,
                                                         container=False)
                    self.vector_search_top_k = gr.Slider(minimum=1, maximum=10, value=4, step=1, interactive=True,
                                                         label="TOP-K", show_label=True, container=False)

                default_model = self.input_models.value + self.vision_models.value + self.project_models.value + self.vector_search_to_history.value
                self.models_box = gr.State(default_model)
                func_box.md_division_line()
                with gr.Accordion(label='LLMs调优参数', open=True):
                    default_params, response_format = toolbox.get_conf('LLM_DEFAULT_PARAMETER', 'RESPONSE_FORMAT')
                    self.top_p = gr.Slider(minimum=-0, maximum=1.0, value=default_params['top_p'], step=0.01,
                                           interactive=True, show_label=True,
                                           label="Top-p", container=False)
                    self.temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True,
                                                 label="Temperature", container=False, show_label=True)
                    self.n_choices_slider = gr.Slider(minimum=1, maximum=10, value=default_params['n_choices'],
                                                      step=1, show_label=True,
                                                      interactive=True, label="n choices", container=False,
                                                      )
                    self.stop_sequence_txt = gr.Textbox(show_label=True, placeholder=i18n("停止符，用英文逗号隔开..."),
                                                        label="stop", value=default_params['stop'], lines=1,
                                                        container=False)
                    self.presence_penalty_slider = gr.Slider(minimum=-2.0, maximum=5,
                                                             step=0.01, interactive=True, label="presence penalty",
                                                             container=False, show_label=True,
                                                             value=default_params['presence_penalty'],
                                                             )
                    self.frequency_penalty_slider = gr.Slider(minimum=-2.0, maximum=2,
                                                              value=default_params['frequency_penalty'], step=0.01,
                                                              interactive=True, label="frequency penalty",
                                                              container=False, show_label=True)

                    self.user_identifier_txt = gr.Textbox(show_label=True, placeholder=i18n("用于定位滥用行为"),
                                                          label=i18n("用户名"), value=default_params['user_identifier'],
                                                          lines=1, container=False)
                    self.response_format_select = gr.Dropdown(choices=response_format,
                                                              label=i18n('返回数据类型'),
                                                              value=default_params['response_format'],
                                                              interactive=True, container=False, show_label=True)
                    self.max_generation_slider = gr.Slider(minimum=1, maximum=1024*32, show_label=True,
                                                           value=default_params['max_generation'],
                                                           step=1, interactive=True, label="max generations",
                                                           container=False)
                    func_box.md_division_line()
                    self.max_context_length_slider = gr.Slider(minimum=1, maximum=32768, show_label=True,
                                                               value=default_params['max_context'],
                                                               step=1, interactive=True, label="max context",
                                                               container=False)
                    self.logit_bias_txt = gr.Textbox(show_label=True, placeholder=f"word:likelihood",
                                                     label="logit bias", value=default_params['logit_bias'], lines=1,
                                                     container=False)
                    self.max_length_sl = gr.Slider(minimum=256, maximum=4096, value=4096, step=1, interactive=True,
                                                   label="MaxLength", visible=False,
                                                   container=False)
            # temp = gr.Markdown(self.description)

    def draw_tools_area(self):
        with gr.Column(elem_id="toolbox-area", scale=1):
            with gr.Box(elem_id="chuanhu-toolbox"):
                self._draw_tools_head()
                self.status_display = gr.Markdown('', elem_id="status-display")
                with gr.Tabs(elem_id="toolbox-tabs"):
                    self._draw_function_chat()
                    self._draw_plugin_chat()
                    self._draw_setting_chat()
