from toolbox import CatchException, update_ui, gen_time_str
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import input_clipping
import copy, json

def get_fn_lib():
    return {
        "BatchTranslatePDFDocuments_MultiThreaded": {
                "module": "crazy_functions.批量翻译PDF文档_多线程",  
                "function": "批量翻译PDF文档",
                "description": "Translate PDF Documents",
                "arg_1_description": "A path containing pdf files.",
            },
        "SummarizingWordDocuments": {
                "module": "crazy_functions.总结word文档",  
                "function": "总结word文档",
                "description": "Summarize Word Documents",
                "arg_1_description": "A path containing Word files.",
            },
        "ImageGeneration": {
                "module": "crazy_functions.图片生成",  
                "function": "图片生成",
                "description": "Generate a image that satisfies some description.",
                "arg_1_description": "Descriptions about the image to be generated.",
            },
        "TranslateMarkdownFromEnglishToChinese": {
                "module": "crazy_functions.批量Markdown翻译",  
                "function": "Markdown中译英",
                "description": "Translate Markdown Documents from English to Chinese.",
                "arg_1_description": "A path containing Markdown files.",
            },
        "SummaryAudioVideo": {
                "module": "crazy_functions.总结音视频",  
                "function": "总结音视频",
                "description": "Get text from a piece of audio and summarize this audio.",
                "arg_1_description": "A path containing audio files.",
            },
    }

functions = [
    {
        "name": k,
        "description": v['description'],
        "parameters": {
            "type": "object",
            "properties": {
                "plugin_arg_1": {
                    "type": "string",
                    "description": v['arg_1_description'],
                },
            },
            "required": ["plugin_arg_1"],
        },
    } for k, v in get_fn_lib().items()
]

def inspect_dependency(chatbot, history):
    return True

def eval_code(code, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import importlib
    try:
        tmp = get_fn_lib()[code['name']]
        fp, fn = tmp['module'], tmp['function']
        fn_plugin = getattr(importlib.import_module(fp, fn), fn)
        arg = json.loads(code['arguments'])['plugin_arg_1']
        yield from fn_plugin(arg, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
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
    chatbot.append(["虚空终端插件的功能？", "根据自然语言的描述, 执行任意插件的命令."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    
    # 输入
    i_say = txt
    # 开始
    llm_kwargs_function_call = copy.deepcopy(llm_kwargs)
    llm_kwargs_function_call['llm_model'] = 'gpt-call-fn' # 修改调用函数
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=txt, 
        llm_kwargs=llm_kwargs_function_call, chatbot=chatbot, history=[], 
        sys_prompt=functions
    )

    # 将代码转为动画
    res = json.loads(gpt_say)['choices'][0]
    if res['finish_reason'] == 'function_call':
        code = json.loads(gpt_say)['choices'][0]
        yield from eval_code(code['message']['function_call'], llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    else:
        chatbot.append(["无法调用相关功能", res])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


