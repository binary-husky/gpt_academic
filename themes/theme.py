import gradio as gr
from comm_tools.toolbox import get_conf
THEME, = get_conf('AVAIL_THEMES')

def load_dynamic_theme(THEME):
    adjust_dynamic_theme = None
    if THEME == 'Chuanhu-Small-and-Beautiful':
        theme_declaration = "<h2 align=\"center\"  class=\"small\">[Chuanhu-Small-and-Beautiful主题]</h2>"
    elif THEME == 'High-Contrast':
        theme_declaration = ""
    elif '/' in THEME:
        from .gradios import dynamic_set_theme
        adjust_dynamic_theme = dynamic_set_theme(THEME)
        theme_declaration = ""
    else:
        theme_declaration = ""
    return adjust_theme, advanced_css, theme_declaration, adjust_dynamic_theme

adjust_theme, advanced_css, theme_declaration, _ = load_dynamic_theme(THEME[0])