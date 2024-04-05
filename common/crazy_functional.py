from common.toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效
from langchain import agents


# < -------------------初始化插件模块--------------- >


def get_crazy_functions():
    get_functions_学术优化()
    get_functions_文档读取()
    get_functions_代码解析()
    get_functions_多功能插件()
    get_functions_云文档()
    get_functions_飞书项目()
    return function_plugins


def get_functions_学术优化():
    # < -------------------学术研究--------------- >
    from crazy_functions import Latex输出PDF结果
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.Latex全文润色 import Latex英文润色
    from crazy_functions.下载arxiv论文翻译摘要 import 下载arxiv论文并翻译摘要
    from crazy_functions import 谷歌检索小助手
    from crazy_functions import Latex全文润色
    from crazy_functions import Latex全文翻译
    function_plugins['学术研究'] = {
        "英文Latex项目全文润色": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对英文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex英文润色)
        },
        "读Tex论文写摘要": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Info": "读取Tex论文并写摘要 | 输入参数为路径",
            "Function": HotReload(读文章写摘要)
        },
        # "[测试功能] 批量总结PDF文档pdfminer": {
        #     "Color": "primary",
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Function": HotReload(批量总结PDF文档pdfminer)
        # },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Info": "使用谷歌学术检索助手搜索指定URL的结果 | 输入参数为谷歌学术搜索页的URL",
            "Function": HotReload(谷歌检索小助手)
        },
        "英文Latex项目全文纠错": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对英文Latex项目全文进行纠错处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex全文润色.Latex英文纠错)
        },
        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "对中文Latex项目全文进行润色处理 | 输入参数为路径或上传压缩包",
            "Function": HotReload(Latex全文润色.Latex中文润色)
        },
        "Latex项目全文中译英": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex全文翻译.Latex中译英)
        },
        "Latex项目全文英译中": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex全文翻译.Latex英译中)
        },
        "一键下载arxiv论文并翻译摘要（先在input输入编号，如1812.10695）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(下载arxiv论文并翻译摘要)
        },
        "Latex英文纠错+高亮修正位置 [需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "如果有必要, 请在此处追加更细致的矫错指令（使用英文）。",
            "Function": HotReload(Latex输出PDF结果.Latex英文纠错加PDF对比)
        },
        "Arixv论文精细翻译（输入arxivID）[需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "Info": "Arixv论文精细翻译 | 输入参数arxiv论文的ID，比如1812.10695",
            "ArgsReminder":
                "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不Latex英文纠错加PDF对比准确的问题。 " +
                "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " + 'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Function": HotReload(Latex输出PDF结果.Latex翻译中文并重新编译PDF)
        },
        "本地Latex论文精细翻译（上传Latex压缩包）[需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "Info": "本地Latex论文精细翻译 | 输入参数是路径",
            "ArgsReminder":
                "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 " +
                "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " + 'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Function": HotReload(Latex输出PDF结果.Latex翻译中文并重新编译PDF)
        }
    }


def get_functions_文档读取():
    # < -------------------文档处理--------------- >
    from crazy_functions.总结word文档 import 总结word文档
    from crazy_functions import 批量总结PDF文档
    from crazy_functions import 批量翻译PDF文档_多线程
    from crazy_functions import 理解PDF文档内容
    from crazy_functions import 批量Markdown翻译
    function_plugins['文档处理'] = {
        "Markdown/Readme英译中": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,
            "Info": "将Markdown翻译为中文 | 输入参数为路径或URL",
            "Function": HotReload(批量Markdown翻译.Markdown英译中)
        },
        "批量Markdown中译英": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Info": "批量将Markdown文件中文翻译为英文 | 输入参数为路径或上传压缩包",
            "Function": HotReload(批量Markdown翻译.Markdown中译英)
        },
        "批量总结Word文档": {
            "AsButton": False,
            "Color": "primary",
            "Info": "批量总结word文档 | 输入参数为路径",
            "Function": HotReload(总结word文档)
        },
        "精准翻译PDF论文": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Info": "精准翻译PDF论文为中文 | 输入参数为路径",
            "Function": HotReload(批量翻译PDF文档_多线程.批量翻译PDF文档)
        },
        "批量总结PDF文档": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "批量总结PDF文档的内容 | 输入参数为路径",
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(批量总结PDF文档)
        },
        "理解PDF文档内容": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "Info": "理解PDF文档的内容并进行回答 | 输入参数为路径",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(理解PDF文档内容.理解PDF文档内容标准文件输入)
        },
        "Markdown翻译": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder": "请输入要翻译成哪种语言，默认为Chinese。",
            "Function": HotReload(批量Markdown翻译.Markdown翻译指定语言)
        },

    }


def get_functions_代码解析():
    # < -------------------开发--------------- >
    from crazy_functions import 生成函数注释
    from crazy_functions import 解析项目源代码
    from crazy_functions.解析JupyterNotebook import 解析ipynb文件
    function_plugins['代码分析'] = {
        "解析整个Python项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": True,
            "Info": "解析Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Python项目)
        },
        "批量生成函数注释": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Info": "批量生成函数的注释 | 输入参数为路径",
            "Function": HotReload(生成函数注释.批量生成函数注释)
        },
        "解析整个Matlab项目": {
            "Color": "stop",
            "AsButton": False,
            "Info": "解析Matlab项目的所有源文件(.m) | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Matlab项目)
        },
        "解析一个C项目的头文件": {
            "Color": "primary",  # 按钮颜色
            "AsButton": True,
            "Info": "解析一个C++项目的所有头文件(.h/.hpp) | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个C++项目的所有源文件（.cpp/.hpp/.c/.h）| 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个C项目)
        },
        "解析一个Golang项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Info": "解析一个Go项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Golang项目)
        },
        "解析一个Rust项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Info": "解析一个Rust项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Rust项目)
        },
        "解析一个Java项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": True,
            "Info": "解析一个Java项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Java项目)
        },
        "解析一个前端项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Info": "解析一个前端项目的所有源文件（js,ts,css等） | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个前端项目)
        },
        "解析整个Lua项目": {
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "解析一个Lua项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Lua项目)
        },
        "解析一个CSharp项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Info": "解析一个CSharp项目的所有源文件 | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个CSharp项目)
        },
        "解析项目源代码（手动指定和筛选源代码文件类型）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "输入时用逗号隔开, *代表通配符, 加了^代表不匹配; 不输入代表全部匹配。例如: \"*.c, ^*.cpp, config.toml, ^*.toml\"",
            # 高级参数输入区的显示提示
            "Function": HotReload(解析项目源代码.解析任意code项目)
        },
        "解析Jupyter Notebook文件": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(解析ipynb文件),
            "Info": "解析Jupyter Notebook文件 | 输入参数为路径",
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "若输入0，则不解析notebook中的Markdown块",  # 高级参数输入区的显示提示
        },
    }


def get_functions_多功能插件():
    # < -------------------试玩插件--------------- >
    from crazy_functions import 对话历史存档
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions import 询问多个大语言模型
    from crazy_functions.联网的ChatGPT_bing版 import 连接bing搜索回答问题
    from crazy_functions.联网的ChatGPT import 连接网络回答问题
    from crazy_functions.图片生成 import 图片生成_DALLE2
    from crazy_functions.图片生成 import 图片生成_DALLE3
    from crazy_functions.数学动画生成manim import 动画生成
    from crazy_functions.交互功能函数模板 import 交互功能模板函数
    from crazy_functions.语音助手 import 语音助手
    from crazy_functions.虚空终端 import 虚空终端
    from crazy_functions.函数动态生成 import 函数动态生成
    from crazy_functions.多智能体 import 多智能体终端
    from crazy_functions.互动小游戏 import 随机小游戏
    function_plugins['多功能'] = {
        "动态代码解释器（CodeInterpreter）": {
            "Group": "智能体",
            "Color": "stop",
            "AsButton": False,
            "Function": HotReload(函数动态生成)
        },
        "历史上的今天": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(高阶功能模板函数),
            "Info": "查看历史上的今天事件 (这是一个面向开发者的插件Demo) | 不需要输入参数",
            "AsButton": True,
        },
        "AutoGen多智能体终端（仅供测试）": {
            "Group": "智能体",
            "Color": "stop",
            "AsButton": False,
            "Function": HotReload(多智能体终端)

        },
        "随机互动小游戏（仅供测试）": {
            "Group": "智能体",
            "Color": "stop",
            "AsButton": False,
            "Function": HotReload(随机小游戏)
        }
        ,
        # "保存当前的对话": {
        #     "AsButton": True,
        #     "Function": HotReload(对话历史存档.对话历史存档)
        # },
        # "[多线程Demo] 解析此项目本身（源码自译解）": {
        #     "Function": HotReload(解析项目源代码.解析项目本身),
        #     "AsButton": False,  # 加入下拉菜单中
        # },
        # "[老旧的Demo] 把本项目源代码切换成全英文": {
        #     # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Function": HotReload(全项目切换英文)
        # "载入对话历史存档（先上传存档或输入路径）": {
        #     "Color": "primary",
        #     "AsButton": False,
        #     "Function": HotReload(对话历史存档.载入对话历史存档)
        # },
        # "删除所有本地对话历史记录（请谨慎操作）": {
        #     "AsButton": False,
        #     "Function": HotReload(对话历史存档.删除所有本地对话历史记录)
        # },
        "连接网络回答问题（Bing）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Info": "连接网络回答问题（需要访问中文Bing）| 输入参数是一个问题",
            "Function": HotReload(连接bing搜索回答问题)
        },
        "连接网络回答问题(谷歌)": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Info": "连接网络回答问题（需要访问谷歌）| 输入参数是一个问题",
            "Function": HotReload(连接网络回答问题)
        },
        "询问多个GPT模型": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "支持任意数量的llm接口，用&符号分隔。例如chatglm&gpt-3.5-turbo&api2d-gpt-4",  # 高级参数输入区的显示提示
            "Function": HotReload(询问多个大语言模型.同时问询_指定模型)
        },
        "图片生成_DALLE2 （先切换模型到openai或api2d）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "在这里输入分辨率, 如1024x1024（默认），支持 256x256, 512x512, 1024x1024",  # 高级参数输入区的显示提示
            "Info": "使用DALLE2生成图片 | 输入参数字符串，提供图像的内容",
            "Function": HotReload(图片生成_DALLE2)
        },
        "图片生成_DALLE3 （先切换模型到openai或api2d）": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "在这里输入分辨率, 如1024x1024（默认），支持 1024x1024, 1792x1024, 1024x1792。如需生成高清图像，请输入 1024x1024-HD, 1792x1024-HD, 1024x1792-HD。",
            # 高级参数输入区的显示提示
            "Info": "使用DALLE3生成图片 | 输入参数字符串，提供图像的内容",
            "Function": HotReload(图片生成_DALLE3)
        },
        "数学动画生成（Manim）": {
            "Color": "primary",
            "AsButton": False,
            "Info": "按照自然语言描述生成一个动画 | 输入参数是一段话",
            "Function": HotReload(动画生成)
        },
        "交互功能模板函数": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(交互功能模板函数)
        },
        "实时语音对话": {
            "Group": "对话",
            "Color": "stop",
            "AsButton": True,
            "Info": "这是一个时刻聆听着的语音对话助手 | 没有输入参数",
            "Function": HotReload(语音助手)
        },
        "插件代理助手": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(虚空终端)
        }

    }


reader_files = ['md', 'txt', 'pdf', 'docx', 'xmind', '智能文档']
desc = '高级参数详细说明请查看项目自述文档， 提交前请使用Json检查器检查是否符合要求'


def get_functions_飞书项目():
    from crazy_functions import Project_飞书项目
    function_plugins['飞书项目'] = {
        "获取前后一周的需求": {
            "Color": "secondary",
            "AsButton": True,
            "Function": HotReload(Project_飞书项目.Project_获取项目数据),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "筛选时间范围": 7,
                "筛选未排期需求": '未排期',
                "提示词分类": "插件定制",
                "定制化流程": [{
                    "提示词": "总结项目数据"
                },],
                "处理文件类型": ['*']
            }
        }
    }


def get_functions_云文档():
    # < -------------------云文档专用--------------- >
    from crazy_functions import Reader_自定义插件流程
    function_plugins['云文档'] = {
        "文档提取测试点": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                "定制化流程": [{
                    "提示词": "提取文档测试点"
                },
                ],
                "处理文件类型": reader_files
            }
        },
        "需求文档转测试用例": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "定制化流程": [{
                    "提示词": "文档转测试用例",
                    "保存结果": "写入测试用例",
                }],
                "写入指定模版": "./docs/template/测试用例模版.xlsx",
                "写入指定Sheet": "测试要点",
                "处理文件类型": reader_files
            }
        },
        "接口文档转测试用例": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "定制化流程": [{
                    "提示词": "文档转Markdown_分割",
                    "保存结果": "结果写入Markdown"
                }, {
                    "提示词": "接口文档转测试用例",
                    "保存结果": "写入测试用例",
                }
                ],
                "写入指定模版": "./docs/template/接口测试用例模板.xlsx",
                "写入指定Sheet": "测试要点",
                "处理文件类型": reader_files
            }
        },
        "测试用例检查优化": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "定制化流程": [{
                    "提示词": "三方评审补充用例场景",
                    "保存结果": "补充测试用例",
                }
                ],
                "写入指定模版": "./docs/template/接口测试用例模板.xlsx",
                "写入指定Sheet": "测试要点",
                "处理文件类型": ['xlsx']
            },

        },
        "文档需求分析问答": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "上下文关联": True,
                "定制化流程": [{
                    "提示词": "需求分析对话"}
                ],
                "处理文件类型": reader_files
            }
        },
        "文档转流程图": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "定制化流程": [{
                    "提示词": "文档转Markdown",
                    "保存结果": "Markdown转换为流程图",
                }
                ],
                "处理文件类型": reader_files
            }
        },
        "批量总结音视频": {
            "Color": "primary",
            "AsButton": True,
            "AdvancedArgs": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Info": "批量总结音频或视频 | 输入参数为路径",
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                '用例下标排序': None,
                "上下文关联": True,
                "定制化流程": [{
                    "提示词": "总结摘要提取",
                    "保存结果": "Markdown转换为流程图",
                }
                ],
                "处理文件类型": ['.mp4', '.m4a', '.wav', '.mpga', '.mpeg', '.mp3', '.avi', '.mkv', '.flac', '.aac'],
            }
        },
        "需求文档转测试用例(全配置)": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(Reader_自定义插件流程.Reader_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": {"llm_model": 'gemini-pro-vision'},
                "提示词分类": "插件定制",
                "多模型并行": "gpt-3.5-turbo-16k-0613&",
                "自动录入知识库": {'个人知识库': '需求文稿'},
                '用例下标排序': None,
                "定制化流程": [{
                    "提示词": "文档转测试用例",
                    "保存结果": "写入测试用例"
                }, {
                    "提示词": "三方评审补充用例场景",
                    "保存结果": "补充测试用例",
                    "关联知识库": {
                        '业务知识库': {"查询列表": ["需求文稿"], "知识库提示词": "补充需求文档内容"},
                    }}
                ],
                "上下文关联": False,
                "写入指定模版": "./docs/template/测试用例模版.xlsx",
                "写入指定Sheet": "测试要点",
                "处理文件类型": reader_files
            }
        },

    }
    return function_plugins


def crazy_func_to_tool():
    crazy_kwargs = get_crazy_functions()
    crazy_tools = []
    for crazy in crazy_kwargs:
        for func in crazy_kwargs[crazy]:
            crazy_tools.append(agents.Tool(name=crazy, func=crazy_kwargs[crazy][func]['Function'], description=func))
    return crazy_tools


function_plugins = {}
crazy_fns_role = get_crazy_functions()
crazy_classification = [i for i in crazy_fns_role]
crazy_fns = {}
for role in crazy_fns_role:
    for k in crazy_fns_role[role]:
        crazy_fns[k] = crazy_fns_role[role][k]

if __name__ == '__main__':
    print(crazy_fns)
