from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, promote_file_to_downloadzone, update_ui_lastest_msg, disable_auto_promotion
from toolbox import write_history_to_file, get_log_folder
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from .pdf_fns.parse_pdf import parse_pdf, get_avail_grobid_url
from colorful import *
import glob
import os
import math

@CatchException
def 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port, only_chinese=True):

    disable_auto_promotion(chatbot)
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量翻译PDF文档。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
        import tiktoken
        import scipdf
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf tiktoken scipdf_parser```。")
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
    grobid_url = get_avail_grobid_url()
    if grobid_url is not None:
        yield from 解析PDF_基于GROBID(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, grobid_url, only_chinese=only_chinese)
    else:
        yield from update_ui_lastest_msg("GROBID服务不可用，请检查config中的GROBID_URL。作为替代，现在将执行效果稍差的旧版代码。", chatbot, history, delay=3)
        yield from 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)


def 解析PDF_基于GROBID(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, grobid_url, only_chinese=True):
    import copy
    import tiktoken
    TOKEN_LIMIT_PER_FRAGMENT = 200
    generated_conclusion_files = []
    generated_html_files = []
    DST_LANG = "中文"
    from crazy_functions.crazy_utils import construct_html
    for index, fp in enumerate(file_manifest):
        chatbot.append(["当前进度：", f"正在连接GROBID服务，请稍候: {grobid_url}\n如果等待时间过长，请修改config中的GROBID_URL，可修改成本地GROBID服务。"]); yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        article_dict = parse_pdf(fp, grobid_url)
        if article_dict is None: raise RuntimeError("解析PDF失败，请检查PDF是否损坏。")
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
        if only_chinese:
            # 直接提取出翻译的内容，然后保存下去：
            chinese_list = []
            # 记录当前的大章节标题：
            last_section_name = ""
            for index, value in enumerate(gpt_response_collection):
                # 先挑选偶数序列号：
                if index % 2 != 0:
                    # 先提取当前英文标题：
                    cur_section_name = gpt_response_collection[index-1].split('\n')[0].split(" Part")[0]

                    # 如果index是1的话，则直接使用first section name：
                    if cur_section_name != last_section_name:
                        cur_value = cur_section_name + '\n'
                        last_section_name = copy.deepcopy(cur_section_name)
                    else:
                        cur_value = ""
                    # 再判断翻译是否错误，如果错误，则直接贴原来的英文：
                    if "The OpenAI account associated" in value:
                        cur_value += gpt_response_collection[index-1]
                    else:
                        # 再做一个小修改：重新修改当前part的标题，默认用英文的
                        cur_value += value

                    chinese_list.append(cur_value)
        
            res_path = write_history_to_file(meta +  ["# Meta Translation" , paper_meta_info] + chinese_list, file_basename=None, file_fullname=None)
            promote_file_to_downloadzone(res_path, rename_file=os.path.basename(fp)+'.md', chatbot=chatbot)
            generated_conclusion_files.append(res_path)
        else:
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
                # 先提取当前英文标题：
                cur_section_name = gpt_response_collection[i-1].split('\n')[0].split(" Part")[0]
                cur_value = cur_section_name + "\n" + gpt_response_collection_html[i]
                gpt_response_collection_html[i] = cur_value

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


def 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import copy
    TOKEN_LIMIT_PER_FRAGMENT = 200
    generated_conclusion_files = []
    generated_html_files = []
    from crazy_functions.crazy_utils import construct_html
    for index, fp in enumerate(file_manifest):
        # 读取PDF文件
        file_content, page_one = read_and_clean_pdf_text(fp)
        file_content = file_content.encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
        page_one = str(page_one).encode('utf-8', 'ignore').decode()      # avoid reading non-utf8 chars

        # 递归地切割PDF文件
        from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf
        # from .crazy_utils import split_main_text
        from request_llm.bridge_all import model_info
        enc = model_info["gpt-3.5-turbo"]['tokenizer']
        def get_token_num(txt): return len(enc.encode(txt, disallowed_special=()))        
        paper_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
            txt=file_content,  get_token_fn=get_token_num, limit=256)
        page_one_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
            txt=page_one, get_token_fn=get_token_num, limit=TOKEN_LIMIT_PER_FRAGMENT)
        ## 用我这个分段切分。
        # paper_fragments = split_main_text(text=file_content, max_token=TOKEN_LIMIT_PER_FRAGMENT)
        # page_one_fragments = split_main_text(text=page_one, max_token=TOKEN_LIMIT_PER_FRAGMENT)
        
        # 为了更好的效果，我们剥离Introduction之后的部分（如果有）
        # paper_meta = page_one_fragments[0].split('introduction')[0].split('Introduction')[0].split('INTRODUCTION')[0]
        paper_meta = page_one_fragments[:]
        
        # 单线，获取文章meta信息
        paper_meta_info = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=f"以下是一篇学术论文的基础信息，请从中提取出“标题”、“收录会议或期刊”、“作者”、“摘要”、“作者单位”、“作者邮箱”这六个部分。请用markdown格式输出，最后用中文翻译摘要部分，不要提取Introduction部分的内容。请提取：{paper_meta}",
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
                "请你作为一个学术翻译，负责把学术论文的部分章节文本，准确翻译成中文。注意：1. 文章中的每一句话都要翻译，并且消除输入文本前后的无意义乱码，2. 请自动识别小章节标题(小标题长度不要超过20个字符，也不要少于3个字符)，并且用'### xxx'的markdown格式标记出来。" for _ in paper_fragments],
            # max_workers=5  # OpenAI所允许的最大并行过载
        )
        gpt_response_collection_md = copy.deepcopy(gpt_response_collection)
        # 整理报告的格式
        add_origin = True
        for i, k in enumerate(gpt_response_collection_md): 
            if i % 2 ==0:
                cur_trans = gpt_response_collection_md[i]
                # 做个小小的处理，把翻译的结果中非常长的“#”去掉
                temp_trans = ""
                for line_text in cur_trans.split('\n'):
                    if len(line_text) == 0:
                        # print("空行")
                        temp_trans += "\n\n"
                    else:
                        if "#" in line_text[0]:
                            if len(line_text.split(' ')) > 12:                                
                                temp_trans += line_text.replace('#', '')
                            else:
                                temp_trans += line_text
                                temp_trans += "\n\n"
                        else:
                            temp_trans += line_text + "\n\n"
                
                # gpt_response_collection_md[i] = f"\n\n---\n\n ## 原文[{i//2}/{len(gpt_response_collection_md)//2}]： \n\n {paper_fragments[i//2].replace('#', '')}  \n\n---\n\n ## 翻译[{i//2}/{len(gpt_response_collection_md)//2}]：\n "
                if add_origin:
                    gpt_response_collection_md[i] = f"\n\n---\n\n ## 原文[{i//2}/{len(gpt_response_collection_md)//2}]： \n\n {paper_fragments[i//2].replace('#', '')}  \n\n---\n\n ## 翻译[{i//2}/{len(gpt_response_collection_md)//2}]：\n "
                else:
                    gpt_response_collection_md[i] = ""                
            else:
                cur_trans = gpt_response_collection_md[i]
                # 做个小小的处理，把翻译的结果中非常长的“#”去掉
                temp_trans = ""
                for line_text in cur_trans.split('\n'):
                    if len(line_text) == 0:
                        # print("空行")
                        temp_trans += "\n\n"
                    else:
                        if "#" in line_text[0]:
                            if len(line_text) > 12:                                
                                temp_trans += line_text.replace('#', '')
                            else:
                                temp_trans += line_text
                                temp_trans += "\n\n"
                        else:
                            temp_trans += line_text + "\n\n"
                            
                gpt_response_collection_md[i] = temp_trans
        final = ["一、论文概况\n\n---\n\n", paper_meta_info.replace('# ', '### ') + '\n\n---\n\n', "二、论文翻译", ""]
        final.extend(gpt_response_collection_md)
        create_report_file_name = f"{os.path.basename(fp)}.trans.md"
        res = write_results_to_file(final, file_name=create_report_file_name)

        # 更新UI
        generated_conclusion_files.append(f'./gpt_log/{create_report_file_name}')
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
            print('writing html result failed:', trimmed_format_exc())

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


