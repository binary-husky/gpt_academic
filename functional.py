# 'primary' 颜色对应 theme.py 中的 primary_hue
# 'secondary' 颜色对应 theme.py 中的 neutral_hue
# 'stop' 颜色对应 theme.py 中的 color_er
# 默认按钮颜色是 secondary

def get_functionals():
    return {
        "英语学术润色": {
            # 前言
            "Prefix":   r"Below is a paragraph from an academic paper. Polish the writing to meet the academic style, " +
                        r"improve the spelling, grammar, clarity, concision and overall readability. When neccessary, rewrite the whole sentence. " +
                        r"Furthermore, list all modification and explain the reasons to do so in markdown table." + "\n\n",
            # 后语 
            "Suffix":   r"",
            "Color":    r"secondary",    # 按钮颜色
        },
        "中文学术润色": {
            "Prefix":   r"作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，" + 
                        r"同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本" + "\n\n",
            "Suffix":   r"",
        },
        "查找语法错误": {
            "Prefix":   r"Below is a paragraph from an academic paper. "+
                        r"Can you help me ensure that the grammar is correct? Please ignore punctuation errors. " +
                        r"List mistakes you find in a two-column markdown table, the first column write the original text, " +
                        r"the second column write the corrected text, only highlight the key words you have changed with bold font." + "\n\n",
            "Suffix":   r"",
        },
        "中译英": {
            "Prefix":   r"Please translate following sentence to English:" + "\n\n",
            "Suffix":   r"",
        },
        "学术中译英": {
            "Prefix":   r"Please translate following sentence to English with academic writing, and provide some related authoritative examples:" + "\n\n",
            "Suffix":   r"",
        },
        "英译中": {
            "Prefix":   r"请翻译成中文：" + "\n\n",
            "Suffix":   r"",
        },
        "找图片": {
            "Prefix":   r"我需要你找一张网络图片。使用Unsplash API(https://source.unsplash.com/960x640/?<英语关键词>)获取图片URL，" +
                        r"然后请使用Markdown格式封装，并且不要有反斜线，不要用代码块。现在，请按以下描述给我发送图片：" + "\n\n",
            "Suffix":   r"",
        },
        "解释代码": {
            "Prefix":   r"请解释以下代码：" + "\n```\n",
            "Suffix":   "\n```\n",
        },
    }
