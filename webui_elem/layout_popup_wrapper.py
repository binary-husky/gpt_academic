# encoding: utf-8
# @Time   : 2023/9/16
# @Author : Spike
# @Descr   :
import gradio as gr
import pandas as pd

from common import func_box, toolbox
from common.configs import LOADER_ENHANCE, ZH_TITLE_ENHANCE
from webui_elem import webui_local

i18n = webui_local.I18nAuto()
get_html = func_box.get_html


def popup_title(txt):
    with gr.Row():
        gr.Markdown(txt)
        gr.HTML(get_html("close_btn.html").format(obj="box"), elem_classes="close-btn")


class Settings:

    def __init__(self):
        pass

    def _draw_setting_senior(self):
        with gr.Tab(label=i18n("高级")):
            worker_num = toolbox.get_conf('DEFAULT_WORKER_NUM')
            self.default_worker_num = gr.Slider(minimum=1, maximum=30, value=worker_num, step=1,
                                                show_label=True, interactive=True, label="插件多线程最大并行",
                                                container=False)
            self.pro_tf_slider = gr.Slider(minimum=1, maximum=200, value=15, step=1, interactive=True,
                                           label="搜索展示详细字符", show_label=True, container=False)
            self.ocr_identifying_trust = gr.Slider(minimum=0.01, maximum=1.0, value=0.60, step=0.01,
                                                   interactive=True, show_label=True, container=False,
                                                   label="Paddleocr OCR 识别信任指数")
            self.secret_css, self.secret_font = gr.Textbox(visible=False), gr.Textbox(visible=False)
            AVAIL_THEMES, latex_option = toolbox.get_conf('AVAIL_THEMES', 'latex_option')
            self.theme_dropdown = gr.Dropdown(AVAIL_THEMES, value=AVAIL_THEMES[0], label=i18n("更换UI主题"),
                                              interactive=True, allow_custom_value=True, show_label=True,
                                              info='更多主题, 请查阅Gradio主题商店: '
                                                   'https://huggingface.co/spaces/gradio/theme-gallery',
                                              container=False)
            self.latex_option = gr.Dropdown(latex_option, value=latex_option[0], label=i18n("更换Latex输出格式"),
                                            interactive=True, container=False, show_label=True, )
            gr.HTML(get_html("appearance_switcher.html").format(
                label=i18n("切换亮暗色主题")), elem_classes="insert-block", visible=False)
            self.single_turn_checkbox = gr.Checkbox(label=i18n("无记忆对话"),
                                                    value=False, elem_classes="switch-checkbox",
                                                    elem_id="gr-single-session-cb", visible=False)

    def _darw_private_operation(self):
        with gr.TabItem('个人中心', id='private'):
            with gr.Row(elem_classes='tab-center'):
                gr.Markdown('#### 粉身碎骨浑不怕 要留清白在人间\n\n'
                            + func_box.html_tag_color('我不会保存你的个人信息，清除浏览器缓存后这里的信息就会被丢弃',
                                                      color='rgb(227 179 51)'))
            self.usageTxt = gr.Markdown(i18n(
                "**发送消息** 或 **提交key** 以显示额度"), elem_id="usage-display",
                elem_classes="insert-block", visible=False)
            self.openai_keys = gr.Textbox(
                show_label=True, placeholder=f"Your OpenAi-API-key...",
                # value=hide_middle_chars(user_api_key.value),
                type="password",  # visible=not HIDE_MY_KEY,
                label="API-Key", container=False, elem_id='api-keys-input')
            self.wps_cookie = gr.Textbox(label='WPS Cookies', type='password', show_label=True,
                                         placeholder=f"Your WPS cookies dict...", container=False,
                                         elem_id='wps-cookies-input')
            self.qq_cookie = gr.Textbox(label='QQ Cookies', type='password', show_label=True,
                                        placeholder=f"Your QQ cookies dict...", container=False,
                                        elem_id='qq-cookies-input')
            self.feishu_cookie = gr.Textbox(label='Feishu Header', type='password', show_label=True,
                                            placeholder=f"Your Feishu header dict...", container=False,
                                            elem_id='feishu-cookies-input')
            self.feishu_project_use_key = gr.Textbox(label='Feishu Project user-key', type='password', show_label=True,
                                                     placeholder=f"Your Project user-key.", container=False,
                                                     elem_id='project-user-key-input')
            self.feishu_project_cookie = gr.Textbox(label='Feishu Project Header', type='password', show_label=True,
                                                    placeholder=f"Your Project header", container=False,
                                                    elem_id='project-cookies-input')
            with gr.Row():
                self.info_perish_btn = gr.Button('清除我来过的痕迹', variant='stop', elem_classes='danger_btn')
                self.exit_login_btn = gr.LogoutButton(icon='', link='/logout')

    def _draw_setting_info(self):
        APPNAME = toolbox.get_conf('APPNAME')
        with gr.Tab(label=i18n("关于"), elem_id="tab-center"):
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


class AdvancedSearch:

    def __init__(self):
        pass

    def draw_popup_search(self):
        with gr.Box(elem_id="spike-search"):
            popup_title("## " + i18n("高级搜索"))
            with gr.Box():
                with gr.Row():
                    self.history_search_txt = gr.Textbox(show_label=False, elem_classes=['search_txt'],
                                                         placeholder="输入你想要搜索的对话记录", container=False)
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
                deleteConfirm_i18n_pref=i18n("你真的要"),
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
        self.devs_document = toolbox.get_conf('devs_document')
        with gr.TabItem('提示词', id='prompt'):
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
                                           placeholder=Tips)
            with gr.Row():
                with gr.Column(elem_classes='column_left'):
                    with gr.Accordion('Prompt Upload', open=False):
                        self.pro_upload_btn = gr.File(file_count='single', file_types=['.yaml', '.json'],
                                                      label=f'上传你的提示词文件, 编写格式请遵循上述开发者文档', )
                    self.prompt_status = gr.Markdown(value='')
                with gr.Column(elem_classes='column_right'):
                    with gr.Row():
                        self.prompt_cls_select = gr.Dropdown(choices=[], value='',
                                                             label='提示词分类',
                                                             elem_classes=['normal_select', 'remove-sr-hide'],
                                                             allow_custom_value=True, interactive=True, container=False)
                        self.pro_name_txt = gr.Textbox(show_label=False, placeholder='提示词名称', container=False)
                    with gr.Row():
                        self.pro_del_btn = gr.Button("删除提示词", size='sm')
                        self.pro_new_btn = gr.Button("保存提示词", variant="primary", size='sm')

    def _draw_tabs_masks(self):
        with gr.TabItem('自定义对话 🎭', id='masks'):
            def_sys = i18n('你是一个xxx角色，你会xxx技能，你将按照xxx要求，回答我的问题')
            self.masks_dataset = gr.Dataframe(value=[['system', def_sys]], datatype='str',
                                              headers=['role', 'content'], col_count=(2, 'fixed'),
                                              interactive=True, show_label=False, row_count=(1, "dynamic"),
                                              wrap=True, type='array', elem_id='mask_tabs')
            self.masks_delete_btn = gr.Button('Del New row', size='sm', elem_id='mk_del')
            self.masks_clear_btn = gr.Button(value='Clear All', size='sm', elem_id='mk_clear')
            with gr.Row():
                with gr.Column(elem_classes='column_left'):
                    gr.Markdown('> user or assistant 为空时，不会加入对话记录')
                    with gr.Accordion('Chatbot Preview', open=False):
                        self.mask_preview_chat = gr.Chatbot(label='', show_label=False)
                    self.mask_status = gr.Markdown(value='')
                with gr.Column(elem_classes='column_right'):
                    with gr.Row():
                        self.mask_cls_select = gr.Dropdown(choices=[], value='',
                                                           label='Masks分类',
                                                           elem_classes=['normal_select', 'remove-sr-hide'],
                                                           allow_custom_value=True, interactive=True, container=False
                                                           )
                        self.masks_name_txt = gr.Textbox(show_label=False, placeholder='Mask名称', container=False)
                    with gr.Row():
                        self.masks_del_btn = gr.Button("删除Mask", size='sm')
                        self.masks_new_btn = gr.Button("保存Mask", variant="primary", size='sm')

    def __draw_new_knowledge_base(self):
        with gr.Column(elem_classes='elem-box-solid') as self.new_knowledge_base:
            with gr.Row():
                self.new_kb_name = gr.Textbox(label='知识库名称', placeholder='知识库命名，尽量不要使用中文',
                                              show_label=True, container=False)
            with gr.Row():
                self.new_kb_introduce = gr.TextArea(label='知识库简介', placeholder='知识库简介，方便Agent调用',
                                                    show_label=True, container=False,
                                                    lines=3, max_lines=4)
            with gr.Row():
                from common.configs import kbs_config, EMBEDDING_MODEL
                from common.utils import list_local_embed_models, list_embed_paths
                kbs_config_list = list(kbs_config.keys())
                with gr.Column(elem_classes='column_left'):
                    self.new_kb_vector_types = gr.Dropdown(choices=kbs_config, value=kbs_config_list[0],
                                                           interactive=True,
                                                           label="向量库类型", allow_custom_value=True,
                                                           container=False, show_label=True,
                                                           elem_classes='normal_select')
                embed_list = list_local_embed_models()
                with gr.Column(elem_classes='column_right'):
                    self.new_kb_embedding_model = gr.Dropdown(choices=embed_list, value=embed_list[0],
                                                              label="本地Embedding模型", allow_custom_value=True,
                                                              container=False, show_label=True,
                                                              elem_classes='normal_select', interactive=True)
            with gr.Row():
                with gr.Column(scale=20, elem_classes='column-unset-min-width'):
                    self.new_kb_private_checkbox = gr.Checkbox(label='私有知识库',
                                                               value=False, show_label=True, )
                with gr.Column(scale=90):
                    self.new_kb_confirm_btn = gr.Button(value='新建', size='lg')

            with gr.Column(elem_classes='elem-box-solid') as self.embedding_download_clo:
                with gr.Row():
                    self.select_embedding_model = gr.Dropdown(label='Embedding模型名称',
                                                              info='允许手动输入模型名称',
                                                              choices=list_embed_paths(),
                                                              interactive=True, allow_custom_value=True)
                with gr.Row():
                    self.download_embedding_model = gr.Button(value='下载/更新所选模型', size='lg')
                with gr.Row():
                    self.embedding_download_status = gr.Markdown()

    def __draw_edit_knowledge_base(self):
        spl = toolbox.get_conf('spl')
        from common.configs import TEXT_SPLITTER_NAME, text_splitter_dict
        with gr.Column(visible=False) as self.edit_knowledge_base:
            with gr.Row():
                self.edit_kb_upload = gr.Files(label='上传知识文件', elem_id='reader-file',
                                               show_label=True, container=False)
            with gr.Row():
                self.edit_kb_cloud = gr.Textbox(show_label=False, placeholder='云文件链接,多个链接使用换行间隔',
                                                elem_classes='no_padding_input')
            with gr.Row():
                self.edit_kb_introduce = gr.Textbox(label='知识库简介', lines=3, max_lines=4,
                                                    placeholder='这个人很懒，什么都没有留下', container=False,
                                                    show_label=True)
            with gr.Column(elem_classes='elem-box-solid'):
                with gr.Row():
                    self.edit_kb_max_paragraph = gr.Number(label='单段文本最大长度', value=250, show_label=True,
                                                           interactive=True)
                    self.edit_kb_similarity_paragraph = gr.Number(label='相邻文本重合长度', value=50,
                                                                  show_label=True, interactive=True)
                    self.edit_kb_tokenizer_select = gr.Dropdown(choices=text_splitter_dict.keys(), interactive=True,
                                                                value=TEXT_SPLITTER_NAME,
                                                                label="内置分词器选择", allow_custom_value=True,
                                                                show_label=True)
                    self.edit_kb_loader_select = gr.Dropdown(choices=LOADER_ENHANCE, value=ZH_TITLE_ENHANCE,
                                                             interactive=True,
                                                             label="Loader增强模式", allow_custom_value=True,
                                                             show_label=True)
                self.edit_kb_confirm_btn = gr.Button(value='添加文件到知识库', size='lg')

            func_box.md_division_line()
            with gr.Row():
                self.edit_kb_file_desc = gr.Markdown('### 选择文件后可对向量库及片段内容进行调整')
            with gr.Row():
                with gr.Column(scale=1, elem_classes=['kb-select-list', 'elem-box-solid']):
                    self.edit_kb_file_list = gr.Radio(label='知识库内文件', show_label=True, container=False,
                                                      choices=[], value='',
                                                      elem_id='knowledge-base-select')
                    with gr.Row():
                        self.edit_kb_the_job = gr.Button(value='关于本项目', size='sm', visible=False,
                                                         variant='primary')
                        self.edit_knowledge_base_del = gr.Button(value='删除知识库', size='sm',
                                                                 elem_classes=['danger_btn', 'kb-file-btn'])
                with gr.Column(scale=4):
                    with gr.Column(elem_classes='elem-box-solid'):
                        with gr.Row():
                            self.edit_kb_file_details = gr.Dataframe(label='文件详情', value=[], type='pandas',
                                                                     interactive=False)
                        with gr.Row():
                            self.edit_kb_info_reload_vector = gr.Button(value='重载向量数据', size='sm',
                                                                        variant='primary')
                            self.edit_kb_info_vector_del = gr.Button(value='删除向量数据', size='sm')
                            self.edit_kb_info_docs_del = gr.Button(value='删除数据源', size='sm')

                    with gr.Column(elem_classes='elem-box-solid'):
                        with gr.Row():
                            self.edit_kb_file_fragment = gr.Dataframe(label='文档片段编辑', value=[],
                                                                      interactive=True, type='pandas',
                                                                      overflow_row_behaviour='paginate',
                                                                      elem_classes='kb-info-fragment',
                                                                      col_count=(4, 'fixed'),
                                                                      row_count=(1, 'dynamic'),
                                                                      datatype=['str', 'number', 'str', 'bool'])
                        with gr.Row():
                            self.edit_kb_info_fragment_save = gr.Button(value='保存更改', size='sm',
                                                                        variant='primary')
                            self.edit_kb_file_fragment_add = gr.Button(value='新增一行', size='sm')

    def _draw_knowledge_base(self):
        with (gr.TabItem('知识库管理', id='langchain_tab', elem_id='langchain_tab')):
            self.knowledge_base_state_dict = gr.State({})
            with gr.Column():
                self.knowledge_base_select = gr.Dropdown(choices=['312', '33213'], value="新建知识库", interactive=True,
                                                         label="选择现有知识库或新建知识库", allow_custom_value=True,
                                                         container=False, show_label=True)

                self.__draw_new_knowledge_base()
                self.__draw_edit_knowledge_base()

    def _draw_popup_files_processor(self):
        with gr.TabItem(i18n('Read everything.'), id='files', elem_id='reader'):
            with gr.Row():
                with gr.Column(elem_classes='column_left'):
                    self.reader_upload = gr.File(label='上传文件', elem_id='reader-file',
                                                 show_label=False)
                with gr.Column(elem_classes='column_left'):
                    self.reader_choice = gr.Dropdown(label='Read Mode', choices=['Markdown', 'Developing...'],
                                                     value='Markdown', allow_custom_value=False, interactive=True, )
                with gr.Column(elem_classes='column_left'):
                    missing_description = """
                    ## File Preview\n\n
                    上传文件自动解析为GPT可接收文本,并自动计算对话预计消耗`Token`
                    """
                    self.reader_show = gr.Markdown(missing_description)
                with gr.Column(elem_classes='column_right'):
                    self.reader_copy = gr.Textbox(label='File Edit', lines=15, max_lines=30, show_copy_button=True)

    def _draw_popup_training(self):
        with gr.TabItem('OpenAi' + i18n('预训练'), id='training_tab', elem_id='training_tab'):
            self.openai_train_status = gr.Markdown(label=i18n("训练状态"), value=i18n(
                "查看[使用介绍](https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/使用教程#微调-gpt-35)"))
            with gr.Row():
                with gr.Column(elem_classes='column_left'):
                    self.dataset_selection = gr.Files(label=i18n("选择数据集"), file_types=[
                        ".xlsx", ".jsonl"], file_count="single")
                    self.dataset_preview_json = gr.JSON(label=i18n("数据集预览"))
                    self.upload_to_openai_btn = gr.Button(
                        i18n("上传到OpenAI"), variant="primary", interactive=False)
                with gr.Column(elem_classes='column_right'):
                    self.openai_ft_file_id = gr.Textbox(label=i18n(
                        "文件ID"), value="", lines=1, placeholder=i18n("上传到 OpenAI 后自动填充"))
                    self.openai_ft_suffix = gr.Textbox(label=i18n(
                        "模型名称后缀"), value="", lines=1, placeholder=i18n("可选，用于区分不同的模型"))
                    self.openai_train_epoch_slider = gr.Slider(label=i18n(
                        "训练轮数（Epochs）"), minimum=1, maximum=100, value=3, step=1, interactive=True)
                    self.openai_start_train_btn = gr.Button(
                        i18n("开始训练"), variant="primary", interactive=False)
                    self.openai_status_refresh_btn = gr.Button(i18n("刷新状态"))
                    self.openai_cancel_all_jobs_btn = gr.Button(
                        i18n("取消所有任务"))
                    self.add_to_models_btn = gr.Button(
                        i18n("添加训练好的模型到模型列表"), interactive=False)

    def draw_popup_prompt(self):
        with gr.Box(elem_id="spike-prompt"):
            popup_title("### " + i18n(f"百宝袋"))
            with gr.Tabs(elem_id="treasure-bag") as self.treasure_bag_tab:
                self._draw_tabs_prompt()
                self._draw_tabs_masks()
                self._draw_knowledge_base()
                self._draw_popup_files_processor()
                self._draw_popup_training()


class GptsStore:

    def _tag_category_tab(self, tab_title, key, gpts_samples, if_search):
        with gr.TabItem(tab_title, id=key) as tab_select:
            if if_search:
                self.gpts_search_input = gr.Textbox('', placeholder='GPTs名称、介绍', show_label=False)
            else:
                self.gpts_search_input = gr.State()
            self.gpts_tags_mapping[key] = {
                'data_set': gr.Dataset(components=[gr.HTML(visible=False)], visible=True,
                                       elem_id='gpts-data-set', samples_per_page=10,
                                       samples=gpts_samples, type='index', container=False),
                "tab": tab_select,
                "search": self.gpts_search_input}
            self.gpts_samples_mapping[key] = gr.State(gpts_samples)

    def draw_popup_gpts(self):
        from common.api_server.gpts_store import get_gpts, gpts_groups_samples
        gpts = get_gpts()
        gpts_samples = gpts_groups_samples(gpts['gpts'])
        with gr.Box(elem_id="gpts-store-select"):
            popup_title("### " + i18n(f"GPTs Store"))
            self.gpts_tags_mapping = {}
            self.gpts_samples_mapping = {}
            with gr.Tabs(elem_id='store-tabs') as self.gpts_store_tabs:
                self._tag_category_tab('🔥 热门应用', '热门应用', gpts_samples, False)
                self._tag_category_tab('🔍 关键词搜索', '关键词搜索', [], True)
                gpts_tags = toolbox.get_conf('GPTS_DEFAULT_CLASSIFICATION')
                gpts_tags = gpts_tags if gpts_tags else gpts['tag']
                for tag in set(gpts_tags):
                    self._tag_category_tab(tag, tag, [], False)


class FakeComponents:

    def __init__(self):
        pass

    def draw_popup_fake(self):
        with gr.Box(elem_id="fake-gradio-components", visible=False):
            self.updateChuanhuBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="update-chuanhu-btn")
            self.changeSingleSessionBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="change-single-session-btn")
            self.changeOnlineSearchBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="change-online-search-btn")
            self.historySelectBtn = gr.Button(
                visible=False, elem_classes="invisible-btn", elem_id="history-select-btn")  # Not used
