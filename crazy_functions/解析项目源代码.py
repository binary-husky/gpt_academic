from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from .crazy_utils import input_clipping

def 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import os, copy
    from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
    msg = '正常'
    inputs_array = []
    inputs_show_user_array = []
    history_array = []
    sys_prompt_array = []
    report_part_1 = []

    assert len(file_manifest) <= 512, "源文件太多（超过512个）, 请缩减输入文件的数量。或者，您也可以选择删除此行警告，并修改代码拆分file_manifest列表，从而实现分批次处理。"
    ############################## <第一步，逐个文件分析，多线程> ##################################
    for index, fp in enumerate(file_manifest):
        # 读取文件
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        prefix = "接下来请你逐文件分析下面的工程" if index==0 else ""
        i_say = prefix + f'请对下面的程序文件做一个概述文件名是{os.path.relpath(fp, project_folder)}，文件代码是 ```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] 请对下面的程序文件做一个概述: {os.path.abspath(fp)}'
        # 装载请求内容
        inputs_array.append(i_say)
        inputs_show_user_array.append(i_say_show_user)
        history_array.append([])
        sys_prompt_array.append("你是一个程序架构分析师，正在分析一个源代码项目。你的回答必须简单明了。")

    # 文件读取完成，对每一个源代码文件，生成一个请求线程，发送到chatgpt进行分析
    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array = inputs_array,
        inputs_show_user_array = inputs_show_user_array,
        history_array = history_array,
        sys_prompt_array = sys_prompt_array,
        llm_kwargs = llm_kwargs,
        chatbot = chatbot,
        show_user_at_complete = True
    )

    # 全部文件解析完成，结果写入文件，准备对工程源代码进行汇总分析
    report_part_1 = copy.deepcopy(gpt_response_collection)
    history_to_return = report_part_1
    res = write_results_to_file(report_part_1)
    chatbot.append(("完成？", "逐个文件分析已完成。" + res + "\n\n正在开始汇总。"))
    yield from update_ui(chatbot=chatbot, history=history_to_return) # 刷新界面

    ############################## <第二步，综合，单线程，分组+迭代处理> ##################################
    batchsize = 16  # 10个文件为一组
    report_part_2 = []
    previous_iteration_files = []
    last_iteration_result = ""
    while True:
        if len(file_manifest) == 0: break
        this_iteration_file_manifest = file_manifest[:batchsize]
        this_iteration_gpt_response_collection = gpt_response_collection[:batchsize*2]
        file_rel_path = [os.path.relpath(fp, project_folder) for index, fp in enumerate(this_iteration_file_manifest)]
        # 把“请对下面的程序文件做一个概述” 替换成 精简的 "文件名：{all_file[index]}"
        for index, content in enumerate(this_iteration_gpt_response_collection):
            if index%2==0: this_iteration_gpt_response_collection[index] = f"{file_rel_path[index//2]}" # 只保留文件名节省token
        previous_iteration_files.extend([os.path.relpath(fp, project_folder) for index, fp in enumerate(this_iteration_file_manifest)])
        previous_iteration_files_string = ', '.join(previous_iteration_files)
        current_iteration_focus = ', '.join([os.path.relpath(fp, project_folder) for index, fp in enumerate(this_iteration_file_manifest)])
        i_say = f'用一张Markdown表格简要描述以下文件的功能：{previous_iteration_files_string}。根据以上分析，用一句话概括程序的整体功能。'
        inputs_show_user = f'根据以上分析，对程序的整体功能和构架重新做出概括，由于输入长度限制，可能需要分组处理，本组文件为 {current_iteration_focus} + 已经汇总的文件组。'
        this_iteration_history = copy.deepcopy(this_iteration_gpt_response_collection)
        this_iteration_history.append(last_iteration_result)
        # 裁剪input
        inputs, this_iteration_history_feed = input_clipping(inputs=i_say, history=this_iteration_history, max_token_limit=2560)
        result = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=inputs, inputs_show_user=inputs_show_user, llm_kwargs=llm_kwargs, chatbot=chatbot,
            history=this_iteration_history_feed,   # 迭代之前的分析
            sys_prompt="你是一个程序架构分析师，正在分析一个项目的源代码。")
        report_part_2.extend([i_say, result])
        last_iteration_result = result

        file_manifest = file_manifest[batchsize:]
        gpt_response_collection = gpt_response_collection[batchsize*2:]

    ############################## <END> ##################################
    history_to_return.extend(report_part_2)
    res = write_results_to_file(history_to_return)
    chatbot.append(("完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history_to_return) # 刷新界面


@CatchException
def 解析项目本身(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob
    file_manifest = [f for f in glob.glob('./*.py') if ('test_project' not in f) and ('gpt_log' not in f)] + \
                    [f for f in glob.glob('./crazy_functions/*.py') if ('test_project' not in f) and ('gpt_log' not in f)]+ \
                    [f for f in glob.glob('./request_llm/*.py') if ('test_project' not in f) and ('gpt_log' not in f)]
    project_folder = './'
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何python文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

@CatchException
def 解析一个Python项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.py', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何python文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个C项目的头文件(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)]  + \
                    [f for f in glob.glob(f'{project_folder}/**/*.hpp', recursive=True)] #+ \
                    # [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.h头文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

@CatchException
def 解析一个C项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.h', recursive=True)]  + \
                    [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.hpp', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.h头文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个Java项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []  # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.java', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.jar', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.xml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.sh', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何java文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个Rect项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []  # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.ts', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.tsx', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.json', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.js', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.jsx', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何Rect文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个Golang项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []  # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.go', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.mod', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.sum', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/go.work', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何golang文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个Lua项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.lua', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.xml', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.json', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.toml', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何lua文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析一个CSharp项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    import glob, os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.cs', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.csproj', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何CSharp文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


@CatchException
def 解析任意code项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    txt_pattern = plugin_kwargs.get("advanced_arg")
    txt_pattern = txt_pattern.replace("，", ",")
    # 将要匹配的模式(例如: *.c, *.cpp, *.py, config.toml)
    pattern_include = [_.lstrip(" ,").rstrip(" ,") for _ in txt_pattern.split(",") if _ != "" and not _.strip().startswith("^")]
    if not pattern_include: pattern_include = ["*"] # 不输入即全部匹配
    # 将要忽略匹配的文件后缀(例如: ^*.c, ^*.cpp, ^*.py)
    pattern_except_suffix = [_.lstrip(" ^*.,").rstrip(" ,") for _ in txt_pattern.split(" ") if _ != "" and _.strip().startswith("^*.")]
    pattern_except_suffix += ['zip', 'rar', '7z', 'tar', 'gz'] # 避免解析压缩文件
    # 将要忽略匹配的文件名(例如: ^README.md)
    pattern_except_name = [_.lstrip(" ^*,").rstrip(" ,").replace(".", "\.") for _ in txt_pattern.split(" ") if _ != "" and _.strip().startswith("^") and not _.strip().startswith("^*.")]
    # 生成正则表达式
    pattern_except = '/[^/]+\.(' + "|".join(pattern_except_suffix) + ')$'
    pattern_except += '|/(' + "|".join(pattern_except_name) + ')$' if pattern_except_name != [] else ''

    history.clear()
    import glob, os, re
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    # 若上传压缩文件, 先寻找到解压的文件夹路径, 从而避免解析压缩文件
    maybe_dir = [f for f in glob.glob(f'{project_folder}/*') if os.path.isdir(f)]
    if len(maybe_dir)>0 and maybe_dir[0].endswith('.extract'):
        extract_folder_path = maybe_dir[0]
    else:
        extract_folder_path = project_folder
    # 按输入的匹配模式寻找上传的非压缩文件和已解压的文件
    file_manifest = [f for pattern in pattern_include for f in glob.glob(f'{extract_folder_path}/**/{pattern}', recursive=True) if "" != extract_folder_path and \
                      os.path.isfile(f) and (not re.search(pattern_except, f) or pattern.endswith('.' + re.search(pattern_except, f).group().split('.')[-1]))]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    yield from 解析源代码新(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)