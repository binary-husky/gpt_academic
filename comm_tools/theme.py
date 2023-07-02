import os.path
from comm_tools import func_box
import gradio as gr
from comm_tools.toolbox import get_conf
CODE_HIGHLIGHT, ADD_WAIFU, ADD_CHUANHU = get_conf('CODE_HIGHLIGHT', 'ADD_WAIFU', 'ADD_CHUANHU')
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
        if ADD_CHUANHU:
            with open(os.path.join(func_box.base_path, "docs/assets/custom.js"), "r", encoding="utf-8") as f, \
                    open(os.path.join(func_box.base_path, "docs/assets/external-scripts.js"), "r", encoding="utf-8") as f1:
                customJS = f.read()
                externalScripts = f1.read()
            js += f'<script>{customJS}</script><script async>{externalScripts}</script>'
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


with open(os.path.join(func_box.base_path, 'docs/assets/custom.css'), "r", encoding="utf-8") as f:
    customCSS = f.read()
custom_css = customCSS
advanced_css = """
#debug_mes {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    z-index: 1; /* 设置更高的 z-index 值 */
    margin-bottom: 10px !important;
}
#chat_txt {
    display: flex;
    flex-direction: column-reverse;
    overflow-y: auto !important;
    z-index: 3;
    flex-grow: 1; /* 自动填充剩余空间 */
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    margin-bottom: 35px !important;
}
#sm_btn {
    display: flex;
    flex-wrap: unset !important; 
    gap: 5px !important;
    width: var(--size-full);
}
textarea {
    resize: none;
    height: 100%; /* 填充父元素的高度 */
}
#main_chatbot {
    height: 75vh !important;
    max-height: 75vh !important;
    /* overflow: auto !important; */
    z-index: 2;
}
#prompt_result{
    height: 60vh !important;
    max-height: 60vh !important;
}
.wrap.svelte-18telvq.svelte-18telvq {
    padding: var(--block-padding) !important;
    height: 100% !important;
    max-height: 95% !important;
    overflow-y: auto !important;
}
.app.svelte-1mya07g.svelte-1mya07g {
    max-width: 100%;
    position: relative;
    /* margin: auto; */
    padding: var(--size-4);
    width: 100%;
    height: 100%;
}
.md-message table {
    margin: 1em 0;
    border-collapse: collapse;
    empty-cells: show;
}

.md-message th, .md-message td {
    border: 1.2px solid var(--border-color-primary);
    padding: 5px;
}

.md-message thead {
    background-color: rgba(175,184,193,0.2);
}

.md-message thead th {
    padding: .5em .2em;
}

.md-message ol, .md-message ul {
    padding-inline-start: 2em !important;
}

/* chat box. */
[class *= "message"] {
    gap: 7px !important;
    border-radius: var(--radius-xl) !important;
    /* padding: var(--spacing-xl) !important; */
    /* font-size: var(--text-md) !important; */
    /* line-height: var(--line-md) !important; */
    /* min-height: calc(var(--text-md)*var(--line-md) + 2*var(--spacing-xl)); */
    /* min-width: calc(var(--text-md)*var(--line-md) + 2*var(--spacing-xl)); */
}
[data-testid = "bot"] {
    max-width: 95%;
    letter-spacing: 0.5px;
    font-weight: normal;
    /* width: auto !important; */
    border-bottom-left-radius: 0 !important;
}

.dark [data-testid = "bot"] {
    max-width: 95%;
    color: #ccd2db !important;
    letter-spacing: 0.5px;
    font-weight: normal;
    /* width: auto !important; */
    border-bottom-left-radius: 0 !important;
}

[data-testid = "user"] {
    max-width: 100%;
    letter-spacing: 0.5px;
    /* width: auto !important; */
    border-bottom-right-radius: 0 !important;
}

/* linein code block. */
.md-message code {
    display: inline;
    white-space: break-spaces;
    border-radius: 6px;
    margin: 0 2px 0 2px;
    padding: .2em .4em .1em .4em;
    background-color: rgba(13, 17, 23, 0.95);
    color: #eff0f2;
}

.dark .md-message code {
    display: inline;
    white-space: break-spaces;
    border-radius: 6px;
    margin: 0 2px 0 2px;
    padding: .2em .4em .1em .4em;
    background-color: rgba(175,184,193,0.2);
}

/* code block css */
.md-message pre code {
    display: block;
    overflow: auto;
    white-space: pre;
    background-color: rgba(13, 17, 23, 0.95);
    border-radius: 10px;
    padding: 1em;
    margin: 1em 2em 1em 0.5em;
}

.dark .md-message pre code {
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
