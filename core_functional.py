# 'primary' 颜色对应 theme.py 中的 primary_hue
# 'secondary' 颜色对应 theme.py 中的 neutral_hue
# 'stop' 颜色对应 theme.py 中的 color_er
# 默认按钮颜色是 secondary
from toolbox import clear_line_break


def get_core_functions():
    return {
        # "英语学术润色": {
        #     # 前言
        #     "Prefix":   r"Below is a paragraph from an academic paper. Polish the writing to meet the academic style, " +
        #                 r"improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. " +
        #                 r"Furthermore, list all modification and explain the reasons to do so in markdown table." + "\n\n",
        #     # 后语
        #     "Suffix":   r"",
        #     "Color":    r"secondary",    # 按钮颜色
        # },
        "中文学术润色": {
            "Prefix":   r"作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，" +
                        r"同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本" + "\n\n",
            "Suffix":   r"",
        },
        # "查找语法错误": {
        #     "Prefix":   r"Can you help me ensure that the grammar and the spelling is correct? " +
        #                 r"Do not try to polish the text, if no mistake is found, tell me that this paragraph is good." +
        #                 r"If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, " +
        #                 r"put the original text the first column, " +
        #                 r"put the corrected text in the second column and highlight the key words you fixed.""\n"
        #                 r"Example:""\n"
        #                 r"Paragraph: How is you? Do you knows what is it?""\n"
        #                 r"| Original sentence | Corrected sentence |""\n"
        #                 r"| :--- | :--- |""\n"
        #                 r"| How **is** you? | How **are** you? |""\n"
        #                 r"| Do you **knows** what **is** **it**? | Do you **know** what **it** **is** ? |""\n"
        #                 r"Below is a paragraph from an academic paper. "
        #                 r"You need to report all grammar and spelling mistakes as the example before."
        #                 + "\n\n",
        #     "Suffix":   r"",
        #     "PreProcess": clear_line_break,    # 预处理：清除换行符
        # },
        # "中译英": {
        #     "Prefix":   r"Please translate following sentence to English:" + "\n\n",
        #     "Suffix":   r"",
        # },
        # "学术中英互译": {
        #     "Prefix":   r"I want you to act as a scientific English-Chinese translator, " +
        #                 r"I will provide you with some paragraphs in one language " +
        #                 r"and your task is to accurately and academically translate the paragraphs only into the other language. " +
        #                 r"Do not repeat the original provided paragraphs after translation. " +
        #                 r"You should use artificial intelligence tools, " +
        #                 r"such as natural language processing, and rhetorical knowledge " +
        #                 r"and experience about effective writing techniques to reply. " +
        #                 r"I'll give you my paragraphs as follows, tell me what language it is written in, and then translate:" + "\n\n",
        #     "Suffix": "",
        #     "Color": "secondary",
        # },
        "解释代码": {
            "Prefix":   r"我希望你担任高级专业程序开发人员。请始终用中文回答我。我的第一个要求是:请解释以下代码，并给代码写上详细的中文注释：" + "\n```\n",
            "Suffix":   "\n```\n",
        },
        "生成代码": {
            "Prefix": r"我希望你担任高级专业程序开发人员。请始终用中文回答我。我的第一个要求是:请根据以下需求生成代码，并给代码写上详细的中文注释：需求是:" + "\n```\n",
            "Suffix": "\n```\n",
        },
        "代码实现业务功能": {
            "Prefix": r"我希望你担任高级专业程序开发人员。请始终用中文回答我，给代码写上详细的中文注释。我的第一个要求是:请盖屋我以下代码实现的业务功能是什么，详细一点：" + "\n```\n",
            "Suffix": "\n```\n",
        },
        "正则表达式": {
            "Prefix": r"我希望你充当正则表达式生成器。您的角色是生成匹配文本中特定模式的正则表达式。您应该以一种可以轻松复制并粘贴"
                      r"到支持正则表达式的文本编辑器或编程语言中的格式提供正则表达式。不要写正则表达式如何工作的"
                      r"解释或例子；只需提供正则表达式本身。我的第一个提示是:" + "\n```\n",
            "Suffix": "\n```\n",
        },
        "英译中": {
            "Prefix": r"翻译成地道的中文：" + "\n\n",
            "Suffix": r"",
        },
        "找图片": {
            "Prefix": r"我需要你找一张网络图片。使用Unsplash API(https://source.unsplash.com/960x640/?<英语关键词>)获取图片URL，" +
                      r"然后请使用Markdown格式封装，并且不要有反斜线，不要用代码块。现在，请按以下描述给我发送图片：" + "\n\n",
            "Suffix": r"",
        },
    }
