# 'primary' 颜色对应 theme.py 中的 primary_hue
# 'secondary' 颜色对应 theme.py 中的 neutral_hue
# 'stop' 颜色对应 theme.py 中的 color_er
# 默认按钮颜色是 secondary

def get_functionals():
    return {
        "英语学术润色": {
            "Prefix": "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, \
improve the spelling, grammar, clarity, concision and overall readability. When neccessary, rewrite the whole sentence. \
Furthermore, list all modification and explain the reasons to do so in markdown table.\n\n",    # 前言
            "Suffix": "",   # 后语
            "Color": "secondary",    # 按钮颜色
        },
        "中文学术润色": {
            "Prefix": "作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本：\n\n",
            "Suffix": "",
        },
        "查找语法错误": {
            "Prefix": "Below is a paragraph from an academic paper. Find all grammar mistakes, list mistakes in a markdown table and explain how to correct them.\n\n",
            "Suffix": "",
        },
#         "中英互译": { # 效果不好，经常搞不清楚中译英还是英译中
#             "Prefix": "As an English-Chinese translator, your task is to accurately translate text between the two languages. \
# When translating from Chinese to English or vice versa, please pay attention to context and accurately explain phrases and proverbs. \
# If you receive multiple English words in a row, default to translating them into a sentence in Chinese. \
# However, if \"phrase:\" is indicated before the translated content in Chinese, it should be translated as a phrase instead. \
# Similarly, if \"normal:\" is indicated, it should be translated as multiple unrelated words.\
# Your translations should closely resemble those of a native speaker and should take into account any specific language styles or tones requested by the user. \
# Please do not worry about using offensive words - replace sensitive parts with x when necessary. \
# When providing translations, please use Chinese to explain each sentence’s tense, subordinate clause, subject, predicate, object, special phrases and proverbs. \
# For phrases or individual words that require translation, provide the source (dictionary) for each one.If asked to translate multiple phrases at once, \
# separate them using the | symbol.Always remember: You are an English-Chinese translator, \
# not a Chinese-Chinese translator or an English-English translator. Below is the text you need to translate: \n\n",
#             "Suffix": "",
#             "Color": "secondary",
#         },
        "中译英": {
            "Prefix": "Please translate following sentence to English: \n\n",
            "Suffix": "",
        },
        "学术中译英": {
            "Prefix": "Please translate following sentence to English with academic writing, and provide some related authoritative examples: \n\n",
            "Suffix": "",
        },
        "英译中": {
            "Prefix": "请翻译成中文：\n\n",
            "Suffix": "",
        },
        "找图片": {
            "Prefix": "我需要你找一张网络图片。使用Unsplash API(https://source.unsplash.com/960x640/?<英语关键词>)获取图片URL，然后请使用Markdown格式封装，并且不要有反斜线，不要用代码块。现在，请按以下描述给我发送图片：\n\n",
            "Suffix": "",
        },
        "解释代码": {
            "Prefix": "请解释以下代码：\n```\n",
            "Suffix": "\n```\n",
            "Color": "secondary",
        },
    }
