import os.path

from toolbox import CatchException, update_ui
from crazy_functions.rag_fns.arxiv_fns.paper_processing import ArxivPaperProcessor


@CatchException
def Rag论文对话(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt: 用户输入，通常是arxiv论文链接
    功能：RAG论文总结和对话
    """
    if_project, if_arxiv = False, False
    if os.path.exists(txt):
        from crazy_functions.rag_fns.doc_fns.document_splitter import SmartDocumentSplitter
        splitter = SmartDocumentSplitter(
            char_range=(1000, 1200),
            max_workers=32  # 可选，默认会根据CPU核心数自动设置
        )
        if_project = True
    else:
        from crazy_functions.rag_fns.arxiv_fns.arxiv_splitter import SmartArxivSplitter
        splitter = SmartArxivSplitter(
            char_range=(1000, 1200),
            root_dir="gpt_log/arxiv_cache"
        )
        if_arxiv = True
    for fragment in splitter.process(txt):
        pass
        # 初始化处理器
    processor = ArxivPaperProcessor()
    rag_handler = RagHandler()

    # Step 1: 下载和提取论文
    download_result = processor.download_and_extract(txt, chatbot, history)
    project_folder, arxiv_id = None, None
    
    for result in download_result:
        if isinstance(result, tuple) and len(result) == 2:
            project_folder, arxiv_id = result
            break

    if not project_folder or not arxiv_id:
        return

    # Step 2: 合并TEX文件
    paper_content = processor.merge_tex_files(project_folder, chatbot, history)
    if not paper_content:
        return
        
    # Step 3: RAG处理
    chatbot.append(["正在构建知识图谱...", "处理中..."])
    yield from update_ui(chatbot=chatbot, history=history)
    
    # 处理论文内容
    rag_handler.process_paper_content(paper_content)
    
    # 生成初始摘要
    summary = rag_handler.query("请总结这篇论文的主要内容，包括研究目的、方法、结果和结论。")
    chatbot.append(["论文摘要", summary])
    yield from update_ui(chatbot=chatbot, history=history)
    
    # 交互式问答
