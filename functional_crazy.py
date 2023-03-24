from predict import predict_no_ui
from toolbox import CatchException, report_execption, write_results_to_file
fast_debug = False

def 解析源代码(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt):
    import time, glob, os
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        前言 = "接下来请你逐文件分析下面的工程" if index==0 else ""
        i_say = 前言 + f'请对下面的程序文件做一个概述文件名是{os.path.relpath(fp, project_folder)}，文件代码是 ```{file_content}```'
        i_say_show_user = 前言 + f'[{index}/{len(file_manifest)}] 请对下面的程序文件做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        print('[1] yield chatbot, history')
        yield chatbot, history, '正常'

        if not fast_debug: 
            msg = '正常'
            # ** gpt request **
            while True:
                try:
                    gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature)
                    break
                except ConnectionAbortedError as e:
                    i_say = i_say[:len(i_say)//2]
                    msg = '文件太长，进行了拦腰截断'

            print('[2] end gpt req')
            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user); history.append(gpt_say)
            print('[3] yield chatbot, history')
            yield chatbot, history, msg
            print('[4] next')
            if not fast_debug: time.sleep(2)

    all_file = ', '.join([os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)])
    i_say = f'根据以上你自己的分析，对程序的整体功能和构架做出概括。然后用一张markdown表格整理每个文件的功能（包括{all_file}）。'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield chatbot, history, '正常'

    if not fast_debug: 
        msg = '正常'
        # ** gpt request **
        while True:
            try:
                gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history)
                break
            except ConnectionAbortedError as e:
                history = [his[len(his)//2:] for his in history]
                msg = '对话历史太长，每段历史拦腰截断'
        

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say); history.append(gpt_say)
        yield chatbot, history, msg
        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield chatbot, history, msg

@CatchException
def 高阶功能模板函数(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    for i in range(5):
        i_say = f'我给出一个数字，你给出该数字的平方。我给出数字：{i}'
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

        gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature) # 请求gpt，需要一段时间

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield chatbot, history, '正常'  # 显示


@CatchException
def 解析项目本身(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    import time, glob, os
    file_manifest = [f for f in glob.glob('*.py')]
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        前言 = "接下来请你分析自己的程序构成，别紧张，" if index==0 else ""
        i_say = 前言 + f'请对下面的程序文件做一个概述文件名是{fp}，文件代码是 ```{file_content}```'
        i_say_show_user = 前言 + f'[{index}/{len(file_manifest)}] 请对下面的程序文件做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'

        if not fast_debug: 
            # ** gpt request **
            gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature)

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user); history.append(gpt_say)
            yield chatbot, history, '正常'
            time.sleep(2)

    i_say = f'根据以上你自己的分析，对程序的整体功能和构架做出概括。然后用一张markdown表格整理每个文件的功能（包括{file_manifest}）。'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield chatbot, history, '正常'

    if not fast_debug: 
        # ** gpt request **
        gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history)

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say); history.append(gpt_say)
        yield chatbot, history, '正常'
        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield chatbot, history, '正常'

@CatchException
def 解析一个Python项目(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield chatbot, history, '正常'
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.py', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何python文件: {txt}")
        yield chatbot, history, '正常'
        return
    yield from 解析源代码(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)


@CatchException
def 解析一个C项目的头文件(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield chatbot, history, '正常'
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)] # + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.h头文件: {txt}")
        yield chatbot, history, '正常'
        return
    yield from 解析源代码(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)


def get_crazy_functionals():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释

    return {
        "[实验功能] 请解析并解构此项目本身": {
            "Function": 解析项目本身
        },
        "[实验功能] 解析整个Python项目（input输入项目根路径）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个Python项目
        },
        "[实验功能] 解析整个C++项目的头文件（input输入项目根路径）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个C项目的头文件
        },
        "[实验功能] 解读latex论文写摘要（input输入项目根路径）": {
            "Color": "stop",    # 按钮颜色
            "Function": 读文章写摘要
        },
        "[实验功能] 批量生成函数注释（input输入项目根路径）": {
            "Color": "stop",    # 按钮颜色
            "Function": 批量生成函数注释
        },
        "[实验功能] 实验功能函数模板": {
            "Color": "stop",    # 按钮颜色
            "Function": 高阶功能模板函数
        },
    }


