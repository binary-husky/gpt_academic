# encoding: utf-8
# @Time   : 2023/8/19
# @Author : Spike
# @Descr   :
import re
import os
import gradio as gr
from typing import List, Tuple, Dict
from gradio_client import utils as client_utils
from gradio import utils
from collections import namedtuple
from common.path_handler import init_path
from shared_utils.config_loader import get_conf


def escape_markdown(text, reverse=False):
    """
    Escape Markdown special characters to HTML-safe equivalents.
    """
    escape_chars = {
        # ' ': '&nbsp;',
        '_': '&#95;',
        '*': '&#42;',
        '[': '&#91;',
        ']': '&#93;',
        '(': '&#40;',
        ')': '&#41;',
        '{': '&#123;',
        '}': '&#125;',
        '#': '&#35;',
        '+': '&#43;',
        '-': '&#45;',
        '.': '&#46;',
        '!': '&#33;',
        '`': '&#96;',
        '>': '&#62;',
        '<': '&#60;',
        '|': '&#124;',
        '$': '&#36;',
        ':': '&#58;',
        # '\n': '<br>',
    }
    if reverse:
        text = text.replace('&nbsp;&nbsp;&nbsp;&nbsp;', '    ')
        for k in escape_chars:
            text = text.replace(escape_chars[k], k)
        return text
    else:
        text = text.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')
        return ''.join(escape_chars.get(c, c) for c in text)


def clip_rawtext(chat_message, need_escape=True):
    # first, clip hr line
    hr_pattern = r'\n\n<hr class="append-display no-in-raw" />(.*?)'
    hr_match = re.search(hr_pattern, chat_message, re.DOTALL)
    message_clipped = chat_message[:hr_match.start()] if hr_match else chat_message
    # second, avoid agent-prefix being escaped
    agent_prefix_pattern = r'<!-- S O PREFIX --><p class="agent-prefix">(.*?)<\/p><!-- E O PREFIX -->'
    agent_matches = re.findall(agent_prefix_pattern, message_clipped)
    final_message = ""
    if agent_matches:
        agent_parts = re.split(agent_prefix_pattern, message_clipped)
        for i, part in enumerate(agent_parts):
            if i % 2 == 0:
                final_message += escape_markdown(part) if need_escape else part
            else:
                final_message += f'<!-- S O PREFIX --><p class="agent-prefix">{part}</p><!-- E O PREFIX -->'
    else:
        final_message = escape_markdown(message_clipped) if need_escape else message_clipped
    return final_message


def convert_bot_before_marked(chat_message):
    """
    注意不能给输出加缩进, 否则会被marked解析成代码块
    """
    if '<div class="md-message">' in chat_message:
        return chat_message
    else:
        raw = f'<div class="raw-message hideM"><pre>{clip_rawtext(chat_message)}</pre></div>'
        # really_raw = f'{START_OF_OUTPUT_MARK}<div class="really-raw hideM">{clip_rawtext(chat_message, need_escape=False)}\n</div>{END_OF_OUTPUT_MARK}'
        code_block_pattern = re.compile(r"```(.*?)(?:```|$)", re.DOTALL)
        code_blocks = code_block_pattern.findall(chat_message)
        non_code_parts = code_block_pattern.split(chat_message)[::2]
        result = []
        for non_code, code in zip(non_code_parts, code_blocks + [""]):
            if non_code.strip():
                result.append(non_code)
            if code.strip():
                code = f"\n```{code}\n```"
                result.append(code)
        result = "".join(result)
        md = f'<div class="md-message">\n\n{result}\n</div>'
        return raw + md


def postprocess(self, y):
    """
    Parameters:
        y: List of lists representing the message and response pairs. Each message and response should be a string, which may be in Markdown format.  It can also be a tuple whose first element is a string filepath or URL to an image/video/audio, and second (optional) element is the alt text, in which case the media file is displayed. It can also be None, in which case that message is not displayed.
    Returns:
        List of lists representing the message and response. Each message and response will be a string of HTML, or a dictionary with media information. Or None if the message is not to be displayed.
    """
    if y is None:
        return []
    processed_messages = []
    for message_pair in y:
        assert isinstance(
            message_pair, (tuple, list)
        ), f"Expected a list of lists or list of tuples. Received: {message_pair}"
        assert (
                len(message_pair) == 2
        ), f"Expected a list of lists of length 2 or list of tuples of length 2. Received: {message_pair}"

        processed_messages.append(
            [
                self._postprocess_chat_messages(message_pair[0], "user"),
                self._postprocess_chat_messages(message_pair[1], "bot"),
            ]
        )
    return processed_messages


def postprocess_chat_messages(self, chat_message, role):
    if chat_message is None:
        return None
    elif isinstance(chat_message, (tuple, list)):
        file_uri = chat_message[0]
        if utils.validate_url(file_uri):
            filepath = file_uri
        else:
            filepath = self.make_temp_copy_if_needed(file_uri)

        mime_type = client_utils.get_mimetype(filepath)
        return {
            "name": filepath,
            "mime_type": mime_type,
            "alt_text": chat_message[1] if len(chat_message) > 1 else None,
            "data": None,  # These last two fields are filled in by the frontend
            "is_file": True,
        }
    elif isinstance(chat_message, str):
        # chat_message = inspect.cleandoc(chat_message)
        # escape html spaces
        # chat_message = chat_message.replace(" ", "&nbsp;")
        if role == "bot":
            chat_message = convert_bot_before_marked(chat_message)
        elif role == "user":
            chat_message = convert_bot_before_marked(chat_message)
        return chat_message
    else:
        raise ValueError(f"Invalid message for Chatbot component: {chat_message}")


def webpath(fn):
    if fn.startswith(init_path.base_path, ):
        web_path = os.path.relpath(fn, init_path.base_path, ).replace('\\', '/')
    else:
        web_path = os.path.abspath(fn)
    return f'file={web_path}?{os.path.getmtime(fn)}'


ScriptFile = namedtuple("ScriptFile", ["basedir", "filename", "path"])


def javascript_html(dirs='javascript', module=True):
    head = ""
    for script in list_scripts(dirs, ".js"):
        head += f'<script type="text/javascript" src="{webpath(script.path)}"></script>\n'
    for script in list_scripts(dirs, ".mjs"):
        head += f'<script type="module" src="{webpath(script.path)}"></script>\n'
    return head


def css_html(dirs='stylesheet'):
    head = ""
    for cssfile in list_scripts(dirs, ".css"):
        head += f'<link rel="stylesheet" property="stylesheet" href="{webpath(cssfile.path)}">'
    return head


def list_scripts(scriptdirname, extension):
    scripts_list = []
    scripts_dir = os.path.join(init_path.base_path, "docs/assets", scriptdirname)
    if os.path.exists(scripts_dir):
        for filename in sorted(os.listdir(scripts_dir)):
            scripts_list.append(ScriptFile(init_path.base_path, filename, os.path.join(scripts_dir, filename)))
    scripts_list = [x for x in scripts_list if
                    os.path.splitext(x.path)[1].lower() == extension and os.path.isfile(x.path)]
    return scripts_list


def reload_javascript():
    spike_js = javascript_html()
    waifu_js = ''
    ADD_WAIFU = get_conf('ADD_WAIFU')
    if ADD_WAIFU:
        waifu_js += f"""
            <script src="{webpath('docs/assets/plugins/waifu_plugin/jquery.min.js')}"></script>
            <script src="{webpath('docs/assets/plugins/waifu_plugin/jquery-ui.min.js')}"></script>
            <script src="{webpath('docs/assets/plugins/waifu_plugin/autoload.js')}"></script>
        """
    plugins_js = javascript_html('plugins/')
    spike_css = css_html()
    # plugins_css = css_html('/plugins')
    meta = """
        <meta name="apple-mobile-web-app-title" content="川虎 Chat">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="application-name" content="川虎 Chat">
        <meta name='viewport' content='width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover'>
        <meta name="theme-color" content="#ffffff">
    """

    def template_response(*args, **kwargs):
        res = GradioTemplateResponseOriginal(*args, **kwargs)
        res.body = res.body.replace(b'</head>', f'{meta}{spike_js}{plugins_js}</head>'.encode("utf8"))
        res.body = res.body.replace(b'</html>', f'{waifu_js}</html>'.encode("utf8"))
        # res.body = res.body.replace(b'</head>', f'{js}</head>'.encode("utf8"))
        res.body = res.body.replace(b'</body>', f'{spike_css}</body>'.encode("utf8"))

        res.init_headers()
        return res

    gr.routes.templates.TemplateResponse = template_response


GradioTemplateResponseOriginal = gr.routes.templates.TemplateResponse


def add_classes_to_gradio_component(comp, is_show=False):
    """
    this adds gradio-* to the component for css styling (ie gradio-button to gr.Button), as well as some others
    code from stable-diffusion-webui <AUTOMATIC1111/stable-diffusion-webui>
    """
    comp.elem_classes = [f"gradio-{comp.get_block_name()}", *(comp.elem_classes or [])]

    if getattr(comp, 'multiselect', False):
        comp.elem_classes.append('multiselect')

    if is_show:  # defy GradioDeprecationWarning 𝙄 𝙘𝙖𝙣 𝙙𝙤 𝙬𝙝𝙖𝙩𝙚𝙫𝙚𝙧 𝙩𝙝𝙚 𝙛**𝙠 𝙄 𝙬𝙖𝙣𝙩 ！！！
        comp.show_label = True


def IOComponent_init(self, *args, **kwargs):
    is_show = False
    if kwargs.get('show_label'):
        is_show = True
    res = original_IOComponent_init(self, *args, **kwargs)
    add_classes_to_gradio_component(self, is_show)
    return res


original_IOComponent_init = gr.components.IOComponent.__init__
gr.components.IOComponent.__init__ = IOComponent_init


def BlockContext_init(self, *args, **kwargs):
    is_show = False
    if kwargs.get('show_label'):
        is_show = True
    res = original_BlockContext_init(self, *args, **kwargs)
    add_classes_to_gradio_component(self, is_show)
    return res


original_BlockContext_init = gr.blocks.BlockContext.__init__
gr.blocks.BlockContext.__init__ = BlockContext_init

if __name__ == '__main__':
    test = ""
    print(escape_markdown(test))
