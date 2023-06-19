from toolbox import CatchException, update_ui, gen_time_str
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import input_clipping


prompt = """
I have to achieve some functionalities by calling one of the functions below.
Your job is to find the correct funtion to use to satisfy my requirement,
and then write python code to call this function with correct parameters.

These are functions you are allowed to choose from:
1. 
    功能描述: 总结音视频内容
    调用函数: ConcludeAudioContent(txt, llm_kwargs)
    参数说明: 
            txt: 音频文件的路径
            llm_kwargs: 模型参数, 永远给定None
2. 
    功能描述: 将每次对话记录写入Markdown格式的文件中
    调用函数: WriteMarkdown()
3.
    功能描述: 将指定目录下的PDF文件从英文翻译成中文
    调用函数: BatchTranslatePDFDocuments_MultiThreaded(txt, llm_kwargs)
    参数说明: 
            txt: PDF文件所在的路径
            llm_kwargs: 模型参数, 永远给定None
4.
    功能描述: 根据文本使用GPT模型生成相应的图像
    调用函数: ImageGeneration(txt, llm_kwargs)
    参数说明: 
            txt: 图像生成所用到的提示文本
            llm_kwargs: 模型参数, 永远给定None
5.
    功能描述: 对输入的word文档进行摘要生成 
    调用函数: SummarizingWordDocuments(input_path, output_path)
    参数说明: 
            input_path: 待处理的word文档路径
            output_path: 摘要生成后的文档路径


You should always anwser with following format:
----------------
Code:
```
class AutoAcademic(object):
    def __init__(self):
        self.selected_function = "FILL_CORRECT_FUNCTION_HERE"      # e.g., "GenerateImage"
        self.txt = "FILL_MAIN_PARAMETER_HERE"      # e.g., "荷叶上的蜻蜓"
        self.llm_kwargs = None
```
Explanation:
只有GenerateImage和生成图像相关, 因此选择GenerateImage函数。
----------------

Now, this is my requirement: 

"""
def get_fn_lib():
    return {
        "BatchTranslatePDFDocuments_MultiThreaded": ("crazy_functions.批量翻译PDF文档_多线程",  "批量翻译PDF文档"),
        "SummarizingWordDocuments": ("crazy_functions.总结word文档",  "总结word文档"),
        "ImageGeneration": ("crazy_functions.图片生成",  "图片生成"),
        "TranslateMarkdownFromEnglishToChinese": ("crazy_functions.批量Markdown翻译",  "Markdown中译英"),
        "SummaryAudioVideo": ("crazy_functions.总结音视频",  "总结音视频"),
    }

def inspect_dependency(chatbot, history):
    return True

def eval_code(code, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import subprocess, sys, os, shutil, importlib

    with open('gpt_log/void_terminal_runtime.py', 'w', encoding='utf8') as f:
        f.write(code)

    try:
        AutoAcademic = getattr(importlib.import_module('gpt_log.void_terminal_runtime', 'AutoAcademic'), 'AutoAcademic')
        # importlib.reload(AutoAcademic)
        auto_dict = AutoAcademic()
        selected_function = auto_dict.selected_function
        txt = auto_dict.txt
        fp, fn = get_fn_lib()[selected_function]
        fn_plugin = getattr(importlib.import_module(fp, fn), fn)
        yield from fn_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    except:
        from toolbox import trimmed_format_exc
        chatbot.append(["执行错误", f"\n```\n{trimmed_format_exc()}\n```\n"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

def get_code_block(reply):
    import re
    pattern = r"```([\s\S]*?)```" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    if len(matches) != 1: 
        raise RuntimeError("GPT is not generating proper code.")
    return matches[0].strip('python') #  code block

@CatchException
def 终端(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本, 例如需要翻译的一段话, 再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数, 暂时没有用武之地
    chatbot         聊天显示框的句柄, 用于显示给用户
    history         聊天历史, 前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    # 清空历史, 以免输入溢出
    history = []    

    # 基本信息：功能、贡献者
    chatbot.append(["函数插件功能？", "根据自然语言执行插件命令, 作者: binary-husky, 插件初始化中 ..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # # 尝试导入依赖, 如果缺少依赖, 则给出安装建议
    # dep_ok = yield from inspect_dependency(chatbot=chatbot, history=history) # 刷新界面
    # if not dep_ok: return
    
    # 输入
    i_say = prompt + txt
    # 开始
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=txt, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=""
    )

    # 将代码转为动画
    code = get_code_block(gpt_say)
    yield from eval_code(code, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
