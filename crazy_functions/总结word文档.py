from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file, predict_no_ui_but_counting_down
fast_debug = False


def 解析docx(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, os
    # pip install python-docx 用于docx格式，跨平台
    # pip install pywin32 用于doc格式，仅支持Win平台

    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        if fp.split(".")[-1] == "docx":
            from docx import Document
            doc = Document(fp)
            file_content = "\n".join([para.text for para in doc.paragraphs])
        else:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.visible = False
            # 打开文件
            print('fp', os.getcwd())
            doc = word.Documents.Open(os.getcwd() + '/' + fp)
            # file_content = doc.Content.Text
            doc = word.ActiveDocument
            file_content = doc.Range().Text
            doc.Close()
            word.Quit()

        print(file_content)

        prefix = "接下来请你逐文件分析下面的论文文件，" if index == 0 else ""
        # private_upload里面的文件名在解压zip后容易出现乱码（rar和7z格式正常），故可以只分析文章内容，不输入文件名
        i_say = prefix + f'请对下面的文章片段用中英文做概述，文件名是{os.path.relpath(fp, project_folder)},' \
                         f'文章内容是 ```{file_content}```'
        i_say_show_user = prefix + f'[{index+1}/{len(file_manifest)}] 假设你是论文审稿专家，请对下面的文章片段做概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        if not fast_debug:
            msg = '正常'
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, llm_kwargs, plugin_kwargs, history=[])  # 带超时倒计时
            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user);
            history.append(gpt_say)
            yield from update_ui(chatbot=chatbot, history=chatbot, msg=msg) # 刷新界面
            if not fast_debug: time.sleep(2)

    """
    # 可按需启用
    i_say = f'根据你上述的分析，对全文进行概括，用学术性语言写一段中文摘要，然后再写一篇英文的。'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


    i_say = f'我想让你做一个论文写作导师。您的任务是使用人工智能工具（例如自然语言处理）提供有关如何改进其上述文章的反馈。' \
            f'您还应该利用您在有效写作技巧方面的修辞知识和经验来建议作者可以更好地以书面形式表达他们的想法和想法的方法。' \
            f'根据你之前的分析，提出建议'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
  
    """

    if not fast_debug:
        msg = '正常'
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say, chatbot, llm_kwargs,
                                                             history=history)  # 带超时倒计时

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=chatbot, msg=msg) # 刷新界面
        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=chatbot, msg=msg) # 刷新界面


@CatchException
def 总结word文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结Word文档。函数插件贡献者: JasonGuo1"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        from docx import Document
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade python-docx pywin32```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.docx', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.doc', recursive=True)]
    # [f for f in glob.glob(f'{project_folder}/**/*.tex', recursive=True)] + \
    # [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
    # [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何.docx或doc文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析docx(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
