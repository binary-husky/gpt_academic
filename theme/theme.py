import gradio as gr
from toolbox import get_conf
THEME, = get_conf('THEME')

if THEME == 'Chuanhu-Small-and-Beautiful':
    from .green import adjust_theme, advanced_css
    theme_declaration = "\t" + "<smaller>[Chuanhu-Small-and-Beautiful主题]</smaller>"
else:
    from .default import adjust_theme, advanced_css
    theme_declaration = ""


