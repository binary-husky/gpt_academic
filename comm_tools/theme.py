import os.path
from comm_tools import func_box
import gradio as gr
from comm_tools.toolbox import get_conf
from collections import namedtuple
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
            button_primary_text_color="white",
            button_primary_text_color_dark="white",
            button_secondary_background_fill="*neutral_100",
            button_secondary_background_fill_hover="*neutral_50",
            button_secondary_background_fill_dark="*neutral_900",
            button_secondary_text_color="*neutral_800",
            button_secondary_text_color_dark="white",
            background_fill_primary="*neutral_50",
            background_fill_primary_dark="#1F1F1F",
            block_title_text_color="*primary_500",
            block_title_background_fill_dark="*primary_900",
            block_label_background_fill_dark="*primary_900",
            input_background_fill="#F6F6F6",
            chatbot_code_background_color="*neutral_950",
            chatbot_code_background_color_dark="*neutral_950",
        )
    except:
        set_theme = None
        print('gradio版本较旧, 不能自定义字体和颜色')
    return set_theme


with open(os.path.join(func_box.base_path, 'docs/assets/custom.css'), "r", encoding="utf-8") as f:
    customCSS = f.read()
custom_css = customCSS


def get_html(filename):
    path = os.path.join(func_box.base_path, "docs/assets", "html", filename)
    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            return file.read()
    return ""


def webpath(fn):
    if fn.startswith(func_box.base_path):
        web_path = os.path.relpath(fn, func_box.base_path).replace('\\', '/')
    else:
        web_path = os.path.abspath(fn)
    return f'file={web_path}?{os.path.getmtime(fn)}'


ScriptFile = namedtuple("ScriptFile", ["basedir", "filename", "path"])


def javascript_html():
    head = ""
    for script in list_scripts("javascript", ".js"):
        head += f'<script type="text/javascript" src="{webpath(script.path)}"></script>\n'
    for script in list_scripts("javascript", ".mjs"):
        head += f'<script type="module" src="{webpath(script.path)}"></script>\n'
    return head


def css_html():
    head = ""
    for cssfile in list_scripts("stylesheet", ".css"):
        head += f'<link rel="stylesheet" property="stylesheet" href="{webpath(cssfile.path)}">'
    return head


def list_scripts(scriptdirname, extension):
    scripts_list = []
    scripts_dir = os.path.join(func_box.base_path, "docs/assets", scriptdirname)
    if os.path.exists(scripts_dir):
        for filename in sorted(os.listdir(scripts_dir)):
            scripts_list.append(ScriptFile(func_box.base_path, filename, os.path.join(scripts_dir, filename)))
    scripts_list = [x for x in scripts_list if
                    os.path.splitext(x.path)[1].lower() == extension and os.path.isfile(x.path)]
    return scripts_list


def reload_javascript():
    print("Reloading javascript...")
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
    css = css_html()
    js += javascript_html()
    js += '<script async src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>'
    js += '<script async type="module" src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>'
    js += '<script async type="module" src="http://spin.js.org/spin.umd.js"></script><link type="text/css" href="https://spin.js.org/spin.css" rel="stylesheet" />'
    def template_response(*args, **kwargs):
        res = GradioTemplateResponseOriginal(*args, **kwargs)
        res.body = res.body.replace(b'</html>', f'{js}</html>'.encode("utf8"))
        res.body = res.body.replace(b'</body>', f'{css}</body>'.encode("utf8"))
        res.init_headers()
        return res
    gr.routes.templates.TemplateResponse = template_response
GradioTemplateResponseOriginal = gr.routes.templates.TemplateResponse