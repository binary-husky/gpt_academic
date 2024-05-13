from toolbox import CatchException, report_exception, get_log_folder, gen_time_str, check_packages
from toolbox import update_ui, promote_file_to_downloadzone, update_ui_lastest_msg, disable_auto_promotion
from toolbox import write_history_to_file, promote_file_to_downloadzone, get_conf, extract_archive
from toolbox import generate_file_link, zip_folder, trimmed_format_exc, trimmed_format_exc_markdown
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from .crazy_utils import get_files_from_everything
from .pdf_fns.parse_pdf import parse_pdf, get_avail_grobid_url, translate_pdf
from colorful import *
import os


@CatchException
def 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    disable_auto_promotion(chatbot)
    # 基本信息：功能、贡献者
    chatbot.append([None, "插件功能：批量翻译PDF文档。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        check_packages(["fitz", "tiktoken", "scipdf"])
    except:
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf tiktoken scipdf_parser```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    success, file_manifest, project_folder = get_files_from_everything(txt, type='.pdf')
    # 检测输入参数，如没有给定输入参数，直接退出
    if not success:
        if txt == "": txt = '空空如也的输入栏'

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.pdf拓展名的文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    DOC2X_API_KEY = get_conf("DOC2X_API_KEY")
    # ------- 第一种方法，效果最好，但是需要DOC2X服务 -------
    if len(DOC2X_API_KEY) != 0:
        try:
            yield from 解析PDF_DOC2X(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, DOC2X_API_KEY, user_request)
            return
        except:
            chatbot.append([None, f"DOC2X服务不可用，现在将执行效果稍差的旧版代码。{trimmed_format_exc_markdown()}"])
            yield from update_ui(chatbot=chatbot, history=history)

    # ------- 第二种方法，效果次优 -------
    grobid_url = get_avail_grobid_url()
    if grobid_url is not None:
        yield from 解析PDF_基于GROBID(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, grobid_url)
        return

    # ------- 第三种方法，早期代码，效果不理想 -------
    yield from update_ui_lastest_msg("GROBID服务不可用，请检查config中的GROBID_URL。作为替代，现在将执行效果稍差的旧版代码。", chatbot, history, delay=3)
    yield from 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
    return



def 解析PDF_DOC2X_单文件(fp, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, DOC2X_API_KEY, user_request):

    def refresh_key(doc2x_api_key):
        import requests, json
        url = "https://api.doc2x.noedgeai.com/api/token/refresh"
        res = requests.post(
            url,
            headers={"Authorization": "Bearer " + doc2x_api_key}
        )
        res_json = []
        if res.status_code == 200:
            decoded = res.content.decode("utf-8")
            res_json = json.loads(decoded)
            doc2x_api_key = res_json['data']['token']
        else:
            raise RuntimeError(format("[ERROR] status code: %d, body: %s" % (res.status_code, res.text)))
        return doc2x_api_key

    def pdf2markdown(filepath):
        import requests, json, os
        markdown_dir = get_log_folder(plugin_name="pdf_ocr")
        doc2x_api_key = DOC2X_API_KEY
        if doc2x_api_key.startswith('sk-'):
            url = "https://api.doc2x.noedgeai.com/api/v1/pdf"
        else:
            doc2x_api_key = refresh_key(doc2x_api_key)
            url = "https://api.doc2x.noedgeai.com/api/platform/pdf"

        chatbot.append((None, "加载PDF文件，发送至DOC2X解析..."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        res = requests.post(
            url,
            files={"file": open(filepath, "rb")},
            data={"ocr": "1"},
            headers={"Authorization": "Bearer " + doc2x_api_key}
        )
        res_json = []
        if res.status_code == 200:
            decoded = res.content.decode("utf-8")
            for z_decoded in decoded.split('\n'):
                if len(z_decoded) == 0: continue
                assert z_decoded.startswith("data: ")
                z_decoded = z_decoded[len("data: "):]
                decoded_json = json.loads(z_decoded)
                res_json.append(decoded_json)
        else:
            raise RuntimeError(format("[ERROR] status code: %d, body: %s" % (res.status_code, res.text)))
        uuid = res_json[0]['uuid']
        to = "md" # latex, md, docx
        url = "https://api.doc2x.noedgeai.com/api/export"+"?request_id="+uuid+"&to="+to

        chatbot.append((None, f"读取解析: {url} ..."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        res = requests.get(url, headers={"Authorization": "Bearer " + doc2x_api_key})
        md_zip_path = os.path.join(markdown_dir, gen_time_str() + '.zip')
        if res.status_code == 200:
            with open(md_zip_path, "wb") as f: f.write(res.content)
        else:
            raise RuntimeError(format("[ERROR] status code: %d, body: %s" % (res.status_code, res.text)))
        promote_file_to_downloadzone(md_zip_path, chatbot=chatbot)
        chatbot.append((None, f"完成解析 {md_zip_path} ..."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return md_zip_path

    def deliver_to_markdown_plugin(md_zip_path, user_request):
        from crazy_functions.批量Markdown翻译 import Markdown英译中
        import shutil, re

        time_tag = gen_time_str()
        target_path_base = get_log_folder(chatbot.get_user())
        file_origin_name = os.path.basename(md_zip_path)
        this_file_path = os.path.join(target_path_base, file_origin_name)
        os.makedirs(target_path_base, exist_ok=True)
        shutil.copyfile(md_zip_path, this_file_path)
        ex_folder = this_file_path + ".extract"
        extract_archive(
            file_path=this_file_path, dest_dir=ex_folder
        )

        # edit markdown files
        success, file_manifest, project_folder = get_files_from_everything(ex_folder, type='.md')
        for generated_fp in file_manifest:
            # 修正一些公式问题
            with open(generated_fp, 'r', encoding='utf8') as f:
                content = f.read()
            # 将公式中的\[ \]替换成$$
            content = content.replace(r'\[', r'$$').replace(r'\]', r'$$')
            # 将公式中的\( \)替换成$
            content = content.replace(r'\(', r'$').replace(r'\)', r'$')
            content = content.replace('```markdown', '\n').replace('```', '\n')
            with open(generated_fp, 'w', encoding='utf8') as f:
                f.write(content)
            promote_file_to_downloadzone(generated_fp, chatbot=chatbot)
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

            # 生成在线预览html
            file_name = '在线预览翻译（原文）' + gen_time_str() + '.html'
            preview_fp = os.path.join(ex_folder, file_name)
            from shared_utils.advanced_markdown_format import markdown_convertion_for_file
            with open(generated_fp, "r", encoding="utf-8") as f:
                md = f.read()
                # Markdown中使用不标准的表格，需要在表格前加上一个emoji，以便公式渲染
                md = re.sub(r'^<table>', r'😃<table>', md, flags=re.MULTILINE)
            html = markdown_convertion_for_file(md)
            with open(preview_fp, "w", encoding="utf-8") as f: f.write(html)
            chatbot.append([None, f"生成在线预览：{generate_file_link([preview_fp])}"])
            promote_file_to_downloadzone(preview_fp, chatbot=chatbot)



        chatbot.append((None, f"调用Markdown插件 {ex_folder} ..."))
        plugin_kwargs['markdown_expected_output_dir'] = ex_folder

        translated_f_name = 'translated_markdown.md'
        generated_fp = plugin_kwargs['markdown_expected_output_path'] = os.path.join(ex_folder, translated_f_name)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        yield from Markdown英译中(ex_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
        if os.path.exists(generated_fp):
            # 修正一些公式问题
            with open(generated_fp, 'r', encoding='utf8') as f: content = f.read()
            content = content.replace('```markdown', '\n').replace('```', '\n')
            # Markdown中使用不标准的表格，需要在表格前加上一个emoji，以便公式渲染
            content = re.sub(r'^<table>', r'😃<table>', content, flags=re.MULTILINE)
            with open(generated_fp, 'w', encoding='utf8') as f: f.write(content)
            # 生成在线预览html
            file_name = '在线预览翻译' + gen_time_str() + '.html'
            preview_fp = os.path.join(ex_folder, file_name)
            from shared_utils.advanced_markdown_format import markdown_convertion_for_file
            with open(generated_fp, "r", encoding="utf-8") as f:
                md = f.read()
            html = markdown_convertion_for_file(md)
            with open(preview_fp, "w", encoding="utf-8") as f: f.write(html)
            promote_file_to_downloadzone(preview_fp, chatbot=chatbot)
            # 生成包含图片的压缩包
            dest_folder = get_log_folder(chatbot.get_user())
            zip_name = '翻译后的带图文档.zip'
            zip_folder(source_folder=ex_folder, dest_folder=dest_folder, zip_name=zip_name)
            zip_fp = os.path.join(dest_folder, zip_name)
            promote_file_to_downloadzone(zip_fp, chatbot=chatbot)
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    md_zip_path = yield from pdf2markdown(fp)
    yield from deliver_to_markdown_plugin(md_zip_path, user_request)

def 解析PDF_DOC2X(file_manifest, *args):
    for index, fp in enumerate(file_manifest):
        yield from 解析PDF_DOC2X_单文件(fp, *args)
    return

def 解析PDF_基于GROBID(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, grobid_url):
    import copy, json
    TOKEN_LIMIT_PER_FRAGMENT = 1024
    generated_conclusion_files = []
    generated_html_files = []
    DST_LANG = "中文"
    from crazy_functions.pdf_fns.report_gen_html import construct_html
    for index, fp in enumerate(file_manifest):
        chatbot.append(["当前进度：", f"正在连接GROBID服务，请稍候: {grobid_url}\n如果等待时间过长，请修改config中的GROBID_URL，可修改成本地GROBID服务。"]); yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        article_dict = parse_pdf(fp, grobid_url)
        grobid_json_res = os.path.join(get_log_folder(), gen_time_str() + "grobid.json")
        with open(grobid_json_res, 'w+', encoding='utf8') as f:
            f.write(json.dumps(article_dict, indent=4, ensure_ascii=False))
        promote_file_to_downloadzone(grobid_json_res, chatbot=chatbot)

        if article_dict is None: raise RuntimeError("解析PDF失败，请检查PDF是否损坏。")
        yield from translate_pdf(article_dict, llm_kwargs, chatbot, fp, generated_conclusion_files, TOKEN_LIMIT_PER_FRAGMENT, DST_LANG)
    chatbot.append(("给出输出文件清单", str(generated_conclusion_files + generated_html_files)))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


def 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    """
    此函数已经弃用
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
                "请你作为一个学术翻译，负责把学术论文准确翻译成中文。注意文章中的每一句话都要翻译。" for _ in paper_fragments],
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


