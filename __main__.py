import os
import gradio as gr
from chromadb.api import fastapi
import fastapi

from common.utils import list_local_embed_models
from request_llms.bridge_all import predict
from common.toolbox import find_free_port, on_file_uploaded, \
    get_conf, ArgsGeneralWrapper
from webui_elem.overwrites import postprocess_chat_messages, postprocess, reload_javascript
# 问询记录, python 版本建议3.9+（越新越好）
# 一些普通功能模块
from common.core_functional import get_core_functions
from common.logger_handler import init_path

functional = get_core_functions()

# 处理markdown文本格式的转变 暂时屏蔽这个高亮代码
# gr.Chatbot.postprocess = format_io
gr.Chatbot._postprocess_chat_messages = postprocess_chat_messages
gr.Chatbot.postprocess = postprocess

# 代理与自动更新
from common.check_proxy import check_proxy, auto_update
from common import func_box
from webui_elem import func_signals, webui_local

os.makedirs("gpt_log", exist_ok=True)
print("所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log, 请注意自我隐私保护哦！")

# 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, LAYOUT, API_KEY, AVAIL_LLM_MODELS, CUSTOM_PATH = \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'LAYOUT',
             'API_KEY', 'AVAIL_LLM_MODELS', 'CUSTOM_PATH')

proxy_info = check_proxy(proxies)
# 如果WEB_PORT是-1, 则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
os.environ['no_proxy'] = '*'  # 避免代理网络产生意外污染
i18n = webui_local.I18nAuto()
get_html = func_box.get_html

from webui_elem.layout_history_menu import LeftElem
from webui_elem.layout_chatbot_area import ChatbotElem
from webui_elem.layout_tools_menu import RightElem
from webui_elem.layout_popup_wrapper import Settings, Config, FakeComponents, AdvancedSearch, Prompt, GptsStore


class ChatBot(LeftElem, ChatbotElem, RightElem, Settings, Config, FakeComponents, AdvancedSearch, Prompt, GptsStore):

    def __init__(self):
        super().__init__()
        self.initial_prompt = ""
        self.cancel_handles = []
        self.app_name = get_conf('APPNAME')
        self.__url = f'http://{func_box.ipaddr()}:{PORT}'
        # self.__gr_url = gr.State(self.__url)

    def signals_sm_btn(self):
        self.model_select_dropdown.select(func_signals.update_chat, inputs=[self.model_select_dropdown, self.cookies],
                                          outputs=[self.chatbot, self.cookies])
        self.sm_upload.upload(on_file_uploaded, [self.sm_upload, self.chatbot, self.user_input, self.cookies],
                              [self.chatbot, self.user_input])
        self.sm_upload.clear(fn=func_signals.sm_upload_clear,
                             inputs=[self.cookies],
                             outputs=[self.sm_upload, self.cookies])
        self.sm_code_block.click(fn=lambda x: x + '```\n\n```', inputs=[self.user_input], outputs=[self.user_input])
        self.sm_upload_history.click(func_signals.get_user_upload, [self.chatbot, self.user_input],
                                     outputs=[self.chatbot])
        self.sm_history.click(fn=None, inputs=None, outputs=None, _js='()=>{menuClick();}')
        # self.langchain_dropdown.select(fn=Langchain_cn.obtaining_knowledge_base_files,
        #                                inputs=[self.langchain_dropdown, self.chatbot,
        #                                        self.models_box],
        #                                outputs=[self.chatbot, self.status_display]
        #                                )
        self.delLastBtn.click(func_signals.delete_latest_chat, inputs=[self.chatbot, self.history, self.cookies],
                              outputs=[self.chatbot, self.history, self.cookies])
        self.retry_queue = self.retryBtn.click(fn=ArgsGeneralWrapper(predict),
                                               inputs=self.input_combo + [gr.State('RetryChat')],
                                               outputs=self.output_combo, show_progress=True)
        self.cancel_handles.append(self.retry_queue)

    def signals_prompt_func(self):
        self.multiplexing_edit_check.change(fn=func_signals.change_check_txt,
                                            inputs=[self.multiplexing_edit_check, self.pro_fp_state],
                                            outputs=[self.pro_func_prompt])
        self.pro_private_check.select(fn=func_signals.prompt_reduce,
                                      inputs=[self.pro_private_check, self.pro_fp_state],
                                      outputs=[self.pro_func_prompt, self.pro_fp_state, self.pro_private_check]
                                      )
        self.pro_func_prompt.select(fn=func_signals.prompt_input,
                                    inputs=[self.multiplexing_edit_check, self.user_input, self.cookies,
                                            self.model_select_dropdown, self.pro_func_prompt, self.pro_fp_state],
                                    outputs=[self.treasure_bag_tab,
                                             self.prompt_cls_select, self.pro_edit_txt, self.pro_name_txt,
                                             self.mask_cls_select, self.masks_dataset, self.masks_name_txt,
                                             *self.llms_cookies_combo, gr.State(),
                                             self.historySelectList, self.saveFileName,
                                             self.user_input],
                                    _js='(a,b,c,e,f)=>{return reuse_or_edit(a,b,c,e,f);}')
        self.prompt_search_txt.submit(fn=func_signals.prompt_search,
                                      inputs=[self.pro_private_check, self.prompt_search_txt,
                                              self.pro_tf_slider, self.pro_fp_state],
                                      outputs=[self.pro_func_prompt, self.pro_fp_state])
        self.pro_upload_btn.upload(fn=func_signals.prompt_upload_refresh,
                                   inputs=[self.pro_upload_btn, self.pro_history_state, self.pro_private_check],
                                   outputs=[self.pro_func_prompt, self.pro_history_state, self.pro_private_check])

    def signals_prompt_edit(self):
        self.history_search_txt.submit(fn=func_signals.draw_results,
                                       inputs=[self.history_search_txt, self.pro_history_state, self.pro_tf_slider],
                                       outputs=[self.pro_history_list, self.pro_history_state])
        self.pro_history_list.click(fn=func_signals.show_prompt_result,
                                    inputs=[self.pro_history_list, self.pro_history_state, self.cookies],
                                    outputs=[self.historySelectList, *self.llms_cookies_combo],
                                    ).then(None, None, None, _js='()=>{closeBtnClick();}')
        self.pro_del_btn.click(func_signals.prompt_delete,
                               inputs=[self.pro_name_txt, self.pro_fp_state, self.prompt_cls_select],
                               outputs=[self.pro_func_prompt, self.pro_fp_state, self.spike_toast])
        self.pro_new_btn.click(None, None, None, _js='()=>{closeBtnClick();}')
        self.pro_new_btn.click(fn=func_signals.prompt_save,
                               inputs=[self.pro_edit_txt, self.pro_name_txt, self.pro_fp_state, self.prompt_cls_select],
                               outputs=[self.pro_func_prompt, self.pro_fp_state, self.spike_toast])

    def signals_masks(self):
        self.masks_dataset.change(fn=func_signals.mask_setting_role, inputs=[self.masks_dataset],
                                  outputs=[self.masks_dataset, self.mask_preview_chat])
        self.masks_delete_btn.click(fn=func_signals.mask_del_new_row, inputs=[self.masks_dataset],
                                    outputs=[self.masks_dataset])
        self.masks_clear_btn.click(func_signals.mask_clear_all,
                                   inputs=[self.masks_dataset,
                                           gr.HTML(value=i18n('Mask Tab'), visible=False),
                                           gr.HTML(value=i18n('Clear All'), visible=False)],
                                   outputs=[self.masks_dataset],
                                   _js='(a,b,c)=>{return showConfirmationDialog(a,b,c);}')
        self.masks_del_btn.click(func_signals.prompt_delete,
                                 inputs=[self.masks_name_txt, self.pro_fp_state, self.mask_cls_select],
                                 outputs=[self.pro_func_prompt, self.pro_fp_state, self.spike_toast])
        self.masks_new_btn.click(None, None, None, _js='()=>{closeBtnClick();}')
        self.masks_new_btn.click(fn=func_signals.prompt_save,
                                 inputs=[self.masks_dataset, self.masks_name_txt,
                                         self.pro_fp_state, self.mask_cls_select],
                                 outputs=[self.pro_func_prompt, self.pro_fp_state, self.spike_toast])

    def signals_reader(self):
        self.reader_upload.upload(fn=func_signals.reader_analysis_output,
                                  inputs=[self.reader_upload, self.reader_choice],
                                  outputs=[self.reader_show, self.reader_copy, self.spike_toast])

    def signals_gpts_store(self):
        for tag in self.gpts_tags_mapping:
            self.gpts_tags_mapping[tag]['tab'].select(
                fn=func_signals.gpts_tag_select,
                inputs=[gr.HTML(value='', visible=False), self.gpts_samples_mapping[tag]],
                outputs=[self.gpts_tags_mapping[tag]['data_set'], self.gpts_samples_mapping[tag]],
                _js="(a, b)=>{return gpts_tabs_select(a, b);}")

            self.gpts_tags_mapping[tag]['data_set'].click(None, None, None, _js='()=>{closeBtnClick();}')
            self.gpts_tags_mapping[tag]['data_set'].click(
                fn=func_signals.gpts_select_model,
                inputs=[self.gpts_tags_mapping[tag]['data_set'], self.gpts_samples_mapping[tag], self.cookies],
                outputs=[self.historySelectList, self.model_select_dropdown, *self.llms_cookies_combo])
        key_search = '🔍 关键词搜索'
        self.gpts_tags_mapping[key_search]['search'].submit(
            fn=func_signals.gpts_tag_select,
            inputs=[self.gpts_tags_mapping[key_search]['search'], self.gpts_samples_mapping[key_search]],
            outputs=[self.gpts_tags_mapping[key_search]['data_set'], self.gpts_samples_mapping[key_search]]
        )

    def signals_plugin(self):
        from common.crazy_functional import crazy_fns_role, crazy_fns
        fn_btn_dict = {crazy_fns_role[role][k]['Button']: {role: k} for role in crazy_fns_role for k in
                       crazy_fns_role[role] if crazy_fns_role[role][k].get('Button')}

        def show_plugin_btn(plu_list):
            new_btn_list = []
            fns_list = []
            if not plu_list:
                return [*[fns.update(visible=False) for fns in fn_btn_dict], gr.update(choices=[])]
            else:
                for fns in fn_btn_dict:
                    if list(fn_btn_dict[fns].keys())[0] in plu_list:
                        new_btn_list.append(fns.update(visible=True))
                    else:
                        new_btn_list.append(fns.update(visible=False))
                for role in crazy_fns_role:
                    if role in plu_list:
                        for k in crazy_fns_role[role]:
                            if not crazy_fns_role[role][k].get("AsButton", True):
                                fns_list.append(k)
                            elif crazy_fns_role[role][k].get('AdvancedArgs', False):
                                fns_list.append(k)
                return [*new_btn_list, gr.update(choices=fns_list)]

        # 文件上传区，接收文件后与chatbot的互动
        self.file_upload.upload(on_file_uploaded, [self.file_upload, self.chatbot, self.user_input, self.cookies],
                                [self.chatbot, self.user_input])
        # 函数插件-固定按钮区
        self.plugin_dropdown.select(fn=show_plugin_btn, inputs=[self.plugin_dropdown],
                                    outputs=[*fn_btn_dict.keys(), self.dropdown_fn])
        for i in crazy_fns_role:
            role_fns = crazy_fns_role[i]
            for k in role_fns:
                if not role_fns[k].get("AsButton", True): continue
                click_handle = role_fns[k]["Button"].click(**self.clear_agrs).then(
                    ArgsGeneralWrapper(role_fns[k]["Function"]),
                    [*self.input_combo, gr.State(k),
                     gr.State(role_fns[k].get('Parameters', False))],
                    self.output_combo)
                # click_handle.then(on_report_generated, [self.cookies, self.file_upload, self.chatbot],
                #                   [self.cookies, self.file_upload, self.chatbot])
                self.cancel_handles.append(click_handle)

        # 函数插件-下拉菜单与随变按钮的互动
        def on_dropdown_changed(k):
            # 按钮颜色随变
            variant = crazy_fns[k]["Color"] if "Color" in crazy_fns[k] else "secondary"
            ret = {self.switchy_bt: self.switchy_bt.update(value=k, variant=variant, visible=True),
                   self.area_crazy_fn: gr.update()}
            # 参数取随变
            fns_value = func_box.txt_converter_json(str(crazy_fns[k].get('Parameters', '')))
            fns_lable = f"插件[{k}]的高级参数说明：\n" + crazy_fns[k].get("ArgsReminder", f"没有提供高级参数功能说明")
            temp_dict = dict(visible=True, interactive=True, value=str(fns_value), label=fns_lable)
            #  是否唤起高级插件参数区
            if crazy_fns[k].get("AdvancedArgs", False):
                ret.update(
                    {self.plugin_advanced_arg: gr.update(**temp_dict), self.area_crazy_fn: gr.update(open=False)})
            else:
                ret.update({self.plugin_advanced_arg: gr.update(visible=False, label=f"插件[{k}]不需要高级参数。")})
            return ret

        self.dropdown_fn.select(on_dropdown_changed, [self.dropdown_fn],
                                [self.switchy_bt, self.plugin_advanced_arg, self.area_crazy_fn])

        # 随变按钮的回调函数注册
        def route(k, ipaddr: gr.Request, *args, **kwargs):
            if k in [r"打开插件列表", r"请先从插件列表中选择"]: return
            append = list(args)
            append[-1] = func_box.txt_converter_json(append[-1])
            append.append(ipaddr)
            append.append(k)
            args = tuple(append)
            yield from ArgsGeneralWrapper(crazy_fns[k]["Function"])(*args, **kwargs)

        click_handle = self.switchy_bt.click(**self.clear_agrs).then(
            route, [self.switchy_bt, *self.input_combo], self.output_combo)
        # click_handle.then(on_report_generated,
        #       [self.cookies, self.file_upload, self.chatbot],
        #       [self.cookies, self.file_upload, self.chatbot])
        self.cancel_handles.append(click_handle)
        # 终止按钮的回调函数注册
        self.cancelBtn.click(fn=lambda: (self.cancelBtn.update(visible=False), self.submitBtn.update(visible=True)),
                             inputs=[], outputs=[self.cancelBtn, self.submitBtn], cancels=self.cancel_handles).then(
            fn=func_signals.stop_chat_refresh, inputs=[self.chatbot, self.cookies],
            outputs=[]
        )

    def signals_knowledge_base(self):
        self.show_hide_combo = [self.new_knowledge_base, self.edit_knowledge_base]
        self.file_details_combo = [self.knowledge_base_select, self.edit_kb_introduce,
                                   self.edit_kb_file_list, self.edit_kb_file_details, self.edit_kb_file_fragment]

        self.kb_edit_confirm_combo = [self.edit_kb_upload, self.knowledge_base_select, self.edit_kb_introduce,
                                      self.edit_kb_max_paragraph, self.edit_kb_similarity_paragraph,
                                      self.edit_kb_tokenizer_select, self.edit_kb_loader_select]

        self.knowledge_base_select.select(fn=func_signals.kb_select_show, inputs=[self.knowledge_base_select],
                                          outputs=self.show_hide_combo).then(
            fn=func_signals.kb_name_select_then, inputs=[self.knowledge_base_select],
            outputs=self.file_details_combo)

        self.new_kb_name.change(fn=func_signals.kb_name_change_btn, inputs=[self.new_kb_name],
                                outputs=[self.new_kb_confirm_btn])

        self.edit_kb_upload.change(fn=func_signals.kb_upload_btn, inputs=[self.edit_kb_upload, self.edit_kb_cloud],
                                   outputs=[self.edit_kb_confirm_btn])
        self.edit_kb_cloud.change(fn=func_signals.kb_upload_btn, inputs=[self.edit_kb_upload, self.edit_kb_cloud],
                                  outputs=[self.edit_kb_confirm_btn])

        self.edit_kb_introduce.input(fn=func_signals.kb_introduce_change_btn,
                                     inputs=[self.knowledge_base_select, self.edit_kb_introduce],
                                     outputs=[self.spike_toast])

        self.edit_kb_file_fragment_add.click(func_signals.kb_date_add_row, inputs=[self.edit_kb_file_fragment],
                                             outputs=[self.edit_kb_file_fragment])

        self.new_kb_confirm_btn.click(fn=func_signals.kb_new_confirm,
                                      inputs=[self.new_kb_name, self.new_kb_vector_types,
                                              self.new_kb_embedding_model, self.new_kb_introduce],
                                      outputs=self.show_hide_combo + self.file_details_combo + [self.kb_input_select])

        self.download_embedding_model.click(func_signals.kb_download_embedding_model,
                                            inputs=[self.select_embedding_model],
                                            outputs=[self.embedding_download_status]
                                            ).then(fn=lambda: gr.update(choices=list_local_embed_models()),
                                                   inputs=[],
                                                   outputs=[self.new_kb_embedding_model])

        self.edit_kb_confirm_btn.click(func_signals.kb_file_update_confirm,
                                       inputs=self.kb_edit_confirm_combo + [self.edit_kb_cloud],
                                       outputs=self.file_details_combo)
        self.edit_kb_file_list.input(
            fn=func_signals.kb_select_file, inputs=[self.knowledge_base_select, self.edit_kb_file_list],
            outputs=[self.edit_kb_file_details, self.edit_kb_file_fragment]
        )

        self.edit_knowledge_base_del.click(fn=func_signals.kb_base_del,
                                           inputs=[self.knowledge_base_select,
                                                   self.knowledge_base_select,
                                                   gr.HTML('删除知识库',
                                                           visible=False)],
                                           outputs=self.show_hide_combo + [self.knowledge_base_select,
                                                                           self.kb_input_select],
                                           _js="(a,b,c)=>{return showConfirmationDialog(a,b,c);}")
        self.edit_kb_info_docs_del.click(func_signals.kb_docs_file_source_del,
                                         inputs=[self.knowledge_base_select, self.edit_kb_file_list,
                                                 gr.HTML('删除数据源', visible=False)],
                                         outputs=[self.spike_toast, self.edit_kb_file_list, self.edit_kb_file_details,
                                                  self.edit_kb_file_fragment],
                                         _js="(a,b,c)=>{return showConfirmationDialog(a,b,c);}")

        self.edit_kb_info_vector_del.click(func_signals.kb_vector_del,
                                           inputs=[self.knowledge_base_select, self.edit_kb_file_list,
                                                   self.edit_kb_file_details],
                                           outputs=[self.spike_toast, self.edit_kb_file_details,
                                                    self.edit_kb_file_fragment])

        self.edit_kb_info_reload_vector.click(func_signals.kb_vector_reload,
                                              inputs=self.kb_edit_confirm_combo + [self.edit_kb_file_list],
                                              outputs=[self.spike_toast, self.edit_kb_file_details,
                                                       self.edit_kb_file_fragment])

        self.edit_kb_info_fragment_save.click(fn=func_signals.kb_base_changed_save,
                                              inputs=self.kb_edit_confirm_combo + [self.edit_kb_file_list,
                                                                                   self.edit_kb_file_fragment],
                                              outputs=[self.spike_toast, self.edit_kb_file_fragment])

    def signals_history(self):
        self.llms_cookies_combo = [self.chatbot, self.history, self.cookies,
                                   self.top_p, self.temperature, self.n_choices_slider, self.stop_sequence_txt,
                                   self.presence_penalty_slider, self.frequency_penalty_slider,
                                   self.user_identifier_txt, self.response_format_select,
                                   self.max_context_length_slider, self.max_generation_slider, self.logit_bias_txt,
                                   self.system_prompt, self.model_select_dropdown]
        self.historySelectList.input(fn=func_signals.select_history,
                                     inputs=[self.historySelectList, self.model_select_dropdown, self.cookies],
                                     outputs=[*self.llms_cookies_combo, self.saveFileName])
        self.renameHistoryBtn.click(func_signals.rename_history,
                                    inputs=[self.saveFileName, self.historySelectList],
                                    outputs=[self.historySelectList],
                                    _js='(a,b,c,d)=>{return saveChatHistory(a,b,c,d);}')
        self.historyDeleteBtn.click(func_signals.delete_history,
                                    inputs=[self.cookies, self.historySelectList, self.historyDeleteBtn],
                                    outputs=[self.historySelectList, *self.llms_cookies_combo],
                                    _js='(a,b,c)=>{return showConfirmationDialog(a,b,c);}')
        self.uploadFileBtn.upload(fn=func_signals.import_history, inputs=[self.uploadFileBtn],
                                  outputs=[self.historySelectList])
        self.historyRefreshBtn.click(func_signals.refresh_history, inputs=[self.cookies],
                                     outputs=[self.historySelectList, *self.llms_cookies_combo])
        self.historyDownloadBtn.click(func_signals.download_history_json, inputs=[self.historySelectList],
                                      outputs=[self.status_display])
        self.historyMarkdownDownloadBtn.click(func_signals.download_history_md, inputs=[self.historySelectList],
                                              outputs=[self.status_display])
        self.historyMasksConverterBtn.click(func_signals.converter_history_masks,
                                            inputs=[self.chatbot, self.system_prompt], outputs=[self.masks_dataset]
                                            ).then(lambda: gr.Tabs.update('masks'),
                                                   inputs=None, outputs=[self.treasure_bag_tab],
                                                   _js='()=>{open_treasure_chest();}')
        self.historySearchTextbox.submit(fn=func_signals.draw_results,
                                         inputs=[self.historySearchTextbox, self.pro_history_state, self.pro_tf_slider],
                                         outputs=[self.pro_history_list, self.pro_history_state],
                                         ).then(fn=lambda x: x, inputs=[self.historySearchTextbox],
                                                outputs=[self.history_search_txt]).then(None, None, None,
                                                                                        _js='()=>{openSearch();}')

        self.gptsStoreBtn.click(None, None, None, _js='()=>{openGptsStore();}')

    def signals_input_setting(self):
        # 注册input
        self.input_combo = [self.cookies, self.max_length_sl, self.model_select_dropdown, self.input_copy,
                            self.top_p, self.temperature, self.n_choices_slider, self.stop_sequence_txt,
                            self.max_context_length_slider, self.max_generation_slider, self.presence_penalty_slider,
                            self.frequency_penalty_slider, self.logit_bias_txt,
                            self.user_identifier_txt, self.response_format_select,
                            self.chatbot, self.history, self.system_prompt, self.plugin_advanced_arg,
                            self.single_turn_checkbox, self.use_websearch_checkbox]
        # 知识库
        self.know_combo = [self.kb_input_select, self.vector_search_score, self.vector_search_top_k]
        self.input_combo.extend(self.know_combo)
        # 高级设置
        self.models_combo = [self.input_models, self.vision_models, self.project_models, self.vector_search_to_history]
        self.input_models.input(func_signals.update_models,
                                inputs=self.models_combo,
                                outputs=[self.models_box])
        self.vision_models.input(func_signals.update_models,
                                 inputs=self.models_combo,
                                 outputs=[self.models_box])
        self.project_models.input(func_signals.update_models,
                                  inputs=self.models_combo,
                                  outputs=[self.models_box])
        self.vector_search_to_history.input(func_signals.update_models,
                                            inputs=self.models_combo,
                                            outputs=[self.models_box])
        self.setting_combo = [self.models_box, self.history_round_num, self.default_worker_num,
                              self.ocr_identifying_trust]
        self.input_combo.extend(self.setting_combo)
        # 个人信息
        self.user_combo = [self.openai_keys, self.wps_cookie, self.qq_cookie, self.feishu_cookie,
                           self.feishu_project_use_key, self.feishu_project_cookie]
        self.input_combo.extend(self.user_combo)

        self.output_combo = [self.cookies, self.chatbot, self.history, self.status_display, self.cancelBtn,
                             self.submitBtn]
        self.predict_args = dict(fn=ArgsGeneralWrapper(predict), inputs=self.input_combo,
                                 outputs=self.output_combo, show_progress=True)
        self.clear_agrs = dict(fn=func_signals.clear_input,
                               inputs=[self.user_input, self.cookies],
                               outputs=[self.user_input, self.input_copy, self.cancelBtn, self.chatbot,
                                        self.submitBtn, self.historySelectList, self.sm_upload])
        # 提交按钮、重置按钮
        submit_handle = self.user_input.submit(**self.clear_agrs).then(**self.predict_args)
        click_handle = self.submitBtn.click(**self.clear_agrs).then(**self.predict_args)
        self.cancel_handles.append(submit_handle)
        self.cancel_handles.append(click_handle)
        self.emptyBtn.click(func_signals.clear_chat_cookie, [self.model_select_dropdown, self.cookies],
                            [*self.llms_cookies_combo, self.status_display,
                             self.historySelectList, self.saveFileName])
        self.changeSingleSessionBtn.click(
            fn=lambda value: gr.update(value=value), inputs=[self.single_turn_checkbox],
            outputs=[self.single_turn_checkbox], _js='(a)=>{return bgChangeSingleSession(a);}'
        )
        self.changeOnlineSearchBtn.click(
            fn=lambda value: gr.update(value=value), inputs=[self.use_websearch_checkbox],
            outputs=[self.use_websearch_checkbox], _js='(a)=>{return bgChangeOnlineSearch(a);}'
        )

    def signals_settings_popup(self):
        self.theme_dropdown.select(func_signals.on_theme_dropdown_changed, [self.theme_dropdown],
                                   [self.secret_css, self.theme_dropdown]).then(
            None, [self.secret_css], None, _js="(css) => {return setThemeClass(css)}")
        self.latex_option.select(fn=func_signals.switch_latex_output,
                                 inputs=[self.latex_option], outputs=[self.chatbot])

    # gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
    def auto_opentab_delay(self, is_open=False):
        import threading, webbrowser, time
        print(f"如果浏览器没有自动打开，请复制并转到以下URL：")
        print(f"\t 本地访问: http://localhost:{PORT}{CUSTOM_PATH}")
        print(f"\t 局域网访问: {self.__url}{CUSTOM_PATH}")
        if is_open:
            def open():
                time.sleep(2)  # 打开浏览器
                webbrowser.open_new_tab(f"http://localhost:{PORT}{CUSTOM_PATH}?__theme=dark")

            threading.Thread(target=open, name="open-browser", daemon=True).start()
            threading.Thread(target=auto_update, name="self-upgrade", daemon=True).start()
        # threading.Thread(target=warm_up_modules, name="warm-up", daemon=True).start()

    def block_title(self):
        self.cookies = gr.State({'api_key': API_KEY, 'llm_model': LLM_MODEL})
        self.history = gr.State([])
        with gr.Row(elem_id="chuanhu-header"):
            gr.HTML(get_html("header_title.html").format(
                app_title=self.app_name), elem_id="app-title")
        with gr.Row(elem_id="float-display"):
            self.user_info = gr.Markdown(
                value="getting user info...", elem_id="user-info")
            self.update_info = gr.HTML(get_html("update.html").format(
                current_version='',
                version_time='',
                cancel_btn=i18n("取消"),
                update_btn=i18n("更新"),
                seenew_btn=i18n("详情"),
                ok_btn=i18n("好"),
            ), visible=False)

    def main(self):
        # 做一些外观色彩上的调整
        from webui_elem.theme import adjust_theme
        with gr.Blocks(title=self.app_name, theme=adjust_theme) as self.demo:
            self.block_title()
            with gr.Row(equal_height=True, elem_id="chuanhu-body"):
                self.draw_history_area()
                self.draw_chatbot_area()
                self.draw_tools_area()

            with gr.Row(elem_id="popup-wrapper"):
                with gr.Box(elem_id="chuanhu-popup"):
                    self.draw_popup_settings()
                    self.draw_popup_config()
                    self.draw_popup_fake()
                    self.draw_popup_search()
                    self.draw_popup_prompt()
                    self.draw_popup_gpts()
            # 函数注册，需要在Blocks下进行
            self.signals_history()
            self.signals_input_setting()
            self.signals_sm_btn()
            self.signals_prompt_func()
            self.signals_prompt_edit()
            self.signals_plugin()
            self.signals_knowledge_base()
            self.signals_reader()
            self.signals_settings_popup()
            self.signals_masks()
            self.signals_gpts_store()
            # self.demo.load(fn=func_signals.mobile_access, inputs=[],
            #                outputs=[self.sm_btn_column, self.langchain_dropdown])
            self.demo.load(fn=func_signals.refresh_load_data,
                           inputs=[self.pro_fp_state],
                           outputs=[self.pro_func_prompt, self.pro_fp_state, self.copyright_display,
                                    self.pro_private_check, self.prompt_cls_select, self.mask_cls_select,
                                    self.knowledge_base_select, self.kb_input_select])
            self.demo.load(fn=func_signals.refresh_user_data,
                           inputs=[self.cookies, gr.State(proxy_info)],
                           outputs=[self.historySelectList, *self.llms_cookies_combo,
                                    self.saveFileName, self.status_display])

        # Start
        self.auto_opentab_delay()
        self.demo.queue(concurrency_count=CONCURRENT_COUNT)
        # 过滤掉不允许用户访问的路径
        self.demo.blocked_paths = func_box.get_files_and_dirs(
            path=init_path.base_path, filter_allow=['users_private', 'gpt_log', 'docs'])
        login_html = '登陆即注册，请记住你自己的账号和密码'
        self.demo.auth_message = login_html
        if AUTHENTICATION == 'SQL':
            self.demo.auth = func_signals.user_login
        # gr.mount_gradio_app     # rewriting
        self.demo.dev_mode = False
        self.demo.config = self.demo.get_config_file()
        self.demo.favicon_path = get_conf('favicon_path')
        self.demo.validate_queue_settings()
        from gradio.routes import App
        gradio_app = App.create_app(self.demo)
        return gradio_app


def init_gradio_app():
    from common.api_server.gradio_app import file_authorize_user
    from common.api_server.base import create_app

    gradio_app = ChatBot().main()
    # --- --- replace gradio endpoint to forbid access to sensitive files --- ---
    dependencies = []
    endpoint = None
    gradio_app: fastapi  # 增加类型提示，避免警告
    for route in list(gradio_app.router.routes):
        if route.path == "/file/{path:path}":
            gradio_app.router.routes.remove(route)
        if route.path == "/file={path_or_url:path}":
            dependencies = route.dependencies
            endpoint = route.endpoint
            gradio_app.router.routes.remove(route)

    @gradio_app.get("/file/{path:path}", dependencies=dependencies)
    @gradio_app.head("/file={path_or_url:path}", dependencies=dependencies)
    @gradio_app.get("/file={path_or_url:path}", dependencies=dependencies)
    async def file(path_or_url: str, request: fastapi.Request):
        if not file_authorize_user(path_or_url, request, gradio_app):
            return {"detail": "Hack me? How dare you?"}
        return await endpoint(path_or_url, request)

    server_app = create_app()

    server_app.mount(CUSTOM_PATH, gradio_app)

    # 启用Gradio原生事件，不然会卡Loading哟
    @server_app.on_event("startup")
    async def start_queue():
        if gradio_app.get_blocks().enable_queue:
            gradio_app.get_blocks().startup_events()

    return server_app


def init_start():
    import uvicorn
    from common.logger_handler import init_config, logger
    # 初始化外部java script
    reload_javascript()
    # 初始化gradio fastapi
    gradio_app = init_gradio_app()
    # 检查/初始化数据库
    info_path = os.path.join(init_path.private_knowledge_path, 'info.db')
    if not os.path.exists(info_path):
        from common.knowledge_base.migrate import create_tables, folder2db
        from common.db.repository.prompt_repository import batch_import_prompt_dir
        create_tables()
        batch_import_prompt_dir()
        folder2db([], mode="recreate_vs")
        logger.info('create kb tables, initialization Prompt')
    # 正式开启启动
    logger.info('start...')
    app_reload = get_conf('app_reload')
    config = uvicorn.Config(gradio_app, host="0.0.0.0", port=PORT, reload=app_reload)
    server = uvicorn.Server(config)
    init_config()
    server.run()


if __name__ == '__main__':
    init_start()
