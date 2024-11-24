from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效
from toolbox import trimmed_format_exc
from loguru import logger

def get_crazy_functions():
    from crazy_functions.AntFin import AntFinTest

    function_plugins = {
        "蚂小财测试": {
            "Group": "智能体",
            "Color": "stop",
            "AsButton": False,
            "Info": "蚂小财测试",
            "Function": HotReload(AntFinTest),
        },
    }


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

        "蚂小财测试": 
            "蚂小财测试",  # 映射到上面的 `询问多个GPT模型` 插件
    }
