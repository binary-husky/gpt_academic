#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :
import gradio as gr
from comm_tools import webui_local, func_box, toolbox

i18n = webui_local.I18nAuto()
get_html = func_box.get_html


def popup_title(txt):
    with gr.Row():
        gr.Markdown(txt)
        gr.HTML(get_html("close_btn.html").format(
            obj="box"), elem_classes="close-btn")


class Settings:

    def __init__(self):
        pass

    def _draw_setting_senior(self):
        with gr.Tab(label=i18n("高级")):
            self.usageTxt = gr.Markdown(i18n(
                "**发送消息** 或 **提交key** 以显示额度"), elem_id="usage-display",
                elem_classes="insert-block", visible=False)
            self.keyTxt = gr.Textbox(
                show_label=True, placeholder=f"Your API-key...",
                # value=hide_middle_chars(user_api_key.value),
                type="password",  # visible=not HIDE_MY_KEY,
                label="API-Key",
            ).style(container=False)
            self.models_box = gr.CheckboxGroup(choices=['input加密', '预加载知识库'], value=['input加密'],
                                               label="对话模式").style(container=False)
            self.secret_css, self.secret_font = gr.Textbox(visible=False), gr.Textbox(visible=False)
            AVAIL_THEMES, latex_option = toolbox.get_conf('AVAIL_THEMES', 'latex_option')
            self.theme_dropdown = gr.Dropdown(AVAIL_THEMES, value=AVAIL_THEMES[0], label=i18n("更换UI主题"),
                                              interactive=True, allow_custom_value=True,
                                              info='更多主题, 请查阅Gradio主题商店: '
                                                   'https://huggingface.co/spaces/gradio/theme-gallery',
                                              ).style(container=False)
            self.latex_option = gr.Dropdown(latex_option, value=latex_option[0], label=i18n("更换Latex输出格式"),
                                            interactive=True).style(container=False)
            gr.HTML(get_html("appearance_switcher.html").format(
                label=i18n("切换亮暗色主题")), elem_classes="insert-block", visible=False)
            self.single_turn_checkbox = gr.Checkbox(label=i18n(
                "无记忆对话"), value=False, elem_classes="switch-checkbox",
                elem_id="gr-single-session-cb", visible=False)

    def _darw_private_operation(self):
        with gr.TabItem('个人中心', id='private', elem_id='about-tab',):
            with gr.Row():
                gr.Markdown('####  粉身碎骨浑不怕 要留清白在人间\n\n'
                            '这里是删除个人文件信息的地方，`注意！！这里的所有操作不可逆，请谨慎操作！！！！`')
            with gr.Row():
                gr.Markdown('待完善')

    def _draw_setting_info(self):
        APPNAME, = toolbox.get_conf('APPNAME')
        with gr.Tab(label=i18n("关于"), elem_id="about-tab"):
            gr.Markdown("# " + i18n(APPNAME))
            gr.HTML(get_html("footer.html").format(versions=''), elem_id="footer")
            gr.Markdown('', elem_id="description")


    def draw_popup_settings(self):
        with gr.Box(elem_id="chuanhu-setting"):
            popup_title("## " + i18n("设置"))
            with gr.Tabs(elem_id="chuanhu-setting-tabs"):
                self._draw_setting_senior()
                self._darw_private_operation()
                self._draw_setting_info()


class Training:

    def __init__(self):
        pass

    def _draw_title(self):
        with gr.Tab(label="OpenAI " + i18n("微调")):
            self.openai_train_status = gr.Markdown(label=i18n("训练状态"), value=i18n(
                "查看[使用介绍](https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/使用教程#微调-gpt-35)"))

    def _draw_prepare_dataset(self):
        with gr.Tab(label=i18n("准备数据集")):
            self.dataset_preview_json = gr.JSON(
                label=i18n("数据集预览"), readonly=True)
            self.dataset_selection = gr.Files(label=i18n("选择数据集"), file_types=[
                ".xlsx", ".jsonl"], file_count="single")
            self.upload_to_openai_btn = gr.Button(
                i18n("上传到OpenAI"), variant="primary", interactive=False)

    def _draw_pre_training(self):
        with gr.Tab(label=i18n("训练")):
            self.openai_ft_file_id = gr.Textbox(label=i18n(
                "文件ID"), value="", lines=1, placeholder=i18n("上传到 OpenAI 后自动填充"))
            self.openai_ft_suffix = gr.Textbox(label=i18n(
                "模型名称后缀"), value="", lines=1, placeholder=i18n("可选，用于区分不同的模型"))
            self.openai_train_epoch_slider = gr.Slider(label=i18n(
                "训练轮数（Epochs）"), minimum=1, maximum=100, value=3, step=1, interactive=True)
            self.openai_start_train_btn = gr.Button(
                i18n("开始训练"), variant="primary", interactive=False)

    def _draw_training_status(self):
        with gr.Tab(label=i18n("状态")):
            self.openai_status_refresh_btn = gr.Button(i18n("刷新状态"))
            self.openai_cancel_all_jobs_btn = gr.Button(
                i18n("取消所有任务"))
            self.add_to_models_btn = gr.Button(
                i18n("添加训练好的模型到模型列表"), interactive=False)

    def draw_popup_training(self):
        with gr.Box(elem_id="chuanhu-training"):
            popup_title("## " + i18n("训练"))
            with gr.Tabs(elem_id="chuanhu-training-tabs"):
                self._draw_title()
                self._draw_prepare_dataset()
                self._draw_pre_training()
                self._draw_training_status()


class AdvancedSearch:

    def __init__(self):
        pass

    def draw_popup_search(self):
        with gr.Box(elem_id="spike-search"):
            popup_title("## " + i18n("高级搜索"))
            with gr.Box():
                with gr.Row():
                    with gr.Row(elem_classes='input-search'):
                        self.history_search_txt = gr.Textbox(show_label=False, elem_classes='search_txt',
                                                         placeholder="输入你想要搜索的对话记录或提示词").style(container=False)
                        self.pro_entry_btn = gr.Button("搜索", variant="primary", elem_classes='short_btn').style(
                            full_width=False, size="sm")
                with gr.Box(elem_classes='search-box-pop'):
                    with gr.Row(elem_classes='search-example'):
                        self.pro_history_state = gr.State({'samples': None})
                        self.pro_history_list = gr.Dataset(components=[gr.HTML(visible=False)], samples_per_page=10,
                                                              visible=False, label='搜索结果',
                                                              samples=[[". . ."] for i in range(20)], type='index')

class Config:

    def __init__(self):
        pass

    def draw_popup_config(self):
        with gr.Box(elem_id="web-config", visible=False):
            gr.HTML(get_html('web_config.html').format(
                enableCheckUpdate_config='',
                hideHistoryWhenNotLoggedIn_config='',
                forView_i18n=i18n("仅供查看"),
                deleteConfirm_i18n_pref=i18n("你真的要删除 "),
                deleteConfirm_i18n_suff=i18n(" 吗？"),
                usingLatest_i18n=i18n("您使用的就是最新版！"),
                updatingMsg_i18n=i18n("正在尝试更新..."),
                updateSuccess_i18n=i18n("更新成功，请重启本程序"),
                updateFailure_i18n=i18n(
                    '更新失败，请尝试<a href="https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/使用教程#手动更新" target="_blank">手动更新</a>'),
                regenerate_i18n=i18n("重新生成"),
                deleteRound_i18n=i18n("删除这轮问答"),
                renameChat_i18n=i18n("重命名该对话"),
                validFileName_i18n=i18n("请输入有效的文件名，不要包含以下特殊字符："),
            ))


class Prompt:

    def __init__(self):
        pass

    def _draw_tabs_prompt(self):
        preset_prompt, devs_document = toolbox.get_conf('preset_prompt', 'devs_document')
        with gr.TabItem('提示词', id='prompt'):
            with gr.Row():
                with gr.Column(elem_classes='column_left') as self.prompt_upload_column:
                    jump_link = f'<a href="{devs_document}" target="_blank">Developer Documentation</a>'
                    self.pro_devs_link = gr.HTML(jump_link)
                    self.pro_upload_btn = gr.File(file_count='single', file_types=['.yaml', '.json'],
                                                  label=f'上传你的提示词文件, 编写格式请遵循上述开发者文档', )
                with gr.Column(elem_classes='column_right') as self.prompt_edit_column:
                    Tips = "用 BORF 分析法设计GPT 提示词:\n" \
                           "1、阐述背景 B(Background): 说明背景，为chatGPT提供充足的信息\n" \
                           "2、定义目标 O(Objectives):“我们希望实现什么”\n" \
                           "3、定义关键结果 R(key Result):“我要什么具体效果”\n" \
                           "4、试验并调整，改进 E(Evolve):三种改进方法自由组合\n" \
                           "\t 改进输入：从答案的不足之处着手改进背景B,目标O与关键结果R\n" \
                           "\t 改进答案：在后续对话中指正chatGPT答案缺点\n" \
                           "\t 重新生成：尝试在`提示词`不变的情况下多次生成结果，优中选优\n" \
                           "\t 熟练使用占位符{{{v}}}:  当`提示词`存在占位符，则优先将{{{v}}}替换为预期文本"
                    self.pro_edit_txt = gr.Textbox(show_label=False, lines=12,
                                                   elem_classes='no_padding_input',
                                                   placeholder=Tips).style()
                    with gr.Row():
                        self.pro_name_txt = gr.Textbox(show_label=False, placeholder='提示词名称').style(container=False)
                    with gr.Row():
                        self.pro_private_check = gr.Dropdown(choices=[], value=preset_prompt['value'],
                                                             label='保存提示词分类', elem_classes='normal_select'
                                                             ).style(container=False)
                        self.pro_class_name = gr.Textbox(show_label=False,
                                                         placeholder='*必填，保存Prompt同时创建分类',
                                                         visible=False).style(container=False)
                    with gr.Row():
                        self.pro_del_btn = gr.Button("删除提示词", ).style(size='sm', full_width=True)
                        self.pro_new_btn = gr.Button("保存提示词", variant="primary").style(size='sm', full_width=True)

    def _draw_tabs_masks(self):
        with gr.TabItem('Masks 🎭', id='masks'):
            def_sys = i18n('你是一个xxx角色，你会xxx技能，你将按照xxx要求，回答我的问题')
            self.masks_dataset = gr.Dataframe(value=[['system', def_sys]], datatype='markdown',
                                              headers=['role', 'content'], col_count=(2, 'fixed'),
                                              interactive=True, show_label=False, row_count=(1, "dynamic"),
                                              wrap=True, type='array', elem_id='mask_tabs')
            self.masks_delete_btm = gr.Button('Del New Row', size='sm', elem_id='mk_del')
            self.masks_clear_btn = gr.Button(value='Clear All', size='sm', elem_id='mk_clear')

    def draw_popup_prompt(self):
        with gr.Box(elem_id="spike-prompt"):
            popup_title("## " + i18n("提示词 对话面具"))
            with gr.Tabs(elem_id="prompt-tabs"):
                self._draw_tabs_prompt()
                self._draw_tabs_masks()


class FakeComponents:

    def __init__(self):
        pass

    def draw_popup_fakec(self):
        with gr.Box(elem_id="fake-gradio-components", visible=False):
            self.updateChuanhuBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="update-chuanhu-btn")
            self.changeSingleSessionBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="change-single-session-btn")
            self.changeOnlineSearchBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="change-online-search-btn")
            self.historySelectBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="history-select-btn")  # Not used



