import gradio as gr

def define_gui_floating_menu(customize_btns, functional, predefined_btns, cookies, web_cookie_cache):
    with gr.Floating(init_x="20%", init_y="50%", visible=False, width="40%", drag="top", elem_id="f_area_input_secondary") as area_input_secondary:
        with gr.Accordion("浮动输入区", open=True, elem_id="input-panel2"):
            with gr.Row() as row:
                row.style(equal_height=True)
                with gr.Column(scale=10):
                    txt2 = gr.Textbox(show_label=False, placeholder="Input question here.",
                                    elem_id='user_input_float', lines=8, label="输入区2").style(container=False)
                    txt2.submit(None, None, None, _js="""click_real_submit_btn""")
                with gr.Column(scale=1, min_width=40):
                    submitBtn2 = gr.Button("提交", variant="primary"); submitBtn2.style(size="sm")
                    submitBtn2.click(None, None, None, _js="""click_real_submit_btn""")
                    resetBtn2 = gr.Button("重置", variant="secondary"); resetBtn2.style(size="sm")
                    stopBtn2 = gr.Button("停止", variant="secondary"); stopBtn2.style(size="sm")
                    clearBtn2 = gr.Button("清除", elem_id="elem_clear2", variant="secondary", visible=False); clearBtn2.style(size="sm")


    with gr.Floating(init_x="20%", init_y="50%", visible=False, width="40%", drag="top", elem_id="f_area_customize") as area_customize:
        with gr.Accordion("自定义菜单", open=True, elem_id="edit-panel"):
            with gr.Row() as row:
                with gr.Column(scale=10):
                    AVAIL_BTN = [btn for btn in customize_btns.keys()] + [k for k in functional]
                    basic_btn_dropdown = gr.Dropdown(AVAIL_BTN, value="自定义按钮1", label="选择一个需要自定义基础功能区按钮").style(container=False)
                    basic_fn_title = gr.Textbox(show_label=False, placeholder="输入新按钮名称", lines=1).style(container=False)
                    basic_fn_prefix = gr.Textbox(show_label=False, placeholder="输入新提示前缀", lines=4).style(container=False)
                    basic_fn_suffix = gr.Textbox(show_label=False, placeholder="输入新提示后缀", lines=4).style(container=False)
                with gr.Column(scale=1, min_width=70):
                    basic_fn_confirm = gr.Button("确认并保存", variant="primary"); basic_fn_confirm.style(size="sm")
                    basic_fn_clean   = gr.Button("恢复默认", variant="primary"); basic_fn_clean.style(size="sm")

                    from shared_utils.cookie_manager import assign_btn__fn_builder
                    assign_btn = assign_btn__fn_builder(customize_btns, predefined_btns, cookies, web_cookie_cache)
                    # update btn
                    h = basic_fn_confirm.click(assign_btn, [web_cookie_cache, cookies, basic_btn_dropdown, basic_fn_title, basic_fn_prefix, basic_fn_suffix],
                                            [web_cookie_cache, cookies, *customize_btns.values(), *predefined_btns.values()])
                    h.then(None, [web_cookie_cache], None, _js="""(web_cookie_cache)=>{localStorage.setItem("web_cookie_cache", web_cookie_cache);}""")
                    # clean up btn
                    h2 = basic_fn_clean.click(assign_btn, [web_cookie_cache, cookies, basic_btn_dropdown, basic_fn_title, basic_fn_prefix, basic_fn_suffix, gr.State(True)],
                                            [web_cookie_cache, cookies, *customize_btns.values(), *predefined_btns.values()])
                    h2.then(None, [web_cookie_cache], None, _js="""(web_cookie_cache)=>{localStorage.setItem("web_cookie_cache", web_cookie_cache);}""")
    return area_input_secondary, txt2, area_customize, submitBtn2, resetBtn2, clearBtn2, stopBtn2