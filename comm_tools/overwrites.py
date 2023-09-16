#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/19
# @Author : Spike
# @Descr   :
import re
from typing import List, Tuple, Dict
from gradio_client import utils as client_utils
from gradio import utils


def escape_markdown(text):
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
        '\n': '<br>',
    }
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