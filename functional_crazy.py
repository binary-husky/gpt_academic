
def get_crazy_functionals():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数
    from crazy_functions.代码重写为全英文_多线程 import 全项目切换英文

    return {
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



