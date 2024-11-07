from toolbox import get_log_folder
from toolbox import update_ui, promote_file_to_downloadzone
from toolbox import write_history_to_file, promote_file_to_downloadzone
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from crazy_functions.crazy_utils import read_and_clean_pdf_text
from shared_utils.colorful import *
from loguru import logger
import os

def 解析PDF_简单拆解(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    """
    注意：此函数已经弃用！！新函数位于：crazy_functions/pdf_fns/parse_pdf.py
    """
    import copy
    TOKEN_LIMIT_PER_FRAGMENT = 1024
    generated_conclusion_files = []
    generated_html_files = []
    from crazy_functions.pdf_fns.report_gen_html import construct_html
    for index, fp in enumerate(file_manifest):
        # 读取PDF文件
        file_content, page_one = read_and_clean_pdf_text(fp)
        file_content = file_content.encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
        page_one = str(page_one).encode('utf-8', 'ignore').decode()      # avoid reading non-utf8 chars

        # 递归地切割PDF文件
        from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
        paper_fragments = breakdown_text_to_satisfy_token_limit(txt=file_content, limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs['llm_model'])
        page_one_fragments = breakdown_text_to_satisfy_token_limit(txt=page_one, limit=TOKEN_LIMIT_PER_FRAGMENT//4, llm_model=llm_kwargs['llm_model'])

        # 为了更好的效果，我们剥离Introduction之后的部分（如果有）
        paper_meta = page_one_fragments[0].split('introduction')[0].split('Introduction')[0].split('INTRODUCTION')[0]

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
                f"你需要翻译以下内容：\n{frag}" for frag in paper_fragments],
            inputs_show_user_array=[f"\n---\n 原文： \n\n {frag.replace('#', '')}  \n---\n 翻译：\n " for frag in paper_fragments],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[[paper_meta] for _ in paper_fragments],
            sys_prompt_array=[
                "请你作为一个学术翻译，负责把学术论文准确翻译成中文。注意文章中的每一句话都要翻译。" + plugin_kwargs.get("additional_prompt", "")
                for _ in paper_fragments],
            # max_workers=5  # OpenAI所允许的最大并行过载
        )
        gpt_response_collection_md = copy.deepcopy(gpt_response_collection)
        # 整理报告的格式
        for i,k in enumerate(gpt_response_collection_md):
            if i%2==0:
                gpt_response_collection_md[i] = f"\n\n---\n\n ## 原文[{i//2}/{len(gpt_response_collection_md)//2}]： \n\n {paper_fragments[i//2].replace('#', '')}  \n\n---\n\n ## 翻译[{i//2}/{len(gpt_response_collection_md)//2}]：\n "
            else:
                gpt_response_collection_md[i] = gpt_response_collection_md[i]
        final = ["一、论文概况\n\n---\n\n", paper_meta_info.replace('# ', '### ') + '\n\n---\n\n', "二、论文翻译", ""]
        final.extend(gpt_response_collection_md)
        create_report_file_name = f"{os.path.basename(fp)}.trans.md"
        res = write_history_to_file(final, create_report_file_name)
        promote_file_to_downloadzone(res, chatbot=chatbot)

        # 更新UI
        generated_conclusion_files.append(f'{get_log_folder()}/{create_report_file_name}')
        chatbot.append((f"{fp}完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        # write html
        try:
            ch = construct_html()
            orig = ""
            trans = ""
            gpt_response_collection_html = copy.deepcopy(gpt_response_collection)
            for i,k in enumerate(gpt_response_collection_html):
                if i%2==0:
                    gpt_response_collection_html[i] = paper_fragments[i//2].replace('#', '')
                else:
                    gpt_response_collection_html[i] = gpt_response_collection_html[i]
            final = ["论文概况", paper_meta_info.replace('# ', '### '),  "二、论文翻译",  ""]
            final.extend(gpt_response_collection_html)
            for i, k in enumerate(final):
                if i%2==0:
                    orig = k
                if i%2==1:
                    trans = k
                    ch.add_row(a=orig, b=trans)
            create_report_file_name = f"{os.path.basename(fp)}.trans.html"
            generated_html_files.append(ch.save_file(create_report_file_name))
        except:
            from toolbox import trimmed_format_exc
            logger.error('writing html result failed:', trimmed_format_exc())

    # 准备文件的下载
    for pdf_path in generated_conclusion_files:
        # 重命名文件
        rename_file = f'翻译-{os.path.basename(pdf_path)}'
        promote_file_to_downloadzone(pdf_path, rename_file=rename_file, chatbot=chatbot)
    for html_path in generated_html_files:
        # 重命名文件
        rename_file = f'翻译-{os.path.basename(html_path)}'
        promote_file_to_downloadzone(html_path, rename_file=rename_file, chatbot=chatbot)
    chatbot.append(("给出输出文件清单", str(generated_conclusion_files + generated_html_files)))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


