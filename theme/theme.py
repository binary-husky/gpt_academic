import gradio as gr
from toolbox import get_conf
THEME, = get_conf('THEME')

if THEME == 'Chuanhu-Keldos-Green':
    from .green import adjust_theme, advanced_css
    theme_declaration = "\t" + "[Chuanhu-Keldos暗绿主题]"
else:
    from .default import adjust_theme, advanced_css
    theme_declaration = ""


