import os
import json
from init_task import init_task

os.environ['no_proxy'] = '*'  # 避免代理网络产生意外污染

help_menu_description = \
    """
    CopyRight © 2024 [binaryYuki??](https://github.com/binaryYuki) All Rights Reserved.
    </br></br>普通对话使用说明: 1. 输入问题; 2. 点击提交
    </br></br>基础功能区使用说明: 1. 输入文本; 2. 点击任意基础功能区按钮
    </br></br>函数插件区使用说明: 1. 输入路径/问题, 或者上传文件; 2. 点击任意函数插件区按钮
    </br></br>虚空终端使用说明: 点击虚空终端, 然后根据提示输入指令, 再次点击虚空终端
    </br></br>如何保存对话: 点击保存当前的对话按钮
    </br></br>如何语音对话: 请阅读Wiki
    </br></br>如何临时更换API_KEY: 在输入区输入临时API_KEY后提交（网页刷新后失效）"""

from loguru import logger


def enable_log(PATH_LOGGING):
    """
    启用日志记录
    """
    from shared_utils.logging import setup_logging
    setup_logging(PATH_LOGGING)

def encode_plugin_info(k, plugin)->str:
    import copy
    from themes.theme import to_cookie_str
    plugin_ = copy.copy(plugin)
    plugin_.pop("Function", None)
    plugin_.pop("Class", None)
    plugin_.pop("Button", None)
    plugin_["Info"] = plugin.get("Info", k)
    if plugin.get("AdvancedArgs", False):
        plugin_["Label"] = f"插件[{k}]的高级参数说明：" + plugin.get("ArgsReminder", f"没有提供高级参数功能说明")
    else:
        plugin_["Label"] = f"插件[{k}]不需要高级参数。"
    return to_cookie_str(plugin_)

def main():
    import gradio as gr
    # print(f"Gradio Version: {gr.__version__}")
    # if gr.__version__ not in ['3.32.9', '3.32.10', '3.32.11']:
    #     raise ModuleNotFoundError("使用项目内置Gradio获取最优体验! 请运行 `pip install -r requirements.txt` 指令安装内置Gradio及其他依赖, 详情信息见requirements.txt.")

    # 一些基础工具
    from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, \
        DummyWith

    # 对话、日志记录
    enable_log(get_conf("PATH_LOGGING"))

    # 对话句柄
    from request_llms.bridge_all import predict

    # 读取配置
    proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION = get_conf('proxies', 'WEB_PORT', 'LLM_MODEL',
                                                                              'CONCURRENT_COUNT', 'AUTHENTICATION')
    CHATBOT_HEIGHT, LAYOUT, AVAIL_LLM_MODELS, AUTO_CLEAR_TXT = get_conf('CHATBOT_HEIGHT', 'LAYOUT', 'AVAIL_LLM_MODELS',
                                                                        'AUTO_CLEAR_TXT')
    ENABLE_AUDIO, AUTO_CLEAR_TXT, PATH_LOGGING, AVAIL_THEMES, THEME, ADD_WAIFU = get_conf('ENABLE_AUDIO',
                                                                                          'AUTO_CLEAR_TXT',
                                                                                          'PATH_LOGGING',
                                                                                          'AVAIL_THEMES', 'THEME',
                                                                                          'ADD_WAIFU')
    NUM_CUSTOM_BASIC_BTN, SSL_KEYFILE, SSL_CERTFILE = get_conf('NUM_CUSTOM_BASIC_BTN', 'SSL_KEYFILE', 'SSL_CERTFILE')
    DARK_MODE, INIT_SYS_PROMPT, ADD_WAIFU, TTS_TYPE = get_conf('DARK_MODE', 'INIT_SYS_PROMPT', 'ADD_WAIFU', 'TTS_TYPE')
    if LLM_MODEL not in AVAIL_LLM_MODELS: AVAIL_LLM_MODELS += [LLM_MODEL]

    # 如果WEB_PORT是-1, 则随机选取WEB端口
    PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
    from check_proxy import get_current_version
    from themes.theme import adjust_theme, advanced_css, theme_declaration, js_code_clear, js_code_show_or_hide, js_code_show_or_hide_group2
    from themes.theme import js_code_for_toggle_darkmode
    from themes.theme import load_dynamic_theme, to_cookie_str, from_cookie_str, assign_user_uuid
    title_html = f"""
                <h1 align="center">GPT Academic {get_current_version()}</h1>
                <h5 align="center">binaryYuki's Edition</h5>
                {theme_declaration}
                """


    # 一些普通功能模块
    from core_functional import get_core_functions
    functional = get_core_functions()

    # 高级函数插件
    from crazy_functional import get_crazy_functions, get_multiplex_button_functions
    DEFAULT_FN_GROUPS = get_conf('DEFAULT_FN_GROUPS')
    plugins = get_crazy_functions()
    all_plugin_groups = list(set([g for _, plugin in plugins.items() for g in plugin['Group'].split('|')]))
    match_group = lambda tags, groups: any([g in groups for g in tags.split('|')])

    # 处理markdown文本格式的转变
    gr.Chatbot.postprocess = format_io

    # 做一些外观色彩上的调整
    set_theme = adjust_theme()

    # 代理与自动更新
    from check_proxy import check_proxy, auto_update, warm_up_modules
    proxy_info = check_proxy(proxies)

    # 切换布局
    gr_L1 = lambda: gr.Row().style()
    gr_L2 = lambda scale, elem_id: gr.Column(scale=scale, elem_id=elem_id, min_width=400)
    if LAYOUT == "TOP-DOWN":
        gr_L1 = lambda: DummyWith()
        gr_L2 = lambda scale, elem_id: gr.Row()
        CHATBOT_HEIGHT /= 2

    cancel_handles = []
    customize_btns = {}
    predefined_btns = {}
    from shared_utils.cookie_manager import make_cookie_cache, make_history_cache
    with gr.Blocks(title="GPT Academic", theme=set_theme, analytics_enabled=False, css=advanced_css) as app_block:
        gr.HTML(title_html)
        secret_css = gr.Textbox(visible=False, elem_id="secret_css")
        register_advanced_plugin_init_arr = ""

        cookies, web_cookie_cache = make_cookie_cache() # 定义 后端state（cookies）、前端（web_cookie_cache）两兄弟
        with gr_L1():
            with gr_L2(scale=2, elem_id="gpt-chat"):
                chatbot = gr.Chatbot(label=f"当前模型：{LLM_MODEL}", elem_id="gpt-chatbot")
                if LAYOUT == "TOP-DOWN":  chatbot.style(height=CHATBOT_HEIGHT)
                history, _, _ = make_history_cache() # 定义 后端state（history）、前端（history_cache）、后端setter（history_cache_update）三兄弟
            with gr_L2(scale=1, elem_id="gpt-panel"):
                with gr.Accordion("输入区", open=True, elem_id="input-panel") as area_input_primary:
                    with gr.Row():
                        txt = gr.Textbox(show_label=False, placeholder="Input question here.",
                                         elem_id='user_input_main').style(container=False)
                    with gr.Row(elem_id="gpt-submit-row"):
                        multiplex_submit_btn = gr.Button("提交", elem_id="elem_submit_visible", variant="primary")
                        multiplex_sel = gr.Dropdown(
                            choices=get_multiplex_button_functions().keys(), value="常规对话",
                            interactive=True, label='', show_label=False,
                            elem_classes='normal_mut_select', elem_id="gpt-submit-dropdown").style(container=False)
                        submit_btn = gr.Button("提交", elem_id="elem_submit", variant="primary", visible=False)
                    with gr.Row():
                        resetBtn = gr.Button("重置", elem_id="elem_reset", variant="secondary")
                        resetBtn.style(size="sm")
                        stopBtn = gr.Button("停止", elem_id="elem_stop", variant="secondary")
                        stopBtn.style(size="sm")
                        clearBtn = gr.Button("清除", elem_id="elem_clear", variant="secondary", visible=False)
                        clearBtn.style(size="sm")
                    if ENABLE_AUDIO:
                        with gr.Row():
                            audio_mic = gr.Audio(source="microphone", type="numpy", elem_id="elem_audio",
                                                 streaming=True, show_label=False).style(container=False)
                    with gr.Row():
                        status = gr.Markdown(f"Tip: 按Enter提交, 按Shift+Enter换行。支持将文件直接粘贴到输入区。",
                                             elem_id="state-panel")

                with gr.Accordion("基础功能区", open=True, elem_id="basic-panel") as area_basic_fn:
                    with gr.Row():
                        for k in range(NUM_CUSTOM_BASIC_BTN):
                            customize_btn = gr.Button("自定义按钮" + str(k+1), visible=False, variant="secondary", info_str=f'基础功能区: 自定义按钮')
                            customize_btn.style(size="sm")
                            customize_btns.update({"自定义按钮" + str(k+1): customize_btn})
                        for k in functional:
                            if ("Visible" in functional[k]) and (not functional[k]["Visible"]): continue
                            variant = functional[k]["Color"] if "Color" in functional[k] else "secondary"
                            functional[k]["Button"] = gr.Button(k, variant=variant, info_str=f'基础功能区: {k}')
                            functional[k]["Button"].style(size="sm")
                            predefined_btns.update({k: functional[k]["Button"]})
                with gr.Accordion("函数插件区", open=True, elem_id="plugin-panel") as area_crazy_fn:
                    with gr.Row():
                        gr.Markdown("<small>插件可读取“输入区”文本/路径作为参数（上传文件自动修正路径）</small>")
                    with gr.Row(elem_id="input-plugin-group"):
                        plugin_group_sel = gr.Dropdown(choices=all_plugin_groups, label='', show_label=False, value=DEFAULT_FN_GROUPS,
                                                      multiselect=True, interactive=True, elem_classes='normal_mut_select').style(container=False)
                    with gr.Row():
                        for index, (k, plugin) in enumerate(plugins.items()):
                            if not plugin.get("AsButton", True): continue
                            visible = True if match_group(plugin['Group'], DEFAULT_FN_GROUPS) else False
                            variant = plugins[k]["Color"] if "Color" in plugin else "secondary"
                            info = plugins[k].get("Info", k)
                            btn_elem_id = f"plugin_btn_{index}"
                            plugin['Button'] = plugins[k]['Button'] = gr.Button(k, variant=variant,
                                                                                visible=visible,
                                                                                info_str=f'函数插件区: {info}',
                                                                                elem_id=btn_elem_id).style(size="sm")
                            plugin['ButtonElemId'] = btn_elem_id
                    with gr.Row():
                        with gr.Accordion("更多函数插件", open=True):
                            dropdown_fn_list = []
                            for k, plugin in plugins.items():
                                if not match_group(plugin['Group'], DEFAULT_FN_GROUPS): continue
                                if not plugin.get("AsButton", True):
                                    dropdown_fn_list.append(k)  # 排除已经是按钮的插件
                                elif plugin.get('AdvancedArgs', False):
                                    dropdown_fn_list.append(k)  # 对于需要高级参数的插件，亦在下拉菜单中显示
                            with gr.Row():
                                dropdown = gr.Dropdown(dropdown_fn_list, value=r"点击这里输入「关键词」搜索插件",
                                                       label="", show_label=False).style(container=False)
                            with gr.Row():
                                plugin_advanced_arg = gr.Textbox(show_label=True, label="高级参数输入区", visible=False,
                                                                 elem_id="advance_arg_input_legacy",
                                                                 placeholder="这里是特殊函数插件的高级参数输入区").style(
                                    container=False)
                            with gr.Row():
                                switchy_bt = gr.Button(r"请先从插件列表中选择", variant="secondary",
                                                       elem_id="elem_switchy_bt").style(size="sm")
                    with gr.Row():
                        with gr.Accordion("点击展开“文件下载区”。", open=False) as area_file_up:
                            file_upload = gr.Files(label="任何文件, 推荐上传压缩文件(zip, tar)", file_count="multiple",
                                                   elem_id="elem_upload")


        # 左上角工具栏定义
        from themes.gui_toolbar import define_gui_toolbar
        checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature = \
            define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU,
                               help_menu_description, js_code_for_toggle_darkmode)

        # 浮动菜单定义
        from themes.gui_floating_menu import define_gui_floating_menu
        area_input_secondary, txt2, area_customize, _, resetBtn2, clearBtn2, stopBtn2 = \
            define_gui_floating_menu(customize_btns, functional, predefined_btns, cookies, web_cookie_cache)

        # 浮动时间线定义
        gr.Spark()

        # 插件二级菜单的实现
        from themes.gui_advanced_plugin_class import define_gui_advanced_plugin_class
        new_plugin_callback, route_switchy_bt_with_arg, usr_confirmed_arg = \
            define_gui_advanced_plugin_class(plugins)

        # 功能区显示开关与功能区的互动
        def fn_area_visibility(a):
            ret = {}
            ret.update({area_input_primary: gr.update(visible=("浮动输入区" not in a))})
            ret.update({area_input_secondary: gr.update(visible=("浮动输入区" in a))})
            ret.update({plugin_advanced_arg: gr.update(visible=("插件参数区" in a))})
            if "浮动输入区" in a: ret.update({txt: gr.update(value="")})
            return ret

        checkboxes.select(fn_area_visibility, [checkboxes],
                          [area_basic_fn, area_crazy_fn, area_input_primary, area_input_secondary, txt, txt2,
                           plugin_advanced_arg])
        checkboxes.select(None, [checkboxes], None, _js=js_code_show_or_hide)

        # 功能区显示开关与功能区的互动
        def fn_area_visibility_2(a):
            ret = {}
            ret.update({area_customize: gr.update(visible=("自定义菜单" in a))})
            return ret

        checkboxes_2.select(fn_area_visibility_2, [checkboxes_2], [area_customize])
        checkboxes_2.select(None, [checkboxes_2], None, _js=js_code_show_or_hide_group2)

        # 整理反复出现的控件句柄组合
        input_combo = [cookies, max_length_sl, md_dropdown, txt, txt2, top_p, temperature, chatbot, history,
                       system_prompt, plugin_advanced_arg]
        input_combo_order = ["cookies", "max_length_sl", "md_dropdown", "txt", "txt2", "top_p", "temperature",
                             "chatbot", "history", "system_prompt", "plugin_advanced_arg"]
        output_combo = [cookies, chatbot, history, status]
        predict_args = dict(fn=ArgsGeneralWrapper(predict), inputs=[*input_combo, gr.State(True)], outputs=output_combo)

        # 提交按钮、重置按钮
        multiplex_submit_btn.click(
            None, [multiplex_sel], None, _js="""(multiplex_sel)=>multiplex_function_begin(multiplex_sel)""")
        txt.submit(
            None, [multiplex_sel], None, _js="""(multiplex_sel)=>multiplex_function_begin(multiplex_sel)""")
        multiplex_sel.select(
            None, [multiplex_sel], None, _js=f"""(multiplex_sel)=>run_multiplex_shift(multiplex_sel)""")
        cancel_handles.append(submit_btn.click(**predict_args))
        resetBtn.click(None, None, [chatbot, history, status], _js="""(a,b,c)=>clear_conversation(a,b,c)""")   # 先在前端快速清除chatbot&status
        resetBtn2.click(None, None, [chatbot, history, status], _js="""(a,b,c)=>clear_conversation(a,b,c)""")  # 先在前端快速清除chatbot&status
        # reset_server_side_args = (lambda history: ([], [], "已重置"), [history], [chatbot, history, status])
        # resetBtn.click(*reset_server_side_args)    # 再在后端清除history
        # resetBtn2.click(*reset_server_side_args)   # 再在后端清除history
        clearBtn.click(None, None, [txt, txt2], _js=js_code_clear)
        clearBtn2.click(None, None, [txt, txt2], _js=js_code_clear)
        if AUTO_CLEAR_TXT:
            submit_btn.click(None, None, [txt, txt2], _js=js_code_clear)
        # 基础功能区的回调函数注册
        for k in functional:
            if ("Visible" in functional[k]) and (not functional[k]["Visible"]): continue
            click_handle = functional[k]["Button"].click(fn=ArgsGeneralWrapper(predict), inputs=[*input_combo, gr.State(True), gr.State(k)], outputs=output_combo)
            cancel_handles.append(click_handle)
        for btn in customize_btns.values():
            click_handle = btn.click(fn=ArgsGeneralWrapper(predict), inputs=[*input_combo, gr.State(True), gr.State(btn.value)], outputs=output_combo)
            cancel_handles.append(click_handle)
        # 文件上传区，接收文件后与chatbot的互动
        file_upload.upload(on_file_uploaded, [file_upload, chatbot, txt, txt2, checkboxes, cookies], [chatbot, txt, txt2, cookies]).then(None, None, None,   _js=r"()=>{toast_push('上传完毕 ...'); cancel_loading_status();}")
        file_upload_2.upload(on_file_uploaded, [file_upload_2, chatbot, txt, txt2, checkboxes, cookies], [chatbot, txt, txt2, cookies]).then(None, None, None, _js=r"()=>{toast_push('上传完毕 ...'); cancel_loading_status();}")
        # 函数插件-固定按钮区
        for k in plugins:
            register_advanced_plugin_init_arr += f"""register_plugin_init("{k}","{encode_plugin_info(k, plugins[k])}");"""
            if plugins[k].get("Class", None):
                plugins[k]["JsMenu"] = plugins[k]["Class"]().get_js_code_for_generating_menu(k)
                register_advanced_plugin_init_arr += """register_advanced_plugin_init_code("{k}","{gui_js}");""".format(k=k, gui_js=plugins[k]["JsMenu"])
            if not plugins[k].get("AsButton", True): continue
            if plugins[k].get("Class", None) is None:
                assert plugins[k].get("Function", None) is not None
                click_handle = plugins[k]["Button"].click(None, inputs=[], outputs=None, _js=f"""()=>run_classic_plugin_via_id("{plugins[k]["ButtonElemId"]}")""")
            else:
                click_handle = plugins[k]["Button"].click(None, inputs=[], outputs=None, _js=f"""()=>run_advanced_plugin_launch_code("{k}")""")

        # 函数插件-下拉菜单与随变按钮的互动（新版-更流畅）
        dropdown.select(None, [dropdown], None, _js=f"""(dropdown)=>run_dropdown_shift(dropdown)""")

        # 模型切换时的回调
        def on_md_dropdown_changed(k):
            return {chatbot: gr.update(label="当前模型："+k)}
        md_dropdown.select(on_md_dropdown_changed, [md_dropdown], [chatbot])

        # 主题修改
        def on_theme_dropdown_changed(theme, secret_css):
            adjust_theme, css_part1, _, adjust_dynamic_theme = load_dynamic_theme(theme)
            if adjust_dynamic_theme:
                css_part2 = adjust_dynamic_theme._get_theme_css()
            else:
                css_part2 = adjust_theme()._get_theme_css()
            return css_part2 + css_part1
        theme_handle = theme_dropdown.select(on_theme_dropdown_changed, [theme_dropdown, secret_css], [secret_css]) # , _js="""change_theme_prepare""")
        theme_handle.then(None, [theme_dropdown, secret_css], None, _js="""change_theme""")

        switchy_bt.click(None, [switchy_bt], None, _js="(switchy_bt)=>on_flex_button_click(switchy_bt)")

        # 随变按钮的回调函数注册
        def route(request: gr.Request, k, *args, **kwargs):
            if k not in [r"点击这里搜索插件列表", r"请先从插件列表中选择"]:
                if plugins[k].get("Class", None) is None:
                    assert plugins[k].get("Function", None) is not None
                    yield from ArgsGeneralWrapper(plugins[k]["Function"])(request, *args, **kwargs)
        # 旧插件的高级参数区确认按钮（隐藏）
        old_plugin_callback = gr.Button(r"未选定任何插件", variant="secondary", visible=False, elem_id="old_callback_btn_for_plugin_exe")
        click_handle_ng = old_plugin_callback.click(route, [switchy_bt, *input_combo], output_combo)
        click_handle_ng.then(on_report_generated, [cookies, file_upload, chatbot], [cookies, file_upload, chatbot]).then(None, [switchy_bt], None, _js=r"(fn)=>on_plugin_exe_complete(fn)")
        cancel_handles.append(click_handle_ng)
        # 新一代插件的高级参数区确认按钮（隐藏）
        click_handle_ng = new_plugin_callback.click(route_switchy_bt_with_arg,
                                                    [
                                                        gr.State(["new_plugin_callback", "usr_confirmed_arg"] + input_combo_order), # 第一个参数: 指定了后续参数的名称
                                                        new_plugin_callback, usr_confirmed_arg, *input_combo                        # 后续参数: 真正的参数
                                                    ], output_combo)
        click_handle_ng.then(on_report_generated, [cookies, file_upload, chatbot], [cookies, file_upload, chatbot]).then(None, [switchy_bt], None, _js=r"(fn)=>on_plugin_exe_complete(fn)")
        cancel_handles.append(click_handle_ng)
        # 终止按钮的回调函数注册
        stopBtn.click(fn=None, inputs=None, outputs=None, cancels=cancel_handles)
        stopBtn2.click(fn=None, inputs=None, outputs=None, cancels=cancel_handles)
        plugins_as_btn = {name:plugin for name, plugin in plugins.items() if plugin.get('Button', None)}
        def on_group_change(group_list):
            btn_list = []
            fns_list = []
            if not group_list: # 处理特殊情况：没有选择任何插件组
                return [*[plugin['Button'].update(visible=False) for _, plugin in plugins_as_btn.items()], gr.Dropdown.update(choices=[])]
            for k, plugin in plugins.items():
                if plugin.get("AsButton", True):
                    btn_list.append(plugin['Button'].update(visible=match_group(plugin['Group'], group_list))) # 刷新按钮
                    if plugin.get('AdvancedArgs', False): dropdown_fn_list.append(k) # 对于需要高级参数的插件，亦在下拉菜单中显示
                elif match_group(plugin['Group'], group_list): fns_list.append(k) # 刷新下拉列表
            return [*btn_list, gr.Dropdown.update(choices=fns_list)]
        plugin_group_sel.select(fn=on_group_change, inputs=[plugin_group_sel], outputs=[*[plugin['Button'] for name, plugin in plugins_as_btn.items()], dropdown])

        # 是否启动语音输入功能
        if ENABLE_AUDIO:
            from crazy_functions.live_audio.audio_io import RealtimeAudioDistribution
            rad = RealtimeAudioDistribution()
            def deal_audio(audio, cookies):
                rad.feed(cookies['uuid'].hex, audio)
            audio_mic.stream(deal_audio, inputs=[audio_mic, cookies])

        # 生成当前浏览器窗口的uuid（刷新失效）
        app_block.load(assign_user_uuid, inputs=[cookies], outputs=[cookies])

        # 初始化（前端）
        from shared_utils.cookie_manager import load_web_cookie_cache__fn_builder
        load_web_cookie_cache = load_web_cookie_cache__fn_builder(customize_btns, cookies, predefined_btns)
        app_block.load(load_web_cookie_cache, inputs = [web_cookie_cache, cookies],
            outputs = [web_cookie_cache, cookies, *customize_btns.values(), *predefined_btns.values()], _js="""persistent_cookie_init""")
        app_block.load(None, inputs=[], outputs=None, _js=f"""()=>GptAcademicJavaScriptInit("{DARK_MODE}","{INIT_SYS_PROMPT}","{ADD_WAIFU}","{LAYOUT}","{TTS_TYPE}")""")    # 配置暗色主题或亮色主题
        app_block.load(None, inputs=[], outputs=None, _js="""()=>{REP}""".replace("REP", register_advanced_plugin_init_arr))

    # Gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
    def run_delayed_tasks():
        import threading, webbrowser, time
        logger.info(f"如果浏览器没有自动打开，请复制并转到以下URL：")
        if DARK_MODE:   logger.info(f"\t「暗色主题已启用（支持动态切换主题）」: http://localhost:{PORT}")
        else:           logger.info(f"\t「亮色主题已启用（支持动态切换主题）」: http://localhost:{PORT}")

        def auto_updates(): time.sleep(0); auto_update()
        def open_browser(): time.sleep(2); webbrowser.open_new_tab(f"http://localhost:{PORT}")
        def warm_up_mods(): time.sleep(6); warm_up_modules()

        threading.Thread(target=auto_updates, name="self-upgrade", daemon=True).start() # 查看自动更新
        threading.Thread(target=warm_up_mods, name="warm-up",      daemon=True).start() # 预热tiktoken模块
        if get_conf('AUTO_OPEN_BROWSER'):
            threading.Thread(target=open_browser, name="open-browser", daemon=True).start() # 打开浏览器页面

    # 运行一些异步任务：自动更新、打开浏览器页面、预热tiktoken模块
    run_delayed_tasks()

    # 最后，正式开始服务
    from shared_utils.fastapi_server import start_app
    start_app(app_block, CONCURRENT_COUNT, AUTHENTICATION, PORT, SSL_KEYFILE, SSL_CERTFILE)


if __name__ == "__main__":
    init_task()
    main()