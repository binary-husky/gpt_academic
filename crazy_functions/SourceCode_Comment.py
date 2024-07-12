import os, copy
from toolbox import CatchException, report_exception, update_ui, zip_result, promote_file_to_downloadzone, update_ui_lastest_msg
from shared_utils.fastapi_server import validate_path_safety
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.agent_fns.python_comment_agent import PythonCodeComment
from crazy_functions.diagram_fns.file_tree import FileNode

def 注释源代码(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):

    summary_batch_isolation = True
    inputs_array = []
    inputs_show_user_array = []
    history_array = []
    sys_prompt_array = []

    assert len(file_manifest) <= 512, "源文件太多（超过512个）, 请缩减输入文件的数量。或者，您也可以选择删除此行警告，并修改代码拆分file_manifest列表，从而实现分批次处理。"

    # 建立文件树
    file_tree_struct = FileNode("root", build_manifest=True)
    for file_path in file_manifest:
        file_tree_struct.add_file(file_path, file_path)

    # <第一步，逐个文件分析，多线程>
    for index, fp in enumerate(file_manifest):
        # 读取文件
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        prefix = ""
        i_say = prefix + f'Please analyse the following source code at {os.path.relpath(fp, project_folder)}, the code is:\n```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] 请用一句话对下面的程序文件做一个整体概述: {fp}'
        # 装载请求内容
        MAX_TOKEN_SINGLE_FILE = 2560
        i_say, _ = input_clipping(inputs=i_say, history=[], max_token_limit=MAX_TOKEN_SINGLE_FILE)
        inputs_array.append(i_say)
        inputs_show_user_array.append(i_say_show_user)
        history_array.append([])
        sys_prompt_array.append("You are a software architecture analyst analyzing a source code project. Do not dig into details, tell me what the code is doing in general. Your answer must be short, simple and clear.")
    # 文件读取完成，对每一个源代码文件，生成一个请求线程，发送到大模型进行分析
    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array = inputs_array,
        inputs_show_user_array = inputs_show_user_array,
        history_array = history_array,
        sys_prompt_array = sys_prompt_array,
        llm_kwargs = llm_kwargs,
        chatbot = chatbot,
        show_user_at_complete = True
    )

    # <第二步，逐个文件分析，生成带注释文件>
    chatbot.append([None, f"正在处理:"])
    for i_say, gpt_say, fp in zip(gpt_response_collection[0::2], gpt_response_collection[1::2], file_manifest):
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        yield from update_ui_lastest_msg(f"正在处理: {fp}", chatbot=chatbot, history=history, delay=0)
        pcc = PythonCodeComment(llm_kwargs, language='English')
        pcc.read_file(path=fp, brief=gpt_say)
        revised_path, revised_content = yield from pcc.begin_comment_source_code(chatbot, history)
        file_tree_struct.manifest[fp].revised_path = revised_path
        file_tree_struct.manifest[fp].revised_content = revised_content
    
    # <第三步，将结果写回源文件>
    for i_say, gpt_say, fp in zip(gpt_response_collection[0::2], gpt_response_collection[1::2], file_manifest):
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(file_tree_struct.manifest[fp].revised_content)

    # <第四步，压缩结果>
    zip_res = zip_result(project_folder)
    promote_file_to_downloadzone(file=zip_res, chatbot=chatbot)

    # <END>
    chatbot.append((None, "所有源文件均已处理完毕。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面



@CatchException
def 注释Python项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
        validate_path_safety(project_folder, chatbot.get_user())
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.py', recursive=True)]
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何python文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    yield from 注释源代码(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
