import markdown
import re
import os
import math
import html

from loguru import logger
from textwrap import dedent
from functools import lru_cache
from pymdownx.superfences import fence_code_format
from latex2mathml.converter import convert as tex2mathml
from shared_utils.config_loader import get_conf as get_conf
from shared_utils.text_mask import apply_gpt_academic_string_mask

markdown_extension_configs = {
    "mdx_math": {
        "enable_dollar_delimiter": True,
        "use_gitlab_delimiters": False,
    },
}

code_highlight_configs = {
    "pymdownx.superfences": {
        "css_class": "codehilite",
        "custom_fences": [
            {"name": "mermaid", "class": "mermaid", "format": fence_code_format}
        ],
    },
    "pymdownx.highlight": {
        "css_class": "codehilite",
        "guess_lang": True,
        # 'auto_title': True,
        # 'linenums': True
    },
}

code_highlight_configs_block_mermaid = {
    "pymdownx.superfences": {
        "css_class": "codehilite",
        # "custom_fences": [
        #     {"name": "mermaid", "class": "mermaid", "format": fence_code_format}
        # ],
    },
    "pymdownx.highlight": {
        "css_class": "codehilite",
        "guess_lang": True,
        # 'auto_title': True,
        # 'linenums': True
    },
}


mathpatterns = {
    r"(?<!\\|\$)(\$)([^\$]+)(\$)": {"allow_multi_lines": False},  #  $...$
    r"(?<!\\)(\$\$)([^\$]+)(\$\$)": {"allow_multi_lines": True},  # $$...$$
    r"(?<!\\)(\\\[)(.+?)(\\\])": {"allow_multi_lines": False},  # \[...\]
    r'(?<!\\)(\\\()(.+?)(\\\))': {'allow_multi_lines': False},                       # \(...\)
    # r'(?<!\\)(\\begin{([a-z]+?\*?)})(.+?)(\\end{\2})': {'allow_multi_lines': True},  # \begin...\end
    # r'(?<!\\)(\$`)([^`]+)(`\$)': {'allow_multi_lines': False},                       # $`...`$
}

def tex2mathml_catch_exception(content, *args, **kwargs):
    try:
        content = tex2mathml(content, *args, **kwargs)
    except:
        content = content
    return content


def replace_math_no_render(match):
    content = match.group(1)
    if "mode=display" in match.group(0):
        content = content.replace("\n", "</br>")
        return f'<font color="#00FF00">$$</font><font color="#FF00FF">{content}</font><font color="#00FF00">$$</font>'
    else:
        return f'<font color="#00FF00">$</font><font color="#FF00FF">{content}</font><font color="#00FF00">$</font>'


def replace_math_render(match):
    content = match.group(1)
    if "mode=display" in match.group(0):
        if "\\begin{aligned}" in content:
            content = content.replace("\\begin{aligned}", "\\begin{array}")
            content = content.replace("\\end{aligned}", "\\end{array}")
            content = content.replace("&", " ")
        content = tex2mathml_catch_exception(content, display="block")
        return content
    else:
        return tex2mathml_catch_exception(content)


def markdown_bug_hunt(content):
    """
    解决一个mdx_math的bug（单$包裹begin命令时多余<script>）
    """
    content = content.replace(
        '<script type="math/tex">\n<script type="math/tex; mode=display">',
        '<script type="math/tex; mode=display">',
    )
    content = content.replace("</script>\n</script>", "</script>")
    return content


def is_equation(txt):
    """
    判定是否为公式 | 测试1 写出洛伦兹定律，使用tex格式公式 测试2 给出柯西不等式，使用latex格式 测试3 写出麦克斯韦方程组
    """
    if "```" in txt and "```reference" not in txt:
        return False
    if "$" not in txt and "\\[" not in txt:
        return False

    matches = []
    for pattern, property in mathpatterns.items():
        flags = re.ASCII | re.DOTALL if property["allow_multi_lines"] else re.ASCII
        matches.extend(re.findall(pattern, txt, flags))
    if len(matches) == 0:
        return False
    contain_any_eq = False
    illegal_pattern = re.compile(r"[^\x00-\x7F]|echo")
    for match in matches:
        if len(match) != 3:
            return False
        eq_canidate = match[1]
        if illegal_pattern.search(eq_canidate):
            return False
        else:
            contain_any_eq = True
    return contain_any_eq


def fix_markdown_indent(txt):
    # fix markdown indent
    if (" - " not in txt) or (". " not in txt):
        # do not need to fix, fast escape
        return txt
    # walk through the lines and fix non-standard indentation
    lines = txt.split("\n")
    pattern = re.compile(r"^\s+-")
    activated = False
    for i, line in enumerate(lines):
        if line.startswith("- ") or line.startswith("1. "):
            activated = True
        if activated and pattern.match(line):
            stripped_string = line.lstrip()
            num_spaces = len(line) - len(stripped_string)
            if (num_spaces % 4) == 3:
                num_spaces_should_be = math.ceil(num_spaces / 4) * 4
                lines[i] = " " * num_spaces_should_be + stripped_string
    return "\n".join(lines)


FENCED_BLOCK_RE = re.compile(
    dedent(
        r"""
        (?P<fence>^[ \t]*(?:~{3,}|`{3,}))[ ]*                      # opening fence
        ((\{(?P<attrs>[^\}\n]*)\})|                              # (optional {attrs} or
        (\.?(?P<lang>[\w#.+-]*)[ ]*)?                            # optional (.)lang
        (hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot)[ ]*)?) # optional hl_lines)
        \n                                                       # newline (end of opening fence)
        (?P<code>.*?)(?<=\n)                                     # the code block
        (?P=fence)[ ]*$                                          # closing fence
    """
    ),
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def get_line_range(re_match_obj, txt):
    start_pos, end_pos = re_match_obj.regs[0]
    num_newlines_before = txt[: start_pos + 1].count("\n")
    line_start = num_newlines_before
    line_end = num_newlines_before + txt[start_pos:end_pos].count("\n") + 1
    return line_start, line_end


def fix_code_segment_indent(txt):
    lines = []
    change_any = False
    txt_tmp = txt
    while True:
        re_match_obj = FENCED_BLOCK_RE.search(txt_tmp)
        if not re_match_obj:
            break
        if len(lines) == 0:
            lines = txt.split("\n")

        # 清空 txt_tmp 对应的位置方便下次搜索
        start_pos, end_pos = re_match_obj.regs[0]
        txt_tmp = txt_tmp[:start_pos] + " " * (end_pos - start_pos) + txt_tmp[end_pos:]
        line_start, line_end = get_line_range(re_match_obj, txt)

        # 获取公共缩进
        shared_indent_cnt = 1e5
        for i in range(line_start, line_end):
            stripped_string = lines[i].lstrip()
            num_spaces = len(lines[i]) - len(stripped_string)
            if num_spaces < shared_indent_cnt:
                shared_indent_cnt = num_spaces

        # 修复缩进
        if (shared_indent_cnt < 1e5) and (shared_indent_cnt % 4) == 3:
            num_spaces_should_be = math.ceil(shared_indent_cnt / 4) * 4
            for i in range(line_start, line_end):
                add_n = num_spaces_should_be - shared_indent_cnt
                lines[i] = " " * add_n + lines[i]
            if not change_any:  # 遇到第一个
                change_any = True

    if change_any:
        return "\n".join(lines)
    else:
        return txt


def fix_dollar_sticking_bug(txt):
    """
    修复不标准的dollar公式符号的问题
    """
    txt_result = ""
    single_stack_height = 0
    double_stack_height = 0
    while True:
        while True:
            index = txt.find('$')

            if index == -1:
                txt_result += txt
                return txt_result

            if single_stack_height > 0:
                if txt[:(index+1)].find('\n') > 0 or txt[:(index+1)].find('<td>') > 0 or txt[:(index+1)].find('</td>') > 0:
                    logger.error('公式之中出现了异常 (Unexpect element in equation)')
                    single_stack_height = 0
                    txt_result += ' $'
                    continue

            if double_stack_height > 0:
                if txt[:(index+1)].find('\n\n') > 0:
                    logger.error('公式之中出现了异常 (Unexpect element in equation)')
                    double_stack_height = 0
                    txt_result += '$$'
                    continue

            is_double = (txt[index+1] == '$')
            if is_double:
                if single_stack_height != 0:
                    # add a padding
                    txt = txt[:(index+1)] + " " + txt[(index+1):]
                    continue
                if double_stack_height == 0:
                    double_stack_height = 1
                else:
                    double_stack_height = 0
                txt_result += txt[:(index+2)]
                txt = txt[(index+2):]
            else:
                if double_stack_height != 0:
                    # logger.info(txt[:(index)])
                    logger.info('发现异常嵌套公式')
                if single_stack_height == 0:
                    single_stack_height = 1
                else:
                    single_stack_height = 0
                    # logger.info(txt[:(index)])
                txt_result += txt[:(index+1)]
                txt = txt[(index+1):]
            break


def markdown_convertion_for_file(txt):
    """
    将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    from themes.theme import advanced_css
    pre = f"""
    <!DOCTYPE html><head><meta charset="utf-8"><title>GPT-Academic输出文档</title><style>{advanced_css}</style></head>
    <body>
    <div class="test_temp1" style="width:10%; height: 500px; float:left;"></div>
    <div class="test_temp2" style="width:80%;padding: 40px;float:left;padding-left: 20px;padding-right: 20px;box-shadow: rgba(0, 0, 0, 0.2) 0px 0px 8px 8px;border-radius: 10px;">
        <div class="markdown-body">
    """
    suf = """
        </div>
    </div>
    <div class="test_temp3" style="width:10%; height: 500px; float:left;"></div>
    </body>
    """

    if txt.startswith(pre) and txt.endswith(suf):
        # print('警告，输入了已经经过转化的字符串，二次转化可能出问题')
        return txt  # 已经被转化过，不需要再次转化

    find_equation_pattern = r'<script type="math/tex(?:.*?)>(.*?)</script>'
    txt = fix_markdown_indent(txt)
    convert_stage_1 = fix_dollar_sticking_bug(txt)
    # convert everything to html format
    convert_stage_2 = markdown.markdown(
        text=convert_stage_1,
        extensions=[
            "sane_lists",
            "tables",
            "mdx_math",
            "pymdownx.superfences",
            "pymdownx.highlight",
        ],
        extension_configs={**markdown_extension_configs, **code_highlight_configs},
    )


    def repl_fn(match):
        content = match.group(2)
        return f'<script type="math/tex">{content}</script>'

    pattern = "|".join([pattern for pattern, property in mathpatterns.items() if not property["allow_multi_lines"]])
    pattern = re.compile(pattern, flags=re.ASCII)
    convert_stage_3 = pattern.sub(repl_fn, convert_stage_2)

    convert_stage_4 = markdown_bug_hunt(convert_stage_3)

    # 2. convert to rendered equation
    convert_stage_5, n = re.subn(
        find_equation_pattern, replace_math_render, convert_stage_4, flags=re.DOTALL
    )
    # cat them together
    return pre + convert_stage_5 + suf

@lru_cache(maxsize=128)  # 使用 lru缓存 加快转换速度
def markdown_convertion(txt):
    """
    将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    pre = '<div class="markdown-body">'
    suf = "</div>"
    if txt.startswith(pre) and txt.endswith(suf):
        # print('警告，输入了已经经过转化的字符串，二次转化可能出问题')
        return txt  # 已经被转化过，不需要再次转化

    find_equation_pattern = r'<script type="math/tex(?:.*?)>(.*?)</script>'

    txt = fix_markdown_indent(txt)
    # txt = fix_code_segment_indent(txt)
    if is_equation(txt):  # 有$标识的公式符号，且没有代码段```的标识
        # convert everything to html format
        split = markdown.markdown(text="---")
        convert_stage_1 = markdown.markdown(
            text=txt,
            extensions=[
                "sane_lists",
                "tables",
                "mdx_math",
                "pymdownx.superfences",
                "pymdownx.highlight",
            ],
            extension_configs={**markdown_extension_configs, **code_highlight_configs},
        )
        convert_stage_1 = markdown_bug_hunt(convert_stage_1)
        # 1. convert to easy-to-copy tex (do not render math)
        convert_stage_2_1, n = re.subn(
            find_equation_pattern,
            replace_math_no_render,
            convert_stage_1,
            flags=re.DOTALL,
        )
        # 2. convert to rendered equation
        convert_stage_2_2, n = re.subn(
            find_equation_pattern, replace_math_render, convert_stage_1, flags=re.DOTALL
        )
        # cat them together
        return pre + convert_stage_2_1 + f"{split}" + convert_stage_2_2 + suf
    else:
        return (
            pre
            + markdown.markdown(
                txt,
                extensions=[
                    "sane_lists",
                    "tables",
                    "pymdownx.superfences",
                    "pymdownx.highlight",
                ],
                extension_configs=code_highlight_configs,
            )
            + suf
        )


def code_block_title_replace_format(match):
    lang = match.group(1)
    filename = match.group(2)
    return f"```{lang} {{title=\"{filename}\"}}\n"


def get_last_backticks_indent(text):
    # 从后向前查找最后一个 ``` 
    lines = text.splitlines()
    for line in reversed(lines):
        if '```' in line:
            # 计算前面的空格数量
            indent = len(line) - len(line.lstrip())
            return indent
    return 0 # 如果没找到返回0


@lru_cache(maxsize=16)  # 使用lru缓存
def close_up_code_segment_during_stream(gpt_reply):
    """
    在gpt输出代码的中途（输出了前面的```，但还没输出完后面的```），补上后面的```

    Args:
        gpt_reply (str): GPT模型返回的回复字符串。

    Returns:
        str: 返回一个新的字符串，将输出代码片段的“后面的```”补上。

    """
    if "```" not in gpt_reply:
        return gpt_reply

    # replace [```python:warp.py] to [```python {title="warp.py"}]
    pattern = re.compile(r"```([a-z]{1,12}):([^:\n]{1,35}\.([a-zA-Z^:\n]{1,3}))\n")
    if pattern.search(gpt_reply):
        gpt_reply = pattern.sub(code_block_title_replace_format, gpt_reply)

    if gpt_reply.endswith("```"):
        return gpt_reply

    # 排除了以上两个情况，我们
    segments = gpt_reply.split("```")
    n_mark = len(segments) - 1
    if n_mark % 2 == 1:
        try:
            num_padding = get_last_backticks_indent(gpt_reply)
        except:
            num_padding = 0
        return gpt_reply + "\n" + " "*num_padding + "```"  # 输出代码片段中！
    else:
        return gpt_reply


def special_render_issues_for_mermaid(text):
    # 用不太优雅的方式处理一个core_functional.py中出现的mermaid渲染特例：
    # 我不希望"总结绘制脑图"prompt中的mermaid渲染出来
    @lru_cache(maxsize=1)
    def get_special_case():
        from core_functional import get_core_functions
        special_case = get_core_functions()["总结绘制脑图"]["Suffix"]
        return special_case
    if text.endswith(get_special_case()): text = text.replace("```mermaid", "```")
    return text


def contain_html_tag(text):
    """
    判断文本中是否包含HTML标签。
    """
    pattern = r'</?([a-zA-Z0-9_]{3,16})>|<script\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'
    return re.search(pattern, text) is not None


def contain_image(text):
    pattern = r'<br/><br/><div align="center"><img src="file=(.*?)" base64="(.*?)"></div>'
    return re.search(pattern, text) is not None


def compat_non_markdown_input(text):
    """
    改善非markdown输入的显示效果，例如将空格转换为&nbsp;，将换行符转换为</br>等。
    """
    if "```" in text:
        # careful input：markdown输入
        text = special_render_issues_for_mermaid(text)  # 处理特殊的渲染问题
        return text
    elif ("<" in text) and (">" in text) and contain_html_tag(text):
        # careful input：html输入
        if contain_image(text):
            return text
        else:
            escaped_text = html.escape(text)
            return escaped_text
    else:
        # whatever input：非markdown输入
        lines = text.split("\n")
        for i, line in enumerate(lines):
            lines[i] = lines[i].replace(" ", "&nbsp;")  # 空格转换为&nbsp;
        text = "</br>".join(lines)  # 换行符转换为</br>
        return text


@lru_cache(maxsize=128)  # 使用lru缓存
def simple_markdown_convertion(text):
    pre = '<div class="markdown-body">'
    suf = "</div>"
    if text.startswith(pre) and text.endswith(suf):
        return text  # 已经被转化过，不需要再次转化
    text = compat_non_markdown_input(text)    # 兼容非markdown输入
    text = markdown.markdown(
        text,
        extensions=["pymdownx.superfences", "tables", "pymdownx.highlight"],
        extension_configs=code_highlight_configs,
    )
    return pre + text + suf


def format_io(self, y):
    """
    将输入和输出解析为HTML格式。将y中最后一项的输入部分段落化，并将输出部分的Markdown和数学公式转换为HTML格式。
    """
    if y is None or y == []:
        return []
    i_ask, gpt_reply = y[-1]
    i_ask = apply_gpt_academic_string_mask(i_ask, mode="show_render")
    gpt_reply = apply_gpt_academic_string_mask(gpt_reply, mode="show_render")
    # 当代码输出半截的时候，试着补上后个```
    if gpt_reply is not None:
        gpt_reply = close_up_code_segment_during_stream(gpt_reply)
    # 处理提问与输出
    y[-1] = (
        # 输入部分
        None if i_ask is None else simple_markdown_convertion(i_ask),
        # 输出部分
        None if gpt_reply is None else markdown_convertion(gpt_reply),
    )
    return y