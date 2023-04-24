import gradio as gr
from toolbox import get_conf
CODE_HIGHLIGHT, = get_conf('CODE_HIGHLIGHT')
# gradio可用颜色列表
# gr.themes.utils.colors.slate (石板色)
# gr.themes.utils.colors.gray (灰色)
# gr.themes.utils.colors.zinc (锌色)
# gr.themes.utils.colors.neutral (中性色)
# gr.themes.utils.colors.stone (石头色)
# gr.themes.utils.colors.red (红色)
# gr.themes.utils.colors.orange (橙色)
# gr.themes.utils.colors.amber (琥珀色)
# gr.themes.utils.colors.yellow (黄色)
# gr.themes.utils.colors.lime (酸橙色)
# gr.themes.utils.colors.green (绿色)
# gr.themes.utils.colors.emerald (祖母绿)
# gr.themes.utils.colors.teal (青蓝色)
# gr.themes.utils.colors.cyan (青色)
# gr.themes.utils.colors.sky (天蓝色)
# gr.themes.utils.colors.blue (蓝色)
# gr.themes.utils.colors.indigo (靛蓝色)
# gr.themes.utils.colors.violet (紫罗兰色)
# gr.themes.utils.colors.purple (紫色)
# gr.themes.utils.colors.fuchsia (洋红色)
# gr.themes.utils.colors.pink (粉红色)
# gr.themes.utils.colors.rose (玫瑰色)


def adjust_theme():
    try:
        color_er = gr.themes.utils.colors.fuchsia
        set_theme = gr.themes.Default(
            primary_hue=gr.themes.utils.colors.orange,
            neutral_hue=gr.themes.utils.colors.gray,
            font=["sans-serif", "Microsoft YaHei", "ui-sans-serif", "system-ui",
                  "sans-serif", gr.themes.utils.fonts.GoogleFont("Source Sans Pro")],
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
    except:
        set_theme = None
        print('gradio版本较旧, 不能自定义字体和颜色')
    return set_theme


advanced_css = """
/* 设置表格的外边距为1em，内部单元格之间边框合并，空单元格显示. */
.markdown-body table {
    margin: 1em 0;
    border-collapse: collapse;
    empty-cells: show;
}

/* 设置表格单元格的内边距为5px，边框粗细为1.2px，颜色为--border-color-primary. */
.markdown-body th, .markdown-body td {
    border: 1.2px solid var(--border-color-primary);
    padding: 5px;
}

/* 设置表头背景颜色为rgba(175,184,193,0.2)，透明度为0.2. */
.markdown-body thead {
    background-color: rgba(175,184,193,0.2);
}

/* 设置表头单元格的内边距为0.5em和0.2em. */
.markdown-body thead th {
    padding: .5em .2em;
}

/* 去掉列表前缀的默认间距，使其与文本线对齐. */
.markdown-body ol, .markdown-body ul {
    padding-inline-start: 2em !important;
}

/* 设定聊天气泡的样式，包括圆角、最大宽度和阴影等. */
[class *= "message"] {
    border-radius: var(--radius-xl) !important;
    /* padding: var(--spacing-xl) !important; */
    /* font-size: var(--text-md) !important; */
    /* line-height: var(--line-md) !important; */
    /* min-height: calc(var(--text-md)*var(--line-md) + 2*var(--spacing-xl)); */
    /* min-width: calc(var(--text-md)*var(--line-md) + 2*var(--spacing-xl)); */
}
[data-testid = "bot"] {
    max-width: 95%;
    /* width: auto !important; */
    border-bottom-left-radius: 0 !important;
}
[data-testid = "user"] {
    max-width: 100%;
    /* width: auto !important; */
    border-bottom-right-radius: 0 !important;
}

/* 行内代码的背景设为淡灰色，设定圆角和间距. */
.markdown-body code {
    display: inline;
    white-space: break-spaces;
    border-radius: 6px;
    margin: 0 2px 0 2px;
    padding: .2em .4em .1em .4em;
    background-color: rgba(13, 17, 23, 0.95);
}

.dark .markdown-body code {
    display: inline;
    white-space: break-spaces;
    border-radius: 6px;
    margin: 0 2px 0 2px;
    padding: .2em .4em .1em .4em;
    background-color: rgba(175,184,193,0.2);
}

/* 设定代码块的样式，包括背景颜色、内、外边距、圆角。 */
.markdown-body pre code {
    display: block;
    overflow: auto;
    white-space: pre;
    background-color: rgba(13, 17, 23, 0.95);
    border-radius: 10px;
    padding: 1em;
    margin: 1em 2em 1em 0.5em;
}

.dark .markdown-body pre code {
    display: block;
    overflow: auto;
    white-space: pre;
    background-color: rgba(175,184,193,0.2);
    border-radius: 10px;
    padding: 1em;
    margin: 1em 2em 1em 0.5em;
}

"""

if CODE_HIGHLIGHT:
    advanced_css += """

.codehilite .hll { background-color: #6e7681 }
.codehilite .c { color: #8b949e; font-style: italic } /* Comment */
.codehilite .err { color: #f85149 } /* Error */
.codehilite .esc { color: #c9d1d9 } /* Escape */
.codehilite .g { color: #c9d1d9 } /* Generic */
.codehilite .k { color: #ff7b72 } /* Keyword */
.codehilite .l { color: #a5d6ff } /* Literal */
.codehilite .n { color: #c9d1d9 } /* Name */
.codehilite .o { color: #ff7b72; font-weight: bold } /* Operator */
.codehilite .x { color: #c9d1d9 } /* Other */
.codehilite .p { color: #c9d1d9 } /* Punctuation */
.codehilite .ch { color: #8b949e; font-style: italic } /* Comment.Hashbang */
.codehilite .cm { color: #8b949e; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #8b949e; font-weight: bold; font-style: italic } /* Comment.Preproc */
.codehilite .cpf { color: #8b949e; font-style: italic } /* Comment.PreprocFile */
.codehilite .c1 { color: #8b949e; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #8b949e; font-weight: bold; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #ffa198; background-color: #490202 } /* Generic.Deleted */
.codehilite .ge { color: #c9d1d9; font-style: italic } /* Generic.Emph */
.codehilite .gr { color: #ffa198 } /* Generic.Error */
.codehilite .gh { color: #79c0ff; font-weight: bold } /* Generic.Heading */
.codehilite .gi { color: #56d364; background-color: #0f5323 } /* Generic.Inserted */
.codehilite .go { color: #8b949e } /* Generic.Output */
.codehilite .gp { color: #8b949e } /* Generic.Prompt */
.codehilite .gs { color: #c9d1d9; font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #79c0ff } /* Generic.Subheading */
.codehilite .gt { color: #ff7b72 } /* Generic.Traceback */
.codehilite .g-Underline { color: #c9d1d9; text-decoration: underline } /* Generic.Underline */
.codehilite .kc { color: #79c0ff } /* Keyword.Constant */
.codehilite .kd { color: #ff7b72 } /* Keyword.Declaration */
.codehilite .kn { color: #ff7b72 } /* Keyword.Namespace */
.codehilite .kp { color: #79c0ff } /* Keyword.Pseudo */
.codehilite .kr { color: #ff7b72 } /* Keyword.Reserved */
.codehilite .kt { color: #ff7b72 } /* Keyword.Type */
.codehilite .ld { color: #79c0ff } /* Literal.Date */
.codehilite .m { color: #a5d6ff } /* Literal.Number */
.codehilite .s { color: #a5d6ff } /* Literal.String */
.codehilite .na { color: #c9d1d9 } /* Name.Attribute */
.codehilite .nb { color: #c9d1d9 } /* Name.Builtin */
.codehilite .nc { color: #f0883e; font-weight: bold } /* Name.Class */
.codehilite .no { color: #79c0ff; font-weight: bold } /* Name.Constant */
.codehilite .nd { color: #d2a8ff; font-weight: bold } /* Name.Decorator */
.codehilite .ni { color: #ffa657 } /* Name.Entity */
.codehilite .ne { color: #f0883e; font-weight: bold } /* Name.Exception */
.codehilite .nf { color: #d2a8ff; font-weight: bold } /* Name.Function */
.codehilite .nl { color: #79c0ff; font-weight: bold } /* Name.Label */
.codehilite .nn { color: #ff7b72 } /* Name.Namespace */
.codehilite .nx { color: #c9d1d9 } /* Name.Other */
.codehilite .py { color: #79c0ff } /* Name.Property */
.codehilite .nt { color: #7ee787 } /* Name.Tag */
.codehilite .nv { color: #79c0ff } /* Name.Variable */
.codehilite .ow { color: #ff7b72; font-weight: bold } /* Operator.Word */
.codehilite .pm { color: #c9d1d9 } /* Punctuation.Marker */
.codehilite .w { color: #6e7681 } /* Text.Whitespace */
.codehilite .mb { color: #a5d6ff } /* Literal.Number.Bin */
.codehilite .mf { color: #a5d6ff } /* Literal.Number.Float */
.codehilite .mh { color: #a5d6ff } /* Literal.Number.Hex */
.codehilite .mi { color: #a5d6ff } /* Literal.Number.Integer */
.codehilite .mo { color: #a5d6ff } /* Literal.Number.Oct */
.codehilite .sa { color: #79c0ff } /* Literal.String.Affix */
.codehilite .sb { color: #a5d6ff } /* Literal.String.Backtick */
.codehilite .sc { color: #a5d6ff } /* Literal.String.Char */
.codehilite .dl { color: #79c0ff } /* Literal.String.Delimiter */
.codehilite .sd { color: #a5d6ff } /* Literal.String.Doc */
.codehilite .s2 { color: #a5d6ff } /* Literal.String.Double */
.codehilite .se { color: #79c0ff } /* Literal.String.Escape */
.codehilite .sh { color: #79c0ff } /* Literal.String.Heredoc */
.codehilite .si { color: #a5d6ff } /* Literal.String.Interpol */
.codehilite .sx { color: #a5d6ff } /* Literal.String.Other */
.codehilite .sr { color: #79c0ff } /* Literal.String.Regex */
.codehilite .s1 { color: #a5d6ff } /* Literal.String.Single */
.codehilite .ss { color: #a5d6ff } /* Literal.String.Symbol */
.codehilite .bp { color: #c9d1d9 } /* Name.Builtin.Pseudo */
.codehilite .fm { color: #d2a8ff; font-weight: bold } /* Name.Function.Magic */
.codehilite .vc { color: #79c0ff } /* Name.Variable.Class */
.codehilite .vg { color: #79c0ff } /* Name.Variable.Global */
.codehilite .vi { color: #79c0ff } /* Name.Variable.Instance */
.codehilite .vm { color: #79c0ff } /* Name.Variable.Magic */
.codehilite .il { color: #a5d6ff } /* Literal.Number.Integer.Long */

.dark .codehilite .hll { background-color: #2C3B41 }
.dark .codehilite .c { color: #79d618; font-style: italic } /* Comment */
.dark .codehilite .err { color: #FF5370 } /* Error */
.dark .codehilite .esc { color: #89DDFF } /* Escape */
.dark .codehilite .g { color: #EEFFFF } /* Generic */
.dark .codehilite .k { color: #BB80B3 } /* Keyword */
.dark .codehilite .l { color: #C3E88D } /* Literal */
.dark .codehilite .n { color: #EEFFFF } /* Name */
.dark .codehilite .o { color: #89DDFF } /* Operator */
.dark .codehilite .p { color: #89DDFF } /* Punctuation */
.dark .codehilite .ch { color: #79d618; font-style: italic } /* Comment.Hashbang */
.dark .codehilite .cm { color: #79d618; font-style: italic } /* Comment.Multiline */
.dark .codehilite .cp { color: #79d618; font-style: italic } /* Comment.Preproc */
.dark .codehilite .cpf { color: #79d618; font-style: italic } /* Comment.PreprocFile */
.dark .codehilite .c1 { color: #79d618; font-style: italic } /* Comment.Single */
.dark .codehilite .cs { color: #79d618; font-style: italic } /* Comment.Special */
.dark .codehilite .gd { color: #FF5370 } /* Generic.Deleted */
.dark .codehilite .ge { color: #89DDFF } /* Generic.Emph */
.dark .codehilite .gr { color: #FF5370 } /* Generic.Error */
.dark .codehilite .gh { color: #C3E88D } /* Generic.Heading */
.dark .codehilite .gi { color: #C3E88D } /* Generic.Inserted */
.dark .codehilite .go { color: #79d618 } /* Generic.Output */
.dark .codehilite .gp { color: #FFCB6B } /* Generic.Prompt */
.dark .codehilite .gs { color: #FF5370 } /* Generic.Strong */
.dark .codehilite .gu { color: #89DDFF } /* Generic.Subheading */
.dark .codehilite .gt { color: #FF5370 } /* Generic.Traceback */
.dark .codehilite .kc { color: #89DDFF } /* Keyword.Constant */
.dark .codehilite .kd { color: #BB80B3 } /* Keyword.Declaration */
.dark .codehilite .kn { color: #89DDFF; font-style: italic } /* Keyword.Namespace */
.dark .codehilite .kp { color: #89DDFF } /* Keyword.Pseudo */
.dark .codehilite .kr { color: #BB80B3 } /* Keyword.Reserved */
.dark .codehilite .kt { color: #BB80B3 } /* Keyword.Type */
.dark .codehilite .ld { color: #C3E88D } /* Literal.Date */
.dark .codehilite .m { color: #F78C6C } /* Literal.Number */
.dark .codehilite .s { color: #C3E88D } /* Literal.String */
.dark .codehilite .na { color: #BB80B3 } /* Name.Attribute */
.dark .codehilite .nb { color: #82AAFF } /* Name.Builtin */
.dark .codehilite .nc { color: #FFCB6B } /* Name.Class */
.dark .codehilite .no { color: #EEFFFF } /* Name.Constant */
.dark .codehilite .nd { color: #82AAFF } /* Name.Decorator */
.dark .codehilite .ni { color: #89DDFF } /* Name.Entity */
.dark .codehilite .ne { color: #FFCB6B } /* Name.Exception */
.dark .codehilite .nf { color: #82AAFF } /* Name.Function */
.dark .codehilite .nl { color: #82AAFF } /* Name.Label */
.dark .codehilite .nn { color: #FFCB6B } /* Name.Namespace */
.dark .codehilite .nx { color: #EEFFFF } /* Name.Other */
.dark .codehilite .py { color: #FFCB6B } /* Name.Property */
.dark .codehilite .nt { color: #FF5370 } /* Name.Tag */
.dark .codehilite .nv { color: #89DDFF } /* Name.Variable */
.dark .codehilite .ow { color: #89DDFF; font-style: italic } /* Operator.Word */
.dark .codehilite .pm { color: #89DDFF } /* Punctuation.Marker */
.dark .codehilite .w { color: #EEFFFF } /* Text.Whitespace */
.dark .codehilite .mb { color: #F78C6C } /* Literal.Number.Bin */
.dark .codehilite .mf { color: #F78C6C } /* Literal.Number.Float */
.dark .codehilite .mh { color: #F78C6C } /* Literal.Number.Hex */
.dark .codehilite .mi { color: #F78C6C } /* Literal.Number.Integer */
.dark .codehilite .mo { color: #F78C6C } /* Literal.Number.Oct */
.dark .codehilite .sa { color: #BB80B3 } /* Literal.String.Affix */
.dark .codehilite .sb { color: #C3E88D } /* Literal.String.Backtick */
.dark .codehilite .sc { color: #C3E88D } /* Literal.String.Char */
.dark .codehilite .dl { color: #EEFFFF } /* Literal.String.Delimiter */
.dark .codehilite .sd { color: #79d618; font-style: italic } /* Literal.String.Doc */
.dark .codehilite .s2 { color: #C3E88D } /* Literal.String.Double */
.dark .codehilite .se { color: #EEFFFF } /* Literal.String.Escape */
.dark .codehilite .sh { color: #C3E88D } /* Literal.String.Heredoc */
.dark .codehilite .si { color: #89DDFF } /* Literal.String.Interpol */
.dark .codehilite .sx { color: #C3E88D } /* Literal.String.Other */
.dark .codehilite .sr { color: #89DDFF } /* Literal.String.Regex */
.dark .codehilite .s1 { color: #C3E88D } /* Literal.String.Single */
.dark .codehilite .ss { color: #89DDFF } /* Literal.String.Symbol */
.dark .codehilite .bp { color: #89DDFF } /* Name.Builtin.Pseudo */
.dark .codehilite .fm { color: #82AAFF } /* Name.Function.Magic */
.dark .codehilite .vc { color: #89DDFF } /* Name.Variable.Class */
.dark .codehilite .vg { color: #89DDFF } /* Name.Variable.Global */
.dark .codehilite .vi { color: #89DDFF } /* Name.Variable.Instance */
.dark .codehilite .vm { color: #82AAFF } /* Name.Variable.Magic */
.dark .codehilite .il { color: #F78C6C } /* Literal.Number.Integer.Long */

"""
