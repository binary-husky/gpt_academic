from toolbox import CatchException, update_ui
from crazy_functions.rag_essay_fns.paper_processing import ArxivPaperProcessor
from crazy_functions.rag_essay_fns.rag_handler import RagHandler
import asyncio

@CatchException
def Rag论文对话(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt: 用户输入，通常是arxiv论文链接
    功能：RAG论文总结和对话
    """
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
    chatbot.append(["知识图谱构建完成", "您可以开始提问了。支持以下类型的问题：\n1. 论文的具体内容\n2. 研究方法的细节\n3. 实验结果分析\n4. 与其他工作的比较"])
    yield from update_ui(chatbot=chatbot, history=history)
    
    # 等待用户提问并回答
    while True:
        question = yield from wait_user_input()
        if not question:
            break
            
        # 根据问题类型选择不同的查询模式
        if "比较" in question or "关系" in question:
            mode = "global"  # 使用全局模式处理比较类问题
        elif "具体" in question or "细节" in question:
            mode = "local"   # 使用局部模式处理细节问题
        else:
            mode = "hybrid"  # 默认使用混合模式
            
        response = rag_handler.query(question, mode=mode)
        chatbot.append([question, response])
        yield from update_ui(chatbot=chatbot, history=history)