from comm_tools.toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效
from langchain import agents

# < -------------------初始化插件模块--------------- >
function_plugins = {}

def get_crazy_functions():
    get_functions_学术优化()
    get_functions_文档读取()
    get_functions_代码解析()
    get_functions_多功能插件()
    get_functions_金山专用()
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
        "英文Latex项目全文润色（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英文润色)
        },
        "读Tex论文写摘要": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
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
            "Function": HotReload(谷歌检索小助手)
        },
        "英文Latex项目全文纠错（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex全文润色.Latex英文纠错)
        },
        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex全文润色.Latex中文润色)
        },
        "Latex项目全文中译英（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex全文翻译.Latex中译英)
        },
        "Latex项目全文英译中（输入路径或上传压缩包）": {
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
        "Arixv翻译（输入arxivID）[需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
            "ArgsReminder":
                "如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不Latex英文纠错加PDF对比准确的问题。 " +
                "例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: " + 'If the term "agent" is used in this section, it should be translated to "智能体". ',
            "Function": HotReload(Latex输出PDF结果.Latex翻译中文并重新编译PDF)
        },
        "本地论文翻译（上传Latex压缩包）[需Latex]": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,
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
    function_plugins['文档处理理解'] = {
        "Markdown/Readme英译中": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(批量Markdown翻译.Markdown英译中)
        },
        "批量Markdown中译英": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(批量Markdown翻译.Markdown中译英)
        },
        "批量总结Word文档": {
            "AsButton": False,
            "Color": "primary",
            "Function": HotReload(总结word文档)
        },
        "批量翻译PDF文档（多线程）": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(批量翻译PDF文档_多线程.批量翻译PDF文档)
        },
        "[测试功能] 批量总结PDF文档": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(批量总结PDF文档)
        },
        "理解PDF文档内容 （模仿ChatPDF）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(理解PDF文档内容.理解PDF文档内容标准文件输入)
        },
        "Markdown翻译（手动指定语言）": {
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
            "Info": "解析一个Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析项目源代码.解析一个Python项目)
        },
        "批量生成函数注释": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Function": HotReload(生成函数注释.批量生成函数注释)
        },
        "解析一个C项目的头文件": {
            "Color": "primary",  # 按钮颜色
            "AsButton": True,
            "Function": HotReload(解析项目源代码.解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析项目源代码.解析一个C项目)
        },
        "解析一个Golang项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Function": HotReload(解析项目源代码.解析一个Golang项目)
        },
        "解析一个Rust项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Function": HotReload(解析项目源代码.解析一个Rust项目)
        },
        "解析一个Java项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": True,
            "Function": HotReload(解析项目源代码.解析一个Java项目)
        },
        "解析一个前端项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
            "Function": HotReload(解析项目源代码.解析一个前端项目)
        },
        "解析一个CSharp项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,
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
        "[测试功能] 解析Jupyter Notebook文件": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(解析ipynb文件),
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
    from crazy_functions.图片生成 import 图片生成
    from crazy_functions.数学动画生成manim import 动画生成
    from crazy_functions.交互功能函数模板 import 交互功能模板函数
    from crazy_functions.语音助手 import 语音助手
    from crazy_functions.虚空终端 import 自动终端
    function_plugins['好玩的插件'] = {
        "询问多个GPT模型": {
            "Color": "primary",  # 按钮颜色
            "Function": HotReload(询问多个大语言模型.同时问询)
        },
        "[插件demo] 历史上的今天": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(高阶功能模板函数),
            "AsButton": True,
        },

        "保存当前的对话": {
            "AsButton": True,
            "Function": HotReload(对话历史存档.对话历史存档)
        },
        # "[多线程Demo] 解析此项目本身（源码自译解）": {
        #     "Function": HotReload(解析项目源代码.解析项目本身),
        #     "AsButton": False,  # 加入下拉菜单中
        # },
        # "[老旧的Demo] 把本项目源代码切换成全英文": {
        #     # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Function": HotReload(全项目切换英文)
        "载入对话历史存档（先上传存档或输入路径）": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(对话历史存档.载入对话历史存档)
        },
        "删除所有本地对话历史记录（请谨慎操作）": {
            "AsButton": False,
            "Function": HotReload(对话历史存档.删除所有本地对话历史记录)
        },
        "连接网络回答问题（中文Bing版，输入问题后点击该插件）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(连接bing搜索回答问题)
        },
        "连接网络回答问题（输入问题后点击该插件，需要访问谷歌）": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(连接网络回答问题)
        },
        "询问多个GPT模型（手动指定询问哪些模型）": {
            "Color": "primary",
            "AsButton": False,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "支持任意数量的llm接口，用&符号分隔。例如chatglm&gpt-3.5-turbo&api2d-gpt-4",  # 高级参数输入区的显示提示
            "Function": HotReload(询问多个大语言模型.同时问询_指定模型)
        },
        "图片生成（先切换模型到openai或api2d）": {
            "Color": "primary",
            "AsButton": True,
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "在这里输入分辨率, 如256x256（默认）",  # 高级参数输入区的显示提示
            "Function": HotReload(图片生成)
        },
        "数学动画生成（Manim）": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(动画生成)
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

def get_functions_金山专用():
    # < -------------------金山文档专用--------------- >
    from crazy_functions import KDOCS_轻文档分析
    from crazy_functions import 总结音视频
    from crazy_functions import KDOCS_流程图_图片分析
    desc = '高级参数详细说明请查看项目自述文档, 若有更改，提交前请使用Json检查器检查是否符合要求'
    function_plugins['金山文档专用'] = {
        "文档提取测试点": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_文档提取测试点),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                "提示词分类": '插件定制',
                '格式化文档提示词': '提取文档测试点',
                "显示过程": True,
            }
        },
        "测试点转测试用例": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_转客户端测试用例),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                "提示词分类": '插件定制',
                "预期产出提示词": '文档转测试用例',
                '写入指定模版': 'https://www.kdocs.cn/l/civeYz1Wg2OK',
                '写入指定Sheet': '测试要点',
                "显示过程": False,
            }
        },
        "文档转客户端测试用例": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_转客户端测试用例),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                "提示词分类": '插件定制',
                "格式化文档提示词": '提取文档测试点',
                "预期产出提示词": '文档转测试用例',
                '写入指定模版': 'https://www.kdocs.cn/l/civeYz1Wg2OK',
                '写入指定Sheet': '测试要点',
                "显示过程": False,
            }
        },
        "文档转客户端测试用例(多阶段生成)": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.Kdocs_多阶段生成回答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "开启OCR": True,
                "提示词分类": "插件定制",
                "自动录入知识库": {'业务知识库': '需求文稿'},
                "阶段性产出": {
                    "一阶段": {
                        "提示词": "提取文档测试点",
                        "调用方法": "格式化文档",
                        "关联知识库": {
                            '历史版本测试用例': {"查询列表": ["Apple端测试用例"], "知识库提示词": "用例反推测试点"},
                        }
                    },
                    "二阶段": {
                        "提示词": "文档转测试用例",
                        "调用方法": "写入测试用例"
                    },
                    "三阶段": {
                        "提示词": "三方评审补充用例场景",
                        "调用方法": "补充测试用例",
                        "关联知识库": {
                            '业务知识库': {"查询列表": ["需求文稿"], "知识库提示词": "补充需求文档内容"},
                        }
                    }
                },
                "写入指定模版": "https://www.kdocs.cn/l/civeYz1Wg2OK",
                "写入指定Sheet": "测试要点",
                "显示过程": False
            }
        },
        "文档转接口测试用例": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_转接口测试用例),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                "提示词分类": '插件定制',
                '格式化文档提示词': '文档转Markdown_分割',
                "预期产出提示词": '接口文档转测试用例',
                '写入指定模版': 'https://www.kdocs.cn/l/ckuTJWR6vBtJ',
                '写入指定Sheet': '测试要点',
                "显示过程": False,
            }
        },
        "测试用例检查优化": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_测试用例检查优化),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                '读取指定Sheet': '测试要点',
                "提示词分类": '插件定制',
                "预期产出提示词": '补充测试用例场景',
                "显示过程": False,
            }
        },
        "文档需求分析问答": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_需求分析问答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': False,
                "提示词分类": '插件定制',
                '格式化文档提示词': '文档转Markdown',
                "预期产出提示词": '需求分析对话',
                "显示过程": True,
            }
        },
        "文档转流程图": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_文档转流程图),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                '开启OCR': True,
                "提示词分类": '插件定制',
                '格式化文档提示词': '文档转Markdown',
            }
        },
        "批量总结音视频": {
            "Color": "primary",
            "AsButton": True,
            "AdvancedArgs": True,
            "Function": HotReload(总结音视频.Kdocs音频提取总结),
            "ArgsReminder": desc,  # 高级参数输入区的显示提示
            "Parameters": {
                "提示词分类": '插件定制',
                "预期产出提示词": '总结摘要提取',
            }
        },
        "批量理解流程图、图片": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_流程图_图片分析.批量分析流程图或图片),
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
