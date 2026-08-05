from typing import List, Dict, Any, Tuple
from .base_handler import BaseHandler
from crazy_functions.review_fns.query_analyzer import SearchCriteria
import asyncio

class 文献综述功能(BaseHandler):
    """文献综述处理器"""

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
        """处理文献综述请求，返回最终的prompt"""

        # 获取搜索参数
        search_params = self._get_search_params(plugin_kwargs)

        # 使用_search_all_sources替代原来的并行搜索
        all_papers = await self._search_all_sources(criteria, search_params)

        if not all_papers:
            return self._generate_apology_prompt(criteria)

        self.ranked_papers = self.paper_ranker.rank_papers(
            query=criteria.original_query,
            papers=all_papers,
            search_criteria=criteria
        )

        # 检查排序后的论文数量
        if not self.ranked_papers:
            return self._generate_apology_prompt(criteria)

        # 检查是否包含PubMed论文
        has_pubmed_papers = any(paper.url and 'pubmed.ncbi.nlm.nih.gov' in paper.url
                               for paper in self.ranked_papers)

        if has_pubmed_papers:
            return self._generate_medical_review_prompt(criteria)
        else:
            return self._generate_general_review_prompt(criteria)

    def _generate_medical_review_prompt(self, criteria: SearchCriteria) -> str:
        """生成医学文献综述prompt"""
        return f"""Current time: {self._get_current_time()}

Conduct a systematic medical literature review on {criteria.main_topic} based STRICTLY on the provided articles.

Available literature for review:
{self._format_papers(self.ranked_papers)}

IMPORTANT: If the user query contains specific requirements for the review structure or format, those requirements take precedence over the following guidelines.

Please structure your medical review following these guidelines:

1. Research Overview
   - Main research questions and objectives from the studies
   - Types of studies included (clinical trials, observational studies, etc.)
   - Study populations and settings
   - Time period of the research

2. Key Findings
   - Main outcomes and results reported in abstracts
   - Primary endpoints and their measurements
   - Statistical significance when reported
   - Observed trends across studies

3. Methods Summary
   - Study designs used
   - Major interventions or treatments studied
   - Key outcome measures
   - Patient populations studied

4. Clinical Relevance
   - Reported clinical implications
   - Main conclusions from authors
   - Reported benefits and risks
   - Treatment responses when available

5. Research Status
   - Current research focus areas
   - Reported limitations
   - Gaps identified in abstracts
   - Authors' suggested future directions

CRITICAL REQUIREMENTS:

Citation Rules (MANDATORY):
- EVERY finding or statement MUST be supported by citations [N], where N is the number matching the paper in the provided literature list
- When reporting outcomes, ALWAYS cite the source studies using the exact paper numbers from the literature list
- For findings supported by multiple studies, use consecutive numbers as shown in the literature list [1,2,3]
- Use ONLY the papers provided in the available literature list above
- Citations must appear immediately after each statement
- Citation numbers MUST match the numbers assigned to papers in the literature list above (e.g., if a finding comes from the first paper in the list, cite it as [1])
- DO NOT change or reorder the citation numbers - they must exactly match the paper numbers in the literature list

Content Guidelines:
- Present only information available in the provided papers
- If certain information is not available, simply omit that aspect rather than explicitly stating its absence
- Focus on synthesizing and presenting available findings
- Maintain professional medical writing style
- Present limitations and gaps as research opportunities rather than missing information

Writing Style:
- Use precise medical terminology
- Maintain objective reporting
- Use consistent terminology throughout
- Present a cohesive narrative without referencing data limitations

Language requirement:
- If the query explicitly specifies a language, use that language
- Otherwise, match the language of the original user query
"""

    def _generate_general_review_prompt(self, criteria: SearchCriteria) -> str:
        """生成通用文献综述prompt"""
        current_time = self._get_current_time()
        final_prompt = f"""Current time: {current_time}

Conduct a comprehensive literature review on {criteria.main_topic} focusing on the following aspects:
{', '.join(criteria.sub_topics)}

Available literature for review:
{self._format_papers(self.ranked_papers)}

IMPORTANT: If the user query contains specific requirements for the review structure or format, those requirements take precedence over the following guidelines.

Please structure your review following these guidelines:

1. Introduction and Research Background
   - Current state and significance of the research field
   - Key research problems and challenges
   - Research development timeline and evolution

2. Research Directions and Classifications
   - Major research directions and their relationships
   - Different technical approaches and their characteristics
   - Comparative analysis of various solutions

3. Core Technologies and Methods
   - Key technological breakthroughs
   - Advantages and limitations of different methods
   - Technical challenges and solutions

4. Applications and Impact
   - Real-world applications and use cases
   - Industry influence and practical value
   - Implementation challenges and solutions

5. Future Trends and Prospects
   - Emerging research directions
   - Unsolved problems and challenges
   - Potential breakthrough points

CRITICAL REQUIREMENTS:

Citation Rules (MANDATORY):
- EVERY finding or statement MUST be supported by citations [N], where N is the number matching the paper in the provided literature list
- When reporting outcomes, ALWAYS cite the source studies using the exact paper numbers from the literature list
- For findings supported by multiple studies, use consecutive numbers as shown in the literature list [1,2,3]
- Use ONLY the papers provided in the available literature list above
- Citations must appear immediately after each statement
- Citation numbers MUST match the numbers assigned to papers in the literature list above (e.g., if a finding comes from the first paper in the list, cite it as [1])
- DO NOT change or reorder the citation numbers - they must exactly match the paper numbers in the literature list

Writing Style:
- Maintain academic and professional tone
- Focus on objective analysis with proper citations
- Ensure logical flow and clear structure

Content Requirements:
- Base ALL analysis STRICTLY on the provided papers with explicit citations
- When introducing any concept, method, or finding, immediately follow with [N]
- For each research direction or approach, cite the specific papers [N] that proposed or developed it
- When discussing limitations or challenges, cite the papers [N] that identified them
- DO NOT include information from sources outside the provided paper list
- DO NOT make unsupported claims or statements

Language requirement:
- If the query explicitly specifies a language, use that language
- Otherwise, match the language of the original user query
"""

        return final_prompt
