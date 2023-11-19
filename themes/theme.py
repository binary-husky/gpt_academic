import gradio as gr
from toolbox import get_conf
THEME = get_conf('THEME')

def load_dynamic_theme(THEME):
    adjust_dynamic_theme = None
    if THEME == 'Chuanhu-Small-and-Beautiful':
        from .green import adjust_theme, advanced_css
        theme_declaration = "<h2 align=\"center\"  class=\"small\">[Chuanhu-Small-and-Beautiful主题]</h2>"
    elif THEME == 'High-Contrast':
        from .contrast import adjust_theme, advanced_css
        theme_declaration = ""
    elif '/' in THEME:
        from .gradios import adjust_theme, advanced_css
        from .gradios import dynamic_set_theme
        adjust_dynamic_theme = dynamic_set_theme(THEME)
        theme_declaration = ""
    else:
        from .default import adjust_theme, advanced_css
        theme_declaration = ""
    return adjust_theme, advanced_css, theme_declaration, adjust_dynamic_theme

adjust_theme, advanced_css, theme_declaration, _ = load_dynamic_theme(THEME)