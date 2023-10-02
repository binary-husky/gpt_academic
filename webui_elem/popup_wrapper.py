#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :
import gradio as gr
from comm_tools import webui_local, func_box, toolbox

i18n = webui_local.I18nAuto()
get_html = func_box.get_html


class Settings:

    def __init__(self):
        pass

    def _draw_setting_model(self):
        with gr.Tab(label=i18n("模型")):
            self.usageTxt = gr.Markdown(i18n(
                "**发送消息** 或 **提交key** 以显示额度"), elem_id="usage-display",
                elem_classes="insert-block", visible=False)
            self.keyTxt = gr.Textbox(
                show_label=True, placeholder=f"Your API-key...",
                # value=hide_middle_chars(user_api_key.value),
                type="password",  # visible=not HIDE_MY_KEY,
                label="API-Key",
            )
            self.models_box = gr.CheckboxGroup(choices=['input加密', '预加载知识库'], value=['input加密'],
                                               label="对话模式")

    def _draw_setting_senior(self):
        with gr.Tab(label=i18n("高级")):
            self.secret_css, self.secret_font = gr.Textbox(visible=False), gr.Textbox(visible=False)
            AVAIL_THEMES, latex_option = toolbox.get_conf('AVAIL_THEMES', 'latex_option')
            self.theme_dropdown = gr.Dropdown(AVAIL_THEMES, value=AVAIL_THEMES[0], label=i18n("更换UI主题"),
                                         interactive=True).style(container=False)
            self.latex_option = gr.Dropdown(AVAIL_THEMES, value=latex_option[0], label=i18n("更换Latex输出格式"),
                                       interactive=True).style(container=False)
            gr.HTML(get_html("appearance_switcher.html").format(
                label=i18n("切换亮暗色主题")), elem_classes="insert-block", visible=False)
            self.single_turn_checkbox = gr.Checkbox(label=i18n(
                "单轮对话"), value=False, elem_classes="switch-checkbox",
                elem_id="gr-single-session-cb", visible=False)
            # checkUpdateBtn = gr.Button(i18n("🔄 检查更新..."), visible=check_update)

    def _darw_private_operation(self):
        with gr.TabItem('个人中心', id='private', elem_id='bout-tab',):
            with gr.Row():
                gr.Markdown('####  粉身碎骨浑不怕 要留清白在人间\n\n'
                            '这里是删除个人文件信息的地方，`注意！！这里的所有操作不可逆，请谨慎操作！！！！`')
            with gr.Row():
                gr.Markdown('待完善')

    def _draw_setting_info(self):
        with gr.Tab(label=i18n("关于"), elem_id="about-tab"):
            gr.Markdown("# " + i18n("川虎Chat"))
            gr.HTML(get_html("footer.html").format(versions=''), elem_id="footer")
            gr.Markdown('', elem_id="description")


    def draw_popup_settings(self):
        with gr.Box(elem_id="chuanhu-setting"):
            with gr.Row():
                gr.Markdown("## " + i18n("设置"))
                gr.HTML(get_html("close_btn.html").format(
                    obj="box"), elem_classes="close-btn")
            with gr.Tabs(elem_id="chuanhu-setting-tabs"):
                self._draw_setting_model()
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
            with gr.Row():
                gr.Markdown("## " + i18n("训练"))
                gr.HTML(get_html("close_btn.html").format(
                    obj="box"), elem_classes="close-btn")
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
            with gr.Row():
                gr.Markdown("## " + i18n("高级搜索"))
                gr.HTML(get_html("close_btn.html").format(
                    obj="box"), elem_classes="close-btn")
            with gr.Box(elem_classes='search-box-pop'):
                with gr.Row(elem_classes='search-show'):
                    self.pro_results = gr.Chatbot(label='提示词和对话记录').style()
                with gr.Row(elem_classes='search-example'):
                    self.pro_prompt_state = gr.State({'samples': None})
                    self.pro_prompt_list = gr.Dataset(components=[gr.HTML(visible=False)], samples_per_page=10,
                                                          visible=False, label='搜索结果',
                                                          samples=[[". . ."] for i in range(20)], type='index')
                with gr.Row(elem_classes='input-search'):
                    self.pro_search_txt = gr.Textbox(show_label=False, elem_classes='search_txt',
                                                     placeholder="输入你想要搜索的对话记录或提示词").style(container=False)
                    self.pro_entry_btn = gr.Button("搜索", variant="primary", elem_classes='short_btn').style(
                        full_width=False, size="sm")
                    self.pro_reuse_btn = gr.Button("复用下文", variant="secondary", elem_classes='short_btn').style(
                        full_width=False, size="sm")
                    self.pro_clear_btn = gr.Button("重置搜索", variant="stop", elem_classes='short_btn').style(
                        full_width=False, size="sm")

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



