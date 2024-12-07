from toolbox import get_log_folder, gen_time_str, get_conf
from toolbox import update_ui, promote_file_to_downloadzone
from toolbox import promote_file_to_downloadzone, extract_archive
from toolbox import generate_file_link, zip_folder
from crazy_functions.crazy_utils import get_files_from_everything
from shared_utils.colorful import *
from loguru import logger
import os
import requests
import time


def retry_request(max_retries=3, delay=3):
    """
    Decorator for retrying HTTP requests
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.error(
                            f"Request failed, retrying... ({attempt + 1}/{max_retries}) Error: {e}"
                        )
                        time.sleep(delay)
                        continue
                    raise e
            return None

        return wrapper

    return decorator


@retry_request()
def make_request(method, url, **kwargs):
    """
    Make HTTP request with retry mechanism
    """
    return requests.request(method, url, **kwargs)


def doc2x_api_response_status(response, uid=""):
    """
    Check the status of Doc2x API response
    Args:
        response_data: Response object from Doc2x API
    """
    response_json = response.json()
    response_data = response_json.get("data", {})
    code = response_json.get("code", "Unknown")
    meg = response_data.get("message", response_json)
    trace_id = response.headers.get("trace-id", "Failed to get trace-id")
    if response.status_code != 200:
        raise RuntimeError(
            f"Doc2x return an error:\nTrace ID: {trace_id} {uid}\n{response.status_code} - {response_json}"
        )
    if code in ["parse_page_limit_exceeded", "parse_concurrency_limit"]:
        raise RuntimeError(
            f"Reached the limit of Doc2x:\nTrace ID: {trace_id} {uid}\n{code} - {meg}"
        )
    if code not in ["ok", "success"]:
        raise RuntimeError(
            f"Doc2x return an error:\nTrace ID: {trace_id} {uid}\n{code} - {meg}"
        )
    return response_data


def 解析PDF_DOC2X_转Latex(pdf_file_path):
    zip_file_path, unzipped_folder = 解析PDF_DOC2X(pdf_file_path, format="tex")
    return unzipped_folder


def 解析PDF_DOC2X(pdf_file_path, format="tex"):
    """
    format: 'tex', 'md', 'docx'
    """

    DOC2X_API_KEY = get_conf("DOC2X_API_KEY")
    latex_dir = get_log_folder(plugin_name="pdf_ocr_latex")
    markdown_dir = get_log_folder(plugin_name="pdf_ocr")
    doc2x_api_key = DOC2X_API_KEY

    # < ------ 第1步：预上传获取URL，然后上传文件 ------ >
    logger.info("Doc2x 上传文件：预上传获取URL")
    res = make_request(
        "POST",
        "https://v2.doc2x.noedgeai.com/api/v2/parse/preupload",
        headers={"Authorization": "Bearer " + doc2x_api_key},
        timeout=15,
    )
    res_data = doc2x_api_response_status(res)
    upload_url = res_data["url"]
    uuid = res_data["uid"]

    logger.info("Doc2x 上传文件：上传文件")
    with open(pdf_file_path, "rb") as file:
        res = make_request("PUT", upload_url, data=file, timeout=60)
    res.raise_for_status()

    # < ------ 第2步：轮询等待 ------ >
    logger.info("Doc2x 处理文件中：轮询等待")
    params = {"uid": uuid}
    max_attempts = 60
    attempt = 0
    while attempt < max_attempts:
        res = make_request(
            "GET",
            "https://v2.doc2x.noedgeai.com/api/v2/parse/status",
            headers={"Authorization": "Bearer " + doc2x_api_key},
            params=params,
            timeout=15,
        )
        res_data = doc2x_api_response_status(res)
        if res_data["status"] == "success":
            break
        elif res_data["status"] == "processing":
            time.sleep(5)
            logger.info(f"Doc2x is processing at {res_data['progress']}%")
            attempt += 1
        else:
            raise RuntimeError(f"Doc2x return an error: {res_data}")
    if attempt >= max_attempts:
        raise RuntimeError("Doc2x processing timeout after maximum attempts")

    # < ------ 第3步：提交转化 ------ >
    logger.info("Doc2x 第3步：提交转化")
    data = {
        "uid": uuid,
        "to": format,
        "formula_mode": "dollar",
        "filename": "output"
    }
    res = make_request(
        "POST",
        "https://v2.doc2x.noedgeai.com/api/v2/convert/parse",
        headers={"Authorization": "Bearer " + doc2x_api_key},
        json=data,
        timeout=15,
    )
    doc2x_api_response_status(res, uid=f"uid: {uuid}")

    # < ------ 第4步：等待结果 ------ >
    logger.info("Doc2x 第4步：等待结果")
    params = {"uid": uuid}
    max_attempts = 36
    attempt = 0
    while attempt < max_attempts:
        res = make_request(
            "GET",
            "https://v2.doc2x.noedgeai.com/api/v2/convert/parse/result",
            headers={"Authorization": "Bearer " + doc2x_api_key},
            params=params,
            timeout=15,
        )
        res_data = doc2x_api_response_status(res, uid=f"uid: {uuid}")
        if res_data["status"] == "success":
            break
        elif res_data["status"] == "processing":
            time.sleep(3)
            logger.info("Doc2x still processing to convert file")
            attempt += 1
    if attempt >= max_attempts:
        raise RuntimeError("Doc2x conversion timeout after maximum attempts")

    # < ------ 第5步：最后的处理 ------ >
    logger.info("Doc2x 第5步：下载转换后的文件")

    if format == "tex":
        target_path = latex_dir
    if format == "md":
        target_path = markdown_dir
    os.makedirs(target_path, exist_ok=True)

    max_attempt = 3
    # < ------ 下载 ------ >
    for attempt in range(max_attempt):
        try:
            result_url = res_data["url"]
            res = make_request("GET", result_url, timeout=60)
            zip_path = os.path.join(target_path, gen_time_str() + ".zip")
            unzip_path = os.path.join(target_path, gen_time_str())
            if res.status_code == 200:
                with open(zip_path, "wb") as f:
                    f.write(res.content)
            else:
                raise RuntimeError(f"Doc2x return an error: {res.json()}")
        except Exception as e:
            if attempt < max_attempt - 1:
                logger.error(f"Failed to download uid = {uuid} file, retrying... {e}")
                time.sleep(3)
                continue
            else:
                raise e

    # < ------ 解压 ------ >
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(unzip_path)
    return zip_path, unzip_path


def 解析PDF_DOC2X_单文件(
    fp,
    project_folder,
    llm_kwargs,
    plugin_kwargs,
    chatbot,
    history,
    system_prompt,
    DOC2X_API_KEY,
    user_request,
):
    def pdf2markdown(filepath):
        chatbot.append((None, f"Doc2x 解析中"))
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

        md_zip_path, unzipped_folder = 解析PDF_DOC2X(filepath, format="md")

        promote_file_to_downloadzone(md_zip_path, chatbot=chatbot)
        chatbot.append((None, f"完成解析 {md_zip_path} ..."))
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
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
        extract_archive(file_path=this_file_path, dest_dir=ex_folder)

        # edit markdown files
        success, file_manifest, project_folder = get_files_from_everything(
            ex_folder, type=".md"
        )
        for generated_fp in file_manifest:
            # 修正一些公式问题
            with open(generated_fp, "r", encoding="utf8") as f:
                content = f.read()
            # 将公式中的\[ \]替换成$$
            content = content.replace(r"\[", r"$$").replace(r"\]", r"$$")
            # 将公式中的\( \)替换成$
            content = content.replace(r"\(", r"$").replace(r"\)", r"$")
            content = content.replace("```markdown", "\n").replace("```", "\n")
            with open(generated_fp, "w", encoding="utf8") as f:
                f.write(content)
            promote_file_to_downloadzone(generated_fp, chatbot=chatbot)
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

            # 生成在线预览html
            file_name = "在线预览翻译（原文）" + gen_time_str() + ".html"
            preview_fp = os.path.join(ex_folder, file_name)
            from shared_utils.advanced_markdown_format import (
                markdown_convertion_for_file,
            )

            with open(generated_fp, "r", encoding="utf-8") as f:
                md = f.read()
            #     # Markdown中使用不标准的表格，需要在表格前加上一个emoji，以便公式渲染
            #     md = re.sub(r'^<table>', r'.<table>', md, flags=re.MULTILINE)
            html = markdown_convertion_for_file(md)
            with open(preview_fp, "w", encoding="utf-8") as f:
                f.write(html)
            chatbot.append([None, f"生成在线预览：{generate_file_link([preview_fp])}"])
            promote_file_to_downloadzone(preview_fp, chatbot=chatbot)

        chatbot.append((None, f"调用Markdown插件 {ex_folder} ..."))
        plugin_kwargs["markdown_expected_output_dir"] = ex_folder

        translated_f_name = "translated_markdown.md"
        generated_fp = plugin_kwargs["markdown_expected_output_path"] = os.path.join(
            ex_folder, translated_f_name
        )
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        yield from Markdown英译中(
            ex_folder,
            llm_kwargs,
            plugin_kwargs,
            chatbot,
            history,
            system_prompt,
            user_request,
        )
        if os.path.exists(generated_fp):
            # 修正一些公式问题
            with open(generated_fp, "r", encoding="utf8") as f:
                content = f.read()
            content = content.replace("```markdown", "\n").replace("```", "\n")
            # Markdown中使用不标准的表格，需要在表格前加上一个emoji，以便公式渲染
            # content = re.sub(r'^<table>', r'.<table>', content, flags=re.MULTILINE)
            with open(generated_fp, "w", encoding="utf8") as f:
                f.write(content)
            # 生成在线预览html
            file_name = "在线预览翻译" + gen_time_str() + ".html"
            preview_fp = os.path.join(ex_folder, file_name)
            from shared_utils.advanced_markdown_format import (
                markdown_convertion_for_file,
            )

            with open(generated_fp, "r", encoding="utf-8") as f:
                md = f.read()
            html = markdown_convertion_for_file(md)
            with open(preview_fp, "w", encoding="utf-8") as f:
                f.write(html)
            promote_file_to_downloadzone(preview_fp, chatbot=chatbot)
            # 生成包含图片的压缩包
            dest_folder = get_log_folder(chatbot.get_user())
            zip_name = "翻译后的带图文档.zip"
            zip_folder(
                source_folder=ex_folder, dest_folder=dest_folder, zip_name=zip_name
            )
            zip_fp = os.path.join(dest_folder, zip_name)
            promote_file_to_downloadzone(zip_fp, chatbot=chatbot)
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    md_zip_path = yield from pdf2markdown(fp)
    yield from deliver_to_markdown_plugin(md_zip_path, user_request)


def 解析PDF_基于DOC2X(file_manifest, *args):
    for index, fp in enumerate(file_manifest):
        yield from 解析PDF_DOC2X_单文件(fp, *args)
    return
