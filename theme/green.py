import gradio as gr
from toolbox import get_conf
CODE_HIGHLIGHT, ADD_WAIFU = get_conf('CODE_HIGHLIGHT', 'ADD_WAIFU')

def adjust_theme():
    try:
        set_theme = gr.themes.Soft(
            primary_hue=gr.themes.Color(
                c50="#EBFAF2",
                c100="#CFF3E1",
                c200="#A8EAC8",
                c300="#77DEA9",
                c400="#3FD086",
                c500="#02C160",
                c600="#06AE56",
                c700="#05974E",
                c800="#057F45",
                c900="#04673D",
                c950="#2E5541",
                name="small_and_beautiful",
            ),
            secondary_hue=gr.themes.Color(
                c50="#576b95",
                c100="#576b95",
                c200="#576b95",
                c300="#576b95",
                c400="#576b95",
                c500="#576b95",
                c600="#576b95",
                c700="#576b95",
                c800="#576b95",
                c900="#576b95",
                c950="#576b95",
            ),
            neutral_hue=gr.themes.Color(
                name="gray",
                c50="#f6f7f8",
                # c100="#f3f4f6",
                c100="#F2F2F2",
                c200="#e5e7eb",
                c300="#d1d5db",
                c400="#B2B2B2",
                c500="#808080",
                c600="#636363",
                c700="#515151",
                c800="#393939",
                # c900="#272727",
                c900="#2B2B2B",
                c950="#171717",
            ),

            radius_size=gr.themes.sizes.radius_sm,
        ).set(
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_dark="*primary_600",
            button_primary_background_fill_hover="*primary_400",
            button_primary_border_color="*primary_500",
            button_primary_border_color_dark="*primary_600",
            button_primary_text_color="wihte",
            button_primary_text_color_dark="white",
            button_secondary_background_fill="*neutral_100",
            button_secondary_background_fill_hover="*neutral_50",
            button_secondary_background_fill_dark="*neutral_900",
            button_secondary_text_color="*neutral_800",
            button_secondary_text_color_dark="white",
            background_fill_primary="#F7F7F7",
            background_fill_primary_dark="#1F1F1F",
            block_title_text_color="*primary_500",
            block_title_background_fill_dark="*primary_900",
            block_label_background_fill_dark="*primary_900",
            input_background_fill="#F6F6F6",
            chatbot_code_background_color="*neutral_950",
            chatbot_code_background_color_dark="*neutral_950",
        )
        js = ''
        # 添加一个萌萌的看板娘
        if ADD_WAIFU:
            js += """
                <script src="file=docs/waifu_plugin/jquery.min.js"></script>
                <script src="file=docs/waifu_plugin/jquery-ui.min.js"></script>
                <script src="file=docs/waifu_plugin/autoload.js"></script>
            """
        gradio_original_template_fn = gr.routes.templates.TemplateResponse
        def gradio_new_template_fn(*args, **kwargs):
            res = gradio_original_template_fn(*args, **kwargs)
            res.body = res.body.replace(b'</html>', f'{js}</html>'.encode("utf8"))
            res.init_headers()
            return res
        gr.routes.templates.TemplateResponse = gradio_new_template_fn   # override gradio template
    except:
        set_theme = None
        print('gradio版本较旧, 不能自定义字体和颜色')
    return set_theme


with open("theme/green.css", "r", encoding="utf-8") as f:
    advanced_css = f.read()
