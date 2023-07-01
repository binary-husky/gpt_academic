from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效


def get_crazy_functions():
    ###################### 第一组插件 ###########################
    from crazy_functions.读文章写摘要 import 读文章写摘要
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
    from crazy_functions.Latex全文润色 import Latex英文润色
    from crazy_functions.询问多个大语言模型 import 同时问询
    from crazy_functions.解析项目源代码 import 解析一个Lua项目
    from crazy_functions.解析项目源代码 import 解析一个CSharp项目
    from crazy_functions.总结word文档 import 总结word文档
    from crazy_functions.辅助回答 import 猜你想问
    from crazy_functions.解析JupyterNotebook import 解析ipynb文件
    from crazy_functions.对话历史存档 import 对话历史存档
    from crazy_functions.对话历史存档 import 载入对话历史存档
    from crazy_functions.对话历史存档 import 删除所有本地对话历史记录
    from crazy_functions import KDOCS_轻文档分析
    from crazy_functions.批量Markdown翻译 import Markdown英译中
    function_plugins = {
        "猜你想问": {
            "Function": HotReload(猜你想问)
        },
        "解析整个Python项目": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,
            "Function": HotReload(解析一个Python项目)
        },

        "保存当前的对话": {
            "AsButton": True,
            "Function": HotReload(对话历史存档)
        },
        "载入对话历史存档（先上传存档或输入路径）": {
            "Color": "primary",
            "AsButton":False,
            "Function": HotReload(载入对话历史存档)
        },
        "Kdocs_多文件转测试用例(输入框输入文档链接)": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_转测试用例),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "is_show 是否显示过程",  # 高级参数输入区的显示提示
            "Parameters": {
                "is_show": False,
                "prompt": '文档转测试用例',
                'img_ocr': False
            }
        },
        "需求文档转测试用例(输入框输入需求文档)": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.需求转测试用例),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "is_show 是否显示过程",  # 高级参数输入区的显示提示
            "Parameters": {
                "is_show": False,
                "prompt": '文档转测试用例',
                'img_ocr': False,
                'to_markdown': False,
            }
        },
        "KDocs需求分析问答": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_需求分析问答),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "is_show 是否显示过程",  # 高级参数输入区的显示提示
            "Parameters": {
                "is_show": True,
                "prompt": '需求分析对话',
                'img_ocr': False,
                'to_markdown': False,
            }
        },
        "KDocs文档转流程图": {
            "Color": "primary",
            "AsButton": True,
            "Function": HotReload(KDOCS_轻文档分析.KDocs_文档转流程图),
            "AdvancedArgs": True,  # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "is_show 是否显示过程",  # 高级参数输入区的显示提示
            "Parameters": {
                'to_markdown': True,
            }
        },

        "删除所有本地对话历史记录（请谨慎操作）": {
            "AsButton":False,
            "Function": HotReload(删除所有本地对话历史记录)
        },

        "[测试功能] 解析Jupyter Notebook文件": {
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(解析ipynb文件),
            "AdvancedArgs": True, # 调用时，唤起高级参数输入区（默认False）
            "ArgsReminder": "若输入0，则不解析notebook中的Markdown块", # 高级参数输入区的显示提示
        },
        "批量总结Word文档": {
            "AsButton": False,
            "Color": "primary",
            "Function": HotReload(总结word文档)
        },
        "解析整个C++项目头文件": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.hpp/.c/.h）": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个C项目)
        },
        "解析整个Go项目": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Golang项目)
        },
        "解析整个Rust项目": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Rust项目)
        },
        "解析整个Java项目": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Java项目)
        },
        "解析整个前端项目（js,ts,css等）": {
            "Color": "primary",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个前端项目)
        },
        "解析整个Lua项目": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Lua项目)
        },
        "解析整个CSharp项目": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个CSharp项目)
        },
        "读Tex论文写摘要": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(读文章写摘要)
        },
        "Markdown/Readme英译中": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,
            "Function": HotReload(Markdown英译中)
        },
        "批量生成函数注释": {
            "Color": "primary",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(批量生成函数注释)
        },
        "[多线程Demo] 解析此项目本身（源码自译解）": {
            "Function": HotReload(解析项目本身),
            "AsButton": False,  # 加入下拉菜单中
        },
        # "[老旧的Demo] 把本项目源代码切换成全英文": {
        #     # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Function": HotReload(全项目切换英文)
        # },
        "[插件demo] 历史上的今天": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(高阶功能模板函数),
            "AsButton": False,
        },

    }
    ###################### 第二组插件 ###########################
    # [第二组插件]: 经过充分测试
    from crazy_functions.批量总结PDF文档 import 批量总结PDF文档
    # from crazy_functions.批量总结PDF文档pdfminer import 批量总结PDF文档pdfminer
    from crazy_functions.批量翻译PDF文档_多线程 import 批量翻译PDF文档
    from crazy_functions.谷歌检索小助手 import 谷歌检索小助手
    from crazy_functions.理解PDF文档内容 import 理解PDF文档内容标准文件输入
    from crazy_functions.Latex全文润色 import Latex中文润色
    from crazy_functions.Latex全文润色 import Latex英文纠错
    from crazy_functions.Latex全文翻译 import Latex中译英
    from crazy_functions.Latex全文翻译 import Latex英译中
    from crazy_functions.批量Markdown翻译 import Markdown中译英

    function_plugins.update({
        "批量翻译PDF文档（多线程）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(批量翻译PDF文档)
        },
        "询问多个GPT模型": {
            "Color": "primary",    # 按钮颜色
            "Function": HotReload(同时问询)
        },
        "[测试功能] 批量总结PDF文档": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(批量总结PDF文档)
        },
        # "[测试功能] 批量总结PDF文档pdfminer": {
        #     "Color": "primary",
        #     "AsButton": False,  # 加入下拉菜单中
        #     "Function": HotReload(批量总结PDF文档pdfminer)
        # },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(谷歌检索小助手)
        },
        "理解PDF文档内容 （模仿ChatPDF）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(理解PDF文档内容标准文件输入)
        },
        "英文Latex项目全文润色（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英文润色)
        },
        "英文Latex项目全文纠错（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英文纠错)
        },
        "中文Latex项目全文润色（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex中文润色)
        },
        "Latex项目全文中译英（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex中译英)
        },
        "Latex项目全文英译中（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Latex英译中)
        },
        "批量Markdown中译英（输入路径或上传压缩包）": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Color": "primary",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(Markdown中译英)
        },


    })

    ###################### 第三组插件 ###########################
    # [第三组插件]: 尚未充分测试的函数插件
    from crazy_functions.联网的ChatGPT import 连接网络回答问题
    function_plugins.update({
        "连接网络回答问题": {
            "Color": "primary",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(连接网络回答问题)
        }
    })
