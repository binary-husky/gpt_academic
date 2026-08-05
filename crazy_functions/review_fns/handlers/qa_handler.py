from typing import List, Dict, Any
from .base_handler import BaseHandler
from crazy_functions.review_fns.query_analyzer import SearchCriteria
from textwrap import dedent
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency as request_gpt

class 学术问答功能(BaseHandler):
    """学术问答处理器"""

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
        """处理学术问答请求，返回最终的prompt"""

        # 1. 获取搜索参数
        search_params = self._get_search_params(plugin_kwargs)

        # 2. 搜索相关论文
        papers = await self._search_relevant_papers(criteria, search_params)
        if not papers:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = dedent(f"""Current time: {current_time}

            Based on the following paper abstracts, please answer this academic question: {criteria.original_query}

            Available papers for reference:
            {self._format_papers(self.ranked_papers)}

            Please structure your response in the following format:

            1. Core Answer (2-3 paragraphs)
            - Provide a clear, direct answer synthesizing key findings
            - Support main points with citations [1,2,etc.]
            - Focus on consensus and differences across papers

            2. Key Evidence (2-3 paragraphs)
            - Present supporting evidence from abstracts
            - Compare methodologies and results
            - Highlight significant findings with citations

            3. Research Context (1-2 paragraphs)
            - Discuss current trends and developments
            - Identify research gaps or limitations
            - Suggest potential future directions

            Guidelines:
            - Base your answer ONLY on the provided abstracts
            - Use numbered citations [1], [2,3], etc. for every claim
            - Maintain academic tone and objectivity
            - Synthesize findings across multiple papers
            - Focus on the most relevant information to the question

            Constraints:
            - Do not include information beyond the provided abstracts
            - Avoid speculation or personal opinions
            - Do not elaborate on technical details unless directly relevant
            - Keep citations concise and focused
            - Use [N] citations for every major claim or finding
            - Cite multiple papers [1,2,3] when showing consensus
            - Place citations immediately after the relevant statements

            Note: Provide citations for every major claim to ensure traceability to source papers.
            Language requirement:
            - If the query explicitly specifies a language, use that language. Use Chinese to answer if no language is specified.
            - Otherwise, match the language of the original user query
            """
        )

        return final_prompt

    async def _search_relevant_papers(self, criteria: SearchCriteria, search_params: Dict) -> List:
        """搜索相关论文"""
        # 使用_search_all_sources替代原来的并行搜索
        all_papers = await self._search_all_sources(criteria, search_params)

        if not all_papers:
            return []

        # 使用BGE重排序
        self.ranked_papers = self.paper_ranker.rank_papers(
            query=criteria.main_topic,
            papers=all_papers,
            search_criteria=criteria
        )

        return self.ranked_papers or []

    async def _generate_answer(
        self,
        criteria: SearchCriteria,
        papers: List,
        chatbot: List[List[str]],
        history: List[List[str]],
        system_prompt: str,
        llm_kwargs: Dict[str, Any]
    ) -> List[List[str]]:
        """生成答案"""

        # 构建提示
        qa_prompt = dedent(f"""Please answer the following academic question based on recent research papers.

            Question: {criteria.main_topic}

            Relevant papers:
            {self._format_papers(papers)}

            Please provide:
            1. A direct answer to the question
            2. Supporting evidence from the papers
            3. Different perspectives or approaches if applicable
            4. Current limitations and open questions
            5. References to specific papers

            Format your response in markdown with clear sections."""
        )
        # 调用LLM生成答案
        for response_chunk in request_gpt(
            inputs_array=[qa_prompt],
            inputs_show_user_array=["Generating answer..."],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[history],
            sys_prompt_array=[system_prompt]
        ):
            pass  # 等待生成完成

        # 获取最后的回答
        if chatbot and len(chatbot[-1]) >= 2:
            answer = chatbot[-1][1]
            chatbot.append(["Here is the answer:", answer])
        else:
            chatbot.append(["Here is the answer:", "Failed to generate answer."])

        return chatbot
