import gradio as gr
import json
from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, DummyWith

def define_gui_advanced_plugin_class(plugins):
    # 定义新一代插件的高级参数区
    with gr.Floating(init_x="50%", init_y="50%", visible=False, width="30%", drag="top", elem_id="plugin_arg_menu"):
        with gr.Accordion("选择插件参数", open=True, elem_id="plugin_arg_panel"):
            for u in range(8):
                with gr.Row():
                    gr.Textbox(show_label=True, label="T1", placeholder="请输入", lines=1, visible=False, elem_id=f"plugin_arg_txt_{u}").style(container=False)
            for u in range(8):
                with gr.Row(): # PLUGIN_ARG_MENU
                    gr.Dropdown(label="T1", value="请选择", choices=[], visible=True, elem_id=f"plugin_arg_drop_{u}", interactive=True)

            with gr.Row():
                # 这个隐藏textbox负责装入当前弹出插件的属性
                gr.Textbox(show_label=False, placeholder="请输入", lines=1, visible=False,
                        elem_id=f"invisible_current_pop_up_plugin_arg").style(container=False)
                usr_confirmed_arg = gr.Textbox(show_label=False, placeholder="请输入", lines=1, visible=False,
                        elem_id=f"invisible_current_pop_up_plugin_arg_final").style(container=False)

                arg_confirm_btn = gr.Button("确认参数并执行", variant="stop")
                arg_confirm_btn.style(size="sm")

                arg_cancel_btn = gr.Button("取消", variant="stop")
                arg_cancel_btn.click(None, None, None, _js="""()=>close_current_pop_up_plugin()""")
                arg_cancel_btn.style(size="sm")

                arg_confirm_btn.click(None, None, None, _js="""()=>execute_current_pop_up_plugin()""")
                invisible_callback_btn_for_plugin_exe = gr.Button(r"未选定任何插件", variant="secondary", visible=False, elem_id="invisible_callback_btn_for_plugin_exe").style(size="sm")
                # 随变按钮的回调函数注册
                def route_switchy_bt_with_arg(request: gr.Request, input_order, *arg):
                    arguments = {k:v for k,v in zip(input_order, arg)}
                    which_plugin = arguments.pop('new_plugin_callback')
                    if which_plugin in [r"未选定任何插件"]: return
                    usr_confirmed_arg = arguments.pop('usr_confirmed_arg')
                    arg_confirm: dict = {}
                    usr_confirmed_arg_dict = json.loads(usr_confirmed_arg)
                    for arg_name in usr_confirmed_arg_dict:
                        arg_confirm.update({arg_name: str(usr_confirmed_arg_dict[arg_name]['user_confirmed_value'])})
                    plugin_obj = plugins[which_plugin]["Class"]
                    arguments['plugin_advanced_arg'] = arg_confirm
                    if arg_confirm.get('main_input', None) is not None:
                        arguments['txt'] = arg_confirm['main_input']
                    yield from ArgsGeneralWrapper(plugin_obj.execute)(request, *arguments.values())
    return invisible_callback_btn_for_plugin_exe, route_switchy_bt_with_arg, usr_confirmed_arg

