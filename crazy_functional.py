from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效
from toolbox import trimmed_format_exc
from loguru import logger

def get_crazy_functions():
    from crazy_functions.Paper_Abstract_Writer import Paper_Abstract_Writer
    from crazy_functions.Program_Comment_Gen import 批量Program_Comment_Gen
    from crazy_functions.SourceCode_Analyse import 解析项目本身
    from crazy_functions.SourceCode_Analyse import 解析一个Python项目
    from crazy_functions.SourceCode_Analyse import 解析一个Matlab项目
    from crazy_functions.SourceCode_Analyse import 解析一个C项目的头文件
    from crazy_functions.SourceCode_Analyse import 解析一个C项目
    from crazy_functions.SourceCode_Analyse import 解析一个Golang项目
    from crazy_functions.SourceCode_Analyse import 解析一个Rust项目
    from crazy_functions.SourceCode_Analyse import 解析一个Java项目
    from crazy_functions.SourceCode_Analyse import 解析一个前端项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.高级功能函数模板 import Demo_Wrap
    from crazy_functions.Latex_Project_Polish import Latex英文润色
    from crazy_functions.Multi_LLM_Query import 同时问询
    from crazy_functions.SourceCode_Analyse import 解析一个Lua项目
    from crazy_functions.SourceCode_Analyse import 解析一个CSharp项目
    from crazy_functions.Word_Summary import Word_Summary
    from crazy_functions.SourceCode_Analyse_JupyterNotebook import 解析ipynb文件
    from crazy_functions.Conversation_To_File import 载入对话历史存档
    from crazy_functions.Conversation_To_File import 对话历史存档
    from crazy_functions.Conversation_To_File import Conversation_To_File_Wrap
    from crazy_functions.Conversation_To_File import 删除所有本地对话历史记录
    from crazy_functions.Helpers import 清除缓存
    from crazy_functions.Markdown_Translate import Markdown英译中
    from crazy_functions.PDF_Summary import PDF_Summary
    from crazy_functions.PDF_Translate import 批量翻译PDF文档
    from crazy_functions.Google_Scholar_Assistant_Legacy import Google_Scholar_Assistant_Legacy
    from crazy_functions.PDF_QA import PDF_QA标准文件输入
    from crazy_functions.Latex_Project_Polish import Latex中文润色
    from crazy_functions.Latex_Project_Polish import Latex英文纠错
    from crazy_functions.Markdown_Translate import Markdown中译英
    from crazy_functions.Void_Terminal import Void_Terminal
    from crazy_functions.Mermaid_Figure_Gen import Mermaid_Gen
    from crazy_functions.PDF_Translate_Wrap import PDF_Tran
    from crazy_functions.Latex_Function import Latex英文纠错加PDF对比
    from crazy_functions.Latex_Function import Latex翻译中文并重新编译PDF
    from crazy_functions.Latex_Function import PDF翻译中文并重新编译PDF
    from crazy_functions.Latex_Function_Wrap import Arxiv_Localize
    from crazy_functions.Latex_Function_Wrap import PDF_Localize
    from crazy_functions.Internet_GPT import 连接网络回答问题
    from crazy_functions.Internet_GPT_Wrap import NetworkGPT_Wrap
    from crazy_functions.Image_Generate import 图片生成_DALLE2, 图片生成_DALLE3, 图片修改_DALLE2
    from crazy_functions.Image_Generate_Wrap import ImageGen_Wrap
    from crazy_functions.SourceCode_Comment import 注释Python项目
    from crazy_functions.SourceCode_Comment_Wrap import SourceCodeComment_Wrap
    from crazy_functions.VideoResource_GPT import 多媒体任务
    from crazy_functions.Document_Conversation import 批量文件询问
    from crazy_functions.Document_Conversation_Wrap import Document_Conversation_Wrap


    function_plugins = {
        "多媒体智能体": {
            "Group": "智能体",
            "Color": "stop",
            "AsButton": False,
            "Info": "【仅测试】多媒体任务",
            "Function": HotReload(多媒体任务),
        },
        "虚空终端": {
            "Group": "对话|编程|学术|智能体",
            "Color": "stop",
            "AsButton": True,
            "Info": "使用自然语言实现您的想法",
            "Function": HotReload(Void_Terminal),
        },
        "解析整个Python项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": True,
            "Info": "解析一个Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析一个Python项目),
        },
        "注释Python项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "上传一系列python源文件(或者压缩包), 为这些代码添加docstring | 输入参数为路径",
            "Function": HotReload(注释Python项目),
            "Class": SourceCodeComment_Wrap,
        },
        "载入对话历史存档（先上传存档或输入路径）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "Info": "载入对话历史存档 | 输入参数为路径",
            "Function": HotReload(载入对话历史存档),
        },
        "删除所有本地对话历史记录（谨慎操作）": {
            "Group": "对话",
            "AsButton": False,
            "Info": "删除所有本地对话历史记录，谨慎操作 | 不需要输入参数",
            "Function": HotReload(删除所有本地对话历史记录),
        },
        "清除所有缓存文件（谨慎操作）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "清除所有缓存文件，谨慎操作 | 不需要输入参数",
            "Function": HotReload(清除缓存),
        },
        "生成多种Mermaid图表(从当前对话或路径(.pdf/.md/.docx)中生产图表）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "Info" : "基于当前对话或文件生成多种Mermaid图表,图表类型由模型判断",
            "Function": None,
            "Class": Mermaid_Gen
        },
        "Arxiv论文翻译": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": True,
            "Info": "ArXiv论文精细翻译 | 输入参数arxiv论文的ID，比如1812.10695",
            "Function": HotReload(Latex翻译中文并重新编译PDF),  # 当注册Class后，Function旧接口仅会在“虚空终端”中起作用
            "Class": Arxiv_Localize,    # 新一代插件需要注册Class
        },
        "批量总结Word文档": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "Info": "批量总结word文档 | 输入参数为路径",
            "Function": HotReload(Word_Summary),
        },
        "解析整个Matlab项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "解析一个Matlab项目的所有源文件(.m) | 输入参数为路径",
            "Function": HotReload(解析一个Matlab项目),
        },
        "解析整个C++项目头文件": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有头文件(.h/.hpp) | 输入参数为路径",
            "Function": HotReload(解析一个C项目的头文件),
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有源文件（.cpp/.hpp/.c/.h）| 输入参数为路径",
            "Function": HotReload(解析一个C项目),
        },
        "解析整个Go项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Go项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Golang项目),
        },
        "解析整个Rust项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Rust项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Rust项目),
        },
        "解析整个Java项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Java项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Java项目),
        },
        "解析整个前端项目（js,ts,css等）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个前端项目的所有源文件（js,ts,css等） | 输入参数为路径",
            "Function": HotReload(解析一个前端项目),
        },
        "解析整个Lua项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Lua项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Lua项目),
        },
        "解析整个CSharp项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个CSharp项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个CSharp项目),
        },
        "解析Jupyter Notebook文件": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "解析Jupyter Notebook文件 | 输入参数为路径",
            "Function": HotReload(解析ipynb文件),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "若输入0，则不解析notebook中的Markdown块",  # 高级参数输入区的显示提示
        },
        "读Tex论文写摘要": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "Info": "读取Tex论文并写摘要 | 输入参数为路径",
            "Function": HotReload(Paper_Abstract_Writer),
        },
        "翻译README或MD": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": True,
            "Info": "将Markdown翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(Markdown英译中),
        },
        "翻译Markdown或README（支持Github链接）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "将Markdown或README翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(Markdown英译中),
        },
        "批量生成函数注释": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量生成函数的注释 | 输入参数为路径",
            "Function": HotReload(批量Program_Comment_Gen),
        },
        "保存当前的对话": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": True,
            "Info": "保存当前的对话 | 不需要输入参数",
            "Function": HotReload(对话历史存档),    # 当注册Class后，Function旧接口仅会在“Void_Terminal”中起作用
            "Class": Conversation_To_File_Wrap     # 新一代插件需要注册Class
        },
        "[多线程Demo]解析此项目本身（源码自译解）": {
            "Group": "对话|编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "多线程解析并翻译此项目的源码 | 不需要输入参数",
            "Function": HotReload(解析项目本身),
        },
        "查互联网后回答": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": True,  # 加入下拉菜单中
            # "Info": "连接网络回答问题（需要访问谷歌）| 输入参数是一个问题",
            "Function": HotReload(连接网络回答问题),
            "Class": NetworkGPT_Wrap     # 新一代插件需要注册Class
        },
        "历史上的今天": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "Info": "查看历史上的今天事件 (这是一个面向开发者的插件Demo) | 不需要输入参数",
            "Function": None,
            "Class": Demo_Wrap, # 新一代插件需要注册Class
        },
        "PDF论文翻译": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": True,
            "Info": "精准翻译PDF论文为中文 | 输入参数为路径",
            "Function": HotReload(批量翻译PDF文档), # 当注册Class后，Function旧接口仅会在“Void_Terminal”中起作用
            "Class": PDF_Tran,  # 新一代插件需要注册Class
        },
        "询问多个GPT模型": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": True,
            "Function": HotReload(同时问询),
        },
        "批量总结PDF文档": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量总结PDF文档的内容 | 输入参数为路径",
            "Function": HotReload(PDF_Summary),
        },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "使用谷歌学术检索助手搜索指定URL的结果 | 输入参数为谷歌学术搜索页的URL",
            "Function": HotReload(Google_Scholar_Assistant_Legacy),
        },
        "理解PDF文档内容 （模仿ChatPDF）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "理解PDF文档的内容并进行回答 | 输入参数为路径",
            "Function": HotReload(PDF_QA标准文件输入),
        },
        "英文Latex项目全文润色（输入路径或上传压缩包）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对英文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex英文润色),
        },

        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对中文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex中文润色),
        },
        # 已经被新插件取代
        # "英文Latex项目全文纠错（输入路径或上传压缩包）": {
        #     "Group": "学术",
        #     "Color": "stop",
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Info": "对英文Latex项目全文进行纠错处理 | 输入参数为路径或上传压缩包",
        #     "Function": HotReload(Latex英文纠错),
        # },
        # 已经被新插件取代
        # "Latex项目全文中译英（输入路径或上传压缩包）": {
        #     "Group": "学术",
        #     "Color": "stop",
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Info": "对Latex项目全文进行中译英处理 | 输入参数为路径或上传压缩包",
        #     "Function": HotReload(Latex中译英)
        # },
        # 已经被新插件取代
        # "Latex项目全文英译中（输入路径或上传压缩包）": {
        #     "Group": "学术",
        #     "Color": "stop",
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Info": "对Latex项目全文进行英译中处理 | 输入参数为路径或上传压缩包",
        #     "Function": HotReload(Latex英译中)
        # },
        "批量Markdown中译英（输入路径或上传压缩包）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量将Markdown文件中文翻译为英文 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Markdown中译英),
        },
        "Latex英文纠错+高亮修正位置 [需Latex]": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "如果有必要, 请在此处追加更细致的矫错指令（使用英文）。",
            "Function": HotReload(Latex英文纠错加PDF对比),
        },
        "📚Arxiv论文精细翻译（输入arxivID）[需Latex]": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": r"如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 "
                            r"例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: "
                            r'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Info": "ArXiv论文精细翻译 | 输入参数arxiv论文的ID，比如1812.10695",
            "Function": HotReload(Latex翻译中文并重新编译PDF),  # 当注册Class后，Function旧接口仅会在“Void_Terminal”中起作用
            "Class": Arxiv_Localize,    # 新一代插件需要注册Class
        },
        "📚本地Latex论文精细翻译（上传Latex项目）[需Latex]": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": r"如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 "
                            r"例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: "
                            r'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Info": "本地Latex论文精细翻译 | 输入参数是路径",
            "Function": HotReload(Latex翻译中文并重新编译PDF),
        },
        "PDF翻译中文并重新编译PDF（上传PDF）[需Latex]": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": r"如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 "
                            r"例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: "
                            r'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Info": "PDF翻译中文，并重新编译PDF | 输入参数为路径",
            "Function": HotReload(PDF翻译中文并重新编译PDF),   # 当注册Class后，Function旧接口仅会在“Void_Terminal”中起作用
            "Class": PDF_Localize   # 新一代插件需要注册Class
        },
        "批量文件询问 (支持自定义总结各种文件)": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": False,
            "Info": "先上传文件，点击此按钮，进行提问",
            "Function": HotReload(批量文件询问),
            "Class": Document_Conversation_Wrap,
        },
    }

    function_plugins.update(
        {
            "🎨图片生成（DALLE2/DALLE3, 使用前切换到GPT系列模型）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "Info": "使用 DALLE2/DALLE3 生成图片 | 输入参数字符串，提供图像的内容",
                "Function": HotReload(图片生成_DALLE2),   # 当注册Class后，Function旧接口仅会在“Void_Terminal”中起作用
                "Class": ImageGen_Wrap  # 新一代插件需要注册Class
            },
        }
    )

    function_plugins.update(
        {
            "🎨图片修改_DALLE2 （使用前请切换模型到GPT系列）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": False,  # 调用时，唤起高级参数输入区（默认False）
                # "Info": "使用DALLE2修改图片 | 输入参数字符串，提供图像的内容",
                "Function": HotReload(图片修改_DALLE2),
            },
        }
    )








    try:
        from crazy_functions.Arxiv_Downloader import 下载arxiv论文并翻译摘要

        function_plugins.update(
            {
                "一键下载arxiv论文并翻译摘要（先在input输入编号，如1812.10695）": {
                    "Group": "学术",
                    "Color": "stop",
                    "AsButton": False,  # 加入下拉菜单中
                    # "Info": "下载arxiv论文并翻译摘要 | 输入参数为arxiv编号如1812.10695",
                    "Function": HotReload(下载arxiv论文并翻译摘要),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")


    try:
        from crazy_functions.SourceCode_Analyse import 解析任意code项目

        function_plugins.update(
            {
                "解析项目源代码（手动指定和筛选源代码文件类型）": {
                    "Group": "编程",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
                    "ArgsReminder": '输入时用逗号隔开, *代表通配符, 加了^代表不匹配; 不输入代表全部匹配。例如: "*.c, ^*.cpp, config.toml, ^*.toml"',  # 高级参数输入区的显示提示
                    "Function": HotReload(解析任意code项目),
                },
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Multi_LLM_Query import 同时问询_指定模型

        function_plugins.update(
            {
                "询问多个GPT模型（手动指定询问哪些模型）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
                    "ArgsReminder": "支持任意数量的llm接口，用&符号分隔。例如chatglm&gpt-3.5-turbo&gpt-4",  # 高级参数输入区的显示提示
                    "Function": HotReload(同时问询_指定模型),
                },
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")



    try:
        from crazy_functions.Audio_Summary import Audio_Summary

        function_plugins.update(
            {
                "批量总结音视频（输入路径或上传压缩包）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "调用openai api 使用whisper-1模型, 目前支持的格式:mp4, m4a, wav, mpga, mpeg, mp3。此处可以输入解析提示，例如：解析为简体中文（默认）。",
                    "Info": "批量总结音频或视频 | 输入参数为路径",
                    "Function": HotReload(Audio_Summary),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from toolbox import get_conf as _get_conf
        if _get_conf("CAMB_API_KEY"):
            from crazy_functions.CambAI_Translation import CambAI_Translation
            from crazy_functions.CambAI_Transcription import CambAI_Transcription
            from crazy_functions.CambAI_AudioSeparation import CambAI_AudioSeparation
            from crazy_functions.CambAI_VoiceClone import CambAI_VoiceClone

            function_plugins.update({
                "CAMB AI 翻译": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "请输入 '源语言代码,目标语言代码'，例如 '1,75'（英文->中文）。语言代码参考CAMB AI文档。",
                    "Info": "使用CAMB AI进行140+语言的高质量翻译 | 输入文本或上传文件",
                    "Function": HotReload(CambAI_Translation),
                },
                "CAMB AI 语音转文字": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "请输入语言代码（整数），例如 '1' 表示英文。默认为1。",
                    "Info": "使用CAMB AI进行语音转文字，支持说话人识别 | 输入参数为音频文件路径",
                    "Function": HotReload(CambAI_Transcription),
                },
                "CAMB AI 音频分离": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "Info": "使用CAMB AI将音频分离为人声和背景音轨 | 输入参数为音频文件路径",
                    "Function": HotReload(CambAI_AudioSeparation),
                },
                "CAMB AI 声音克隆": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "请输入 '声音名称,性别代码'，例如 'MyVoice,2'。性别代码: 0=未指定, 1=男, 2=女。",
                    "Info": "使用CAMB AI从音频样本克隆声音 | 上传10-30秒音频文件",
                    "Function": HotReload(CambAI_VoiceClone),
                },
            })
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load CAMB AI function plugins failed")

    try:
        from crazy_functions.Math_Animation_Gen import 动画生成

        function_plugins.update(
            {
                "数学动画生成（Manim）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "Info": "按照自然语言描述生成一个动画 | 输入参数是一段话",
                    "Function": HotReload(动画生成),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Markdown_Translate import Markdown翻译指定语言

        function_plugins.update(
            {
                "Markdown翻译（指定翻译成何种语言）": {
                    "Group": "编程",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "请输入要翻译成哪种语言，默认为Chinese。",
                    "Function": HotReload(Markdown翻译指定语言),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Vectorstore_QA import 知识库文件注入

        function_plugins.update(
            {
                "构建知识库（先上传文件素材,再运行此插件）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "此处待注入的知识库名称id, 默认为default。文件进入知识库后可长期保存。可以通过再次调用本插件的方式，向知识库追加更多文档。",
                    "Function": HotReload(知识库文件注入),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Vectorstore_QA import 读取知识库作答

        function_plugins.update(
            {
                "知识库文件注入（构建知识库后,再运行此插件）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "AdvancedArgs": True,
                    "ArgsReminder": "待提取的知识库名称id, 默认为default, 您需要构建知识库后再运行此插件。",
                    "Function": HotReload(读取知识库作答),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Interactive_Func_Template import 交互功能模板函数

        function_plugins.update(
            {
                "交互功能模板Demo函数（查找wallhaven.cc的壁纸）": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "Function": HotReload(交互功能模板函数),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")


    try:
        from toolbox import get_conf

        ENABLE_AUDIO = get_conf("ENABLE_AUDIO")
        if ENABLE_AUDIO:
            from crazy_functions.Audio_Assistant import Audio_Assistant

            function_plugins.update(
                {
                    "实时语音对话": {
                        "Group": "对话",
                        "Color": "stop",
                        "AsButton": True,
                        "Info": "这是一个时刻聆听着的语音对话助手 | 没有输入参数",
                        "Function": HotReload(Audio_Assistant),
                    }
                }
            )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.PDF_Translate_Nougat import 批量翻译PDF文档

        function_plugins.update(
            {
                "精准翻译PDF文档（NOUGAT）": {
                    "Group": "学术",
                    "Color": "stop",
                    "AsButton": False,
                    "Function": HotReload(批量翻译PDF文档),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    try:
        from crazy_functions.Dynamic_Function_Generate import Dynamic_Function_Generate

        function_plugins.update(
            {
                "动态代码解释器（CodeInterpreter）": {
                    "Group": "智能体",
                    "Color": "stop",
                    "AsButton": False,
                    "Function": HotReload(Dynamic_Function_Generate),
                }
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    # try:
    #     from crazy_functions.Multi_Agent_Legacy import Multi_Agent_Legacy终端
    #     function_plugins.update(
    #         {
    #             "AutoGenMulti_Agent_Legacy终端（仅供测试）": {
    #                 "Group": "智能体",
    #                 "Color": "stop",
    #                 "AsButton": False,
    #                 "Function": HotReload(Multi_Agent_Legacy终端),
    #             }
    #         }
    #     )
    # except:
    #     logger.error(trimmed_format_exc())
    #     logger.error("Load function plugin failed")

    try:
        from crazy_functions.Rag_Interface import Rag问答

        function_plugins.update(
            {
                "Rag智能召回": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": False,
                    "Info": "将问答数据记录到向量库中，作为长期参考。",
                    "Function": HotReload(Rag问答),
                },
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")

    # try:
    #     from crazy_functions.Document_Optimize import 自定义智能文档处理
    #     function_plugins.update(
    #         {
    #             "一键处理文档（支持自定义全文润色、降重等）": {
    #                 "Group": "学术",
    #                 "Color": "stop",
    #                 "AsButton": False,
    #                 "AdvancedArgs": True,
    #                 "ArgsReminder": "请输入处理指令和要求（可以详细描述），如：请帮我润色文本，要求幽默点。默认调用润色指令。",
    #                 "Info": "保留文档结构，智能处理文档内容 | 输入参数为文件路径",
    #                 "Function": HotReload(自定义智能文档处理)
    #             },
    #         }
    #     )
    # except:
    #     logger.error(trimmed_format_exc())
    #     logger.error("Load function plugin failed")



    try:
        from crazy_functions.Paper_Reading import 快速论文解读
        function_plugins.update(
            {
                "速读论文": {
                    "Group": "学术",
                    "Color": "stop",
                    "AsButton": False,
                    "Info": "上传一篇论文进行快速分析和解读 |  输入参数为论文路径或DOI/arXiv ID",
                    "Function": HotReload(快速论文解读),
                },
            }
        )
    except:
        logger.error(trimmed_format_exc())
        logger.error("Load function plugin failed")


    # try:
    #     from crazy_functions.高级功能函数模板 import 测试图表渲染
    #     function_plugins.update({
    #         "绘制逻辑关系（测试图表渲染）": {
    #             "Group": "智能体",
    #             "Color": "stop",
    #             "AsButton": True,
    #             "Function": HotReload(测试图表渲染)
    #         }
    #     })
    # except:
    #     logger.error(trimmed_format_exc())
    #     print('Load function plugin failed')


    """
    设置默认值:
    - 默认 Group = 对话
    - 默认 AsButton = True
    - 默认 AdvancedArgs = False
    - 默认 Color = secondary
    """
    for name, function_meta in function_plugins.items():
        if "Group" not in function_meta:
            function_plugins[name]["Group"] = "对话"
        if "AsButton" not in function_meta:
            function_plugins[name]["AsButton"] = True
        if "AdvancedArgs" not in function_meta:
            function_plugins[name]["AdvancedArgs"] = False
        if "Color" not in function_meta:
            function_plugins[name]["Color"] = "secondary"

    return function_plugins




def get_multiplex_button_functions():
    """多路复用主提交按钮的功能映射
    """
    return {
        "常规对话":
            "",

        "查互联网后回答":
            "查互联网后回答",

        "多模型对话":
            "询问多个GPT模型", # 映射到上面的 `询问多个GPT模型` 插件

        "智能召回 RAG":
            "Rag智能召回", # 映射到上面的 `Rag智能召回` 插件

        "多媒体查询":
            "多媒体智能体", # 映射到上面的 `多媒体智能体` 插件
    }
