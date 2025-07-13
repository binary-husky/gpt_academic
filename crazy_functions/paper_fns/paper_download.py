import re
import os
import zipfile
from toolbox import CatchException, update_ui, promote_file_to_downloadzone, get_log_folder, get_user

from pathlib import Path
from datetime import datetime

def extract_paper_id(txt):
    """从输入文本中提取论文ID"""
    # 尝试匹配DOI（将DOI匹配提前，因为其格式更加明确）
    doi_patterns = [
        r'doi.org/([\w\./-]+)',        # doi.org/10.1234/xxx
        r'doi:\s*([\w\./-]+)',         # doi: 10.1234/xxx
        r'(10\.\d{4,}/[\w\.-]+)',      # 直接输入DOI: 10.1234/xxx
    ]

    for pattern in doi_patterns:
        match = re.search(pattern, txt, re.IGNORECASE)
        if match:
            return ('doi', match.group(1))

    # 尝试匹配arXiv ID
    arxiv_patterns = [
        r'arxiv.org/abs/(\d+\.\d+)',           # arxiv.org/abs/2103.14030
        r'arxiv.org/pdf/(\d+\.\d+)',           # arxiv.org/pdf/2103.14030
        r'arxiv/(\d+\.\d+)',                   # arxiv/2103.14030
        r'^(\d{4}\.\d{4,5})$',                 # 直接输入ID: 2103.14030
        # 添加对早期arXiv ID的支持
        r'arxiv.org/abs/([\w-]+/\d{7})',       # arxiv.org/abs/math/0211159
        r'arxiv.org/pdf/([\w-]+/\d{7})',       # arxiv.org/pdf/hep-th/9901001
        r'^([\w-]+/\d{7})$',                   # 直接输入: math/0211159
    ]

    for pattern in arxiv_patterns:
        match = re.search(pattern, txt, re.IGNORECASE)
        if match:
            paper_id = match.group(1)
            # 如果是新格式（YYMM.NNNNN）或旧格式（category/NNNNNNN），都直接返回
            if re.match(r'^\d{4}\.\d{4,5}$', paper_id) or re.match(r'^[\w-]+/\d{7}$', paper_id):
                return ('arxiv', paper_id)

    return None

def extract_paper_ids(txt):
    """从输入文本中提取多个论文ID"""
    paper_ids = []

    # 首先按换行符分割
    for line in txt.strip().split('\n'):
        line = line.strip()
        if not line:  # 跳过空行
            continue

        # 对每一行再按空格分割
        for item in line.split():
            item = item.strip()
            if not item:  # 跳过空项
                continue
            paper_info = extract_paper_id(item)
            if paper_info:
                paper_ids.append(paper_info)

    # 去除重复项，保持顺序
    unique_paper_ids = []
    seen = set()
    for paper_info in paper_ids:
        if paper_info not in seen:
            seen.add(paper_info)
            unique_paper_ids.append(paper_info)

    return unique_paper_ids

def format_arxiv_id(paper_id):
    """格式化arXiv ID，处理新旧两种格式"""
    # 如果是旧格式 (e.g. astro-ph/0404140)，需要去掉arxiv:前缀
    if '/' in paper_id:
        return paper_id.replace('arxiv:', '')  # 确保移除可能存在的arxiv:前缀
    return paper_id

def get_arxiv_paper(paper_id):
    """获取arXiv论文，处理新旧两种格式"""
    import arxiv

    # 尝试不同的查询方式
    query_formats = [
        paper_id,                    # 原始ID
        paper_id.replace('/', ''),   # 移除斜杠
        f"id:{paper_id}",           # 添加id:前缀
    ]

    for query in query_formats:
        try:
            # 使用Search查询
            search = arxiv.Search(
                query=query,
                max_results=1
            )
            result = next(arxiv.Client().results(search))
            if result:
                return result
        except:
            continue

        try:
            # 使用id_list查询
            search = arxiv.Search(id_list=[query])
            result = next(arxiv.Client().results(search))
            if result:
                return result
        except:
            continue

    return None

def create_zip_archive(files, save_path):
    """将多个PDF文件打包成zip"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"papers_{timestamp}.zip"
    zip_path = str(save_path / zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            if os.path.exists(file):
                # 只添加文件名，不包含路径
                zipf.write(file, os.path.basename(file))

    return zip_path

@CatchException
def 论文下载(txt: str, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt: 用户输入，可以是DOI、arxiv ID或相关链接，支持多行输入进行批量下载
    """
    from crazy_functions.doc_fns.text_content_loader import TextContentLoader
    from crazy_functions.review_fns.data_sources.arxiv_source import ArxivSource
    from crazy_functions.review_fns.data_sources.scihub_source import SciHub
    # 解析输入
    paper_infos = extract_paper_ids(txt)
    if not paper_infos:
        chatbot.append(["输入解析", "未能识别任何论文ID或DOI，请检查输入格式。支持以下格式：\n- arXiv ID (例如：2103.14030)\n- arXiv链接\n- DOI (例如：10.1234/xxx)\n- DOI链接\n\n多个论文ID请用换行分隔。"])
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 创建保存目录 - 使用时间戳创建唯一文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_save_dir = get_log_folder(get_user(chatbot), plugin_name='paper_download')
    save_dir = os.path.join(base_save_dir, f"papers_{timestamp}")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = Path(save_dir)

    # 记录下载结果
    success_count = 0
    failed_papers = []
    downloaded_files = []  # 记录成功下载的文件路径

    chatbot.append([f"开始下载", f"支持多行输入下载多篇论文，共检测到 {len(paper_infos)} 篇论文，开始下载..."])
    yield from update_ui(chatbot=chatbot, history=history)

    for id_type, paper_id in paper_infos:
        try:
            if id_type == 'arxiv':
                chatbot.append([f"正在下载", f"从arXiv下载论文 {paper_id}..."])
                yield from update_ui(chatbot=chatbot, history=history)

                # 使用改进的arxiv查询方法
                formatted_id = format_arxiv_id(paper_id)
                paper_result = get_arxiv_paper(formatted_id)

                if not paper_result:
                    failed_papers.append((paper_id, "未找到论文"))
                    continue

                # 下载PDF
                try:
                    filename = f"arxiv_{paper_id.replace('/', '_')}.pdf"
                    pdf_path = str(save_path / filename)
                    paper_result.download_pdf(filename=pdf_path)
                    if os.path.exists(pdf_path):
                        downloaded_files.append(pdf_path)
                except Exception as e:
                    failed_papers.append((paper_id, f"PDF下载失败: {str(e)}"))
                    continue

            else:  # doi
                chatbot.append([f"正在下载", f"从Sci-Hub下载论文 {paper_id}..."])
                yield from update_ui(chatbot=chatbot, history=history)

                sci_hub = SciHub(
                    doi=paper_id,
                    path=save_path
                )
                pdf_path = sci_hub.fetch()
                if pdf_path and os.path.exists(pdf_path):
                    downloaded_files.append(pdf_path)

            # 检查下载结果
            if pdf_path and os.path.exists(pdf_path):
                promote_file_to_downloadzone(pdf_path, chatbot=chatbot)
                success_count += 1
            else:
                failed_papers.append((paper_id, "下载失败"))

        except Exception as e:
            failed_papers.append((paper_id, str(e)))

        yield from update_ui(chatbot=chatbot, history=history)

    # 创建ZIP压缩包
    if downloaded_files:
        try:
            zip_path = create_zip_archive(downloaded_files, Path(base_save_dir))
            promote_file_to_downloadzone(zip_path, chatbot=chatbot)
            chatbot.append([
                f"创建压缩包",
                f"已将所有下载的论文打包为: {os.path.basename(zip_path)}"
            ])
            yield from update_ui(chatbot=chatbot, history=history)
        except Exception as e:
            chatbot.append([
                f"创建压缩包失败",
                f"打包文件时出现错误: {str(e)}"
            ])
            yield from update_ui(chatbot=chatbot, history=history)

    # 生成最终报告
    summary = f"下载完成！成功下载 {success_count} 篇论文。\n"
    if failed_papers:
        summary += "\n以下论文下载失败：\n"
        for paper_id, reason in failed_papers:
            summary += f"- {paper_id}: {reason}\n"

    if downloaded_files:
        summary += f"\n所有论文已存放在文件夹 '{save_dir}' 中，并打包到压缩文件中。您可以在下载区找到单个PDF文件和压缩包。"

    chatbot.append([
        f"下载完成",
        summary
    ])
    yield from update_ui(chatbot=chatbot, history=history)

    # 如果下载成功且用户想要直接阅读内容
    if downloaded_files:
        chatbot.append([
            "提示",
            "正在读取论文内容进行分析，请稍候..."
        ])
        yield from update_ui(chatbot=chatbot, history=history)

        # 使用TextContentLoader加载整个文件夹的PDF文件内容
        loader = TextContentLoader(chatbot, history)

        # 删除提示信息
        chatbot.pop()

        # 加载PDF内容 - 传入文件夹路径而不是单个文件路径
        yield from loader.execute(save_dir)

        # 添加提示信息
        chatbot.append([
            "提示",
            "论文内容已加载完毕，您可以直接向AI提问有关该论文的问题。"
        ])
        yield from update_ui(chatbot=chatbot, history=history)

if __name__ == "__main__":
    # 测试代码
    import asyncio
    async def test():
        # 测试批量输入
        batch_inputs = [
            # 换行分隔的测试
            """https://arxiv.org/abs/2103.14030
            math/0211159
            10.1038/s41586-021-03819-2""",

            # 空格分隔的测试
            "https://arxiv.org/abs/2103.14030 math/0211159 10.1038/s41586-021-03819-2",

            # 混合分隔的测试
            """https://arxiv.org/abs/2103.14030 math/0211159
            10.1038/s41586-021-03819-2 https://doi.org/10.1038/s41586-021-03819-2
            2103.14030""",
        ]

        for i, test_input in enumerate(batch_inputs, 1):
            print(f"\n测试用例 {i}:")
            print(f"输入: {test_input}")
            results = extract_paper_ids(test_input)
            print(f"解析结果:")
            for result in results:
                print(f"  {result}")

    asyncio.run(test())
