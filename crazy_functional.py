from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效


def get_crazy_functions():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个Matlab项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.解析项目源代码 import 解析一个Golang项目
    from crazy_functions.解析项目源代码 import 解析一个Rust项目
    from crazy_functions.解析项目源代码 import 解析一个Java项目
    from crazy_functions.解析项目源代码 import 解析一个前端项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.Latex全文润色 import Latex英文润色
    from crazy_functions.询问多个大语言模型 import 同时问询
    from crazy_functions.解析项目源代码 import 解析一个Lua项目
    from crazy_functions.解析项目源代码 import 解析一个CSharp项目
    from crazy_functions.总结word文档 import 总结word文档
    from crazy_functions.解析JupyterNotebook import 解析ipynb文件
    from crazy_functions.对话历史存档 import 对话历史存档
    from crazy_functions.对话历史存档 import 载入对话历史存档
    from crazy_functions.对话历史存档 import 删除所有本地对话历史记录
    from crazy_functions.辅助功能 import 清除缓存
    from crazy_functions.批量Markdown翻译 import Markdown英译中
    from crazy_functions.批量总结PDF文档 import 批量总结PDF文档
    from crazy_functions.批量翻译PDF文档_多线程 import 批量翻译PDF文档
    from crazy_functions.谷歌检索小助手 import 谷歌检索小助手
    from crazy_functions.理解PDF文档内容 import 理解PDF文档内容标准文件输入
    from crazy_functions.Latex全文润色 import Latex中文润色
    from crazy_functions.Latex全文润色 import Latex英文纠错
    from crazy_functions.Latex全文翻译 import Latex中译英
    from crazy_functions.Latex全文翻译 import Latex英译中
    from crazy_functions.批量Markdown翻译 import Markdown中译英
    from crazy_functions.虚空终端 import 虚空终端


    function_plugins = {
        "虚空终端": {
            "Group": "对话|编程|学术|智能体",
            "Color": "stop",
            "AsButton": True,
            "Function": HotReload(虚空终端)
        },
        "解析整个Python项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": True,
            "Info": "解析一个Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析一个Python项目)
        },
        "载入对话历史存档（先上传存档或输入路径）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "Info": "载入对话历史存档 | 输入参数为路径",
            "Function": HotReload(载入对话历史存档)
        },
        "删除所有本地对话历史记录（谨慎操作）": {
            "Group": "对话",
            "AsButton": False,
            "Info": "删除所有本地对话历史记录，谨慎操作 | 不需要输入参数",
            "Function": HotReload(删除所有本地对话历史记录)
        },
        "清除所有缓存文件（谨慎操作）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "清除所有缓存文件，谨慎操作 | 不需要输入参数",
            "Function": HotReload(清除缓存)
        },
        "批量总结Word文档": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": True,
            "Info": "批量总结word文档 | 输入参数为路径",
            "Function": HotReload(总结word文档)
        },
        "解析整个Matlab项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "解析一个Matlab项目的所有源文件(.m) | 输入参数为路径",
            "Function": HotReload(解析一个Matlab项目)
        },
        "解析整个C++项目头文件": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有头文件(.h/.hpp) | 输入参数为路径",
            "Function": HotReload(解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有源文件（.cpp/.hpp/.c/.h）| 输入参数为路径",
            "Function": HotReload(解析一个C项目)
        },
        "解析整个Go项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Go项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Golang项目)
        },
        "解析整个Rust项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Rust项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Rust项目)
        },
        "解析整个Java项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Java项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Java项目)
        },
        "解析整个前端项目（js,ts,css等）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个前端项目的所有源文件（js,ts,css等） | 输入参数为路径",
            "Function": HotReload(解析一个前端项目)
        },
        "解析整个Lua项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Lua项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个Lua项目)
        },
        "解析整个CSharp项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个CSharp项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析一个CSharp项目)
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
            "Function": HotReload(读文章写摘要)
        },
        "翻译README或MD": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": True,
            "Info": "将Markdown翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(Markdown英译中)
        },
        "翻译Markdown或README（支持Github链接）": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,
            "Info": "将Markdown或README翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(Markdown英译中)
        },
        "批量生成函数注释": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量生成函数的注释 | 输入参数为路径",
            "Function": HotReload(批量生成函数注释)
        },
        "保存当前的对话": {
            "Group": "对话",
            "AsButton": True,
            "Info": "保存当前的对话 | 不需要输入参数",
            "Function": HotReload(对话历史存档)
        },
        "[多线程Demo]解析此项目本身（源码自译解）": {
            "Group": "对话|编程",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "多线程解析并翻译此项目的源码 | 不需要输入参数",
            "Function": HotReload(解析项目本身)
        },
        "历史上的今天": {
            "Group": "对话",
            "AsButton": True,
            "Info": "查看历史上的今天事件 (这是一个面向开发者的插件Demo) | 不需要输入参数",
            "Function": HotReload(高阶功能模板函数)
        },
        "精准翻译PDF论文": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": True,  
            "Info": "精准翻译PDF论文为中文 | 输入参数为路径",
            "Function": HotReload(批量翻译PDF文档)
        },
        "询问多个GPT模型": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": True,
            "Function": HotReload(同时问询)
        },
        "批量总结PDF文档": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量总结PDF文档的内容 | 输入参数为路径",
            "Function": HotReload(批量总结PDF文档)
        },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "使用谷歌学术检索助手搜索指定URL的结果 | 输入参数为谷歌学术搜索页的URL",
            "Function": HotReload(谷歌检索小助手)
        },
        "理解PDF文档内容 （模仿ChatPDF）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "理解PDF文档的内容并进行回答 | 输入参数为路径",
            "Function": HotReload(理解PDF文档内容标准文件输入)
        },
        "英文Latex项目全文润色（输入路径或上传压缩包）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对英文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex英文润色)
        },
        "英文Latex项目全文纠错（输入路径或上传压缩包）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对英文Latex项目全文进行纠错处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex英文纠错)
        },
        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对中文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex中文润色)
        },

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
            "Function": HotReload(Markdown中译英)
        },
    }

    # -=--=- 尚未充分测试的实验性插件 & 需要额外依赖的插件 -=--=-
    try:
        from crazy_functions.下载arxiv论文翻译摘要 import 下载arxiv论文并翻译摘要
        function_plugins.update({
            "一键下载arxiv论文并翻译摘要（先在input输入编号，如1812.10695）": {
                "Group": "学术",
                "Color": "stop",
                "AsButton": False,  # 加入下拉菜单中
                # "Info": "下载arxiv论文并翻译摘要 | 输入参数为arxiv编号如1812.10695",
                "Function": HotReload(下载arxiv论文并翻译摘要)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.联网的ChatGPT import 连接网络回答问题
        function_plugins.update({
            "连接网络回答问题（输入问题后点击该插件，需要访问谷歌）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,  # 加入下拉菜单中
                # "Info": "连接网络回答问题（需要访问谷歌）| 输入参数是一个问题",
                "Function": HotReload(连接网络回答问题)
            }
        })
        from crazy_functions.联网的ChatGPT_bing版 import 连接bing搜索回答问题
        function_plugins.update({
            "连接网络回答问题（中文Bing版，输入问题后点击该插件）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,  # 加入下拉菜单中
                "Info": "连接网络回答问题（需要访问中文Bing）| 输入参数是一个问题",
                "Function": HotReload(连接bing搜索回答问题)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.解析项目源代码 import 解析任意code项目
        function_plugins.update({
            "解析项目源代码（手动指定和筛选源代码文件类型）": {
                "Group": "编程",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
                "ArgsReminder": "输入时用逗号隔开, *代表通配符, 加了^代表不匹配; 不输入代表全部匹配。例如: \"*.c, ^*.cpp, config.toml, ^*.toml\"",  # 高级参数输入区的显示提示
                "Function": HotReload(解析任意code项目)
            },
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.询问多个大语言模型 import 同时问询_指定模型
        function_plugins.update({
            "询问多个GPT模型（手动指定询问哪些模型）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
                "ArgsReminder": "支持任意数量的llm接口，用&符号分隔。例如chatglm&gpt-3.5-turbo&api2d-gpt-4",  # 高级参数输入区的显示提示
                "Function": HotReload(同时问询_指定模型)
            },
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.图片生成 import 图片生成
        function_plugins.update({
            "图片生成（先切换模型到openai或api2d）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
                "ArgsReminder": "在这里输入分辨率, 如256x256（默认）",  # 高级参数输入区的显示提示
                "Info": "图片生成 | 输入参数字符串，提供图像的内容",
                "Function": HotReload(图片生成)
            },
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.总结音视频 import 总结音视频
        function_plugins.update({
            "批量总结音视频（输入路径或上传压缩包）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder": "调用openai api 使用whisper-1模型, 目前支持的格式:mp4, m4a, wav, mpga, mpeg, mp3。此处可以输入解析提示，例如：解析为简体中文（默认）。",
                "Info": "批量总结音频或视频 | 输入参数为路径",
                "Function": HotReload(总结音视频)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.数学动画生成manim import 动画生成
        function_plugins.update({
            "数学动画生成（Manim）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "Info": "按照自然语言描述生成一个动画 | 输入参数是一段话",
                "Function": HotReload(动画生成)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.批量Markdown翻译 import Markdown翻译指定语言
        function_plugins.update({
            "Markdown翻译（指定翻译成何种语言）": {
                "Group": "编程",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder": "请输入要翻译成哪种语言，默认为Chinese。",
                "Function": HotReload(Markdown翻译指定语言)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.Langchain知识库 import 知识库问答
        function_plugins.update({
            "构建知识库（先上传文件素材,再运行此插件）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder": "此处待注入的知识库名称id, 默认为default。文件进入知识库后可长期保存。可以通过再次调用本插件的方式，向知识库追加更多文档。",
                "Function": HotReload(知识库问答)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.Langchain知识库 import 读取知识库作答
        function_plugins.update({
            "知识库问答（构建知识库后,再运行此插件）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder": "待提取的知识库名称id, 默认为default, 您需要构建知识库后再运行此插件。",
                "Function": HotReload(读取知识库作答)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.交互功能函数模板 import 交互功能模板函数
        function_plugins.update({
            "交互功能模板Demo函数（查找wallhaven.cc的壁纸）": {
                "Group": "对话",
                "Color": "stop",
                "AsButton": False,
                "Function": HotReload(交互功能模板函数)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.Latex输出PDF结果 import Latex英文纠错加PDF对比
        function_plugins.update({
            "Latex英文纠错+高亮修正位置 [需Latex]": {
                "Group": "学术",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder": "如果有必要, 请在此处追加更细致的矫错指令（使用英文）。",
                "Function": HotReload(Latex英文纠错加PDF对比)
            }
        })
        from crazy_functions.Latex输出PDF结果 import Latex翻译中文并重新编译PDF
        function_plugins.update({
            "Arixv论文精细翻译（输入arxivID）[需Latex]": {
                "Group": "学术",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder":
                    "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 " +
                    "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " +
                    'If the term "agent" is used in this section, it should be translated to "智能体". ',
                "Info": "Arixv论文精细翻译 | 输入参数arxiv论文的ID，比如1812.10695",
                "Function": HotReload(Latex翻译中文并重新编译PDF)
            }
        })
        function_plugins.update({
            "本地Latex论文精细翻译（上传Latex项目）[需Latex]": {
                "Group": "学术",
                "Color": "stop",
                "AsButton": False,
                "AdvancedArgs": True,
                "ArgsReminder":
                    "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 " +
                    "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " +
                    'If the term "agent" is used in this section, it should be translated to "智能体". ',
                "Info": "本地Latex论文精细翻译 | 输入参数是路径",
                "Function": HotReload(Latex翻译中文并重新编译PDF)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from toolbox import get_conf
        ENABLE_AUDIO, = get_conf('ENABLE_AUDIO')
        if ENABLE_AUDIO:
            from crazy_functions.语音助手 import 语音助手
            function_plugins.update({
                "实时语音对话": {
                    "Group": "对话",
                    "Color": "stop",
                    "AsButton": True,
                    "Info": "这是一个时刻聆听着的语音对话助手 | 没有输入参数",
                    "Function": HotReload(语音助手)
                }
            })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.批量翻译PDF文档_NOUGAT import 批量翻译PDF文档
        function_plugins.update({
            "精准翻译PDF文档（NOUGAT）": {
                "Group": "学术",
                "Color": "stop",
                "AsButton": False,
                "Function": HotReload(批量翻译PDF文档)
            }
        })
    except:
        print('Load function plugin failed')

    try:
        from crazy_functions.函数动态生成 import 函数动态生成
        function_plugins.update({
            "动态代码解释器（CodeInterpreter）": {
                "Group": "智能体",
                "Color": "stop",
                "AsButton": False,
                "Function": HotReload(函数动态生成)
            }
        })
    except:
        print('Load function plugin failed')


    # try:
    #     from crazy_functions.chatglm微调工具 import 微调数据集生成
    #     function_plugins.update({
    #         "黑盒模型学习: 微调数据集生成 (先上传数据集)": {
    #             "Color": "stop",
    #             "AsButton": False,
    #             "AdvancedArgs": True,
    #             "ArgsReminder": "针对数据集输入（如 绿帽子*深蓝色衬衫*黑色运动裤）给出指令，例如您可以将以下命令复制到下方: --llm_to_learn=azure-gpt-3.5 --prompt_prefix='根据下面的服装类型提示，想象一个穿着者，对这个人外貌、身处的环境、内心世界、过去经历进行描写。要求：100字以内，用第二人称。' --system_prompt=''",
    #             "Function": HotReload(微调数据集生成)
    #         }
    #     })
    # except:
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
            function_plugins[name]["Group"] = '对话'
        if "AsButton" not in function_meta:
            function_plugins[name]["AsButton"] = True
        if "AdvancedArgs" not in function_meta:
            function_plugins[name]["AdvancedArgs"] = False
        if "Color" not in function_meta:
            function_plugins[name]["Color"] = 'secondary'

    return function_plugins
