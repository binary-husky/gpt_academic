# 'primary' 颜色对应 theme.py 中的 primary_hue
# 'secondary' 颜色对应 theme.py 中的 neutral_hue
# 'stop' 颜色对应 theme.py 中的 color_er
# 默认按钮颜色是 secondary

def get_functionals():
    return {
        "学术英文润色": {
            "Prefix": "I want you to act as a scientific refiner. \
                I will provide you with some paragraphs \
                and your task is to refine and polish the paragraphs academically. \
                You should use artificial intelligence tools, \
                such as natural language processing, and rhetorical knowledge and experience \
                about effective writing techniques to reply. \
                I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, \
                upper level Chinese words and sentences. \
                Keep the meaning same, but make them more logical, concise and powerful. \
                I'll give you my paragraphs as follows:  \n\n",  # 后语
            "Suffix": "",
            "Color": "secondary",  # 按钮颜色
        },
        "学术中文润色": {
            "Prefix": "I want you to act as a scientific refiner. \
                I will provide you with some paragraphs in Chinese \
                and your task is to refine and polish the paragraphs academically also in Chinese. \
                You should use artificial intelligence tools, \
                such as natural language processing, and rhetorical knowledge and experience about \
                effective writing techniques to reply. \
                I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, \
                upper level Chinese words and sentences. \
                Keep the meaning same, but make them more logical, concise and powerful. \
                I'll give you my paragraphs as follows:  \n\n",
            "Suffix": "",
            "Color": "secondary",
        },
        "学术中英互译": {
            "Prefix": "I want you to act as a scientific English-Chinese translator, \
                I will provide you with some paragraphs in one language \
                and your task is to accurately and academically translate the paragraphs only into the other language. \
                Do not repeat the original provided paragraphs after translation. \
                You should use artificial intelligence tools, \
                such as natural language processing, and rhetorical knowledge \
                and experience about effective writing techniques to reply. \
                I'll give you my paragraphs as follows:  \n\n",
            "Suffix": "",
            "Color": "secondary",
        },
        "日常中英互译": {
            "Prefix": "I want you to act as an English-Chinese translator, \
                I will provide you with some paragraphs in one language \
                and your task is to accurately translate the paragraphs only into the other language, \
                like a native speaker. \
                Do not repeat the original provided paragraphs after translation. \
                You should use artificial intelligence tools, \
                such as natural language processing, and rhetorical knowledge \
                I'll give you my paragraphs as follows:  \n\n",
            "Suffix": "",
            "Color": "secondary",
        },
        "代码剖析": {
            "Prefix": "请解释以下代码：\n```\n",
            "Suffix": "\n```\n",
            "Color": "secondary",
        },
    }
