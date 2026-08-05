from typing import List, Dict, Any
from .base_handler import BaseHandler
from crazy_functions.review_fns.query_analyzer import SearchCriteria
import asyncio

class Arxiv最新论文推荐功能(BaseHandler):
    """最新论文推荐处理器"""

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
        """处理最新论文推荐请求"""

        # 获取搜索参数
        search_params = self._get_search_params(plugin_kwargs)

        # 获取最新论文
        papers = []
        for category in criteria.arxiv_params["categories"]:
            latest_papers = await self.arxiv.get_latest_papers(
                category=category,
                debug=False,
                batch_size=50
            )
            papers.extend(latest_papers)

        if not papers:
            return self._generate_apology_prompt(criteria)

        # 使用embedding模型对论文进行排序
        self.ranked_papers = self.paper_ranker.rank_papers(
            query=criteria.original_query,
            papers=papers,
            search_criteria=criteria
        )

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = f"""Current time: {current_time}

Based on your interest in {criteria.main_topic}, here are the latest papers from arXiv in relevant categories:
{', '.join(criteria.arxiv_params["categories"])}

Latest papers available:
{self._format_papers(self.ranked_papers)}

Please provide:
1. A clear list of latext papers, organized by themes or approaches


2. Group papers by sub-topics or themes if applicable

3. For each paper:
   - Publication time
   - The key contributions and main findings
   - Why it's relevant to the user's interests
   - How it relates to other latest papers
   - The paper's citation count and citation impact
   - The paper's download link

4. A suggested reading order based on:
   - Paper relationships and dependencies
   - Difficulty level
   - Significance

5. Future Directions
   - Emerging venues and research streams
   - Novel methodological approaches
   - Cross-disciplinary opportunities
   - Research gaps by publication type

IMPORTANT:
- Focus on explaining why each paper is interesting
- Highlight the novelty and potential impact
- Consider the credibility and stage of each publication
- Use the provided paper titles with their links when referring to specific papers
- Base recommendations ONLY on the explicitly provided paper information
- Do not make ANY assumptions about papers beyond the given data
- When information is missing or unclear, acknowledge the limitation
- Never speculate about:
  * Paper quality or rigor not evidenced in the data
  * Research impact beyond citation counts
  * Implementation details not mentioned
  * Author expertise or background
  * Future research directions not stated
- For each paper, cite only verifiable information
- Clearly distinguish between facts and potential implications
- Each paper includes download links in its 📥 PDF Downloads section

Format your response in markdown with clear sections.

Language requirement:
- If the query explicitly specifies a language, use that language
- Otherwise, match the language of the original user query
"""

        return final_prompt
