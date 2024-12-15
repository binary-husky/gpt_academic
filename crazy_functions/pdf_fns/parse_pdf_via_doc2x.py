from toolbox import get_log_folder, gen_time_str, get_conf
from toolbox import update_ui, promote_file_to_downloadzone
from toolbox import promote_file_to_downloadzone, extract_archive
from toolbox import generate_file_link, zip_folder
from crazy_functions.crazy_utils import get_files_from_everything
from shared_utils.colorful import *
from loguru import logger
import os
import time

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



def 解析PDF_DOC2X_转Latex(pdf_file_path):
    zip_file_path, unzipped_folder = 解析PDF_DOC2X(pdf_file_path, format='tex')
    return unzipped_folder


def 解析PDF_DOC2X(pdf_file_path, format='tex'):
    """
        format: 'tex', 'md', 'docx'
    """
    import requests, json, os
    DOC2X_API_KEY = get_conf('DOC2X_API_KEY')
    latex_dir = get_log_folder(plugin_name="pdf_ocr_latex")
    markdown_dir = get_log_folder(plugin_name="pdf_ocr")
    doc2x_api_key = DOC2X_API_KEY


    # < ------ 第1步：上传 ------ >
    logger.info("Doc2x 第1步：上传")
    with open(pdf_file_path, 'rb') as file:
        res = requests.post(
            "https://v2.doc2x.noedgeai.com/api/v2/parse/pdf",
            headers={"Authorization": "Bearer " + doc2x_api_key},
            data=file
        )
    # res_json = []
    if res.status_code == 200:
        res_json = res.json()
    else:
        raise RuntimeError(f"Doc2x return an error: {res.json()}")
    uuid = res_json['data']['uid']

    # < ------ 第2步：轮询等待 ------ >
    logger.info("Doc2x 第2步：轮询等待")
    params = {'uid': uuid}
    while True:
        res = requests.get(
            'https://v2.doc2x.noedgeai.com/api/v2/parse/status',
            headers={"Authorization": "Bearer " + doc2x_api_key},
            params=params
        )
        res_json = res.json()
        if res_json['data']['status'] == "success":
            break
        elif res_json['data']['status'] == "processing":
            time.sleep(3)
            logger.info(f"Doc2x is processing at {res_json['data']['progress']}%")
        elif res_json['data']['status'] == "failed":
            raise RuntimeError(f"Doc2x return an error: {res_json}")


    # < ------ 第3步：提交转化 ------ >
    logger.info("Doc2x 第3步：提交转化")
    data = {
        "uid": uuid,
        "to": format,
        "formula_mode": "dollar",
        "filename": "output"
    }
    res = requests.post(
        'https://v2.doc2x.noedgeai.com/api/v2/convert/parse',
        headers={"Authorization": "Bearer " + doc2x_api_key},
        json=data
    )
    if res.status_code == 200:
        res_json = res.json()
    else:
        raise RuntimeError(f"Doc2x return an error: {res.json()}")


    # < ------ 第4步：等待结果 ------ >
    logger.info("Doc2x 第4步：等待结果")
    params = {'uid': uuid}
    while True:
        res = requests.get(
            'https://v2.doc2x.noedgeai.com/api/v2/convert/parse/result',
            headers={"Authorization": "Bearer " + doc2x_api_key},
            params=params
        )
        res_json = res.json()
        if res_json['data']['status'] == "success":
            break
        elif res_json['data']['status'] == "processing":
            time.sleep(3)
            logger.info(f"Doc2x still processing")
        elif res_json['data']['status'] == "failed":
            raise RuntimeError(f"Doc2x return an error: {res_json}")


    # < ------ 第5步：最后的处理 ------ >
    logger.info("Doc2x 第5步：最后的处理")

    if format=='tex':
        target_path = latex_dir
    if format=='md':
        target_path = markdown_dir
    os.makedirs(target_path, exist_ok=True)

    max_attempt = 3
    # < ------ 下载 ------ >
    for attempt in range(max_attempt):
        try:
            result_url = res_json['data']['url']
            res = requests.get(result_url)
            zip_path = os.path.join(target_path, gen_time_str() + '.zip')
            unzip_path = os.path.join(target_path, gen_time_str())
            if res.status_code == 200:
                with open(zip_path, "wb") as f: f.write(res.content)
            else:
                raise RuntimeError(f"Doc2x return an error: {res.json()}")
        except Exception as e:
            if attempt < max_attempt - 1:
                logger.error(f"Failed to download latex file, retrying... {e}")
                time.sleep(3)
                continue
            else:
                raise e

    # < ------ 解压 ------ >
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    return zip_path, unzip_path


def 解析PDF_DOC2X_单文件(fp, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, DOC2X_API_KEY, user_request):

    def pdf2markdown(filepath):
        chatbot.append((None, f"Doc2x 解析中"))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

        md_zip_path, unzipped_folder = 解析PDF_DOC2X(filepath, format='md')

        promote_file_to_downloadzone(md_zip_path, chatbot=chatbot)
        chatbot.append((None, f"完成解析 {md_zip_path} ..."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return md_zip_path

    def deliver_to_markdown_plugin(md_zip_path, user_request):
        from crazy_functions.Markdown_Translate import Markdown英译中
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
        success, file_manifest, project_folder = get_files_from_everything(ex_folder, type='.md', chatbot=chatbot)
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
            #     # Markdown中使用不标准的表格，需要在表格前加上一个emoji，以便公式渲染
            #     md = re.sub(r'^<table>', r'.<table>', md, flags=re.MULTILINE)
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
            # content = re.sub(r'^<table>', r'.<table>', content, flags=re.MULTILINE)
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

def 解析PDF_基于DOC2X(file_manifest, *args):
    for index, fp in enumerate(file_manifest):
        yield from 解析PDF_DOC2X_单文件(fp, *args)
    return


