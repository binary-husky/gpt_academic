import os
import gradio as gr
import logging

from request_llm.bridge_all import predict
from comm_tools.toolbox import find_free_port, on_file_uploaded, get_user_upload, \
    get_conf, ArgsGeneralWrapper
from comm_tools.overwrites import postprocess_chat_messages, postprocess, reload_javascript
# 问询记录, python 版本建议3.9+（越新越好）
# 一些普通功能模块
from comm_tools.core_functional import get_core_functions
from comm_tools import Langchain_cn, webui_local
functional = get_core_functions()

# 处理markdown文本格式的转变 暂时屏蔽这个高亮代码
# gr.Chatbot.postprocess = format_io
gr.Chatbot._postprocess_chat_messages = postprocess_chat_messages
gr.Chatbot.postprocess = postprocess

# 做一些外观色彩上的调整
from comm_tools.theme import adjust_theme
set_theme = adjust_theme()

# 代理与自动更新
from comm_tools.check_proxy import check_proxy, auto_update
from comm_tools import func_box, func_signals
from comm_tools.check_proxy import get_current_version

os.makedirs("gpt_log", exist_ok=True)
try:
    logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO, encoding="utf-8")
except:
    logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO)
print("所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log, 请注意自我隐私保护哦！")

# 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, LAYOUT, API_KEY, AVAIL_LLM_MODELS, LOCAL_PORT= \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'LAYOUT',
             'API_KEY', 'AVAIL_LLM_MODELS', 'LOCAL_PORT')

proxy_info = check_proxy(proxies)
# 如果WEB_PORT是-1, 则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
if not AUTHENTICATION: AUTHENTICATION = None
os.environ['no_proxy'] = '*'  # 避免代理网络产生意外污染
i18n = webui_local.I18nAuto()
get_html = func_box.get_html

from webui_elem.history_menu import LeftElem
from webui_elem.chatbot_area import ChatbotElem
from webui_elem.tools_menu import RightElem
from webui_elem.popup_wrapper import Settings, Training, Config, FakeComponents


class ChatBot(LeftElem, ChatbotElem, RightElem, Settings, Training, Config, FakeComponents):

    def __init__(self):
        super().__init__()
        self.initial_prompt = ""
        self.cancel_handles = []
        self.app_name, = get_conf('APPNAME')
        self.__url = f'http://{func_box.ipaddr()}:{PORT}'
        # self.__gr_url = gr.State(self.__url)

    def signals_sm_btn(self):
        self.sm_upload.upload(on_file_uploaded, [self.sm_upload, self.chatbot, self.user_input, self.cookies],
                              [self.chatbot, self.user_input])
        self.sm_code_block.click(fn=lambda x: x+'```\n\n```', inputs=[self.user_input], outputs=[self.user_input])
        self.sm_upload_history.click(get_user_upload, [self.chatbot, self.user_input], outputs=[self.chatbot])
        self.langchain_dropdown.select(fn=Langchain_cn.obtaining_knowledge_base_files,
                                       inputs=[self.langchain_classifi, self.langchain_class_name, self.langchain_dropdown, self.chatbot, self.langchain_know_kwargs, self.models_box],
                                       outputs=[self.chatbot, self.status_display, self.langchain_know_kwargs]
                                       )

    def __clear_input(self, inputs):
        return '', inputs, self.cancelBtn.update(visible=True), self.submitBtn.update(visible=False)

    def signals_prompt_func(self):
        self.pro_private_check.select(fn=func_signals.prompt_reduce,
                                      inputs=[self.pro_private_check, self.pro_fp_state],
                                      outputs=[self.pro_func_prompt, self.pro_fp_state, self.pro_private_check]
                                      ).then(fn=func_box.new_button_display, inputs=[self.pro_private_check],
                                             outputs=[self.pro_class_name])
        self.pro_func_prompt.select(fn=func_signals.prompt_input,
                                    inputs=[self.user_input, self.pro_edit_txt, self.pro_name_txt, self.pro_func_prompt,
                                            self.pro_fp_state],
                                    outputs=[self.user_input, self.pro_edit_txt, self.pro_name_txt])
        self.pro_upload_btn.upload(fn=func_signals.prompt_upload_refresh,
                                   inputs=[self.pro_upload_btn, self.pro_prompt_state, self.pro_private_check, self.pro_class_name],
                                   outputs=[self.pro_func_prompt, self.pro_prompt_state, self.pro_private_check])

    def signals_prompt_edit(self):
        self.pro_clear_btn.click(fn=lambda: [], inputs=None, outputs=self.pro_results)
        self.prompt_tab.select(fn=func_signals.draw_results,
                               inputs=[self.pro_search_txt, self.pro_prompt_state, self.pro_tf_slider,
                                       self.pro_private_check],
                               outputs=[self.pro_prompt_list, self.pro_prompt_state])
        self.pro_search_txt.submit(fn=func_signals.draw_results,
                                   inputs=[self.pro_search_txt, self.pro_prompt_state, self.pro_tf_slider,
                                         self.pro_private_check],
                                   outputs=[self.pro_prompt_list, self.pro_prompt_state])
        self.pro_entry_btn.click(fn=func_signals.draw_results,
                                 inputs=[self.pro_search_txt, self.pro_prompt_state, self.pro_tf_slider,
                                         self.pro_private_check],
                                 outputs=[self.pro_prompt_list, self.pro_prompt_state])
        self.pro_prompt_list.click(fn=func_signals.show_prompt_result,
                                   inputs=[self.pro_prompt_list, self.pro_prompt_state, self.pro_results,
                                           self.pro_edit_txt, self.pro_name_txt],
                                   outputs=[self.pro_results, self.pro_edit_txt, self.pro_name_txt, self.prompt_edit_area])
        self.pro_del_btn.click(func_signals.prompt_delete,
                               inputs=[self.pro_name_txt, self.pro_fp_state, self.pro_private_check],
                               outputs=[self.pro_func_prompt, self.pro_fp_state])
        self.pro_new_btn.click(fn=func_signals.prompt_save,
                               inputs=[self.pro_edit_txt, self.pro_name_txt, self.pro_fp_state, self.pro_private_check, self.pro_class_name],
                               outputs=[self.pro_edit_txt, self.pro_name_txt, self.pro_private_check,
                                        self.pro_func_prompt, self.pro_fp_state])
        self.pro_reuse_btn.click(
            fn=func_signals.reuse_chat,
            inputs=[self.pro_results, self.chatbot, self.history, self.user_input],
            outputs=[self.chatbot, self.history, self.user_input]
        )

    def signals_plugin(self):
        from comm_tools.crazy_functional import crazy_fns_role, crazy_classification, crazy_fns
        fn_btn_dict = {crazy_fns_role[role][k]['Button']: {role: k} for role in crazy_fns_role for k in crazy_fns_role[role] if crazy_fns_role[role][k].get('Button')}
        def show_plugin_btn(plu_list):
            new_btn_list = []
            fns_list = []
            if not plu_list:
                return [*[fns.update(visible=False) for fns in fn_btn_dict], gr.Dropdown.update(choices=[])]
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
                return [*new_btn_list, gr.Dropdown.update(choices=fns_list)]

        # 文件上传区，接收文件后与chatbot的互动
        self.file_upload.upload(on_file_uploaded, [self.file_upload, self.chatbot, self.user_input, self.cookies], [self.chatbot, self.user_input])
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
                ret.update({self.plugin_advanced_arg: gr.update(**temp_dict), self.area_crazy_fn: gr.update(open=False)})
            else:
                ret.update({self.plugin_advanced_arg: gr.update(visible=False, label=f"插件[{k}]不需要高级参数。")})
            return ret
        self.dropdown_fn.select(on_dropdown_changed, [self.dropdown_fn], [self.switchy_bt, self.plugin_advanced_arg, self.area_crazy_fn])

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
            inputs=[], outputs=[self.cancelBtn, self.submitBtn], cancels=self.cancel_handles)

    def signals_langchain_cn(self):
        def update_drop(x, llms, cls_name, ipaddr: gr.Request):
            _, available, _,  = Langchain_cn.obtain_classification_knowledge_base(cls_name, ipaddr)
            x = x['know_name']
            if not x:
                return available, gr.update()
            return available, gr.update(label="当前模型：" + llms + "&" + '&'.join([x]))
        self.langchain_classifi.select(fn=Langchain_cn.obtain_classification_knowledge_base,
                                       inputs=[self.langchain_classifi],
                                       outputs=[self.langchain_select, self.langchain_dropdown, self.langchain_status]
                                       ).then(fn=func_box.new_button_display,
                                              inputs=[self.langchain_classifi], outputs=[self.langchain_class_name])
        self.langchain_upload.upload(fn=on_file_uploaded,
                                     inputs=[self.langchain_upload, gr.State(''), self.langchain_know_kwargs, self.cookies],
                                     outputs=[self.langchain_status, self.langchain_know_kwargs])

        def clear_file(kw):
            kw.update({'file_path': ''})
            return kw, f'已清空本地文件调用路径参数'
        self.langchain_upload.clear(fn=clear_file,
                                    inputs=[self.langchain_know_kwargs],
                                    outputs=[self.langchain_know_kwargs, self.langchain_status])

        submit_id = self.langchain_submit.click(fn=Langchain_cn.knowledge_base_writing,
                                                inputs=[self.langchain_classifi, self.langchain_class_name, self.langchain_links, self.langchain_select, self.langchain_name, self.langchain_know_kwargs],
                                                outputs=[self.langchain_status, self.langchain_error, self.langchain_classifi, self.langchain_select, self.langchain_dropdown, self.langchain_know_kwargs]
                                                )
        submit_id.then(fn=update_drop,
                       inputs=[self.langchain_know_kwargs, self.model_select_dropdown, self.langchain_classifi],
                       outputs=[self.langchain_dropdown, self.chatbot])
        self.langchain_stop.click(fn=lambda: '已暂停构建任务', inputs=None, outputs=[self.langchain_status], cancels=[submit_id])

    def signals_history(self):
        self.historySelectList.input(fn=func_signals.select_history, inputs=[self.historySelectList, self.cookies],
                                      outputs=[self.chatbot, self.history, self.saveFileName, self.cookies])
        self.renameHistoryBtn.click(func_signals.rename_history,
                                    inputs=[self.saveFileName, self.historySelectList],
                                    outputs=[self.historySelectList],
                                    _js='(a,b,c,d)=>{return saveChatHistory(a,b,c,d);}')
        self.historyDeleteBtn.click(func_signals.delete_history, inputs=[gr.State('占位耶'), self.historySelectList],
                                    outputs=[self.historySelectList],
                                    _js='(a,b,c)=>{return showConfirmationDialog(a, b, c);}')
        self.uploadFileBtn.upload(fn=func_signals.import_history, inputs=[self.uploadFileBtn], outputs=[self.historySelectList])
        self.historyRefreshBtn.click(func_signals.refresh_history, inputs=None, outputs=[self.historySelectList])

    def signals_input_setting(self):
        # 注册input
        self.input_combo = [self.cookies, self.max_length_sl, self.default_worker_num, self.model_select_dropdown,
                            self.langchain_dropdown, self.langchain_know_kwargs, self.langchain_classifi,
                            self.vector_search_score, self.vector_search_top_k, self.vector_chunk_size,
                            self.input_copy, self.top_p, self.temperature, self.ocr_identifying_trust, self.chatbot,
                            self.history, self.system_prompt, self.models_box, self.plugin_advanced_arg]
        self.output_combo = [self.cookies, self.chatbot, self.history, self.status_display, self.cancelBtn, self.submitBtn,]
        self.predict_args = dict(fn=ArgsGeneralWrapper(predict), inputs=self.input_combo,
                                 outputs=self.output_combo, show_progress=True)
        self.clear_agrs = dict(fn=self.__clear_input, inputs=[self.user_input], outputs=[self.user_input, self.input_copy,
                                                                                  self.cancelBtn, self.submitBtn])

        # 提交按钮、重置按钮
        submit_handle = self.user_input.submit(**self.clear_agrs).then(**self.predict_args)
        click_handle = self.submitBtn.click(**self.clear_agrs).then(**self.predict_args)
        self.cancel_handles.append(submit_handle)
        self.cancel_handles.append(click_handle)
        self.emptyBtn.click(func_signals.clear_chat_cookie, [self.def_cookies],
                            [self.chatbot, self.history, self.cookies, self.status_display, self.historySelectList, self.saveFileName])

    # gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
    def auto_opentab_delay(self, is_open=False):
        import threading, webbrowser, time
        print(f"如果浏览器没有自动打开，请复制并转到以下URL：")
        print(f"\t（亮色主题）: http://localhost:{PORT}")
        print(f"\t（暗色主题）: {self.__url}/?__theme=dark")
        if is_open:
            def open():
                time.sleep(2)  # 打开浏览器
                webbrowser.open_new_tab(f"http://localhost:{PORT}/?__theme=dark")

            threading.Thread(target=open, name="open-browser", daemon=True).start()
            threading.Thread(target=auto_update, name="self-upgrade", daemon=True).start()
        # threading.Thread(target=warm_up_modules, name="warm-up", daemon=True).start()

    def block_title(self):
        share_cookie = {'api_key': API_KEY, 'llm_model': LLM_MODEL, 'local': self.__url}
        self.cookies = gr.State(share_cookie)
        self.def_cookies = gr.State(share_cookie)
        self.history = gr.State([])
        with gr.Row(elem_id="chuanhu-header"):
            gr.HTML(get_html("header_title.html").format(
                app_title=self.app_name), elem_id="app-title")
            self.status_display = gr.Markdown(func_box.get_geoip(), elem_id="status-display")
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
        with gr.Blocks(title=self.app_name, theme=set_theme) as self.demo:
            self.block_title()
            with gr.Row(equal_height=True, elem_id="chuanhu-body"):
                self.draw_history_area()
                self.draw_chatbot_area()
                self.draw_tools_area()

            with gr.Row(elem_id="popup-wrapper"):
                with gr.Box(elem_id="chuanhu-popup"):
                    self.draw_popup_settings()
                    self.draw_popup_training()
                    self.draw_popup_config()
                    self.draw_popup_fakec()
            # 函数注册，需要在Blocks下进行
            self.signals_history()
            self.signals_input_setting()
            self.signals_sm_btn()
            self.signals_prompt_func()
            self.signals_prompt_edit()
            self.signals_plugin()
            self.signals_langchain_cn()
            # self.demo.load(fn=func_signals.mobile_access, inputs=[],
            #                outputs=[self.sm_btn_column, self.langchain_dropdown])
            self.demo.load(fn=func_signals.refresh_load_data,
                           inputs=[self.pro_fp_state],
                           outputs=[self.pro_func_prompt, self.pro_fp_state, self.pro_private_check,
                                    self.historySelectList, self.chatbot, self.history, self.saveFileName,
                                    self.langchain_classifi, self.langchain_select, self.langchain_dropdown])

        # Start
        self.auto_opentab_delay()
        self.demo.queue(concurrency_count=CONCURRENT_COUNT)
        # 过滤掉不允许用户访问的路径
        self.demo.blocked_paths = func_box.get_files_and_dirs(path=func_box.base_path,
                                                              filter_allow=['private_upload', 'gpt_log', 'docs'])
        login_html = ''
        # self.demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
        #     server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION, auth_message=login_html,
        #     allowed_paths=['private_upload'], ssl_verify=False, share=True,
        #     favicon_path='./docs/wps_logo.png')




from comm_tools import base_api
app = base_api.app
PORT = LOCAL_PORT if WEB_PORT <= 0 else WEB_PORT
reload_javascript()
chatbot_main = ChatBot()
chatbot_main.main()
gradio_app = gr.mount_gradio_app(app, chatbot_main.demo, '/gradio')
if __name__ == '__main__':
    import uvicorn
    app_reload, = get_conf('app_reload')
    uvicorn. run("__main__:app", host="0.0.0.0", port=PORT, reload=app_reload)
