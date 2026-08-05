import re
import os
import asyncio
from typing import List, Dict, Tuple
from dataclasses import dataclass
from textwrap import dedent
from toolbox import CatchException, get_conf, update_ui, promote_file_to_downloadzone, get_log_folder, get_user
from toolbox import update_ui, CatchException, report_exception, write_history_to_file
from crazy_functions.review_fns.data_sources.semantic_source import SemanticScholarSource
from crazy_functions.review_fns.data_sources.arxiv_source import ArxivSource
from crazy_functions.review_fns.query_analyzer import QueryAnalyzer
from crazy_functions.review_fns.handlers.review_handler import 文献综述功能
from crazy_functions.review_fns.handlers.recommend_handler import 论文推荐功能
from crazy_functions.review_fns.handlers.qa_handler import 学术问答功能
from crazy_functions.review_fns.handlers.paper_handler import 单篇论文分析功能
from crazy_functions.Conversation_To_File import write_chat_to_file
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.review_fns.handlers.latest_handler import Arxiv最新论文推荐功能
from datetime import datetime

@CatchException
def 学术对话(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
           history: List, system_prompt: str, user_request: str):
    """主函数"""

    # 初始化数据源
    arxiv_source = ArxivSource()
    semantic_source = SemanticScholarSource(
        api_key=get_conf("SEMANTIC_SCHOLAR_KEY")
    )

    # 初始化处理器
    handlers = {
        "review": 文献综述功能(arxiv_source, semantic_source, llm_kwargs),
        "recommend": 论文推荐功能(arxiv_source, semantic_source, llm_kwargs),
        "qa": 学术问答功能(arxiv_source, semantic_source, llm_kwargs),
        "paper": 单篇论文分析功能(arxiv_source, semantic_source, llm_kwargs),
        "latest": Arxiv最新论文推荐功能(arxiv_source, semantic_source, llm_kwargs),
    }

    # 分析查询意图
    chatbot.append([None, "正在分析研究主题和查询要求..."])
    yield from update_ui(chatbot=chatbot, history=history)

    query_analyzer = QueryAnalyzer()
    search_criteria = yield from query_analyzer.analyze_query(txt, chatbot, llm_kwargs)
    handler = handlers.get(search_criteria.query_type)
    if not handler:
        handler = handlers["qa"]  # 默认使用QA处理器

    # 处理查询
    chatbot.append([None, f"使用{handler.__class__.__name__}处理...，可能需要您耐心等待3～5分钟..."])
    yield from update_ui(chatbot=chatbot, history=history)

    final_prompt = asyncio.run(handler.handle(
        criteria=search_criteria,
        chatbot=chatbot,
        history=history,
        system_prompt=system_prompt,
        llm_kwargs=llm_kwargs,
        plugin_kwargs=plugin_kwargs
    ))

    if final_prompt:
        # 检查是否是道歉提示
        if "很抱歉，我们未能找到" in final_prompt:
            chatbot.append([txt, final_prompt])
            yield from update_ui(chatbot=chatbot, history=history)
            return
        # 在 final_prompt 末尾添加用户原始查询要求
        final_prompt += dedent(f"""
        Original user query: "{txt}"

        IMPORTANT NOTE :
        - Your response must directly address the user's original user query above
        - While following the previous guidelines, prioritize answering what the user specifically asked
        - Make sure your response format and content align with the user's expectations
        - Do not translate paper titles, keep them in their original language
        - Do not generate a reference list in your response - references will be handled separately
        """)

        # 使用最终的prompt生成回答
        response = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=final_prompt,
            inputs_show_user=txt,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history=[],
            sys_prompt=f"You are a helpful academic assistant. Response in Chinese by default unless specified language is required in the user's query."
        )

        # 1. 获取文献列表
        papers_list = handler.ranked_papers  # 直接使用原始论文数据

        # 在新的对话中添加格式化的参考文献列表
        if papers_list:
            references = ""
            for idx, paper in enumerate(papers_list, 1):
                # 构建作者列表
                authors = paper.authors[:3]
                if len(paper.authors) > 3:
                    authors.append("et al.")
                authors_str = ", ".join(authors)

                # 构建期刊指标信息
                metrics = []
                if hasattr(paper, 'if_factor') and paper.if_factor:
                    metrics.append(f"IF: {paper.if_factor}")
                if hasattr(paper, 'jcr_division') and paper.jcr_division:
                    metrics.append(f"JCR: {paper.jcr_division}")
                if hasattr(paper, 'cas_division') and paper.cas_division:
                    metrics.append(f"中科院分区: {paper.cas_division}")
                metrics_str = f" [{', '.join(metrics)}]" if metrics else ""

                # 构建DOI链接
                doi_link = ""
                if paper.doi:
                    if "arxiv.org" in str(paper.doi):
                        doi_url = paper.doi
                    else:
                        doi_url = f"https://doi.org/{paper.doi}"
                    doi_link = f" <a href='{doi_url}' target='_blank'>DOI: {paper.doi}</a>"

                # 构建完整的引用
                reference = f"[{idx}] {authors_str}. *{paper.title}*"
                if paper.venue_name:
                    reference += f". {paper.venue_name}"
                if paper.year:
                    reference += f", {paper.year}"
                reference += metrics_str
                if doi_link:
                    reference += f".{doi_link}"
                reference += "  \n"

                references += reference

            # 添加新的对话显示参考文献
            chatbot.append(["参考文献如下：", references])
            yield from update_ui(chatbot=chatbot, history=history)


        # 2. 保存为不同格式
        from .review_fns.conversation_doc.word_doc import WordFormatter
        from .review_fns.conversation_doc.word2pdf import WordToPdfConverter
        from .review_fns.conversation_doc.markdown_doc import MarkdownFormatter
        from .review_fns.conversation_doc.html_doc import HtmlFormatter

        # 创建保存目录
        save_dir =  get_log_folder(get_user(chatbot),  plugin_name='chatscholar')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 生成文件名
        def get_safe_filename(txt, max_length=10):
            # 获取文本前max_length个字符作为文件名
            filename = txt[:max_length].strip()
            # 移除不安全的文件名字符
            filename = re.sub(r'[\\/:*?"<>|]', '', filename)
            # 如果文件名为空，使用时间戳
            if not filename:
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            return filename

        base_filename = get_safe_filename(txt)

        result_files = []  # 收集所有生成的文件
        pdf_path = None  # 用于跟踪PDF是否成功生成

        # 保存为Markdown
        try:
            md_formatter = MarkdownFormatter()
            md_content = md_formatter.create_document(txt, response, papers_list)
            result_file_md = write_history_to_file(
                history=[md_content],
                file_basename=f"markdown_{base_filename}.md"
            )
            result_files.append(result_file_md)
        except Exception as e:
            print(f"Markdown保存失败: {str(e)}")

        # 保存为HTML
        try:
            html_formatter = HtmlFormatter()
            html_content = html_formatter.create_document(txt, response, papers_list)
            result_file_html = write_history_to_file(
                history=[html_content],
                file_basename=f"html_{base_filename}.html"
            )
            result_files.append(result_file_html)
        except Exception as e:
            print(f"HTML保存失败: {str(e)}")

        # 保存为Word
        try:
            word_formatter = WordFormatter()
            try:
                doc = word_formatter.create_document(txt, response, papers_list)
            except Exception as e:
                print(f"Word文档内容生成失败: {str(e)}")
                raise e

            try:
                result_file_docx = os.path.join(
                    os.path.dirname(result_file_md) if result_file_md else save_dir,
                    f"docx_{base_filename}.docx"
                )
                doc.save(result_file_docx)
                result_files.append(result_file_docx)
                print(f"Word文档已保存到: {result_file_docx}")

                # 转换为PDF
                try:
                    pdf_path = WordToPdfConverter.convert_to_pdf(result_file_docx)
                    if pdf_path:
                        result_files.append(pdf_path)
                        print(f"PDF文档已生成: {pdf_path}")
                except Exception as e:
                    print(f"PDF转换失败: {str(e)}")

            except Exception as e:
                print(f"Word文档保存失败: {str(e)}")
                raise e

        except Exception as e:
            print(f"Word格式化失败: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")

        # 保存为BibTeX格式
        try:
            from .review_fns.conversation_doc.reference_formatter import ReferenceFormatter
            ref_formatter = ReferenceFormatter()
            bibtex_content = ref_formatter.create_document(papers_list)

            # 在与其他文件相同目录下创建BibTeX文件
            result_file_bib = os.path.join(
                os.path.dirname(result_file_md) if result_file_md else save_dir,
                f"references_{base_filename}.bib"
            )

            # 直接写入文件
            with open(result_file_bib, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)

            result_files.append(result_file_bib)
            print(f"BibTeX文件已保存到: {result_file_bib}")
        except Exception as e:
            print(f"BibTeX格式保存失败: {str(e)}")

        # 保存为EndNote格式
        try:
            from .review_fns.conversation_doc.endnote_doc import EndNoteFormatter
            endnote_formatter = EndNoteFormatter()
            endnote_content = endnote_formatter.create_document(papers_list)

            # 在与其他文件相同目录下创建EndNote文件
            result_file_enw = os.path.join(
                os.path.dirname(result_file_md) if result_file_md else save_dir,
                f"references_{base_filename}.enw"
            )

            # 直接写入文件
            with open(result_file_enw, 'w', encoding='utf-8') as f:
                f.write(endnote_content)

            result_files.append(result_file_enw)
            print(f"EndNote文件已保存到: {result_file_enw}")
        except Exception as e:
            print(f"EndNote格式保存失败: {str(e)}")

        # 添加所有文件到下载区
        success_files = []
        for file in result_files:
            try:
                promote_file_to_downloadzone(file, chatbot=chatbot)
                success_files.append(os.path.basename(file))
            except Exception as e:
                print(f"文件添加到下载区失败: {str(e)}")

        # 更新成功提示消息
        if success_files:
            chatbot.append(["保存对话记录成功，bib和enw文件支持导入到EndNote、Zotero、JabRef、Mendeley等文献管理软件，HTML文件支持在浏览器中打开，里面包含详细论文源信息", "对话已保存并添加到下载区，可以在下载区找到相关文件"])
        else:
            chatbot.append(["保存对话记录", "所有格式的保存都失败了，请检查错误日志。"])

        yield from update_ui(chatbot=chatbot, history=history)
    else:
        report_exception(chatbot, history, a=f"处理失败", b=f"请尝试其他查询")
        yield from update_ui(chatbot=chatbot, history=history)
