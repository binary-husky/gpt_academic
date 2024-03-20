from toolbox import CatchException, report_exception, get_log_folder, gen_time_str
from toolbox import update_ui, promote_file_to_downloadzone, update_ui_lastest_msg, disable_auto_promotion
from toolbox import write_history_to_file, zip_result
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from .pdf_fns.parse_pdf import parse_pdf, get_avail_grobid_url, translate_pdf
from colorful import *
import copy
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

def 按图片拆分文档(input_pdf_path):
    """
    将会按照图片拆分上下文，将图片单独储存的同时会储存附近的上下文以便后续进行模糊匹配位置。
    """
    import fitz
    import json
    doc = fitz.open(input_pdf_path)
    page_ranges = []  # 用于存储拆分后的页面范围
    current_range_start = 0  # 当前页面范围的起始页
    has_images = False  # 标记当前处理的页面是否含有图片
    
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        img_list = page.get_images(full=True)
        text_blocks = page.get_text("blocks")
        
        if img_list:
            if not has_images and current_range_start < page_number:
                page_ranges.append((current_range_start, page_number - 1))
            page_ranges.append((page_number, page_number))
            has_images = True
        else:
            if has_images:
                current_range_start = page_number
            has_images = False

    if not has_images:
        page_ranges.append((current_range_start, len(doc) - 1))

    files_splited = []
    if not os.path.exists(input_pdf_path.split('.')[0]):
        os.makedirs(input_pdf_path.split('.')[0])
    for start, end in page_ranges:
        output_doc = fitz.open()
        for page_number in range(start, end + 1):
            output_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)
        
        output_pdf_path = f"{input_pdf_path.split('.')[0]}/{start + 1}_to_{end + 1}.pdf"
        output_doc.save(output_pdf_path)
        
        # 对于每个页面范围，检查并保存图片及相关文本
        for page_number in range(start, end + 1):
            page = doc.load_page(page_number)
            images = page.get_images(full=True)
            text_blocks = page.get_text("blocks")
            if images:
                image_folder = f"{input_pdf_path.split('.')[0]}/{start + 1}_to_{end + 1}_images"
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_file_path = f"{image_folder}/{page_number + 1}_{img_index + 1}.png"
                    with open(image_file_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    # 查找与图片相关的文本块
                    img_rect = page.get_image_bbox(img)
                    above_texts, below_texts = [], []
                    for block in text_blocks:
                        block_rect = fitz.Rect(block[:4])
                        if block_rect.y0 < img_rect.y0:
                            above_texts.append(block[4])
                        elif block_rect.y0 > img_rect.y0:
                            below_texts.append(block[4])
                    
                    related_texts = {
                        "above": above_texts[:2],
                        "below": below_texts[:3]
                    }
                    
                    # 保存相关文本到.find文件
                    find_file_path = f"{image_file_path}.find"
                    with open(find_file_path, "w") as find_file:
                        json.dump(related_texts, find_file, ensure_ascii=False, indent=4)
        
        files_splited.append({"path": output_pdf_path, "picture": True if images else False})

    doc.close()
    return files_splited

def 模糊匹配添加图片(markdown_file_path, pdf_file_path):
    import json
    from fuzzywuzzy import process
    import fuzzywuzzy.fuzz as fuzz
    # 从PDF文件路径获取基础路径和图片文件夹路径
    base_path = pdf_file_path.split('.')[0]
    image_folder = f"{base_path}_images"
    
    # 读取Markdown文档内容
    with open(markdown_file_path, 'r', encoding='utf-8') as md_file:
        markdown_content = md_file.readlines()
        markdown_content_stripped = [line.strip() for line in markdown_content]
    
    for find_file_name in os.listdir(image_folder):
        if find_file_name.endswith('.find'):
            image_file_path = f"{image_folder}/{find_file_name[:-5]}"
            with open(f"{image_folder}/{find_file_name}", 'r', encoding='utf-8') as find_file:
                find_data = json.load(find_file)
            # 根据.find文件中的文本信息查找插入位置
            insert_index = None
            search_texts = find_data['below'] + find_data['above']
            for text in search_texts:
                text = text.replace('\n', '').strip()
                # 使用fuzzywuzzy进行模糊匹配
                try:
                    best_match, similarity = process.extractOne(text, markdown_content_stripped, scorer=fuzz.partial_ratio)
                except:
                    continue
                if similarity > 90:
                    line_index = markdown_content_stripped.index(best_match)
                    insert_index = line_index - 1 if text in find_data['above'] else line_index + 1
                    if insert_index < 0:
                        insert_index = 1
                    break

            # 重构路径方便后续编辑
            # print(f"1:{find_file_name}")
            find_file_path = f"{image_folder}/{find_file_name}"
            image_file_path_components = find_file_path[:-5].split('/')
            # print(f"2:{image_file_path_components}")
            image_file_path = "./images/" + "/".join(image_file_path_components[-2:])
            # print(f"3:{image_file_path}")
            if insert_index is not None:
                image_markdown = f"\n![Image]({image_file_path})\n"
                markdown_content.insert(insert_index, image_markdown)
            else:
                # 如果实在没找到，没办法了只能放在最后
                image_markdown = f"\n![Image]({image_file_path})\n"
                markdown_content.append(image_markdown)
                logging.info(f"Fail to find place of {image_file_path}")
    
    # 保存更新后的Markdown文档
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.writelines(markdown_content)

@CatchException
def 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    disable_auto_promotion(chatbot)
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "使用NOUGAT-OCR处理并批量翻译PDF文档。注意,由于NOUGAT使用学术论文进行的训练,在处理非学术文件时可能效果不佳。\n \
        NOUGAT默认情况下会跳过图片部分，您可以在高级参数处输入数字'1'，程序将会尝试将原文图片匹配到译文中(实验性)，这需要原文是\
        非纯图片PDF，并且会导致处理时间变长，默认不会尝试匹配。函数插件贡献者: Binary-Husky, Menghuan1918"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 清空历史，以免输入溢出
    history = []

    from .crazy_utils import get_files_from_everything
    success, file_manifest, project_folder = get_files_from_everything(txt, type='.pdf')
    if len(file_manifest) > 0:
        # 尝试导入依赖，如果缺少依赖，则给出安装建议
        try:
            import nougat
            import tiktoken
        except:
            report_exception(chatbot, history,
                             a=f"解析项目: {txt}",
                             b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade nougat-ocr tiktoken```。")
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
            return
    if plugin_kwargs == 1:
        try:
            import fitz
            import fuzzywuzzy
            import pypandoc
        except:
            report_exception(chatbot, history,
                             a=f"解析项目: {txt}",
                             b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade PyMuPDF fuzzywuzzy pypandoc_binary```。")
            yield from update_ui(chatbot=chatbot, history=history)
            return
    success_mmd, file_manifest_mmd, _ = get_files_from_everything(txt, type='.mmd')
    success = success or success_mmd
    file_manifest += file_manifest_mmd
    chatbot.append(["文件列表：", ", ".join([e.split('/')[-1] for e in file_manifest])]);
    yield from update_ui(      chatbot=chatbot, history=history)
    # 检测输入参数，如没有给定输入参数，直接退出
    if not success:
        if txt == "": txt = '空空如也的输入栏'

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.pdf拓展名的文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    split = plugin_kwargs.get("advanced_arg", "")
    # 开始正式执行任务
    yield from 解析PDF_基于NOUGAT(file_manifest, project_folder, llm_kwargs, split, chatbot, history, system_prompt)

def 编译pdf(image_zip, markdown_file, chatbot, generated_conclusion_files):
    import pypandoc
    import zipfile
    import shutil
    # 将图片压缩包解压
    with zipfile.ZipFile(image_zip, 'r') as zip_ref:
        zip_ref.extractall(f"{os.path.dirname(image_zip)}/images")
    # 将markdown文件编译为pdf,但是转换PDF需要LaTeX环境，保留一个word版本
    output_file = f"{markdown_file.split('.')[0]}.pdf"
    print(f"output_file:{output_file}")
    try:
        pypandoc.convert_file(markdown_file, 'pdf', outputfile=output_file, extra_args=[f'--resource-path={os.path.dirname(image_zip)}','-V', 'geometry:margin=1in'])
        logging.info(f"Converted the markdowm to {output_file}")
    except Exception as e:
        print亮红(f"未能转换为PDF，这可能是由于未配置Tex环境造成的，尝试转换为Word文档。")
        logging.error(e)
        try:
            output_file = f"{markdown_file.split('.')[0]}.docx"
            pypandoc.convert_file(markdown_file, 'docx', outputfile=output_file, extra_args=[f'--resource-path={os.path.dirname(image_zip)}'])
        except Exception as e:
            logging.error(e)
            output_file = None
    # 删除解压出的图片文件夹,并且如编译成功则发送到下载区
    if output_file:
        promote_file_to_downloadzone(output_file, chatbot=chatbot)
        generated_conclusion_files.append(output_file)
    if os.path.exists(f"{os.path.dirname(image_zip)}/images/"):
        shutil.rmtree(f"{os.path.dirname(image_zip)}/images/")

def 解析PDF_基于NOUGAT(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import copy
    import tiktoken
    TOKEN_LIMIT_PER_FRAGMENT = 1024
    generated_conclusion_files = []
    generated_html_files = []
    DST_LANG = "中文"
    from crazy_functions.crazy_utils import nougat_interface
    from crazy_functions.pdf_fns.report_gen_html import construct_html
    nougat_handle = nougat_interface()
    for index, fp in enumerate(file_manifest):
        if fp.endswith('pdf'):
            if plugin_kwargs == "1":
                split_result = 按图片拆分文档(fp)
                files_nougat = []
                chatbot.append(["当前进度：", f"正在解析论文，请稍候，您启用了匹配图片到结果的参数，这会使解析的时间稍微增加。（第一次运行时，需要花费较长时间下载NOUGAT参数）"]); yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

                for file in split_result:
                    if file["picture"]:
                        temp_onougat = yield from nougat_handle.NOUGAT_parse_pdf(file["path"], chatbot, history)
                        files_nougat.append(temp_onougat)
                        模糊匹配添加图片(temp_onougat, file["path"])
                    else:
                        temp_onougat = yield from nougat_handle.NOUGAT_parse_pdf(file["path"], chatbot, history)
                        files_nougat.append(temp_onougat)
                fpp = fp
                with open(fpp, "w", encoding="utf-8") as result_file:
                    for file in files_nougat:
                        with open(file, "r", encoding="utf-8") as temp_file:
                            result_file.write(temp_file.read())
                            result_file.write("\n")
                        os.remove(file)
                for file in split_result:
                    os.remove(file["path"])
                image_folder = f"{fp.split('.')[0]}"
                zip_images = zip_result(image_folder)
                image_zip = promote_file_to_downloadzone(zip_images, rename_file=os.path.basename(zip_images)+'images.zip', chatbot=chatbot)
                promote_file_to_downloadzone(fpp, rename_file=os.path.basename(fpp)+'.nougat.mmd', chatbot=chatbot)
            else:
                chatbot.append(["当前进度：", f"正在解析论文，请稍候。（第一次运行时，需要花费较长时间下载NOUGAT参数）"]); yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
                fpp = yield from nougat_handle.NOUGAT_parse_pdf(fp, chatbot, history)
                promote_file_to_downloadzone(fpp, rename_file=os.path.basename(fpp)+'.nougat.mmd', chatbot=chatbot)
        else:
            chatbot.append(["当前论文无需解析：", fp]); yield from update_ui(      chatbot=chatbot, history=history)
            fpp = fp
        with open(fpp, 'r', encoding='utf8') as f:
            article_content = f.readlines()
        article_dict = markdown_to_dict(article_content)
        logging.info(article_dict)
        yield from translate_pdf(article_dict, llm_kwargs, chatbot, fp, generated_conclusion_files, TOKEN_LIMIT_PER_FRAGMENT, DST_LANG)
        
        if plugin_kwargs == "1":
            markdown_file = generated_conclusion_files[1]
            编译pdf(image_zip, markdown_file, chatbot, generated_conclusion_files)
    if plugin_kwargs == "1":
        chatbot.append(["如要在mmd文档中查看文件，请将压缩包中图片解压到同一目录下的‘images’文件夹中\n给出输出文件清单", str(generated_conclusion_files + generated_html_files)])
    else:
        chatbot.append(("给出输出文件清单", str(generated_conclusion_files + generated_html_files)))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


