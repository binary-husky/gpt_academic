# """
# 'primary' for main call-to-action, 
# 'secondary' for a more subdued style, 
# 'stop' for a stop button.
# """
def 自我程序解构简单案例(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    import time
    from predict import predict_no_ui_no_history
    for i in range(5):
        i_say = f'我给出一个数字，你给出该数字的平方。我给出数字：{i}'
        gpt_say = predict_no_ui_no_history(inputs=i_say, top_p=top_p, temperature=temperature)
        chatbot.append((i_say, gpt_say))
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, '正常'
        time.sleep(10)

def 解析项目本身(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    import time, glob, os
    from predict import predict_no_ui
    file_manifest = [f for f in glob.glob('*.py')]
    
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        前言 = "接下来请你分析自己的程序构成，别紧张，" if index==0 else ""
        i_say = f'请对下面的程序文件做一个概述: ```{file_content}```'
        i_say_show_user = 前言 + f'请对下面的程序文件做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[waiting gpt response]"))
        yield chatbot, history, '正常'

        # ** gpt request **
        gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature)

        chatbot[-1] = (i_say_show_user, gpt_say)
        history.append(i_say_show_user); history.append(gpt_say)
        yield chatbot, history, '正常'
        time.sleep(2)

    i_say = f'根据以上你自己的分析，对程序的整体功能和构架做出概括。然后用一张markdown表格整理每个文件的功能（包括{file_manifest}）。'
    chatbot.append((i_say, "[waiting gpt response]"))
    yield chatbot, history, '正常'

    # ** gpt request **
    gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history)

    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say); history.append(gpt_say)
    yield chatbot, history, '正常'


def 解析一个Python项目(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    import time, glob, os
    from predict import predict_no_ui
    if os.path.exists(txt):
        project_folder = txt
    else:
        chatbot.append((f"解析项目: {txt}", "找不到本地项目: {txt}"))
        history.append(i_say_show_user); history.append(gpt_say)
        return chatbot, history, '正常'

    file_manifest = [f for f in glob.glob(f'{project_folder}/*.py')]
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()

        前言 = "接下来请你逐文件分析下面的Python工程" if index==0 else ""
        i_say = f'请对下面的程序文件做一个概述: ```{file_content}```'
        i_say_show_user = 前言 + f'[{index}/{len(file_manifest)}] 请对下面的程序文件做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[waiting gpt response]"))
        print('[1] yield chatbot, history')
        yield chatbot, history, '正常'

        # ** gpt request **
        gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature)

        print('[2] end gpt req')
        chatbot[-1] = (i_say_show_user, gpt_say)
        history.append(i_say_show_user); history.append(gpt_say)
        print('[3] yield chatbot, history')
        yield chatbot, history, '正常'
        print('[4] next')
        time.sleep(2)

    i_say = f'根据以上你自己的分析，对程序的整体功能和构架做出概括。然后用一张markdown表格整理每个文件的功能（包括{file_manifest}）。'
    chatbot.append((i_say, "[waiting gpt response]"))
    yield chatbot, history, '正常'

    # ** gpt request **
    gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history)

    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say); history.append(gpt_say)
    yield chatbot, history, '正常'


def get_crazy_functionals():
    return {
        "程序解构简单案例": {
            "Function": 自我程序解构简单案例
        },
        "请解析并解构此项目本身": {
            "Function": 解析项目本身
        },
        "解析一整个Python项目（输入栏给定项目完整目录）": {
            "Function": 解析一个Python项目
        },
    }


