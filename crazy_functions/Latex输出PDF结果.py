from toolbox import update_ui, trimmed_format_exc, get_conf, objdump, objload
from toolbox import CatchException, report_execption, update_ui_lastest_msg, zip_result, gen_time_str
import glob, os, requests, time
pj = os.path.join

# =================================== 工具函数 ===============================================    
def switch_prompt(pfg, mode):
    """
    Generate prompts and system prompts based on the mode for proofreading or translating.
    Args:
    - pfg: Proofreader or Translator instance.
    - mode: A string specifying the mode, either 'proofread' or 'translate_zh'.

    Returns:
    - inputs_array: A list of strings containing prompts for users to respond to.
    - sys_prompt_array: A list of strings containing prompts for system prompts.
    """
    n_split = len(pfg.sp_file_contents)
    if mode == 'proofread':
        inputs_array = [r"Below is a section from an academic paper, proofread this section." + 
                        r"Do not modify any latex command such as \section, \cite, \begin, \item and equations. " + 
                        r"Answer me only with the revised text:" + 
                        f"\n\n{frag}" for frag in pfg.sp_file_contents]
        sys_prompt_array = ["You are a professional academic paper writer." for _ in range(n_split)]
    elif mode == 'translate_zh':
        inputs_array = [r"Below is a section from an English academic paper, translate it into Chinese." + 
                        r"Do not modify any latex command such as \section, \cite, \begin, \item and equations. " + 
                        r"Answer me only with the translated text:" + 
                        f"\n\n{frag}" for frag in pfg.sp_file_contents]
        sys_prompt_array = ["You are a professional translator." for _ in range(n_split)]
    else:
        assert False, "未知指令"
    return inputs_array, sys_prompt_array

def desend_to_extracted_folder_if_exist(project_folder):
    """ 
    Descend into the extracted folder if it exists, otherwise return the original folder.

    Args:
    - project_folder: A string specifying the folder path.

    Returns:
    - A string specifying the path to the extracted folder, or the original folder if there is no extracted folder.
    """
    maybe_dir = [f for f in glob.glob(f'{project_folder}/*') if os.path.isdir(f)]
    if len(maybe_dir) == 0: return project_folder
    if maybe_dir[0].endswith('.extract'): return maybe_dir[0]
    return project_folder

def move_project(project_folder):
    """ 
    Create a new work folder and copy the project folder to it.

    Args:
    - project_folder: A string specifying the folder path of the project.

    Returns:
    - A string specifying the path to the new work folder.
    """
    import shutil, time
    time.sleep(2)   # avoid time string conflict
    new_workfolder = f'gpt_log/{gen_time_str()}'
    shutil.copytree(src=project_folder, dst=new_workfolder)
    return new_workfolder

def arxiv_download(chatbot, history, txt):
    if not txt.startswith('https://arxiv.org'): 
        return txt
    
    # <-------------- inspect format ------------->
    chatbot.append([f"检测到arxiv文档连接", '尝试下载 ...']) 
    yield from update_ui(chatbot=chatbot, history=history)
    time.sleep(1) # 刷新界面

    url_ = txt   # https://arxiv.org/abs/1707.06690
    if not txt.startswith('https://arxiv.org/abs/'): 
        msg = f"解析arxiv网址失败, 期望格式例如: https://arxiv.org/abs/1707.06690。实际得到格式: {url_}"
        yield from update_ui_lastest_msg(msg, chatbot=chatbot, history=history) # 刷新界面
        return msg
    
    # <-------------- set format ------------->
    arxiv_id = url_.split('/abs/')[-1]
    url_tar = url_.replace('/abs/', '/e-print/')
    download_dir = './gpt_log/arxiv/'
    os.makedirs(download_dir, exist_ok=True)
    
    # <-------------- download arxiv source file ------------->
    yield from update_ui_lastest_msg("开始下载", chatbot=chatbot, history=history)  # 刷新界面
    proxies, = get_conf('proxies')
    r = requests.get(url_tar, proxies=proxies)
    dst = pj(download_dir, arxiv_id+'.tar')
    with open(dst, 'wb+') as f:
        f.write(r.content)

    # <-------------- extract file ------------->
    yield from update_ui_lastest_msg("下载完成", chatbot=chatbot, history=history)  # 刷新界面
    from toolbox import extract_archive
    extract_dst = f'gpt_log/{gen_time_str()}'
    extract_archive(file_path=dst, dest_dir=extract_dst)
    return extract_dst
# ========================================= 插件主程序1 =====================================================    


@CatchException
def Latex英文纠错加PDF对比(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # <-------------- information about this plugin ------------->
    chatbot.append([ "函数插件功能？",
        "对整个Latex项目进行纠错, 用latex编译为PDF对修正处做高亮。函数插件贡献者: Binary-Husky。注意事项: 目前仅支持GPT3.5/GPT4，其他模型转化效果未知。目前对机器学习类文献转化效果最好，其他类型文献转化效果未知。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


    # <-------------- check deps ------------->
    try:
        import glob, os, time
        os.system(f'pdflatex -version')
        from .latex_utils import Latex精细分解与转化, 编译Latex差别
    except Exception as e:
        chatbot.append([ f"解析项目: {txt}",
            f"尝试执行Latex指令失败。Latex没有安装, 或者不在环境变量PATH中。报错信息\n\n```\n\n{trimmed_format_exc()}\n\n```\n\n"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    

    # <-------------- clear history and read input ------------->
    history = []
    txt = yield from arxiv_download(chatbot, history, txt)
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
    

    # <-------------- if is a zip/tar file ------------->
    project_folder = desend_to_extracted_folder_if_exist(project_folder)


    # <-------------- move latex project away from temp folder ------------->
    project_folder = move_project(project_folder)


    # <-------------- if merge_translate_zh is already generated, skip gpt req ------------->
    if not os.path.exists(project_folder + '/merge_proofread.tex'):
        yield from Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, mode='proofread_latex', switch_prompt=switch_prompt)


    # <-------------- compile PDF ------------->
    success = yield from 编译Latex差别(chatbot, history, main_file_original='merge', main_file_modified='merge_proofread', 
                             work_folder_original=project_folder, work_folder_modified=project_folder, work_folder=project_folder)
    

    # <-------------- zip PDF ------------->
    zip_result(project_folder)
    if success:
        chatbot.append((f"成功啦", '请查收结果（压缩包）...'))
        yield from update_ui(chatbot=chatbot, history=history); time.sleep(1) # 刷新界面
    else:
        chatbot.append((f"失败了", '虽然PDF生成失败了, 但请查收结果（压缩包）, 内含已经翻译的Tex文档, 也是可读的, 您可以到Github Issue区, 用该压缩包+对话历史存档进行反馈 ...'))
        yield from update_ui(chatbot=chatbot, history=history); time.sleep(1) # 刷新界面

    # <-------------- we are done ------------->
    return success


# ========================================= 插件主程序2 =====================================================    

@CatchException
def Latex翻译中文并重新编译PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # <-------------- information about this plugin ------------->
    chatbot.append([
        "函数插件功能？",
        "对整个Latex项目进行翻译, 生成中文PDF。函数插件贡献者: Binary-Husky。注意事项: 目前仅支持GPT3.5/GPT4，其他模型转化效果未知。目前对机器学习类文献转化效果最好，其他类型文献转化效果未知。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


    # <-------------- check deps ------------->
    try:
        import glob, os, time
        os.system(f'pdflatex -version')
        from .latex_utils import Latex精细分解与转化, 编译Latex差别
    except Exception as e:
        chatbot.append([ f"解析项目: {txt}",
            f"尝试执行Latex指令失败。Latex没有安装, 或者不在环境变量PATH中。报错信息\n\n```\n\n{trimmed_format_exc()}\n\n```\n\n"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    

    # <-------------- clear history and read input ------------->
    history = []
    txt = yield from arxiv_download(chatbot, history, txt)
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
    

    # <-------------- if is a zip/tar file ------------->
    project_folder = desend_to_extracted_folder_if_exist(project_folder)


    # <-------------- move latex project away from temp folder ------------->
    project_folder = move_project(project_folder)


    # <-------------- if merge_translate_zh is already generated, skip gpt req ------------->
    if not os.path.exists(project_folder + '/merge_translate_zh.tex'):
        yield from Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, mode='translate_zh', switch_prompt=switch_prompt)


    # <-------------- compile PDF ------------->
    success = yield from 编译Latex差别(chatbot, history, main_file_original='merge', main_file_modified='merge_translate_zh', 
                             work_folder_original=project_folder, work_folder_modified=project_folder, work_folder=project_folder)

    # <-------------- zip PDF ------------->
    zip_result(project_folder)
    if success:
        chatbot.append((f"成功啦", '请查收结果（压缩包）...'))
        yield from update_ui(chatbot=chatbot, history=history); time.sleep(1) # 刷新界面
    else:
        chatbot.append((f"失败了", '虽然PDF生成失败了, 但请查收结果（压缩包）, 内含已经翻译的Tex文档, 也是可读的, 您可以到Github Issue区, 用该压缩包+对话历史存档进行反馈 ...'))
        yield from update_ui(chatbot=chatbot, history=history); time.sleep(1) # 刷新界面

    # <-------------- we are done ------------->
    return success
