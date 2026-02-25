import os
import time
import glob
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Generator, Tuple
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from toolbox import update_ui, promote_file_to_downloadzone, write_history_to_file, CatchException, report_exception
from shared_utils.fastapi_server import validate_path_safety
from crazy_functions.paper_fns.paper_download import extract_paper_id, extract_paper_ids, get_arxiv_paper, format_arxiv_id



@dataclass
class PaperQuestion:
    """论文分析问题类"""
    id: str  # 问题ID
    question: str  # 问题内容
    importance: int  # 重要性 (1-5，5最高)
    description: str  # 问题描述


class PaperAnalyzer:
    """论文快速分析器"""

    def __init__(self, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List, history: List, system_prompt: str):
        """初始化分析器"""
        self.llm_kwargs = llm_kwargs
        self.plugin_kwargs = plugin_kwargs
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.paper_content = ""
        self.results = {}

        # 定义论文分析问题库（已合并为4个核心问题）
        self.questions = [
            PaperQuestion(
                id="research_and_methods",
                question="这篇论文的主要研究问题、目标和方法是什么？请分析：1)论文的核心研究问题和研究动机；2)论文提出的关键方法、模型或理论框架；3)这些方法如何解决研究问题。",
                importance=5,
                description="研究问题与方法"
            ),
            PaperQuestion(
                id="findings_and_innovation",
                question="论文的主要发现、结论及创新点是什么？请分析：1)论文的核心结果与主要发现；2)作者得出的关键结论；3)研究的创新点与对领域的贡献；4)与已有工作的区别。",
                importance=4,
                description="研究发现与创新"
            ),
            PaperQuestion(
                id="methodology_and_data",
                question="论文使用了什么研究方法和数据？请详细分析：1)研究设计与实验设置；2)数据收集方法与数据集特点；3)分析技术与评估方法；4)方法学上的合理性。",
                importance=3,
                description="研究方法与数据"
            ),
            PaperQuestion(
                id="limitations_and_impact",
                question="论文的局限性、未来方向及潜在影响是什么？请分析：1)研究的不足与限制因素；2)作者提出的未来研究方向；3)该研究对学术界和行业可能产生的影响；4)研究结果的适用范围与推广价值。",
                importance=2,
                description="局限性与影响"
            ),
        ]

        # 按重要性排序
        self.questions.sort(key=lambda q: q.importance, reverse=True)

    def _load_paper(self, paper_path: str) -> Generator:
        from crazy_functions.doc_fns.text_content_loader import TextContentLoader
        """加载论文内容"""
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 使用TextContentLoader读取文件
        loader = TextContentLoader(self.chatbot, self.history)

        yield from loader.execute_single_file(paper_path)

        # 获取加载的内容
        if len(self.history) >= 2 and self.history[-2]:
            self.paper_content = self.history[-2]
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return True
        else:
            self.chatbot.append(["错误", "无法读取论文内容，请检查文件是否有效"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return False

    def _analyze_question(self, question: PaperQuestion) -> Generator:
        """分析单个问题 - 直接显示问题和答案"""
        try:
            # 创建分析提示
            prompt = f"请基于以下论文内容回答问题：\n\n{self.paper_content}\n\n问题：{question.question}"

            # 使用单线程版本的请求函数
            response = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=prompt,
                inputs_show_user=question.question,  # 显示问题本身
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history=[],  # 空历史，确保每个问题独立分析
                sys_prompt="你是一个专业的科研论文分析助手，需要仔细阅读论文内容并回答问题。请保持客观、准确，并基于论文内容提供深入分析。"
            )

            if response:
                self.results[question.id] = response
                return True
            return False

        except Exception as e:
            self.chatbot.append(["错误", f"分析问题时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return False

    def _generate_summary(self) -> Generator:
        """生成最终总结报告"""
        self.chatbot.append(["生成报告", "正在整合分析结果，生成最终报告..."])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        summary_prompt = "请基于以下对论文的各个方面的分析，生成一份全面的论文解读报告。报告应该简明扼要地呈现论文的关键内容，并保持逻辑连贯性。"

        for q in self.questions:
            if q.id in self.results:
                summary_prompt += f"\n\n关于{q.description}的分析:\n{self.results[q.id]}"

        try:
            # 使用单线程版本的请求函数，可以在前端实时显示生成结果
            response = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=summary_prompt,
                inputs_show_user="生成论文解读报告",
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history=[],
                sys_prompt="你是一个科研论文解读专家，请将多个方面的分析整合为一份完整、连贯、有条理的报告。报告应当重点突出，层次分明，并且保持学术性和客观性。"
            )

            if response:
                return response
            return "报告生成失败"

        except Exception as e:
            self.chatbot.append(["错误", f"生成报告时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return "报告生成失败: " + str(e)

    def save_report(self, report: str) -> Generator:
        """保存分析报告"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 保存为Markdown文件
        try:
            md_content = f"# 论文快速解读报告\n\n{report}"
            for q in self.questions:
                if q.id in self.results:
                    md_content += f"\n\n## {q.description}\n\n{self.results[q.id]}"

            result_file = write_history_to_file(
                history=[md_content],
                file_basename=f"论文解读_{timestamp}.md"
            )

            if result_file and os.path.exists(result_file):
                promote_file_to_downloadzone(result_file, chatbot=self.chatbot)
                self.chatbot.append(["保存成功", f"解读报告已保存至: {os.path.basename(result_file)}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
            else:
                self.chatbot.append(["警告", "保存报告成功但找不到文件"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
        except Exception as e:
            self.chatbot.append(["警告", f"保存报告失败: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

    def analyze_paper(self, paper_path: str) -> Generator:
        """分析论文主流程"""
        # 加载论文
        success = yield from self._load_paper(paper_path)
        if not success:
            return

        # 分析关键问题 - 直接询问每个问题，不显示进度信息
        for question in self.questions:
            yield from self._analyze_question(question)

        # 生成总结报告
        final_report = yield from self._generate_summary()

        # 显示最终报告
        # self.chatbot.append(["论文解读报告", final_report])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 保存报告
        yield from self.save_report(final_report)


def _find_paper_file(path: str) -> str:
    """查找路径中的论文文件（简化版）"""
    if os.path.isfile(path):
        return path

    # 支持的文件扩展名（按优先级排序）
    extensions = ["pdf", "docx", "doc", "txt", "md", "tex"]

    # 简单地遍历目录
    if os.path.isdir(path):
        try:
            for ext in extensions:
                # 手动检查每个可能的文件，而不使用glob
                potential_file = os.path.join(path, f"paper.{ext}")
                if os.path.exists(potential_file) and os.path.isfile(potential_file):
                    return potential_file

            # 如果没找到特定命名的文件，检查目录中的所有文件
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    file_ext = file.split('.')[-1].lower() if '.' in file else ""
                    if file_ext in extensions:
                        return file_path
        except Exception:
            pass  # 忽略任何错误

    return None


def download_paper_by_id(paper_info, chatbot, history) -> str:
    """下载论文并返回保存路径

    Args:
        paper_info: 元组，包含论文ID类型（arxiv或doi）和ID值
        chatbot: 聊天机器人对象
        history: 历史记录

    Returns:
        str: 下载的论文路径或None
    """
    from crazy_functions.review_fns.data_sources.scihub_source import SciHub
    id_type, paper_id = paper_info

    # 创建保存目录 - 使用时间戳创建唯一文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_name = chatbot.get_user() if hasattr(chatbot, 'get_user') else "default"
    from toolbox import get_log_folder, get_user
    base_save_dir = get_log_folder(get_user(chatbot), plugin_name='paper_download')
    save_dir = os.path.join(base_save_dir, f"papers_{timestamp}")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = Path(save_dir)

    chatbot.append([f"下载论文", f"正在下载{'arXiv' if id_type == 'arxiv' else 'DOI'} {paper_id} 的论文..."])
    update_ui(chatbot=chatbot, history=history)

    pdf_path = None

    try:
        if id_type == 'arxiv':
            # 使用改进的arxiv查询方法
            formatted_id = format_arxiv_id(paper_id)
            paper_result = get_arxiv_paper(formatted_id)

            if not paper_result:
                chatbot.append([f"下载失败", f"未找到arXiv论文: {paper_id}"])
                update_ui(chatbot=chatbot, history=history)
                return None

            # 下载PDF
            filename = f"arxiv_{paper_id.replace('/', '_')}.pdf"
            pdf_path = str(save_path / filename)
            paper_result.download_pdf(filename=pdf_path)

        else:  # doi
            # 下载DOI
            sci_hub = SciHub(
                doi=paper_id,
                path=save_path
            )
            pdf_path = sci_hub.fetch()

        # 检查下载结果
        if pdf_path and os.path.exists(pdf_path):
            promote_file_to_downloadzone(pdf_path, chatbot=chatbot)
            chatbot.append([f"下载成功", f"已成功下载论文: {os.path.basename(pdf_path)}"])
            update_ui(chatbot=chatbot, history=history)
            return pdf_path
        else:
            chatbot.append([f"下载失败", f"论文下载失败: {paper_id}"])
            update_ui(chatbot=chatbot, history=history)
            return None

    except Exception as e:
        chatbot.append([f"下载错误", f"下载论文时出错: {str(e)}"])
        update_ui(chatbot=chatbot, history=history)
        return None


@CatchException
def 快速论文解读(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
             history: List, system_prompt: str, user_request: str):
    """主函数 - 论文快速解读"""
    # 初始化分析器
    chatbot.append(["函数插件功能及使用方式", "论文快速解读：通过分析论文的关键要素，帮助您迅速理解论文内容，适用于各学科领域的科研论文。 <br><br>📋 使用方式：<br>1、直接上传PDF文件或者输入DOI号（仅针对SCI hub存在的论文）或arXiv ID（如2501.03916）<br>2、点击插件开始分析"])
    yield from update_ui(chatbot=chatbot, history=history)

    paper_file = None

    # 检查输入是否为论文ID（arxiv或DOI）
    paper_info = extract_paper_id(txt)

    if paper_info:
        # 如果是论文ID，下载论文
        chatbot.append(["检测到论文ID", f"检测到{'arXiv' if paper_info[0] == 'arxiv' else 'DOI'} ID: {paper_info[1]}，准备下载论文..."])
        yield from update_ui(chatbot=chatbot, history=history)

        # 下载论文 - 完全重新实现
        paper_file = download_paper_by_id(paper_info, chatbot, history)

        if not paper_file:
            report_exception(chatbot, history, a=f"下载论文失败", b=f"无法下载{'arXiv' if paper_info[0] == 'arxiv' else 'DOI'}论文: {paper_info[1]}")
            yield from update_ui(chatbot=chatbot, history=history)
            return
    else:
        # 检查输入路径
        if not os.path.exists(txt):
            report_exception(chatbot, history, a=f"解析论文: {txt}", b=f"找不到文件或无权访问: {txt}")
            yield from update_ui(chatbot=chatbot, history=history)
            return

        # 验证路径安全性
        user_name = chatbot.get_user()
        validate_path_safety(txt, user_name)

        # 查找论文文件
        paper_file = _find_paper_file(txt)

        if not paper_file:
            report_exception(chatbot, history, a=f"解析论文", b=f"在路径 {txt} 中未找到支持的论文文件")
            yield from update_ui(chatbot=chatbot, history=history)
            return

    yield from update_ui(chatbot=chatbot, history=history)

    # 增加调试信息，检查paper_file的类型和值
    chatbot.append(["文件类型检查", f"paper_file类型: {type(paper_file)}, 值: {paper_file}"])
    yield from update_ui(chatbot=chatbot, history=history)
    chatbot.pop()  # 移除调试信息

    # 确保paper_file是字符串
    if paper_file is not None and not isinstance(paper_file, str):
        # 尝试转换为字符串
        try:
            paper_file = str(paper_file)
        except Exception:
            report_exception(chatbot, history, a=f"类型错误", b=f"论文路径不是有效的字符串: {type(paper_file)}")
            yield from update_ui(chatbot=chatbot, history=history)
            return

    # 分析论文
    chatbot.append(["开始分析", f"正在分析论文: {os.path.basename(paper_file)}"])
    yield from update_ui(chatbot=chatbot, history=history)

    analyzer = PaperAnalyzer(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
    yield from analyzer.analyze_paper(paper_file)
