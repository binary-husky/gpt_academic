from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency


def read_and_clean_pdf_text(fp):
    """
    **输入参数说明**
    - `fp`：需要读取和清理文本的pdf文件路径

    **输出参数说明**
    - `meta_txt`：清理后的文本内容字符串
    - `page_one_meta`：第一页清理后的文本内容列表

    **函数功能**
    读取pdf文件并清理其中的文本内容，清理规则包括：
    - 提取所有块元的文本信息，并合并为一个字符串
    - 去除短块（字符数小于100）并替换为回车符
    - 清理多余的空行
    - 合并小写字母开头的段落块并替换为空格
    - 清除重复的换行
    - 将每个换行符替换为两个换行符，使每个段落之间有两个换行符分隔
    """
    import fitz
    import re
    import numpy as np
    # file_content = ""
    with fitz.open(fp) as doc:
        meta_txt = []
        meta_font = []
        for index, page in enumerate(doc):
            # file_content += page.get_text()
            text_areas = page.get_text("dict")  # 获取页面上的文本信息

            # 块元提取                           for each word segment with in line                       for each line         cross-line words                          for each block
            meta_txt.extend([" ".join(["".join([wtf['text'] for wtf in l['spans']]) for l in t['lines']]).replace(
                '- ', '') for t in text_areas['blocks'] if 'lines' in t])
            meta_font.extend([np.mean([np.mean([wtf['size'] for wtf in l['spans']])
                             for l in t['lines']]) for t in text_areas['blocks'] if 'lines' in t])
            if index == 0:
                page_one_meta = [" ".join(["".join([wtf['text'] for wtf in l['spans']]) for l in t['lines']]).replace(
                    '- ', '') for t in text_areas['blocks'] if 'lines' in t]

        def 把字符太少的块清除为回车(meta_txt):
            for index, block_txt in enumerate(meta_txt):
                if len(block_txt) < 100:
                    meta_txt[index] = '\n'
            return meta_txt
        meta_txt = 把字符太少的块清除为回车(meta_txt)

        def 清理多余的空行(meta_txt):
            for index in reversed(range(1, len(meta_txt))):
                if meta_txt[index] == '\n' and meta_txt[index-1] == '\n':
                    meta_txt.pop(index)
            return meta_txt
        meta_txt = 清理多余的空行(meta_txt)

        def 合并小写开头的段落块(meta_txt):
            def starts_with_lowercase_word(s):
                pattern = r"^[a-z]+"
                match = re.match(pattern, s)
                if match:
                    return True
                else:
                    return False
            for _ in range(100):
                for index, block_txt in enumerate(meta_txt):
                    if starts_with_lowercase_word(block_txt):
                        if meta_txt[index-1] != '\n':
                            meta_txt[index-1] += ' '
                        else:
                            meta_txt[index-1] = ''
                        meta_txt[index-1] += meta_txt[index]
                        meta_txt[index] = '\n'
            return meta_txt
        meta_txt = 合并小写开头的段落块(meta_txt)
        meta_txt = 清理多余的空行(meta_txt)

        meta_txt = '\n'.join(meta_txt)
        # 清除重复的换行
        for _ in range(5):
            meta_txt = meta_txt.replace('\n\n', '\n')

        # 换行 -> 双换行
        meta_txt = meta_txt.replace('\n', '\n\n')

    return meta_txt, page_one_meta


@CatchException
def 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, sys_prompt, web_port):
    import glob
    import os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结PDF文档。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
        import tiktoken
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf tiktoken```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(
        f'{project_folder}/**/*.pdf', recursive=True)]

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.tex或.pdf文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, sys_prompt)


def 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, sys_prompt):
    import os
    import tiktoken
    TOKEN_LIMIT_PER_FRAGMENT = 1600
    generated_conclusion_files = []
    for index, fp in enumerate(file_manifest):
        # 读取PDF文件
        file_content, page_one = read_and_clean_pdf_text(fp)
        # 递归地切割PDF文件
        from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf
        from toolbox import get_conf
        enc = tiktoken.encoding_for_model(*get_conf('LLM_MODEL'))
        def get_token_num(txt): return len(enc.encode(txt))
        # 分解文本
        paper_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
            txt=file_content,  get_token_fn=get_token_num, limit=TOKEN_LIMIT_PER_FRAGMENT)
        page_one_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
            txt=str(page_one), get_token_fn=get_token_num, limit=TOKEN_LIMIT_PER_FRAGMENT//4)
        # 为了更好的效果，我们剥离Introduction之后的部分
        paper_meta = page_one_fragments[0].split('introduction')[0].split(
            'Introduction')[0].split('INTRODUCTION')[0]
        # 单线，获取文章meta信息
        paper_meta_info = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=f"以下是一篇学术论文的基础信息，请从中提取出“标题”、“收录会议或期刊”、“作者”、“摘要”、“编号”、“作者邮箱”这六个部分。请用markdown格式输出，最后用中文翻译摘要部分。请提取：{paper_meta}",
            inputs_show_user=f"请从{fp}中提取出“标题”、“收录会议或期刊”等基本信息。",
            llm_kwargs=llm_kwargs,
            chatbot=chatbot, history=[],
            sys_prompt="Your job is to collect information from materials。",
        )
        # 多线，翻译
        gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"以下是你需要翻译的文章段落：\n{frag}" for frag in paper_fragments],
            inputs_show_user_array=[f"" for _ in paper_fragments],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[[paper_meta] for _ in paper_fragments],
            sys_prompt_array=[
                "请你作为一个学术翻译，把整个段落翻译成中文，要求语言简洁，禁止重复输出原文。" for _ in paper_fragments],
            max_workers=16  # OpenAI所允许的最大并行过载
        )

        final = ["", paper_meta_info + '\n\n---\n\n---\n\n---\n\n']
        final.extend(gpt_response_collection)
        create_report_file_name = f"{os.path.basename(fp)}.trans.md"
        res = write_results_to_file(final, file_name=create_report_file_name)
        generated_conclusion_files.append(f'./gpt_log/{create_report_file_name}')
        chatbot.append((f"{fp}完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=chatbot) # 刷新界面

    # 准备文件的下载
    import shutil
    for pdf_path in generated_conclusion_files:
        # 重命名文件
        rename_file = f'./gpt_log/总结论文-{os.path.basename(pdf_path)}'
        if os.path.exists(rename_file):
            os.remove(rename_file)
        shutil.copyfile(pdf_path, rename_file)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    chatbot.append(("给出输出文件清单", str(generated_conclusion_files)))
    yield from update_ui(chatbot=chatbot, history=chatbot, msg=msg) # 刷新界面
