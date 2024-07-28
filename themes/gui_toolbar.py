import gradio as gr

def define_gui_toolbar(AVAIL_LLM_MODELS, LLM_MODEL, INIT_SYS_PROMPT, THEME, AVAIL_THEMES, ADD_WAIFU, help_menu_description, js_code_for_toggle_darkmode):
    with gr.Floating(init_x="0%", init_y="0%", visible=True, width=None, drag="forbidden", elem_id="tooltip"):
        with gr.Row():
            with gr.Tab("上传文件", elem_id="interact-panel"):
                gr.Markdown("请上传本地文件/压缩包供“函数插件区”功能调用。请注意: 上传文件后会自动把输入区修改为相应路径。")
                file_upload_2 = gr.Files(label="任何文件, 推荐上传压缩文件(zip, tar)", file_count="multiple", elem_id="elem_upload_float")

            with gr.Tab("更换模型", elem_id="interact-panel"):
                md_dropdown = gr.Dropdown(AVAIL_LLM_MODELS, value=LLM_MODEL, elem_id="elem_model_sel", label="更换LLM模型/请求源").style(container=False)
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.01,interactive=True, label="Top-p (nucleus sampling)",)
                temperature = gr.Slider(minimum=-0, maximum=2.0, value=1.0, step=0.01, interactive=True, label="Temperature", elem_id="elem_temperature")
                max_length_sl = gr.Slider(minimum=256, maximum=1024*32, value=4096, step=128, interactive=True, label="Local LLM MaxLength",)
                system_prompt = gr.Textbox(show_label=True, lines=2, placeholder=f"System Prompt", label="System prompt", value=INIT_SYS_PROMPT, elem_id="elem_prompt")
                temperature.change(None, inputs=[temperature], outputs=None,
                    _js="""(temperature)=>gpt_academic_gradio_saveload("save", "elem_prompt", "js_temperature_cookie", temperature)""")
                system_prompt.change(None, inputs=[system_prompt], outputs=None,
                    _js="""(system_prompt)=>gpt_academic_gradio_saveload("save", "elem_prompt", "js_system_prompt_cookie", system_prompt)""")
                md_dropdown.change(None, inputs=[md_dropdown], outputs=None,
                    _js="""(md_dropdown)=>gpt_academic_gradio_saveload("save", "elem_model_sel", "js_md_dropdown_cookie", md_dropdown)""")

            with gr.Tab("界面外观", elem_id="interact-panel"):
                theme_dropdown = gr.Dropdown(AVAIL_THEMES, value=THEME, label="更换UI主题").style(container=False)
                checkboxes = gr.CheckboxGroup(["基础功能区", "函数插件区", "浮动输入区", "输入清除键", "插件参数区"], value=["基础功能区", "函数插件区"], label="显示/隐藏功能区", elem_id='cbs').style(container=False)
                opt = ["自定义菜单"]
                value=[]
                if ADD_WAIFU: opt += ["添加Live2D形象"]; value += ["添加Live2D形象"]
                checkboxes_2 = gr.CheckboxGroup(opt, value=value, label="显示/隐藏自定义菜单", elem_id='cbsc').style(container=False)
                dark_mode_btn = gr.Button("切换界面明暗 ☀", variant="secondary").style(size="sm")
                dark_mode_btn.click(None, None, None, _js=js_code_for_toggle_darkmode)
                open_new_tab = gr.Button("打开新对话", variant="secondary").style(size="sm")
                open_new_tab.click(None, None, None, _js=f"""()=>duplicate_in_new_window()""")


            with gr.Tab("帮助", elem_id="interact-panel"):
                gr.Markdown(help_menu_description)
    return checkboxes, checkboxes_2, max_length_sl, theme_dropdown, system_prompt, file_upload_2, md_dropdown, top_p, temperature