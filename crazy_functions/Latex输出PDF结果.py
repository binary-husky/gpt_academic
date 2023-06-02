from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder
import glob, copy, os


def confirm_answer_is_health(bufo, buf, llm_kwargs, default = True):
    # from request_llm.bridge_all import predict_no_ui_long_connection
    # inputs  = f"I asked someone to proofread some text \"{bufo}\", this is what he answered: \"{buf}\"."
    # inputs +=  "Did he answer me with proofreaded text (`true`), or did he just tell me the text has no errors (`false`)?"

    # llm_kwargs_ = copy.deepcopy(llm_kwargs); llm_kwargs_['temperature'] = 0
    # result = predict_no_ui_long_connection( inputs=inputs, llm_kwargs=llm_kwargs_,
    #     history=[], sys_prompt="Answer my question with either `true` or `false`.", observe_window=[])

    # if 'false' in result or 'FALSE' in result or 'False' in result:
    #     return False
    
    # if 'true' in result or 'TRUE' in result or 'True' in result:
    #     return True
    
    # return default
    return len(buf) >= len(bufo) // 3

def Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, language='en', mode='polish'):
    import time, os, re
    from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from .latex_utils import LatexPaperFileGroup, merge_tex_files, LatexPaperSplit

    #  <-------- 读取Latex文件，删除其中的所有注释 ----------> 
    def 寻找主文件(file_manifest):
        for texf in file_manifest:
            with open(texf, 'r', encoding='utf8') as f:
                file_content = f.read()
            if r'\documentclass' in file_content:
                return texf
            else:
                continue
        raise RuntimeError('无法找到一个主Tex文件（包含documentclass关键字）')
    


    maintex = 寻找主文件(file_manifest)
    with open(maintex, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        merged_content = merge_tex_files(project_folder, content)
        # 使用正则表达式查找注释，并替换为空字符串
        merged_content = re.sub(r'(?<!\\)%.*', '', merged_content)
    with open(project_folder + '/merge.tex', 'w', encoding='utf-8', errors='replace') as f:
        f.write(merged_content)

    lps = LatexPaperSplit()
    res = lps.split(merged_content)

    #  <-------- 拆分过长的latex片段 ----------> 
    pfg = LatexPaperFileGroup()
    for index, r in enumerate(res):
        pfg.file_paths.append(index)
        pfg.file_contents.append(r)

    pfg.run_file_split(max_token_limit=1024)
    n_split = len(pfg.sp_file_contents)

    inputs_array = [r"Below is a section from an academic paper, proofread this section." + 
                    r"Do not modify any latex command such as \section, \cite, \begin, \item and equations. " + 
                    r"Answer me only with the revised text:" + 
                f"\n\n{frag}" for frag in pfg.sp_file_contents]
    sys_prompt_array = ["You are a professional academic paper writer." for _ in range(n_split)]
    inputs_show_user_array = [f"Proofread {f}" for f in pfg.sp_file_tag]

    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(n_split)],
        sys_prompt_array=sys_prompt_array,
        # max_workers=5,  # 并行任务数量限制，最多同时执行5个，其他的排队等待
        scroller_max_len = 80
    )

    #  <-------- 文本碎片重组为完整的tex片段 ----------> 
    pfg.sp_file_result = []
    for i_say, gpt_say, orig_content in zip(gpt_response_collection[0::2], gpt_response_collection[1::2], pfg.sp_file_contents):
        pfg.sp_file_result.append(gpt_say)
    pfg.merge_result()

    final_tex = lps.merge_result(pfg.sp_file_result)
    with open(project_folder + '/merge_proofread.tex', 'w', encoding='utf-8', errors='replace') as f:
        f.write(final_tex)
    #  <-------- 整理结果，退出 ----------> 
    create_report_file_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + f"-chatgpt.polish.md"
    res = write_results_to_file(gpt_response_collection, file_name=create_report_file_name)
    history = gpt_response_collection
    chatbot.append((f"完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    return project_folder + '/merge_proofread.tex'



def 编译Latex(main_tex, work_folder):
    import os
    current_dir = os.getcwd()
    os.chdir(work_folder)
    main_file = os.path.basename(main_tex)
    assert main_file.endswith('.tex')
    main_file = main_file[:-4]
    os.system(f'pdflatex {main_file}.tex')
    os.system(f'bibtex {main_file}.aux')
    os.system(f'pdflatex {main_file}.tex')
    os.system(f'pdflatex {main_file}.tex')
    os.chdir(current_dir)
    pdf_output = os.path.join(work_folder, f'{main_file}.pdf')

    assert os.path.exists(pdf_output)
    return pdf_output

def Latex预处理(tar_file):
    from toolbox import extract_archive
    import shutil
    work_folder = 'private_upload/latex_workshop_temp'
    try:
        shutil.rmtree(work_folder)
    except:
        pass
    res = extract_archive(tar_file, dest_dir=work_folder)
    for texf in glob.glob('private_upload/latex_workshop_temp/*.tex'):
        with open(texf, 'r', encoding='utf8') as f:
            file_content = f.read()
        if r'\documentclass' in file_content:
            return texf, work_folder
        else:
            continue
    raise RuntimeError('无法找到一个主Tex文件（包含documentclass关键字）')



@CatchException
def Latex英文纠错加PDF对比(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "对整个Latex项目进行纠错，用latex编译为PDF对修正处做高亮。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import glob, os
        os.system(f'pdflatex -version')
    except Exception as e:
        print(trimmed_format_exc())
        report_execption(chatbot, history, a=f"解析项目: {txt}",
                         b=f"尝试执行Latex指令失败。Latex没有安装，或者不在环境变量PATH中。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    

    history = []    # 清空历史，以免输入溢出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.tex', recursive=True)]
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.tex文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    if not os.path.exists(project_folder + '/merge_proofread.tex'):
        yield from Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, language='en', mode='proofread_latex')

    res_pdf_path = 编译Latex差别(main_file_original='merge', main_file_modified='merge_proofread', 
                             work_folder_original=project_folder, work_folder_modified=project_folder, work_folder=project_folder)
    return res_pdf_path


def 编译Latex差别(main_file_original, main_file_modified, work_folder_original, work_folder_modified, work_folder):
    import os
    current_dir = os.getcwd()
    # <--------------------->

    import os, shutil

    # https://stackoverflow.com/questions/738755/dont-make-me-manually-abort-a-latex-compile-when-theres-an-error
    os.chdir(work_folder_original); os.system(f'pdflatex -interaction=batchmode {main_file_original}.tex'); os.chdir(current_dir)
    os.chdir(work_folder_modified); os.system(f'pdflatex -interaction=batchmode {main_file_modified}.tex'); os.chdir(current_dir)
    os.chdir(work_folder_original); os.system(f'bibtex  {main_file_original}.aux'); os.chdir(current_dir)
    os.chdir(work_folder_modified); os.system(f'bibtex  {main_file_modified}.aux'); os.chdir(current_dir)

    print(    f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/diff.tex')
    os.system(f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/diff.tex')

    os.chdir(work_folder); os.system(f'pdflatex  -interaction=batchmode diff.tex'); os.chdir(current_dir)
    os.chdir(work_folder); os.system(f'bibtex    diff.aux'); os.chdir(current_dir)
    os.chdir(work_folder); os.system(f'pdflatex  -interaction=batchmode diff.tex'); os.chdir(current_dir)
    os.chdir(work_folder); os.system(f'pdflatex  -interaction=batchmode diff.tex'); os.chdir(current_dir)


    # <--------------------->
    os.chdir(current_dir)
    return f'{work_folder}/diff.pdf'


def Latex预处理(pfg, project_folder):
    import shutil, os
    work_folder = 'private_upload/latex_workshop_temp'

    try:
        shutil.rmtree(work_folder)
    except:
        pass
    finally:
        work_folder_original = 'private_upload/latex_workshop_temp/original'
        work_folder_modified = 'private_upload/latex_workshop_temp/modified'
        shutil.copytree(project_folder, work_folder_original, ignore=lambda a,b: ['.git'])
        shutil.copytree(project_folder, work_folder_modified, ignore=lambda a,b: ['.git'])

    for path, result in zip(pfg.file_paths, pfg.file_result):
        path_old = os.path.relpath(path, start=project_folder)
        path_new = os.path.join(work_folder_modified, path_old)
        with open(path_new, 'w', encoding='utf-8') as f:
            f.write(result)

    for main_file_original in glob.glob('private_upload/latex_workshop_temp/original/*.tex'):
        with open(main_file_original, 'r', encoding='utf8') as f:
            file_content = f.read()
        if r'\documentclass' in file_content:
            path_old = os.path.relpath(main_file_original, start=work_folder_original)
            main_file_modified = os.path.relpath(work_folder_modified, start=work_folder_original)
            return main_file_original, main_file_modified, work_folder_original, work_folder_modified, work_folder
        else:
            continue
    raise RuntimeError('无法找到一个主Tex文件, 本程序寻找主Tex文件的方法是查找文件中的documentclass关键字。')
