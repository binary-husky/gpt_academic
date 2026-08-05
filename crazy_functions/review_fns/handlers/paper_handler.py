from typing import List, Dict, Any, Optional, Tuple
from .base_handler import BaseHandler
from crazy_functions.review_fns.query_analyzer import SearchCriteria
import asyncio
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency as request_gpt

class 单篇论文分析功能(BaseHandler):
    """论文分析处理器"""

    def __init__(self, arxiv, semantic, llm_kwargs=None):
        super().__init__(arxiv, semantic, llm_kwargs)

    async def handle(
        self,
        criteria: SearchCriteria,
        chatbot: List[List[str]],
        history: List[List[str]],
        system_prompt: str,
        llm_kwargs: Dict[str, Any],
        plugin_kwargs: Dict[str, Any],
    ) -> str:
        """处理论文分析请求，返回最终的prompt"""

        # 1. 获取论文详情
        paper = await self._get_paper_details(criteria)
        if not paper:
            return self._generate_apology_prompt(criteria)

        # 保存为ranked_papers以便统一接口
        self.ranked_papers = [paper]

        # 2. 构建最终的prompt
        current_time = self._get_current_time()

        # 获取论文信息
        title = getattr(paper, "title", "Unknown Title")
        authors = getattr(paper, "authors", [])
        year = getattr(paper, "year", "Unknown Year")
        abstract = getattr(paper, "abstract", "No abstract available")
        citations = getattr(paper, "citations", "N/A")

        # 添加论文ID信息
        paper_id = ""
        if criteria.paper_source == "arxiv":
            paper_id = f"arXiv ID: {criteria.paper_id}\n"
        elif criteria.paper_source == "doi":
            paper_id = f"DOI: {criteria.paper_id}\n"

        # 格式化作者列表
        authors_str = ', '.join(authors) if isinstance(authors, list) else authors

        final_prompt = f"""Current time: {current_time}

Please provide a comprehensive analysis of the following paper:

{paper_id}Title: {title}
Authors: {authors_str}
Year: {year}
Citations: {citations}
Publication Venue: {paper.venue_name} ({paper.venue_type})
{f"Publisher: {paper.venue_info.get('publisher')}" if paper.venue_info.get('publisher') else ""}
{f"Journal Reference: {paper.venue_info.get('journal_ref')}" if paper.venue_info.get('journal_ref') else ""}
Abstract: {abstract}

Please provide:
1. Publication Context
   - Publication venue analysis and impact factor (if available)
   - Paper type (journal article, conference paper, preprint)
   - Publication timeline and peer review status
   - Publisher reputation and venue prestige

2. Research Context
   - Field positioning and significance
   - Historical context and prior work
   - Related research streams
   - Cross-venue impact analysis

3. Technical Analysis
   - Detailed methodology review
   - Implementation details
   - Experimental setup and results
   - Technical innovations

4. Impact Analysis
   - Citation patterns and influence
   - Cross-venue recognition
   - Industry vs. academic impact
   - Practical applications

5. Critical Review
   - Methodological rigor assessment
   - Result reliability and reproducibility
   - Venue-appropriate evaluation standards
   - Limitations and potential improvements

IMPORTANT:
- Strictly use ONLY the information provided above about the paper
- Do not make ANY assumptions or inferences beyond the given data
- If certain information is not provided, explicitly state that it is unknown
- For any unclear or missing details, acknowledge the limitation rather than speculating
- When discussing methodology or results, only describe what is explicitly stated in the abstract
- Never fabricate or assume any details about:
  * Publication venues or status
  * Implementation details not mentioned
  * Results or findings not stated
  * Impact or influence not supported by the citation count
  * Authors' affiliations or backgrounds
  * Future work or implications not mentioned
- You can find the paper's download options in the 📥 PDF Downloads section
- Available download formats include arXiv PDF, DOI links, and source URLs

Format your response in markdown with clear sections.

Language requirement:
- If the query explicitly specifies a language, use that language
- Otherwise, match the language of the original user query
"""

        return final_prompt

    async def _get_paper_details(self, criteria: SearchCriteria):
        """获取论文详情"""
        try:
            if criteria.paper_source == "arxiv":
                # 使用 arxiv ID 搜索
                papers = await self.arxiv.search_by_id(criteria.paper_id)
                return papers[0] if papers else None

            elif criteria.paper_source == "doi":
                # 尝试从所有来源获取
                paper = await self.semantic.get_paper_by_doi(criteria.paper_id)
                if not paper:
                    # 如果Semantic Scholar没有找到，尝试PubMed
                    papers = await self.pubmed.search(
                        f"{criteria.paper_id}[doi]",
                        limit=1
                    )
                    if papers:
                        return papers[0]
                return paper

            elif criteria.paper_source == "title":
                # 使用_search_all_sources搜索
                search_params = {
                    'max_papers': 1,
                    'min_year': 1900,  # 不限制年份
                    'search_multiplier': 1
                }

                # 设置搜索参数
                criteria.arxiv_params = {
                    "search_type": "basic",
                    "query": f'ti:"{criteria.paper_title}"',
                    "limit": 1
                }
                criteria.semantic_params = {
                    "query": criteria.paper_title,
                    "limit": 1
                }
                criteria.pubmed_params = {
                    "search_type": "basic",
                    "query": f'"{criteria.paper_title}"[Title]',
                    "limit": 1
                }

                papers = await self._search_all_sources(criteria, search_params)
                return papers[0] if papers else None

            # 如果都没有找到，尝试使用 main_topic 作为标题搜索
            if not criteria.paper_title and not criteria.paper_id:
                search_params = {
                    'max_papers': 1,
                    'min_year': 1900,
                    'search_multiplier': 1
                }

                # 设置搜索参数
                criteria.arxiv_params = {
                    "search_type": "basic",
                    "query": f'ti:"{criteria.main_topic}"',
                    "limit": 1
                }
                criteria.semantic_params = {
                    "query": criteria.main_topic,
                    "limit": 1
                }
                criteria.pubmed_params = {
                    "search_type": "basic",
                    "query": f'"{criteria.main_topic}"[Title]',
                    "limit": 1
                }

                papers = await self._search_all_sources(criteria, search_params)
                return papers[0] if papers else None

            return None

        except Exception as e:
            print(f"获取论文详情时出错: {str(e)}")
            return None

    async def _get_citation_context(self, paper: Dict, plugin_kwargs: Dict) -> Tuple[List, List]:
        """获取引用上下文"""
        search_params = self._get_search_params(plugin_kwargs)

        # 使用论文标题构建搜索参数
        title_query = f'ti:"{getattr(paper, "title", "")}"'
        arxiv_params = {
            "query": title_query,
            "limit": search_params['max_papers'],
            "search_type": "basic",
            "sort_by": "relevance",
            "sort_order": "descending"
        }
        semantic_params = {
            "query": getattr(paper, "title", ""),
            "limit": search_params['max_papers']
        }

        citations, references = await asyncio.gather(
            self._search_semantic(
                semantic_params,
                limit_multiplier=search_params['search_multiplier'],
                min_year=search_params['min_year']
            ),
            self._search_arxiv(
                arxiv_params,
                limit_multiplier=search_params['search_multiplier'],
                min_year=search_params['min_year']
            )
        )

        return citations, references

    async def _generate_analysis(
        self,
        paper: Dict,
        citations: List,
        references: List,
        chatbot: List[List[str]],
        history: List[List[str]],
        system_prompt: str,
        llm_kwargs: Dict[str, Any]
    ) -> List[List[str]]:
        """生成论文分析"""

        # 构建提示
        analysis_prompt = f"""Please provide a comprehensive analysis of the following paper:

Paper details:
{self._format_paper(paper)}

Key references (papers cited by this paper):
{self._format_papers(references)}

Important citations (papers that cite this paper):
{self._format_papers(citations)}

Please provide:
1. Paper Overview
   - Main research question/objective
   - Key methodology/approach
   - Main findings/contributions

2. Technical Analysis
   - Detailed methodology review
   - Technical innovations
   - Implementation details
   - Experimental setup and results

3. Impact Analysis
   - Significance in the field
   - Influence on subsequent research (based on citing papers)
   - Relationship to prior work (based on cited papers)
   - Practical applications

4. Critical Review
   - Strengths and limitations
   - Potential improvements
   - Open questions and future directions
   - Alternative approaches

5. Related Research Context
   - How it builds on previous work
   - How it has influenced subsequent research
   - Comparison with alternative approaches

Format your response in markdown with clear sections."""

        # 并行生成概述和技术分析
        for response_chunk in request_gpt(
            inputs_array=[
                analysis_prompt,
                self._get_technical_prompt(paper)
            ],
            inputs_show_user_array=[
                "Generating paper analysis...",
                "Analyzing technical details..."
            ],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[history, []],
            sys_prompt_array=[
                system_prompt,
                "You are an expert at analyzing technical details in research papers."
            ]
        ):
            pass  # 等待生成完成

        # 获取最后的两个回答
        if chatbot and len(chatbot[-2:]) == 2:
            analysis = chatbot[-2][1]
            technical = chatbot[-1][1]
            full_analysis = f"""# Paper Analysis: {paper.title}

## General Analysis
{analysis}

## Technical Deep Dive
{technical}
"""
            chatbot.append(["Here is the paper analysis:", full_analysis])
        else:
            chatbot.append(["Here is the paper analysis:", "Failed to generate analysis."])

        return chatbot

    def _get_technical_prompt(self, paper: Dict) -> str:
        """生成技术分析提示"""
        return f"""Please provide a detailed technical analysis of the following paper:

{self._format_paper(paper)}

Focus on:
1. Mathematical formulations and their implications
2. Algorithm design and complexity analysis
3. Architecture details and design choices
4. Implementation challenges and solutions
5. Performance analysis and bottlenecks
6. Technical limitations and potential improvements

Format your response in markdown, focusing purely on technical aspects."""
