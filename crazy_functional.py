from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效

function_plugins = {}


def get_crazy_functions():
    get_functions_学术优化()
    get_functions_文档读取()
    get_functions_代码解析()
    get_functions_多功能插件()
    return function_plugins

def get_functions_代码解析():
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.解析项目源代码 import 解析一个Golang项目
    from crazy_functions.解析项目源代码 import 解析一个Rust项目
    from crazy_functions.解析项目源代码 import 解析一个Java项目
    from crazy_functions.解析项目源代码 import 解析一个前端项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.代码重写为全英文_多线程 import 全项目切换英文
    from crazy_functions.解析项目源代码 import 解析一个Lua项目
    from crazy_functions.解析项目源代码 import 解析一个CSharp项目
    from crazy_functions.解析JupyterNotebook import 解析ipynb文件
    from crazy_functions.解析项目源代码 import 解析任意code项目
    from crazy_functions.批量Markdown翻译 import Markdown中译英
    function_plugins['代码解析'] = {
        "解析整个Python项目": {
            "Color": "primary",
            "AsButton": True,
            "Info": "解析一个Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析一个Python项目)
        },
        "解析整个C++项目头文件": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有头文件(.h/.hpp) | 输入参数为路径",
            "Function": HotReload(解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有源文件（.cpp/.hpp/.c/.h）| 输入参数为路径",
            "Function": HotReload(解析一个C项目)
        },
        "解析整个Go项目": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Go项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Golang项目)
        },
        "解析整个Rust项目": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Rust项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Rust项目)
        },
        "解析整个Java项目": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Java项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Java项目)
        },
        "解析整个前端项目（js,ts,css等）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个前端项目的所有源文件（js,ts,css等） | 输入参数为路径",
            "Function": HotReload(解析一个前端项目)
        },
        "解析整个Lua项目": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Lua项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Lua项目)
        },
        "解析整个CSharp项目": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个CSharp项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个CSharp项目)
        },
        "解析Jupyter Notebook文件": {
            "Color": "primary",
            "AsButton": False,
            "Info": "解析Jupyter Notebook文件 | 输入参数为路径",
            "Function": HotReload(解析ipynb文件),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "若输入0，则不解析notebook中的Markdown块",  # 高级参数输入区的显示提示
        },
        "批量生成函数注释": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(批量生成函数注释)
        },
        "[多线程Demo] 解析此项目本身（源码自译解）": {
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析项目本身)
        },
        "[插件demo] 历史上的今天": {
            "AsButton": True,
            "Function": HotReload(高阶功能模板函数)
        },
        "批量Markdown中译英（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Markdown中译英)
        },
        "解析项目源代码（手动指定和筛选源代码文件类型）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "输入时用逗号隔开, *代表通配符, 加了^代表不匹配; 不输入代表全部匹配。例如: \"*.c, ^*.cpp, config.toml, ^*.toml\"",
            # 高级参数输入区的显示提示
            "Function": HotReload(解析任意code项目)
        },

    }


def get_functions_文档读取():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.总结word文档 import 总结word文档
    from crazy_functions.批量总结PDF文档 import 批量总结PDF文档
    from crazy_functions.批量翻译PDF文档_多线程 import 批量翻译PDF文档
    from crazy_functions.批量Markdown翻译 import Markdown英译中
    from crazy_functions.理解PDF文档内容 import 理解PDF文档内容标准文件输入
    from crazy_functions.批量Markdown翻译 import Markdown翻译指定语言
    function_plugins['文档读取'] = {
        "批量总结PDF文档": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(批量总结PDF文档)
        },
        "理解PDF文档内容 （模仿ChatPDF）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(理解PDF文档内容标准文件输入)
        },
        "精准翻译PDF论文": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(批量翻译PDF文档)
        },
        "批量总结Word文档": {
            "Color": "primary",
            "AsButton": True,
            "Info": "批量总结word文档 | 输入参数为路径",
            "Function": HotReload(总结word文档)
        },
        "读Tex论文写摘要": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(读文章写摘要)
        },
        "翻译README或.MD": {
            "Color": "primary",
            "AsButton": True,
            "Info": "将Markdown翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(Markdown英译中)
        },
        "翻译Markdown或README（支持Github链接）": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(Markdown英译中)
        },
        "Markdown翻译（手动指定语言）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "请输入要翻译成哪种语言，默认为Chinese。",
            "Function": HotReload(Markdown翻译指定语言)
        },
    }

def get_functions_学术优化():
    from crazy_functions.谷歌检索小助手 import 谷歌检索小助手
    from crazy_functions.Latex全文润色 import Latex中文润色
    from crazy_functions.Latex全文润色 import Latex英文纠错
    from crazy_functions.Latex全文翻译 import Latex中译英
    from crazy_functions.Latex全文翻译 import Latex英译中
    from crazy_functions.Latex全文润色 import Latex英文润色
    from crazy_functions.下载arxiv论文翻译摘要 import 下载arxiv论文并翻译摘要
    from crazy_functions.Latex输出PDF结果 import Latex英文纠错加PDF对比
    from crazy_functions.Latex输出PDF结果 import Latex翻译中文并重新编译PDF
    function_plugins['学术优化'] = {
        "英文Latex项目全文纠错（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英文纠错)
        },
        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex中文润色)
        },
        "Latex项目全文中译英（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex中译英)
        },
        "Latex项目全文英译中（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英译中)
        },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(谷歌检索小助手)
        },
        "英文Latex项目全文润色（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英文润色)
        },
        "Arixv论文精细翻译（输入arxivID）[需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder":
                "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 " +
                "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " +
                'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Function": HotReload(Latex翻译中文并重新编译PDF)
        },
        "Latex英文纠错+高亮修正位置 [需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "如果有必要, 请在此处追加更细致的矫错指令（使用英文）。",
            "Function": HotReload(Latex英文纠错加PDF对比)
        },

    }
    function_plugins['学术优化'].update({
        "一键下载arxiv论文并翻译摘要（先在input输入编号，如1812.10695）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(下载arxiv论文并翻译摘要)
        }
    })

def get_functions_多功能插件():
    from crazy_functions.询问多个大语言模型 import 同时问询
    from crazy_functions.对话历史存档 import 对话历史存档
    from crazy_functions.对话历史存档 import 载入对话历史存档
    from crazy_functions.对话历史存档 import 删除所有本地对话历史记录
    from crazy_functions.辅助功能 import 清除缓存
    from crazy_functions.联网的ChatGPT import 连接网络回答问题
    from crazy_functions.联网的ChatGPT_bing版 import 连接bing搜索回答问题
    from crazy_functions.询问多个大语言模型 import 同时问询_指定模型
    from crazy_functions.图片生成 import 图片生成
    from crazy_functions.总结音视频 import 总结音视频
    from crazy_functions.数学动画生成manim import 动画生成
    from crazy_functions.Langchain知识库 import 知识库问答
    from crazy_functions.Langchain知识库 import 读取知识库作答
    from crazy_functions.交互功能函数模板 import 交互功能模板函数
    from crazy_functions.语音助手 import 语音助手
    from crazy_functions.虚空终端 import 自动终端
    function_plugins['多功能插件'] = {
        "询问多个GPT模型": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(同时问询)
        },
        "保存当前的对话": {
            "AsButton": True,
            "Info": "保存当前的对话 | 不需要输入参数",
            "Function": HotReload(对话历史存档)
        },
        "载入对话历史存档（先上传存档或输入路径）": {
            "Color": "primary",
            "AsButton": False,
            "Info": "载入对话历史存档 | 输入参数为路径",
            "Function": HotReload(载入对话历史存档)
        },
        "删除所有本地对话历史记录（谨慎操作）": {
            "AsButton": False,
            "Info": "删除所有本地对话历史记录，谨慎操作 | 不需要输入参数",
            "Function": HotReload(删除所有本地对话历史记录)
        },
        "清除所有缓存文件（谨慎操作）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "清除所有缓存文件，谨慎操作 | 不需要输入参数",
            "Function": HotReload(清除缓存)
        },
        "连接网络回答问题（输入问题后点击该插件，需要访问谷歌）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(连接网络回答问题)
        },
        "连接网络回答问题（中文Bing版，输入问题后点击该插件）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(连接bing搜索回答问题)
        },
        "询问多个GPT模型（手动指定询问哪些模型）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "支持任意数量的llm接口，用&符号分隔。例如chatglm&gpt-3.5-turbo&api2d-gpt-4",  # 高级参数输入区的显示提示
            "Function": HotReload(同时问询_指定模型)
        },
        "图片生成（先切换模型到openai或api2d）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "在这里输入分辨率, 如256x256（默认）",  # 高级参数输入区的显示提示
            "Info": "图片生成 | 输入参数字符串，提供图像的内容",
            "Function": HotReload(图片生成)
        },
        "批量总结音视频（输入路径或上传压缩包）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "调用openai api 使用whisper-1模型, 目前支持的格式:mp4, m4a, wav, mpga, mpeg, mp3。此处可以输入解析提示，例如：解析为简体中文（默认）。",
            "Info": "批量总结音频或视频 | 输入参数为路径",
            "Function": HotReload(总结音视频)
        },
        "数学动画生成（Manim）": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(动画生成)
        },
        "构建知识库（请先上传文件素材）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "待注入的知识库名称id, 默认为default",
            "Function": HotReload(知识库问答)
        },
        "知识库问答": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "待提取的知识库名称id, 默认为default, 您需要首先调用构建知识库",
            "Function": HotReload(读取知识库作答)
        },
        "交互功能模板函数": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(交互功能模板函数)
        },
        "实时音频采集": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(语音助手)
        },
        "自动终端": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(自动终端)
        }
    }
    # try:
    #     from crazy_functions.chatglm微调工具 import 微调数据集生成
    #     function_plugins['多功能'].update({
    #         "黑盒模型学习: 微调数据集生成 (先上传数据集)": {
    #             "Color": "primary",
    #             "AsButton": False,
    #             "AdvancedArgs": True,
    #             "ArgsReminder": "针对数据集输入（如 绿帽子*深蓝色衬衫*黑色运动裤）给出指令，例如您可以将以下命令复制到下方: --llm_to_learn=azure-gpt-3.5 --prompt_prefix='根据下面的服装类型提示，想象一个穿着者，对这个人外貌、身处的环境、内心世界、过去经历进行描写。要求：100字以内，用第二人称。' --system_prompt=''",
    #             "Function": HotReload(微调数据集生成)
    #         }
    #     })
    # except:
    #     print('Load function plugin failed')

