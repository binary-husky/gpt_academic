from toolbox import CatchException, report_execption, gen_time_str
from toolbox import update_ui, promote_file_to_downloadzone, update_ui_lastest_msg, disable_auto_promotion
from toolbox import write_history_to_file, get_log_folder
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from .pdf_fns.parse_pdf import parse_pdf, get_avail_grobid_url
from colorful import *
import os
import math
import logging

def markdown_to_dict(article_content):
    import markdown
    from bs4 import BeautifulSoup
    cur_t = ""
    cur_c = ""
    results = {}
    for line in article_content:
        if line.startswith('#'):
            if cur_t!="":
                if cur_t not in results:
                    results.update({cur_t:cur_c.lstrip('\n')})
                else:
                    # 处理重名的章节
                    results.update({cur_t + " " + gen_time_str():cur_c.lstrip('\n')})
            cur_t = line.rstrip('\n')
            cur_c = ""
        else:
            cur_c += line
    results_final = {}
    for k in list(results.keys()):
        if k.startswith('# '):
            results_final['title'] = k.split('# ')[-1]
            results_final['authors'] = results.pop(k).lstrip('\n')
        if k.startswith('###### Abstract'):
            results_final['abstract'] = results.pop(k).lstrip('\n')

    results_final_sections = []
    for k,v in results.items():
        results_final_sections.append({
            'heading':k.lstrip("# "),
            'text':v if len(v) > 0 else f"The beginning of {k.lstrip('# ')} section."
        })
    results_final['sections'] = results_final_sections
    return results_final


@CatchException
def 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):

    disable_auto_promotion(chatbot)
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量翻译PDF文档。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import nougat
        import tiktoken
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade nougat-ocr tiktoken```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    from .crazy_utils import get_files_from_everything
    success, file_manifest, project_folder = get_files_from_everything(txt, type='.pdf')
    # 检测输入参数，如没有给定输入参数，直接退出
    if not success:
        if txt == "": txt = '空空如也的输入栏'

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.tex或.pdf文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析PDF_基于NOUGAT(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)




def 解析PDF_基于NOUGAT(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import copy
    import tiktoken
    TOKEN_LIMIT_PER_FRAGMENT = 1280
    generated_conclusion_files = []
    generated_html_files = []
    DST_LANG = "中文"
    from crazy_functions.crazy_utils import nougat_interface, construct_html
    nougat_handle = nougat_interface()
    for index, fp in enumerate(file_manifest):
        chatbot.append(["当前进度：", f"正在解析论文，请稍候。（第一次运行时，需要花费较长时间下载NOUGAT参数）"]); yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        fpp = nougat_handle.NOUGAT_parse_pdf(fp)

        with open(fpp, 'r', encoding='utf8') as f:
            article_content = f.readlines()
        article_dict = markdown_to_dict(article_content)
        logging.info(article_dict)

        prompt = "以下是一篇学术论文的基本信息:\n"
        # title
        title = article_dict.get('title', '无法获取 title'); prompt += f'title:{title}\n\n'
        # authors
        authors = article_dict.get('authors', '无法获取 authors'); prompt += f'authors:{authors}\n\n'
        # abstract
        abstract = article_dict.get('abstract', '无法获取 abstract'); prompt += f'abstract:{abstract}\n\n'
        # command
        prompt += f"请将题目和摘要翻译为{DST_LANG}。"
        meta = [f'# Title:\n\n', title, f'# Abstract:\n\n', abstract ]

        # 单线，获取文章meta信息
        paper_meta_info = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=prompt,
            inputs_show_user=prompt,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot, history=[],
            sys_prompt="You are an academic paper reader。",
        )

        # 多线，翻译
        inputs_array = []
        inputs_show_user_array = []

        # get_token_num
        from request_llm.bridge_all import model_info
        enc = model_info[llm_kwargs['llm_model']]['tokenizer']
        def get_token_num(txt): return len(enc.encode(txt, disallowed_special=()))
        from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf

        def break_down(txt):
            raw_token_num = get_token_num(txt)
            if raw_token_num <= TOKEN_LIMIT_PER_FRAGMENT:
                return [txt]
            else:
                # raw_token_num > TOKEN_LIMIT_PER_FRAGMENT
                # find a smooth token limit to achieve even seperation
                count = int(math.ceil(raw_token_num / TOKEN_LIMIT_PER_FRAGMENT))
                token_limit_smooth = raw_token_num // count + count
                return breakdown_txt_to_satisfy_token_limit_for_pdf(txt, get_token_fn=get_token_num, limit=token_limit_smooth)

        for section in article_dict.get('sections'):
            if len(section['text']) == 0: continue
            section_frags = break_down(section['text'])
            for i, fragment in enumerate(section_frags):
                heading = section['heading']
                if len(section_frags) > 1: heading += f' Part-{i+1}'
                inputs_array.append(
                    f"你需要翻译{heading}章节，内容如下: \n\n{fragment}"
                )
                inputs_show_user_array.append(
                    f"# {heading}\n\n{fragment}"
                )

        gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=inputs_array,
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[meta for _ in inputs_array],
            sys_prompt_array=[
                "请你作为一个学术翻译，负责把学术论文准确翻译成中文。注意文章中的每一句话都要翻译。" for _ in inputs_array],
        )
        res_path = write_history_to_file(meta +  ["# Meta Translation" , paper_meta_info] + gpt_response_collection, file_basename=None, file_fullname=None)
        promote_file_to_downloadzone(res_path, rename_file=os.path.basename(fp)+'.md', chatbot=chatbot)
        generated_conclusion_files.append(res_path)

        ch = construct_html() 
        orig = ""
        trans = ""
        gpt_response_collection_html = copy.deepcopy(gpt_response_collection)
        for i,k in enumerate(gpt_response_collection_html): 
            if i%2==0:
                gpt_response_collection_html[i] = inputs_show_user_array[i//2]
            else:
                gpt_response_collection_html[i] = gpt_response_collection_html[i]

        final = ["", "", "一、论文概况",  "", "Abstract", paper_meta_info,  "二、论文翻译",  ""]
        final.extend(gpt_response_collection_html)
        for i, k in enumerate(final): 
            if i%2==0:
                orig = k
            if i%2==1:
                trans = k
                ch.add_row(a=orig, b=trans)
        create_report_file_name = f"{os.path.basename(fp)}.trans.html"
        html_file = ch.save_file(create_report_file_name)
        generated_html_files.append(html_file)
        promote_file_to_downloadzone(html_file, rename_file=os.path.basename(html_file), chatbot=chatbot)

    chatbot.append(("给出输出文件清单", str(generated_conclusion_files + generated_html_files)))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


