import gradio as gr
from toolbox import get_conf
THEME, = get_conf('THEME')

if THEME == 'Green':
    from .green import adjust_theme, advanced_css
else:
    from .default import adjust_theme, advanced_css


