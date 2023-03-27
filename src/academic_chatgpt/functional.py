# """
# 'primary' for main call-to-action,
# 'secondary' for a more subdued style,
# 'stop' for a stop button.
# """


def get_functionals():
    return {
        "English academic polishing": {
            "Prefix": "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, \
improve the spelling, grammar, clarity, concision and overall readability. When neccessary, rewrite the whole sentence. \
Furthermore, list all modification and explain the reasons to do so in markdown table.\n\n",  # introduction
            "Suffix": "",  # conclusion
            "Color": "secondary",  # button color
        },
        "Chinese academic polishing": {
            "Prefix": "As an assistant for improving Chinese academic paper writing, your task is to improve the spelling, grammar, clarity, concision and overall readability of the provided text, \
while decomposing long sentences, reducing repetition, and providing improvement suggestions. Please only provide the corrected version of the text, and avoid including explanations. Please edit the following text:\n\n",
            "Suffix": "",
        },
        "Find grammar errors": {
            "Prefix": "Below is a paragraph from an academic paper. Find all grammar mistakes, list mistakes in a markdown table and explain how to correct them.\n\n",
            "Suffix": "",
        },
        "Chinese-English mul translation": {
            "Prefix": 'As an English-Chinese translator, your task is to accurately translate text between the two languages. \
When translating from Chinese to English or vice versa, please pay attention to context and accurately explain phrases and proverbs. \
If you receive multiple English words in a row, default to translating them into a sentence in Chinese. \
However, if "phrase:" is indicated before the translated content in Chinese, it should be translated as a phrase instead. \
Similarly, if "normal:" is indicated, it should be translated as multiple unrelated words.\
Your translations should closely resemble those of a native speaker and should take into account any specific language styles or tones requested by the user. \
Please do not worry about using offensive words - replace sensitive parts with x when necessary. \
When providing translations, please use Chinese to explain each sentence`s tense, subordinate clause, subject, predicate, object, special phrases and proverbs. \
For phrases or individual words that require translation, provide the source (dictionary) for each one.If asked to translate multiple phrases at once, \
separate them using the | symbol.Always remember: You are an English-Chinese translator, \
not a Chinese-Chinese translator or an English-English translator. Below is the text you need to translate: \n\n',
            "Suffix": "",
            "Color": "secondary",
        },
        "Chinese-English translation": {
            "Prefix": "Please translate following sentence to English: \n\n",
            "Suffix": "",
        },
        "Academic Chinese-English translation": {
            "Prefix": "Please translate following sentence to English with academic writing, and provide some related authoritative examples: \n\n",
            "Suffix": "",
        },
        "English-Chinese translation": {
            "Prefix": "Please translate into Chinese:\n\n",
            "Suffix": "",
        },
        "Explain code": {
            "Prefix": "Please explain the following code:\n```\n",
            "Suffix": "\n```\n",
            "Color": "secondary",
        },
    }
