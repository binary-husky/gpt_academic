<<<<<<< HEAD
from predict import predict_no_ui
from toolbox import CatchException, report_execption, write_results_to_file, predict_no_ui_but_counting_down
fast_debug = False


def 解析Paper(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt):
    import time, glob, os
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8') as f:
=======
from toolbox import update_ui
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive


def 解析Paper(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, glob, os
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
            file_content = f.read()

        prefix = "接下来请你逐文件分析下面的论文文件，概括其内容" if index==0 else ""
        i_say = prefix + f'请对下面的文章片段用中文做一个概述，文件名是{os.path.relpath(fp, project_folder)}，文章内容是 ```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] 请对下面的文章片段做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
<<<<<<< HEAD
        print('[1] yield chatbot, history')
        yield chatbot, history, '正常'

        if not fast_debug: 
            msg = '正常'
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature, history=[])   # 带超时倒计时

            print('[2] end gpt req')
            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user); history.append(gpt_say)
            print('[3] yield chatbot, history')
            yield chatbot, history, msg
            print('[4] next')
            if not fast_debug: time.sleep(2)
=======
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        msg = '正常'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user, llm_kwargs, chatbot, history=[], sys_prompt=system_prompt)   # 带超时倒计时
        chatbot[-1] = (i_say_show_user, gpt_say)
        history.append(i_say_show_user); history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history, msg=msg) # 刷新界面
        time.sleep(2)
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13

    all_file = ', '.join([os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)])
    i_say = f'根据以上你自己的分析，对全文进行概括，用学术性语言写一段中文摘要，然后再写一段英文摘要（包括{all_file}）。'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
<<<<<<< HEAD
    yield chatbot, history, '正常'

    if not fast_debug: 
        msg = '正常'
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say, chatbot, top_p, temperature, history=history)   # 带超时倒计时

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say); history.append(gpt_say)
        yield chatbot, history, msg
        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield chatbot, history, msg
=======
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    msg = '正常'
    # ** gpt request **
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say, llm_kwargs, chatbot, history=history, sys_prompt=system_prompt)   # 带超时倒计时

    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say); history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history, msg=msg) # 刷新界面
    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    chatbot.append(("完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history, msg=msg) # 刷新界面
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13



@CatchException
<<<<<<< HEAD
def 读文章写摘要(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
=======
def 读文章写摘要(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
<<<<<<< HEAD
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield chatbot, history, '正常'
=======
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.tex', recursive=True)] # + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    if len(file_manifest) == 0:
<<<<<<< HEAD
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.tex文件: {txt}")
        yield chatbot, history, '正常'
        return
    yield from 解析Paper(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)
=======
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.tex文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析Paper(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
