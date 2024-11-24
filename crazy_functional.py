from toolbox import HotReload  # HotReload 的意思是热更新，修改函数插件后，不需要重启程序，代码直接生效
from toolbox import trimmed_format_exc
from loguru import logger

def get_crazy_functions():
    from crazy_functions.SourceCode_Analyse import 解析项目本身

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
            "Function": HotReload(虚空终端),
        },
        "解析整个Python项目": {
            "Group": "编程",
            "Color": "stop",
            "AsButton": True,
            "Info": "解析一个Python项目的所有源文件(.py) | 输入参数为路径",
            "Function": HotReload(解析一个Python项目),
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

        "多模型对话": 
            "询问多个GPT模型", # 映射到上面的 `询问多个GPT模型` 插件

        "智能召回 RAG": 
            "Rag智能召回", # 映射到上面的 `Rag智能召回` 插件

        "多媒体查询": 
            "多媒体智能体", # 映射到上面的 `多媒体智能体` 插件
    }
