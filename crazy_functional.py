from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效


def get_crazy_functions():
    ###################### 第一组插件 ###########################
    # [第一组插件]: 最早期编写的项目插件和一些demo
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.解析项目源代码 import 解析一个Golang项目
    from crazy_functions.解析项目源代码 import 解析一个Java项目
    from crazy_functions.解析项目源代码 import 解析一个Rect项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.代码重写为全英文_多线程 import 全项目切换英文

    function_plugins = {
        "请解析并解构此项目本身（源码自译解）": {
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析项目本身)
        },
        "解析整个Python项目": {
            "Color": "stop",    # 按钮颜色
            "Function": HotReload(解析一个Python项目)
        },
        "解析整个C++项目头文件": {
            "Color": "stop",    # 按钮颜色
            "Function": HotReload(解析一个C项目的头文件)
        },
        "解析整个C++项目（.cpp/.h）": {
            "Color": "stop",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个C项目)
        },
        "解析整个Go项目": {
            "Color": "stop",    # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Golang项目)
        },
        "解析整个Java项目": {
            "Color": "stop",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Java项目)
        },
        "解析整个React项目": {
            "Color": "stop",  # 按钮颜色
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(解析一个Rect项目)
        },
        "读Tex论文写摘要": {
            "Color": "stop",    # 按钮颜色
            "Function": HotReload(读文章写摘要)
        },
        "批量生成函数注释": {
            "Color": "stop",    # 按钮颜色
            "Function": HotReload(批量生成函数注释)
        },
        "[多线程demo] 把本项目源代码切换成全英文": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(全项目切换英文)
        },
        "[函数插件模板demo] 历史上的今天": {
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(高阶功能模板函数)
        },
    }
    ###################### 第二组插件 ###########################
    # [第二组插件]: 经过充分测试，但功能上距离达到完美状态还差一点点
    from crazy_functions.批量总结PDF文档 import 批量总结PDF文档
    from crazy_functions.批量总结PDF文档pdfminer import 批量总结PDF文档pdfminer
    from crazy_functions.总结word文档 import 总结word文档
    from crazy_functions.批量翻译PDF文档_多线程 import 批量翻译PDF文档
    from crazy_functions.谷歌检索小助手 import 谷歌检索小助手

    function_plugins.update({
        "批量翻译PDF文档（多线程）": {
            "Color": "stop",
            "AsButton": True,  # 加入下拉菜单中
            "Function": HotReload(批量翻译PDF文档)
        },
        "[仅供开发调试] 批量总结PDF文档": {
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            # HotReload 的意思是热更新，修改函数插件代码后，不需要重启程序，代码直接生效
            "Function": HotReload(批量总结PDF文档)
        },
        "[仅供开发调试] 批量总结PDF文档pdfminer": {
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(批量总结PDF文档pdfminer)
        },
        "谷歌学术检索助手（输入谷歌学术搜索页url）": {
            "Color": "stop",
            "AsButton": False,  # 加入下拉菜单中
            "Function": HotReload(谷歌检索小助手)
        },
        "批量总结Word文档": {
            "Color": "stop",
            "Function": HotReload(总结word文档)
        },
    })

    ###################### 第三组插件 ###########################
    # [第三组插件]: 尚未充分测试的函数插件，放在这里
    try:
        from crazy_functions.下载arxiv论文翻译摘要 import 下载arxiv论文并翻译摘要
        function_plugins.update({
            "一键下载arxiv论文并翻译摘要（先在input输入编号，如1812.10695）": {
                "Color": "stop",
                "AsButton": False,  # 加入下拉菜单中
                "Function": HotReload(下载arxiv论文并翻译摘要)
            }
        })

    except Exception as err:
        print(f'[下载arxiv论文并翻译摘要] 插件导入失败 {str(err)}')

    ###################### 第n组插件 ###########################
    return function_plugins
