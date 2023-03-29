# UserVisibleLevel是过滤器参数。
# 由于UI界面空间有限，所以通过这种方式决定UI界面中显示哪些插件
# 默认函数插件 VisibleLevel 是 0
# 当 UserVisibleLevel >= 函数插件的 VisibleLevel 时，该函数插件才会被显示出来
UserVisibleLevel = 0

def get_crazy_functionals():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.代码重写为全英文_多线程 import 全项目切换英文

    function_plugins = {
        "[实验] 请解析并解构此项目本身": {
            "Function": 解析项目本身
        },
        "[实验] 解析整个py项目（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个Python项目
        },
        "[实验] 解析整个C++项目头文件（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个C项目的头文件
        },
        "[实验] 解析整个C++项目（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个C项目
        },
        "[实验] 读tex论文写摘要（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 读文章写摘要
        },
        "[实验] 批量生成函数注释（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 批量生成函数注释
        },
        "[实验] 把本项目源代码切换成全英文（多线程demo）": {
            "Function": 全项目切换英文
        },
        "[实验] 历史上的今天（高阶功能模板函数demo）": {
            "Function": 高阶功能模板函数
        },
    }

    # VisibleLevel=1 经过充分测试，但不常用的插件放在这里
    if UserVisibleLevel >= 1:
        function_plugins.update({
        })


    # VisibleLevel=2 尚未充分测试的函数插件，放在这里
    from crazy_functions.批量总结PDF文档 import 批量总结PDF文档
    if UserVisibleLevel >= 2:
        function_plugins.update({
            "[实验] 批量总结PDF文档": {
                "Color": "stop",
                "Function": 批量总结PDF文档
            },
        })

    return function_plugins


