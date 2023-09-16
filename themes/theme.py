import gradio as gr
from toolbox import get_conf
THEME, = get_conf('THEME')

def load_dynamic_theme(THEME):
    if THEME == 'Chuanhu-Small-and-Beautiful':
        from .green import adjust_theme, advanced_css
        theme_declaration = "<h2 align=\"center\"  class=\"small\">[Chuanhu-Small-and-Beautiful主题]</h2>"
    elif THEME == 'High-Contrast':
        from .contrast import adjust_theme, advanced_css
        theme_declaration = ""
    elif '/' in THEME:
        from .gradios import adjust_theme, advanced_css
        theme_declaration = ""
    else:
        from .default import adjust_theme, advanced_css
        theme_declaration = ""
    return adjust_theme, advanced_css, theme_declaration

adjust_theme, advanced_css, theme_declaration = load_dynamic_theme(THEME)