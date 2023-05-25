from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive

def inspect_dependency(chatbot, history):
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import manim
        return True
    except:
        chatbot.append(["导入依赖失败", "使用该模块需要额外依赖，安装方法:```pip install manimgl```"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return False

def gen_time_str():
    import time
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

def eval_manim(code):
    import subprocess, sys, os, shutil

    with open('gpt_log/MyAnimation.py', 'w', encoding='utf8') as f:
        f.write(code)

    subprocess.check_output([sys.executable, '-c', "from gpt_log.MyAnimation import MyAnimation; MyAnimation().render()"])

    try: 
        shutil.copyfile('media/videos/1080p60/MyAnimation.mp4', f'gpt_log/{gen_time_str()}.mp4')
    except: 
        print('generating mp4 failed')
        return "Generating mp4 failed"
    return f'gpt_log/{gen_time_str()}.mp4'

def get_code_block(reply):
    import re
    pattern = r"```([\s\S]*?)```" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    if len(matches) != 1: 
        raise RuntimeError("GPT is not generating proper code.")
    return matches[0].strip('python') #  code block

@CatchException
def 动画生成(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    # 清空历史，以免输入溢出
    history = []    

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "生成数学动画, 作者: binary-husky, 插件初始化中 ..."
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖, 如果缺少依赖, 则给出安装建议
    dep_ok = yield from inspect_dependency(chatbot=chatbot, history=history) # 刷新界面
    if not dep_ok: return
    
    # 开始
    i_say = f'Generate a animation to show:' + txt
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=i_say, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="Write a animation script with 3blue1brown's manim. Name the class as `MyAnimation`. And answer me with a code block wrapped by ```."
    )
    chatbot.append((i_say, gpt_say))
    history.extend([i_say, gpt_say])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
    
    # 将代码转为动画
    code = get_code_block(gpt_say)
    res = eval_manim(code)

    chatbot.append(("生成的视频文件路径", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
