import os
import time
import glob
from typing import Dict, List, Generator, Tuple
from dataclasses import dataclass

from crazy_functions.pdf_fns.text_content_loader import TextContentLoader
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from toolbox import update_ui, promote_file_to_downloadzone, write_history_to_file, CatchException, report_exception
from shared_utils.fastapi_server import validate_path_safety
# 导入论文下载相关函数
from crazy_functions.论文下载 import extract_paper_id, extract_paper_ids, get_arxiv_paper, format_arxiv_id, SciHub
from pathlib import Path
from datetime import datetime, timedelta
import calendar


@dataclass
class RecommendationQuestion:
    """期刊会议推荐分析问题类"""
    id: str  # 问题ID
    question: str  # 问题内容
    importance: int  # 重要性 (1-5，5最高)
    description: str  # 问题描述


class JournalConferenceRecommender:
    """论文期刊会议推荐器"""

    def __init__(self, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List, history: List, system_prompt: str):
        """初始化推荐器"""
        self.llm_kwargs = llm_kwargs
        self.plugin_kwargs = plugin_kwargs
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.paper_content = ""
        self.analysis_results = {}

        # 定义论文分析问题库（针对期刊会议推荐）
        self.questions = [
            RecommendationQuestion(
                id="research_field_and_topic",
                question="请分析这篇论文的研究领域、主题和关键词。具体包括：1)论文属于哪个主要学科领域（如自然科学、工程技术、医学、社会科学、人文学科等）；2)具体的研究子领域或方向；3)论文的核心主题和关键概念；4)重要的学术关键词和专业术语；5)研究的跨学科特征（如果有）；6)研究的地域性特征（国际性研究还是特定地区研究）。",
                importance=5,
                description="研究领域与主题分析"
            ),
            RecommendationQuestion(
                id="methodology_and_approach",
                question="请分析论文的研究方法和技术路线。包括：1)采用的主要研究方法（定量研究、定性研究、理论分析、实验研究、田野调查、文献综述、案例研究等）；2)使用的技术手段、工具或分析方法；3)研究设计的严谨性和创新性；4)数据收集和分析方法的适当性；5)研究方法在该学科中的先进性或传统性；6)方法学上的贡献或局限性。",
                importance=4,
                description="研究方法与技术路线"
            ),
            RecommendationQuestion(
                id="novelty_and_contribution",
                question="请评估论文的创新性和学术贡献。包括：1)研究的新颖性程度（理论创新、方法创新、应用创新等）；2)对现有知识体系的贡献或突破；3)解决问题的重要性和学术价值；4)研究成果的理论意义和实践价值；5)在该学科领域的地位和影响潜力；6)与国际前沿研究的关系；7)对后续研究的启发意义。",
                importance=4,
                description="创新性与学术贡献"
            ),
            RecommendationQuestion(
                id="target_audience_and_scope",
                question="请分析论文的目标受众和应用范围。包括：1)主要面向的学术群体（研究者、从业者、政策制定者等）；2)研究成果的潜在应用领域和受益群体；3)对学术界和实践界的价值；4)研究的国际化程度和跨文化适用性；5)是否适合国际期刊还是区域性期刊；6)语言发表偏好（英文、中文或其他语言）；7)开放获取的必要性和可行性。",
                importance=3,
                description="目标受众与应用范围"
            ),
        ]

        # 按重要性排序
        self.questions.sort(key=lambda q: q.importance, reverse=True)

    def _load_paper(self, paper_path: str) -> Generator:
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

    def _analyze_question(self, question: RecommendationQuestion) -> Generator:
        """分析单个问题"""
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
                sys_prompt="你是一个专业的学术期刊会议推荐专家，需要仔细分析论文内容并提供准确的分析。请保持客观、专业，并基于论文内容提供深入分析。"
            )

            if response:
                self.analysis_results[question.id] = response
                return True
            return False

        except Exception as e:
            self.chatbot.append(["错误", f"分析问题时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return False

    def _generate_journal_recommendations(self) -> Generator:
        """生成期刊推荐"""
        self.chatbot.append(["生成期刊推荐", "正在基于论文分析结果生成期刊推荐..."])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 构建期刊推荐提示
        journal_prompt = """请基于以下论文分析结果，为这篇论文推荐合适的学术期刊。

推荐要求：
1. 根据论文的创新性和工作质量，分别推荐不同级别的期刊：
   - 顶级期刊（影响因子>8或该领域顶级期刊）：2-3个
   - 高质量期刊（影响因子4-8或该领域知名期刊）：3-4个
   - 中等期刊（影响因子1.5-4或该领域认可期刊）：3-4个
   - 入门期刊（影响因子<1.5但声誉良好的期刊）：2-3个

注意：不同学科的影响因子标准差异很大，请根据论文所属学科的实际情况调整标准。
特别是医学领域，需要考虑：
- 临床医学期刊通常影响因子较高（顶级期刊IF>20，高质量期刊IF>10）
- 基础医学期刊影响因子相对较低但学术价值很高
- 专科医学期刊在各自领域内具有权威性
- 医学期刊的临床实用性和循证医学价值

2. 对每个期刊提供详细信息：
   - 期刊全名和缩写
   - 最新影响因子（如果知道）
   - 期刊级别分类（Q1/Q2/Q3/Q4或该学科的分类标准）
   - 主要研究领域和范围
   - 与论文内容的匹配度评分（1-10分）
   - 发表难度评估（容易/中等/困难/极难）
   - 平均审稿周期
   - 开放获取政策
   - 期刊的学科分类（如SCI、SSCI、A&HCI等）
   - 医学期刊特殊信息（如适用）：
     * PubMed收录情况
     * 是否为核心临床期刊
     * 专科领域权威性
     * 循证医学等级要求
     * 临床试验注册要求
     * 伦理委员会批准要求

3. 按推荐优先级排序，并说明推荐理由
4. 提供针对性的投稿建议，考虑该学科的特点

论文分析结果："""

        for q in self.questions:
            if q.id in self.analysis_results:
                journal_prompt += f"\n\n{q.description}:\n{self.analysis_results[q.id]}"

        journal_prompt += "\n\n请提供详细的期刊推荐报告，重点关注期刊的层次性和适配性。请根据论文的具体学科领域，采用该领域通用的期刊评价标准和分类体系。"

        try:
            response = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=journal_prompt,
                inputs_show_user="生成期刊推荐报告",
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history=[],
                sys_prompt="你是一个资深的跨学科学术期刊推荐专家，熟悉各个学科领域不同层次的期刊。请根据论文的具体学科和创新性，推荐从顶级到入门级的各层次期刊。不同学科有不同的期刊评价标准：理工科重视影响因子和SCI收录，社会科学重视SSCI和学科声誉，人文学科重视A&HCI和同行评议，医学领域重视PubMed收录、临床实用性、循证医学价值和伦理规范。请根据论文所属学科采用相应的评价标准。"
            )

            if response:
                return response
            return "期刊推荐生成失败"

        except Exception as e:
            self.chatbot.append(["错误", f"生成期刊推荐时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return "期刊推荐生成失败: " + str(e)

    def _generate_conference_recommendations(self) -> Generator:
        """生成会议推荐"""
        self.chatbot.append(["生成会议推荐", "正在基于论文分析结果生成会议推荐..."])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 获取当前时间信息
        current_time = datetime.now()
        current_date_str = current_time.strftime("%Y年%m月%d日")
        current_year = current_time.year
        current_month = current_time.month

        # 构建会议推荐提示
        conference_prompt = f"""请基于以下论文分析结果，为这篇论文推荐合适的学术会议。

**重要提示：当前时间是{current_date_str}（{current_year}年{current_month}月），请基于这个时间点推断会议的举办时间和投稿截止时间。**

推荐要求：
1. 根据论文的创新性和工作质量，分别推荐不同级别的会议：
   - 顶级会议（该领域最权威的国际会议）：2-3个
   - 高质量会议（该领域知名的国际或区域会议）：3-4个
   - 中等会议（该领域认可的专业会议）：3-4个
   - 专业会议（该领域细分方向的专门会议）：2-3个

注意：不同学科的会议评价标准不同：
- 计算机科学：可参考CCF分类（A/B/C类）
- 工程学：可参考EI收录和影响力
- 医学：可参考会议的临床影响和同行认可度
- 社会科学：可参考会议的学术声誉和参与度
- 人文学科：可参考会议的历史和学术传统
- 自然科学：可参考会议的国际影响力和发表质量

特别是医学会议，需要考虑：
- 临床医学会议重视实用性和临床指导价值
- 基础医学会议重视科学创新和机制研究
- 专科医学会议在各自领域内具有权威性
- 国际医学会议的CME学分认证情况

2. 对每个会议提供详细信息：
   - 会议全名和缩写
   - 会议级别分类（根据该学科的评价标准）
   - 主要研究领域和主题
   - 与论文内容的匹配度评分（1-10分）
   - 录用难度评估（容易/中等/困难/极难）
   - 会议举办周期（年会/双年会/不定期等）
   - **基于当前时间{current_date_str}，推断{current_year}年和{current_year+1}年的举办时间和地点**（请根据往年的举办时间规律进行推断）
   - **基于推断的会议时间，估算论文提交截止时间**（通常在会议前3-6个月）
   - 会议的国际化程度和影响范围
   - 医学会议特殊信息（如适用）：
     * 是否提供CME学分
     * 临床实践指导价值
     * 专科认证机构认可情况
     * 会议论文集的PubMed收录情况
     * 伦理和临床试验相关要求

3. 按推荐优先级排序，并说明推荐理由
4. **基于当前时间{current_date_str}，提供会议投稿的时间规划建议**
   - 哪些会议可以赶上{current_year}年的投稿截止时间
   - 哪些会议需要准备{current_year+1}年的投稿
   - 具体的时间安排建议

论文分析结果："""

        for q in self.questions:
            if q.id in self.analysis_results:
                conference_prompt += f"\n\n{q.description}:\n{self.analysis_results[q.id]}"

        conference_prompt += f"\n\n请提供详细的会议推荐报告，重点关注会议的层次性和时效性。请根据论文的具体学科领域，采用该领域通用的会议评价标准。\n\n**特别注意：请根据当前时间{current_date_str}和各会议的历史举办时间规律，准确推断{current_year}年和{current_year+1}年的会议时间安排，不要使用虚构的时间。**"

        try:
            response = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=conference_prompt,
                inputs_show_user="生成会议推荐报告",
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history=[],
                sys_prompt="你是一个资深的跨学科学术会议推荐专家，熟悉各个学科领域不同层次的学术会议。请根据论文的具体学科和创新性，推荐从顶级到专业级的各层次会议。不同学科有不同的会议评价标准和文化：理工科重视技术创新和国际影响力，社会科学重视理论贡献和社会意义，人文学科重视学术深度和文化价值，医学领域重视临床实用性、CME学分认证、专科权威性和伦理规范。请根据论文所属学科采用相应的评价标准和推荐策略。"
            )

            if response:
                return response
            return "会议推荐生成失败"

        except Exception as e:
            self.chatbot.append(["错误", f"生成会议推荐时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return "会议推荐生成失败: " + str(e)

    def _generate_priority_summary(self, journal_recommendations: str, conference_recommendations: str) -> Generator:
        """生成优先级总结"""
        self.chatbot.append(["生成优先级总结", "正在生成投稿优先级总结..."])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 获取当前时间信息
        current_time = datetime.now()
        current_date_str = current_time.strftime("%Y年%m月%d日")
        current_month = current_time.strftime("%Y年%m月")

        # 计算未来时间点
        def add_months(date, months):
            """安全地添加月份"""
            month = date.month - 1 + months
            year = date.year + month // 12
            month = month % 12 + 1
            day = min(date.day, calendar.monthrange(year, month)[1])
            return date.replace(year=year, month=month, day=day)

        future_6_months = add_months(current_time, 6).strftime('%Y年%m月')
        future_12_months = add_months(current_time, 12).strftime('%Y年%m月')
        future_year = (current_time.year + 1)

        priority_prompt = f"""请基于以下期刊和会议推荐结果，生成一个综合的投稿优先级总结。

**重要提示：当前时间是{current_date_str}（{current_month}），请基于这个时间点制定投稿计划。**

期刊推荐结果：
{journal_recommendations}

会议推荐结果：
{conference_recommendations}

请提供：
1. 综合投稿策略建议（考虑该学科的发表文化和惯例）
   - 期刊优先还是会议优先（不同学科有不同偏好）
   - 国际期刊/会议 vs 国内期刊/会议的选择策略
   - 英文发表 vs 中文发表的考虑

2. 按时间线排列的投稿计划（**基于当前时间{current_date_str}，考虑截止时间和审稿周期**）
   - 短期目标（{current_month}起3-6个月内，即到{future_6_months}）
   - 中期目标（6-12个月内，即到{future_12_months}）
   - 长期目标（1年以上，即{future_year}年以后）

3. 风险分散策略
   - 同时投稿多个不同级别的目标
   - 考虑该学科的一稿多投政策
   - 备选方案和应急策略

4. 针对论文可能需要的改进建议
   - 根据目标期刊/会议的要求调整内容
   - 语言和格式的优化建议
   - 补充实验或分析的建议

5. 预期的发表时间线和成功概率评估（基于当前时间{current_date_str}）

6. 该学科特有的发表注意事项
   - 伦理审查要求（如医学、心理学等）
   - 数据开放要求（如某些自然科学领域）
   - 利益冲突声明（如医学、工程等）
   - 医学领域特殊要求：
     * 临床试验注册要求（ClinicalTrials.gov、中国临床试验注册中心等）
     * 患者知情同意和隐私保护
     * 医学伦理委员会批准证明
     * CONSORT、STROBE、PRISMA等报告规范遵循
     * 药物/器械安全性数据要求
     * CME学分认证相关要求
     * 临床指南和循证医学等级要求
   - 其他学科特殊要求

请以表格形式总结前10个最推荐的投稿目标（期刊+会议），包括优先级排序、预期时间线和成功概率。

**注意：所有时间规划都应基于当前时间{current_date_str}进行计算，不要使用虚构的时间。**"""

        try:
            response = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=priority_prompt,
                inputs_show_user="生成投稿优先级总结",
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history=[],
                sys_prompt="你是一个资深的跨学科学术发表策略专家，熟悉各个学科的发表文化、惯例和要求。请综合考虑不同学科的特点：理工科通常重视期刊发表和影响因子，社会科学平衡期刊和专著，人文学科重视同行评议和学术声誉，医学重视临床意义和伦理规范。请为作者制定最适合其学科背景的投稿策略和时间规划。"
            )

            if response:
                return response
            return "优先级总结生成失败"

        except Exception as e:
            self.chatbot.append(["错误", f"生成优先级总结时出错: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return "优先级总结生成失败: " + str(e)

    def save_recommendations(self, journal_recommendations: str, conference_recommendations: str, priority_summary: str) -> Generator:
        """保存推荐报告"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 保存为Markdown文件
        try:
            md_content = f"""# 论文期刊会议推荐报告

## 投稿优先级总结

{priority_summary}

## 期刊推荐

{journal_recommendations}

## 会议推荐

{conference_recommendations}

---

# 详细分析结果
"""

            # 添加详细分析结果
            for q in self.questions:
                if q.id in self.analysis_results:
                    md_content += f"\n\n## {q.description}\n\n{self.analysis_results[q.id]}"

            result_file = write_history_to_file(
                history=[md_content],
                file_basename=f"期刊会议推荐_{timestamp}.md"
            )

            if result_file and os.path.exists(result_file):
                promote_file_to_downloadzone(result_file, chatbot=self.chatbot)
                self.chatbot.append(["保存成功", f"推荐报告已保存至: {os.path.basename(result_file)}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
            else:
                self.chatbot.append(["警告", "保存报告成功但找不到文件"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
        except Exception as e:
            self.chatbot.append(["警告", f"保存报告失败: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

    def recommend_venues(self, paper_path: str) -> Generator:
        """推荐期刊会议主流程"""
        # 加载论文
        success = yield from self._load_paper(paper_path)
        if not success:
            return

        # 分析关键问题
        for question in self.questions:
            yield from self._analyze_question(question)

        # 分别生成期刊和会议推荐
        journal_recommendations = yield from self._generate_journal_recommendations()
        conference_recommendations = yield from self._generate_conference_recommendations()

        # 生成优先级总结
        priority_summary = yield from self._generate_priority_summary(journal_recommendations, conference_recommendations)

        # 显示结果
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 保存报告
        yield from self.save_recommendations(journal_recommendations, conference_recommendations, priority_summary)

        # 将完整的分析结果和推荐内容添加到历史记录中，方便用户继续提问
        self._add_to_history(journal_recommendations, conference_recommendations, priority_summary)

    def _add_to_history(self, journal_recommendations: str, conference_recommendations: str, priority_summary: str):
        """将分析结果和推荐内容添加到历史记录中"""
        try:
            # 构建完整的内容摘要
            history_content = f"""# 论文期刊会议推荐分析完成

## 📊 投稿优先级总结
{priority_summary}

## 📚 期刊推荐
{journal_recommendations}

## 🏛️ 会议推荐
{conference_recommendations}

## 📋 详细分析结果
"""

            # 添加详细分析结果
            for q in self.questions:
                if q.id in self.analysis_results:
                    history_content += f"\n### {q.description}\n{self.analysis_results[q.id]}\n"

            history_content += "\n---\n💡 您现在可以基于以上分析结果继续提问，比如询问特定期刊的详细信息、投稿策略建议、或者对推荐结果的进一步解释。"

            # 添加到历史记录中
            self.history.append("论文期刊会议推荐分析")
            self.history.append(history_content)

            self.chatbot.append(["✅ 分析完成", "所有分析结果和推荐内容已添加到对话历史中，您可以继续基于这些内容提问。"])

        except Exception as e:
            self.chatbot.append(["警告", f"添加到历史记录时出错: {str(e)}，但推荐报告已正常生成"])
            # 即使添加历史失败，也不影响主要功能


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
def 论文期刊会议推荐(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
                history: List, system_prompt: str, user_request: str):
    """主函数 - 论文期刊会议推荐"""
    # 初始化推荐器
    chatbot.append(["函数插件功能及使用方式", "论文期刊会议推荐：基于论文内容分析，为您推荐合适的学术期刊和会议投稿目标。适用于各个学科专业（自然科学、工程技术、医学、社会科学、人文学科等），根据不同学科的评价标准和发表文化，提供分层次的期刊会议推荐、影响因子分析、发表难度评估、投稿策略建议等。<br><br>📋 使用方式：<br>1、直接上传PDF文件<br>2、输入DOI号或arXiv ID<br>3、点击插件开始分析"])
    yield from update_ui(chatbot=chatbot, history=history)

    paper_file = None

    # 检查输入是否为论文ID（arxiv或DOI）
    paper_info = extract_paper_id(txt)

    if paper_info:
        # 如果是论文ID，下载论文
        chatbot.append(["检测到论文ID", f"检测到{'arXiv' if paper_info[0] == 'arxiv' else 'DOI'} ID: {paper_info[1]}，准备下载论文..."])
        yield from update_ui(chatbot=chatbot, history=history)

        # 下载论文
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

    # 确保paper_file是字符串
    if paper_file is not None and not isinstance(paper_file, str):
        # 尝试转换为字符串
        try:
            paper_file = str(paper_file)
        except Exception:
            report_exception(chatbot, history, a=f"类型错误", b=f"论文路径不是有效的字符串: {type(paper_file)}")
            yield from update_ui(chatbot=chatbot, history=history)
            return

    # 开始推荐
    chatbot.append(["开始分析", f"正在分析论文并生成期刊会议推荐: {os.path.basename(paper_file)}"])
    yield from update_ui(chatbot=chatbot, history=history)

    recommender = JournalConferenceRecommender(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
    yield from recommender.recommend_venues(paper_file)
