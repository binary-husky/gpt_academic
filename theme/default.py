"""
gradio可用颜色列表
gr.themes.utils.colors.slate (石板色)
gr.themes.utils.colors.gray (灰色)
gr.themes.utils.colors.zinc (锌色)
gr.themes.utils.colors.neutral (中性色)
gr.themes.utils.colors.stone (石头色)
gr.themes.utils.colors.red (红色)
gr.themes.utils.colors.orange (橙色)
gr.themes.utils.colors.amber (琥珀色)
gr.themes.utils.colors.yellow (黄色)
gr.themes.utils.colors.lime (酸橙色)
gr.themes.utils.colors.green (绿色)
gr.themes.utils.colors.emerald (祖母绿)
gr.themes.utils.colors.teal (青蓝色)
gr.themes.utils.colors.cyan (青色)
gr.themes.utils.colors.sky (天蓝色)
gr.themes.utils.colors.blue (蓝色)
gr.themes.utils.colors.indigo (靛蓝色)
gr.themes.utils.colors.violet (紫罗兰色)
gr.themes.utils.colors.purple (紫色)
gr.themes.utils.colors.fuchsia (洋红色)
gr.themes.utils.colors.pink (粉红色)
gr.themes.utils.colors.rose (玫瑰色)
"""


import gradio as gr
from toolbox import get_conf
CODE_HIGHLIGHT, ADD_WAIFU = get_conf('CODE_HIGHLIGHT', 'ADD_WAIFU')

def adjust_theme():

    try:
        color_er = gr.themes.utils.colors.fuchsia
        set_theme = gr.themes.Default(
            primary_hue=gr.themes.utils.colors.orange,
            neutral_hue=gr.themes.utils.colors.gray,
            font=["sans-serif", "Microsoft YaHei", "ui-sans-serif", "system-ui"],
            font_mono=["ui-monospace", "Consolas", "monospace", gr.themes.utils.fonts.GoogleFont("IBM Plex Mono")])
        set_theme.set(
            # Colors
            input_background_fill_dark="*neutral_800",
            # Transition
            button_transition="none",
            # Shadows
            button_shadow="*shadow_drop",
            button_shadow_hover="*shadow_drop_lg",
            button_shadow_active="*shadow_inset",
            input_shadow="0 0 0 *shadow_spread transparent, *shadow_inset",
            input_shadow_focus="0 0 0 *shadow_spread *secondary_50, *shadow_inset",
            input_shadow_focus_dark="0 0 0 *shadow_spread *neutral_700, *shadow_inset",
            checkbox_label_shadow="*shadow_drop",
            block_shadow="*shadow_drop",
            form_gap_width="1px",
            # Button borders
            input_border_width="1px",
            input_background_fill="white",
            # Gradients
            stat_background_fill="linear-gradient(to right, *primary_400, *primary_200)",
            stat_background_fill_dark="linear-gradient(to right, *primary_400, *primary_600)",
            error_background_fill=f"linear-gradient(to right, {color_er.c100}, *background_fill_secondary)",
            error_background_fill_dark="*background_fill_primary",
            checkbox_label_background_fill="linear-gradient(to top, *neutral_50, white)",
            checkbox_label_background_fill_dark="linear-gradient(to top, *neutral_900, *neutral_800)",
            checkbox_label_background_fill_hover="linear-gradient(to top, *neutral_100, white)",
            checkbox_label_background_fill_hover_dark="linear-gradient(to top, *neutral_900, *neutral_800)",
            button_primary_background_fill="linear-gradient(to bottom right, *primary_100, *primary_300)",
            button_primary_background_fill_dark="linear-gradient(to bottom right, *primary_500, *primary_600)",
            button_primary_background_fill_hover="linear-gradient(to bottom right, *primary_100, *primary_200)",
            button_primary_background_fill_hover_dark="linear-gradient(to bottom right, *primary_500, *primary_500)",
            button_primary_border_color_dark="*primary_500",
            button_secondary_background_fill="linear-gradient(to bottom right, *neutral_100, *neutral_200)",
            button_secondary_background_fill_dark="linear-gradient(to bottom right, *neutral_600, *neutral_700)",
            button_secondary_background_fill_hover="linear-gradient(to bottom right, *neutral_100, *neutral_100)",
            button_secondary_background_fill_hover_dark="linear-gradient(to bottom right, *neutral_600, *neutral_600)",
            button_cancel_background_fill=f"linear-gradient(to bottom right, {color_er.c100}, {color_er.c200})",
            button_cancel_background_fill_dark=f"linear-gradient(to bottom right, {color_er.c600}, {color_er.c700})",
            button_cancel_background_fill_hover=f"linear-gradient(to bottom right, {color_er.c100}, {color_er.c100})",
            button_cancel_background_fill_hover_dark=f"linear-gradient(to bottom right, {color_er.c600}, {color_er.c600})",
            button_cancel_border_color=color_er.c200,
            button_cancel_border_color_dark=color_er.c600,
            button_cancel_text_color=color_er.c600,
            button_cancel_text_color_dark="white",
        )

        # 添加一个萌萌的看板娘
        if ADD_WAIFU:
            js = """
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

with open("theme/default.css", "r", encoding="utf-8") as f:
    advanced_css = f.read()