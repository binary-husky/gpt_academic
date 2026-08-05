from typing import List, Dict, Any
from .base_handler import BaseHandler
from textwrap import dedent
from crazy_functions.review_fns.query_analyzer import SearchCriteria
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency as request_gpt

class 论文推荐功能(BaseHandler):
    """论文推荐处理器"""

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
        """处理论文推荐请求，返回最终的prompt"""

        search_params = self._get_search_params(plugin_kwargs)

        # 1. 先搜索种子论文
        seed_papers = await self._search_seed_papers(criteria, search_params)
        if not seed_papers:
            return self._generate_apology_prompt(criteria)

        # 使用BGE重排序
        all_papers = seed_papers

        if not all_papers:
            return self._generate_apology_prompt(criteria)

        self.ranked_papers = self.paper_ranker.rank_papers(
            query=criteria.original_query,
            papers=all_papers,
            search_criteria=criteria
        )

        if not self.ranked_papers:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = dedent(f"""Current time: {current_time}

            Based on the user's interest in {criteria.main_topic}, here are relevant papers.

            Available papers for recommendation:
            {self._format_papers(self.ranked_papers)}

            Please provide:
            1. Group papers by sub-topics or themes if applicable

            2. For each paper:
            - Publication time and venue (when available)
            - Journal metrics (when available):
                * Impact Factor (IF)
                * JCR Quartile
                * Chinese Academy of Sciences (CAS) Division
            - The key contributions and main findings
            - Why it's relevant to the user's interests
            - How it relates to other recommended papers
            - The paper's citation count and citation impact
            - The paper's download link

            3. A suggested reading order based on:
            - Journal impact and quality metrics
            - Chronological development of ideas
            - Paper relationships and dependencies
            - Difficulty level
            - Impact and significance

            4. Future Directions
            - Emerging venues and research streams
            - Novel methodological approaches
            - Cross-disciplinary opportunities
            - Research gaps by publication type


            IMPORTANT:
            - Focus on explaining why each paper is valuable
            - Highlight connections between papers
            - Consider both citation counts AND journal metrics when discussing impact
            - When available, use IF, JCR quartile, and CAS division to assess paper quality
            - Mention publication timing when discussing paper relationships
            - When referring to papers, use HTML links in this format:
            * For DOIs: <a href='https://doi.org/DOI_HERE' target='_blank'>DOI: DOI_HERE</a>
            * For titles: <a href='PAPER_URL' target='_blank'>PAPER_TITLE</a>
            - Present papers in a way that shows the evolution of ideas over time
            - Base recommendations ONLY on the explicitly provided paper information
            - Do not make ANY assumptions about papers beyond the given data
            - When information is missing or unclear, acknowledge the limitation
            - Never speculate about:
            * Paper quality or rigor not evidenced in the data
            * Research impact beyond citation counts and journal metrics
            * Implementation details not mentioned
            * Author expertise or background
            * Future research directions not stated
            - For each recommendation, cite only verifiable information
            - Clearly distinguish between facts and potential implications

            Format your response in markdown with clear sections.
            Language requirement:
            - If the query explicitly specifies a language, use that language
            - Otherwise, match the language of the original user query
            """
        )
        return final_prompt

    async def _search_seed_papers(self, criteria: SearchCriteria, search_params: Dict) -> List:
        """搜索种子论文"""
        try:
            # 使用_search_all_sources替代原来的并行搜索
            all_papers = await self._search_all_sources(criteria, search_params)

            if not all_papers:
                return []

            return all_papers

        except Exception as e:
            print(f"搜索种子论文时出错: {str(e)}")
            return []

    async def _get_recommendations(self, seed_papers: List, multiplier: int = 1) -> List:
        """获取推荐论文"""
        recommendations = []
        base_limit = 3 * multiplier

        # 将种子论文添加到推荐列表中
        recommendations.extend(seed_papers)

        # 只使用前5篇论文作为种子
        seed_papers = seed_papers[:5]

        for paper in seed_papers:
            try:
                if paper.doi and paper.doi.startswith("10.48550/arXiv."):
                    # arXiv论文
                    arxiv_id = paper.doi.split(".")[-1]
                    paper_details = await self.arxiv.get_paper_details(arxiv_id)
                    if paper_details and hasattr(paper_details, 'venue'):
                        category = paper_details.venue.split(":")[-1]
                        similar_papers = await self.arxiv.search_by_category(
                            category,
                            limit=base_limit,
                            sort_by='relevance'
                        )
                        recommendations.extend(similar_papers)
                elif paper.doi:  # 只对有DOI的论文获取推荐
                    # Semantic Scholar论文
                    similar_papers = await self.semantic.get_recommended_papers(
                        paper.doi,
                        limit=base_limit
                    )
                    if similar_papers:  # 只添加成功获取的推荐
                        recommendations.extend(similar_papers)
                else:
                    # 对于没有DOI的论文，使用标题进行相关搜索
                    if paper.title:
                        similar_papers = await self.semantic.search(
                            query=paper.title,
                            limit=base_limit
                        )
                        recommendations.extend(similar_papers)

            except Exception as e:
                print(f"获取论文 '{paper.title}' 的推荐时发生错误: {str(e)}")
                continue

        # 去重处理
        seen_dois = set()
        unique_recommendations = []
        for paper in recommendations:
            if paper.doi and paper.doi not in seen_dois:
                seen_dois.add(paper.doi)
                unique_recommendations.append(paper)
            elif not paper.doi and paper not in unique_recommendations:
                unique_recommendations.append(paper)

        return unique_recommendations
