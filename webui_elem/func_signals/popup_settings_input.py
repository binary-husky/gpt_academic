# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *

# 处理latex options
latex_delimiters_dict = {
    'default': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ],
    'strict': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ],
    'all': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
        {"left": "\\begin{equation}", "right": "\\end{equation}", "display": True},
        {"left": "\\begin{align}", "right": "\\end{align}", "display": True},
        {"left": "\\begin{alignat}", "right": "\\end{alignat}", "display": True},
        {"left": "\\begin{gather}", "right": "\\end{gather}", "display": True},
        {"left": "\\begin{CD}", "right": "\\end{CD}", "display": True},
    ],
    'disabled': []
}


def spinner_chatbot_loading(chatbot):
    loading = [''.join(['.' * random.randint(1, 5)])]
    # 将元组转换为列表并修改元素
    loading_msg = copy.deepcopy(chatbot)
    temp_list = list(loading_msg[-1])

    temp_list[1] = pattern_html(temp_list[1]) + f'{random.choice(loading)}'
    # 将列表转换回元组并替换原始元组
    loading_msg[-1] = tuple(temp_list)
    return loading_msg


def filter_database_tables():
    tables = PromptDb(None).get_tables()
    split_tab = []
    for t in tables:
        if str(t).endswith('_sys'):
            split_tab.append(get_database_cls(t))
    split_tab_new = split_tab
    return split_tab_new


def on_theme_dropdown_changed(theme, ):
    from webui_elem.theme import load_dynamic_theme
    adjust_theme, adjust_dynamic_theme = load_dynamic_theme(theme)
    if adjust_dynamic_theme:
        try:
            css_part2 = adjust_dynamic_theme._get_theme_css()
        except:
            raise
    else:
        css_part2 = adjust_theme._get_theme_css()
    return css_part2, gr.update()


def switch_latex_output(select):
    if select not in list(latex_delimiters_dict):
        latex = latex_delimiters_dict['else']
    else:
        latex = latex_delimiters_dict[select]
    return gr.update(latex_delimiters=latex)
