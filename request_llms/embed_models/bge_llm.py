import re
import requests
from loguru import logger
from typing import List, Dict
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from textwrap import dedent
from request_llms.bridge_all import predict_no_ui_long_connection

class BGELLMRanker:
    """使用LLM进行论文相关性判断的类"""
    def __init__(self, llm_kwargs):
        self.llm_kwargs = llm_kwargs

    def is_paper_relevant(self, query: str, paper_text: str) -> bool:
        """判断论文是否与查询相关"""
        prompt = dedent(f"""
            Evaluate if this academic paper contains information that directly addresses the user's query.

            Query: {query}

            Paper Content:
            {paper_text}

            Evaluation Criteria:
            1. The paper must contain core information that directly answers the query
            2. The paper's main research focus must be highly relevant to the query
            3. Papers that only mention query-related content in abstract should be excluded
            4. Papers with superficial or general discussions should be excluded
            5. For queries about "recent" or "latest" advances, paper should be from last 3 years

            Instructions:
            - Carefully evaluate against ALL criteria above
            - Return true ONLY if paper meets ALL criteria
            - If any criteria is not met or unclear, return false
            - Be strict but not overly restrictive

            Output Rules:
            - Must ONLY respond with <decision>true</decision> or <decision>false</decision>
            - true = paper contains relevant information to answer the query
            - false = paper does not contain sufficient relevant information

            Do not include any explanation or additional text."""
        )
        response = predict_no_ui_long_connection(
            inputs=prompt,
            history=[],
            llm_kwargs=self.llm_kwargs,
            sys_prompt="You are an expert at determining paper relevance to queries. Respond only with <decision>true</decision> or <decision>false</decision>."
        )
        # 提取decision标签中的内容
        match = re.search(r'<decision>(.*?)</decision>', response, re.IGNORECASE)
        if match:
            decision = match.group(1).lower()
            return decision == "true"
        else:
            return False

    def batch_check_relevance(self, query: str, paper_texts: List[str], show_progress: bool = True) -> List[bool]:
        """批量检查论文相关性

        Args:
            query: 用户查询
            paper_texts: 论文文本列表
            show_progress: 是否显示进度条

        Returns:
            List[bool]: 相关性判断结果列表
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from tqdm import tqdm

        results = [False] * len(paper_texts)

        # 减少并发线程数以避免连接池耗尽
        max_workers = min(20, len(paper_texts))  # 限制最大线程数

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self.is_paper_relevant, query, text): i
                for i, text in enumerate(paper_texts)
            }
            iterator = as_completed(future_to_idx)
            if show_progress:
                iterator = tqdm(iterator, total=len(paper_texts), desc="判断论文相关性")
            for future in iterator:
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    logger.exception(f"处理论文 {idx} 时出错: {str(e)}")
                    results[idx] = False
        return results

def main():
    # 测试代码
    ranker = BGELLMRanker()

    query = "Recent advances in transformer models"
    paper_text = """
    Title: Attention Is All You Need
    Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely...
    """

    is_relevant = ranker.is_paper_relevant(query, paper_text)
    print(f"Paper relevant: {is_relevant}")

if __name__ == "__main__":
    main()
