from toolbox import update_ui
from toolbox import CatchException, report_execption, write_results_to_file
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
fast_debug = False


def 解析docx(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, os
    # pip install python-docx 用于docx格式，跨平台
    # pip install pywin32 用于doc格式，仅支持Win平台
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
        # private_upload里面的文件名在解压zip后容易出现乱码（rar和7z格式正常），故可以只分析文章内容，不输入文件名
        from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf
        from request_llm.bridge_all import model_info
        max_token = model_info[llm_kwargs['llm_model']]['max_token']
        TOKEN_LIMIT_PER_FRAGMENT = max_token * 3 // 4
        paper_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
            txt=file_content,  
            get_token_fn=model_info[llm_kwargs['llm_model']]['token_cnt'], 
            limit=TOKEN_LIMIT_PER_FRAGMENT
        )
        this_paper_history = []
        for i, paper_frag in enumerate(paper_fragments):
            i_say = f'请对下面的文章片段用中文做概述，文件名是{os.path.relpath(fp, project_folder)}，文章内容是 ```{paper_frag}```'
            i_say_show_user = f'请对下面的文章片段做概述: {os.path.abspath(fp)}的第{i+1}/{len(paper_fragments)}个片段。'
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
            i_say = f"根据以上的对话，总结文章{os.path.abspath(fp)}的主要内容。"
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, 
                inputs_show_user=i_say, 
                llm_kwargs=llm_kwargs,
                chatbot=chatbot, 
                history=this_paper_history,
                sys_prompt="总结文章。"
            )

            history.extend([i_say,gpt_say])
            this_paper_history.extend([i_say,gpt_say])

        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    res = write_results_to_file(history)
    chatbot.append(("所有文件都总结完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


@CatchException
def 总结word文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结Word文档。函数插件贡献者: JasonGuo1。注意, 如果是.doc文件, 请先转化为.docx格式。"])
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
    if txt.endswith('.docx') or txt.endswith('.doc'):
        file_manifest = [txt]
    else:
        file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.docx', recursive=True)] + \
                        [f for f in glob.glob(f'{project_folder}/**/*.doc', recursive=True)]

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何.docx或doc文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析docx(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
