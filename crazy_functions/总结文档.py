from toolbox import update_ui
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.rag_fns.rag_file_support import extract_text, supports_format

fast_debug = False


def 文档总结(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, os
    # pip install python-docx 用于docx格式，跨平台
    # pip install pywin32 用于doc格式，仅支持Win平台
    for index, fp in enumerate(file_manifest):
        file_content = extract_text(fp)
        # private_upload里面的文件名在解压zip后容易出现乱码（rar和7z格式正常），故可以只分析文章内容，不输入文件名
        if file_content==None:
            chatbot.append(
                [f"上传文件: {os.path.basename(fp)}", f"此文件解析失败，无法提取文本内容。失败原因可能为：1.文档格式过于复杂；2. 不支持的文件格式，支持的文件格式后缀有:" + ", ".join(supports_format)+ "等其他文本格式类型文件。"])
            continue
        from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
        from request_llms.bridge_all import model_info
        max_token = model_info[llm_kwargs['llm_model']]['max_token']
        TOKEN_LIMIT_PER_FRAGMENT = max_token * 3 // 4
        paper_fragments = breakdown_text_to_satisfy_token_limit(txt=file_content, limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs['llm_model'])
        this_paper_history = []
        for i, paper_frag in enumerate(paper_fragments):
            i_say = f'请对下面的内容用中文做概述，文件名是{os.path.relpath(fp, project_folder)}，做概述时请注意以下要求：{plugin_kwargs['advanced_arg']}：内容是 ```{paper_frag}```'
            i_say_show_user = f'请对下面的内容片段做概述，做概述时请注意以下要求：{plugin_kwargs['advanced_arg']}: {os.path.abspath(fp)}的第{i+1}/{len(paper_fragments)}个片段。'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=[],
                sys_prompt="总结文章。"
            )

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.extend([i_say_show_user,gpt_say])
            this_paper_history.extend([i_say_show_user,gpt_say])

        # 已经对该文章的所有片段总结完毕，如果文章被切分了，
        if len(paper_fragments) > 1:
            i_say = f"根据以上的对话，总结时请注意以下要求：{plugin_kwargs['advanced_arg']}，总结文件{os.path.abspath(fp)}的主要内容。"
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=this_paper_history,
                sys_prompt="总结文件内容。"
            )

            history.extend([i_say,gpt_say])
            this_paper_history.extend([i_say,gpt_say])

        res = write_history_to_file(history)
        promote_file_to_downloadzone(res, chatbot=chatbot)
        chatbot.append((f"路径{fp}文件解读完成了吗？", "解读完成，存储路径为"+res))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)


@CatchException
def 总结文件(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        f"批量总结各类文件。函数插件贡献者: JasonGuo1 and BoyinLiu。支持的文件类型包括：{', '.join(supports_format)}。"
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单

    file_manifest = [f for f in glob.glob(f'{project_folder}/**', recursive=True) if os.path.isfile(f)]

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何支持的文件类型: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 文档总结(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)