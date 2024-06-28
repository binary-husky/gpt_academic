sample = """
[1]: https://baike.baidu.com/item/%E8%B4%A8%E8%83%BD%E6%96%B9%E7%A8%8B/1884527 "质能方程（质能方程式）_百度百科"
[2]: https://www.zhihu.com/question/348249281 "如何理解质能方程 E＝mc²？ - 知乎"
[3]: https://zhuanlan.zhihu.com/p/32597385 "质能方程的推导与理解 - 知乎 - 知乎专栏"

你好，这是必应。质能方程是描述质量与能量之间的当量关系的方程[^1^][1]。用tex格式，质能方程可以写成$$E=mc^2$$，其中$E$是能量，$m$是质量，$c$是光速[^2^][2] [^3^][3]。
"""
import re


def preprocess_newbing_out(s):
    pattern = r"\^(\d+)\^"  # 匹配^数字^
    pattern2 = r"\[(\d+)\]"  # 匹配^数字^

    def sub(m):
        return "\\[" + m.group(1) + "\\]"  # 将匹配到的数字作为替换值

    result = re.sub(pattern, sub, s)  # 替换操作
    if "[1]" in result:
        result += (
            '<br/><hr style="border-top: dotted 1px #44ac5c;"><br/><small>'
            + "<br/>".join(
                [
                    re.sub(pattern2, sub, r)
                    for r in result.split("\n")
                    if r.startswith("[")
                ]
            )
            + "</small>"
        )
    return result


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
    if gpt_reply.endswith("```"):
        return gpt_reply

    # 排除了以上两个情况，我们
    segments = gpt_reply.split("```")
    n_mark = len(segments) - 1
    if n_mark % 2 == 1:
        # print('输出代码片段中！')
        return gpt_reply + "\n```"
    else:
        return gpt_reply


import markdown
from latex2mathml.converter import convert as tex2mathml


def markdown_convertion(txt):
    """
    将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    pre = '<div class="markdown-body">'
    suf = "</div>"
    if txt.startswith(pre) and txt.endswith(suf):
        # print('警告，输入了已经经过转化的字符串，二次转化可能出问题')
        return txt  # 已经被转化过，不需要再次转化

    markdown_extension_configs = {
        "mdx_math": {
            "enable_dollar_delimiter": True,
            "use_gitlab_delimiters": False,
        },
    }
    find_equation_pattern = r'<script type="math/tex(?:.*?)>(.*?)</script>'

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

    if ("$" in txt) and ("```" not in txt):  # 有$标识的公式符号，且没有代码段```的标识
        # convert everything to html format
        split = markdown.markdown(text="---")
        convert_stage_1 = markdown.markdown(
            text=txt,
            extensions=["mdx_math", "fenced_code", "tables", "sane_lists"],
            extension_configs=markdown_extension_configs,
        )
        convert_stage_1 = markdown_bug_hunt(convert_stage_1)
        # re.DOTALL: Make the '.' special character match any character at all, including a newline; without this flag, '.' will match anything except a newline. Corresponds to the inline flag (?s).
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
                txt, extensions=["fenced_code", "codehilite", "tables", "sane_lists"]
            )
            + suf
        )


sample = preprocess_newbing_out(sample)
sample = close_up_code_segment_during_stream(sample)
sample = markdown_convertion(sample)
with open("tmp.html", "w", encoding="utf8") as f:
    f.write(
        """

<head>
    <title>My Website</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>

    """
    )
    f.write(sample)
