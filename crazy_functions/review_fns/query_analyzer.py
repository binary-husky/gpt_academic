from typing import Dict, List
from dataclasses import dataclass
from textwrap import dedent
from datetime import datetime
import re


@dataclass
class SearchCriteria:
    """搜索条件"""
    query_type: str  # 查询类型: review/recommend/qa/paper
    main_topic: str  # 主题
    sub_topics: List[str]  # 子主题列表
    start_year: int  # 起始年份
    end_year: int  # 结束年份
    arxiv_params: Dict  # arXiv搜索参数
    semantic_params: Dict  # Semantic Scholar搜索参数
    pubmed_params: Dict  # 新增: PubMed搜索参数
    crossref_params: Dict  # 添加 Crossref 参数
    adsabs_params: Dict  # 添加 ADS 参数
    paper_id: str = ""  # 论文ID (arxiv ID 或 DOI)
    paper_title: str = ""  # 论文标题
    paper_source: str = ""  # 论文来源 (arxiv/doi/title)
    original_query: str = ""  # 新增: 原始查询字符串


class QueryAnalyzer:
    """查询分析器"""

    # 响应索引常量
    BASIC_QUERY_INDEX = 0
    PAPER_IDENTIFY_INDEX = 1
    ARXIV_QUERY_INDEX = 2
    ARXIV_CATEGORIES_INDEX = 3
    ARXIV_LATEST_INDEX = 4
    ARXIV_SORT_INDEX = 5
    SEMANTIC_QUERY_INDEX = 6
    SEMANTIC_FIELDS_INDEX = 7
    PUBMED_TYPE_INDEX = 8
    PUBMED_QUERY_INDEX = 9
    CROSSREF_QUERY_INDEX = 10
    ADSABS_QUERY_INDEX = 11

    def __init__(self):
        self.current_year = datetime.now().year
        self.valid_types = {
            "review": ["review", "literature review", "survey"],
            "recommend": ["recommend", "recommendation", "suggest", "similar"],
            "qa": ["qa", "question", "answer", "explain", "what", "how", "why"],
            "paper": ["paper", "analyze", "analysis"]
        }

    def analyze_query(self, query: str, chatbot: List, llm_kwargs: Dict):
        """分析查询意图"""
        from crazy_functions.crazy_utils import \
            request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency as request_gpt
        from crazy_functions.review_fns.prompts.arxiv_prompts import (
            ARXIV_QUERY_PROMPT, ARXIV_CATEGORIES_PROMPT, ARXIV_LATEST_PROMPT,
            ARXIV_SORT_PROMPT, ARXIV_QUERY_SYSTEM_PROMPT, ARXIV_CATEGORIES_SYSTEM_PROMPT, ARXIV_SORT_SYSTEM_PROMPT,
            ARXIV_LATEST_SYSTEM_PROMPT
        )
        from crazy_functions.review_fns.prompts.semantic_prompts import (
            SEMANTIC_QUERY_PROMPT, SEMANTIC_FIELDS_PROMPT,
            SEMANTIC_QUERY_SYSTEM_PROMPT, SEMANTIC_FIELDS_SYSTEM_PROMPT
        )
        from .prompts.paper_prompts import PAPER_IDENTIFY_PROMPT, PAPER_IDENTIFY_SYSTEM_PROMPT
        from .prompts.pubmed_prompts import (
            PUBMED_TYPE_PROMPT, PUBMED_QUERY_PROMPT, PUBMED_SORT_PROMPT,
            PUBMED_TYPE_SYSTEM_PROMPT, PUBMED_QUERY_SYSTEM_PROMPT, PUBMED_SORT_SYSTEM_PROMPT
        )
        from .prompts.crossref_prompts import (
            CROSSREF_QUERY_PROMPT,
            CROSSREF_QUERY_SYSTEM_PROMPT
        )
        from .prompts.adsabs_prompts import ADSABS_QUERY_PROMPT, ADSABS_QUERY_SYSTEM_PROMPT

        # 1. 基本查询分析
        type_prompt = dedent(f"""Please analyze this academic query and respond STRICTLY in the following XML format:

            Query: {query}

            Instructions:
            1. Your response must use XML tags exactly as shown below
            2. Do not add any text outside the tags
            3. Choose query type from: review/recommend/qa/paper
            - review: for literature review or survey requests
            - recommend: for paper recommendation requests
            - qa: for general questions about research topics
            - paper: ONLY for queries about a SPECIFIC paper (with paper ID, DOI, or exact title)
            4. Identify main topic and subtopics
            5. Specify year range if mentioned

            Required format:
            <query_type>ANSWER HERE</query_type>
            <main_topic>ANSWER HERE</main_topic>
            <sub_topics>SUBTOPIC1, SUBTOPIC2, ...</sub_topics>
            <year_range>START_YEAR-END_YEAR</year_range>

            Example responses:

            1. Literature Review Request:
            Query: "Review recent developments in transformer models for NLP from 2020 to 2023"
            <query_type>review</query_type>
            <main_topic>transformer models in natural language processing</main_topic>
            <sub_topics>architecture improvements, pre-training methods, fine-tuning techniques</sub_topics>
            <year_range>2020-2023</year_range>

            2. Paper Recommendation Request:
            Query: "Suggest papers about reinforcement learning in robotics since 2018"
            <query_type>recommend</query_type>
            <main_topic>reinforcement learning in robotics</main_topic>
            <sub_topics>robot control, policy learning, sim-to-real transfer</sub_topics>
            <year_range>2018-2023</year_range>"""
        )

        try:
            # 构建提示数组
            prompts = [
                type_prompt,
                PAPER_IDENTIFY_PROMPT.format(query=query),
                ARXIV_QUERY_PROMPT.format(query=query),
                ARXIV_CATEGORIES_PROMPT.format(query=query),
                ARXIV_LATEST_PROMPT.format(query=query),
                ARXIV_SORT_PROMPT.format(query=query),
                SEMANTIC_QUERY_PROMPT.format(query=query),
                SEMANTIC_FIELDS_PROMPT.format(query=query),
                PUBMED_TYPE_PROMPT.format(query=query),
                PUBMED_QUERY_PROMPT.format(query=query),
                CROSSREF_QUERY_PROMPT.format(query=query),
                ADSABS_QUERY_PROMPT.format(query=query)
            ]

            show_messages = [
                "Analyzing query type...",
                "Identifying paper details...",
                "Determining arXiv search type...",
                "Selecting arXiv categories...",
                "Checking if latest papers requested...",
                "Determining arXiv sort parameters...",
                "Optimizing Semantic Scholar query...",
                "Selecting Semantic Scholar fields...",
                "Determining PubMed search type...",
                "Optimizing PubMed query...",
                "Optimizing Crossref query...",
                "Optimizing ADS query..."
            ]

            sys_prompts = [
                "You are an expert at analyzing academic queries.",
                PAPER_IDENTIFY_SYSTEM_PROMPT,
                ARXIV_QUERY_SYSTEM_PROMPT,
                ARXIV_CATEGORIES_SYSTEM_PROMPT,
                ARXIV_LATEST_SYSTEM_PROMPT,
                ARXIV_SORT_SYSTEM_PROMPT,
                SEMANTIC_QUERY_SYSTEM_PROMPT,
                SEMANTIC_FIELDS_SYSTEM_PROMPT,
                PUBMED_TYPE_SYSTEM_PROMPT,
                PUBMED_QUERY_SYSTEM_PROMPT,
                CROSSREF_QUERY_SYSTEM_PROMPT,
                ADSABS_QUERY_SYSTEM_PROMPT
            ]
            new_llm_kwargs = llm_kwargs.copy()
            # new_llm_kwargs['llm_model'] = 'deepseek-chat'  # deepseek-ai/DeepSeek-V2.5

            # 使用同步方式调用LLM
            responses = yield from request_gpt(
                inputs_array=prompts,
                inputs_show_user_array=show_messages,
                llm_kwargs=new_llm_kwargs,
                chatbot=chatbot,
                history_array=[[] for _ in prompts],
                sys_prompt_array=sys_prompts,
                max_workers=5
            )

            # 从收集的响应中提取我们需要的内容
            extracted_responses = []
            for i in range(len(prompts)):
                if (i * 2 + 1) < len(responses):
                    response = responses[i * 2 + 1]
                    if response is None:
                        raise Exception(f"Response {i} is None")
                    if not isinstance(response, str):
                        try:
                            response = str(response)
                        except:
                            raise Exception(f"Cannot convert response {i} to string")
                    extracted_responses.append(response)
                else:
                    raise Exception(f"未收到第 {i + 1} 个响应")

            # 解析基本信息
            query_type = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "query_type")
            if not query_type:
                print(
                    f"Debug - Failed to extract query_type. Response was: {extracted_responses[self.BASIC_QUERY_INDEX]}")
                raise Exception("无法提取query_type标签内容")
            query_type = query_type.lower()

            main_topic = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "main_topic")
            if not main_topic:
                print(f"Debug - Failed to extract main_topic. Using query as fallback.")
                main_topic = query

            query_type = self._normalize_query_type(query_type, query)

            # 解析arXiv参数
            try:
                arxiv_params = {
                    "query": self._extract_tag(extracted_responses[self.ARXIV_QUERY_INDEX], "query"),
                    "categories": [cat.strip() for cat in
                                   self._extract_tag(extracted_responses[self.ARXIV_CATEGORIES_INDEX],
                                                     "categories").split(",")],
                    "sort_by": self._extract_tag(extracted_responses[self.ARXIV_SORT_INDEX], "sort_by"),
                    "sort_order": self._extract_tag(extracted_responses[self.ARXIV_SORT_INDEX], "sort_order"),
                    "limit": 20
                }

                # 安全地解析limit值
                limit_str = self._extract_tag(extracted_responses[self.ARXIV_SORT_INDEX], "limit")
                if limit_str and limit_str.isdigit():
                    arxiv_params["limit"] = int(limit_str)

            except Exception as e:
                print(f"Warning: Error parsing arXiv parameters: {str(e)}")
                arxiv_params = {
                    "query": "",
                    "categories": [],
                    "sort_by": "relevance",
                    "sort_order": "descending",
                    "limit": 0
                }

            # 解析Semantic Scholar参数
            try:
                semantic_params = {
                    "query": self._extract_tag(extracted_responses[self.SEMANTIC_QUERY_INDEX], "query"),
                    "fields": [field.strip() for field in
                               self._extract_tag(extracted_responses[self.SEMANTIC_FIELDS_INDEX], "fields").split(",")],
                    "sort_by": "relevance",
                    "limit": 20
                }
            except Exception as e:
                print(f"Warning: Error parsing Semantic Scholar parameters: {str(e)}")
                semantic_params = {
                    "query": query,
                    "fields": ["title", "abstract", "authors", "year"],
                    "sort_by": "relevance",
                    "limit": 20
                }

            # 解析PubMed参数
            try:
                # 首先检查是否需要PubMed搜索
                pubmed_search_type = self._extract_tag(extracted_responses[self.PUBMED_TYPE_INDEX], "search_type")

                if pubmed_search_type == "none":
                    # 不需要PubMed搜索，使用空参数
                    pubmed_params = {
                        "search_type": "none",
                        "query": "",
                        "sort_by": "relevance",
                        "limit": 0
                    }
                else:
                    # 需要PubMed搜索，解析完整参数
                    pubmed_params = {
                        "search_type": pubmed_search_type,
                        "query": self._extract_tag(extracted_responses[self.PUBMED_QUERY_INDEX], "query"),
                        "sort_by": "relevance",
                        "limit": 200
                    }
            except Exception as e:
                print(f"Warning: Error parsing PubMed parameters: {str(e)}")
                pubmed_params = {
                    "search_type": "none",
                    "query": "",
                    "sort_by": "relevance",
                    "limit": 0
                }

            # 解析Crossref参数
            try:
                crossref_query = self._extract_tag(extracted_responses[self.CROSSREF_QUERY_INDEX], "query")

                if not crossref_query:
                    crossref_params = {
                        "search_type": "none",
                        "query": "",
                        "sort_by": "relevance",
                        "limit": 0
                    }
                else:
                    crossref_params = {
                        "search_type": "basic",
                        "query": crossref_query,
                        "sort_by": "relevance",
                        "limit": 20
                    }
            except Exception as e:
                print(f"Warning: Error parsing Crossref parameters: {str(e)}")
                crossref_params = {
                    "search_type": "none",
                    "query": "",
                    "sort_by": "relevance",
                    "limit": 0
                }

            # 解析ADS参数
            try:
                adsabs_query = self._extract_tag(extracted_responses[self.ADSABS_QUERY_INDEX], "query")

                if not adsabs_query:
                    adsabs_params = {
                        "search_type": "none",
                        "query": "",
                        "sort_by": "relevance",
                        "limit": 0
                    }
                else:
                    adsabs_params = {
                        "search_type": "basic",
                        "query": adsabs_query,
                        "sort_by": "relevance",
                        "limit": 20
                    }
            except Exception as e:
                print(f"Warning: Error parsing ADS parameters: {str(e)}")
                adsabs_params = {
                    "search_type": "none",
                    "query": "",
                    "sort_by": "relevance",
                    "limit": 0
                }

            print(f"Debug - Extracted information:")
            print(f"Query type: {query_type}")
            print(f"Main topic: {main_topic}")
            print(f"arXiv params: {arxiv_params}")
            print(f"Semantic params: {semantic_params}")
            print(f"PubMed params: {pubmed_params}")
            print(f"Crossref params: {crossref_params}")
            print(f"ADS params: {adsabs_params}")

            # 提取子主题
            sub_topics = []
            if "sub_topics" in query.lower():
                sub_topics_text = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "sub_topics")
                if sub_topics_text:
                    sub_topics = [topic.strip() for topic in sub_topics_text.split(",")]

            # 提取年份范围
            start_year = self.current_year - 5  # 默认最近5年
            end_year = self.current_year
            year_range = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "year_range")
            if year_range:
                try:
                    years = year_range.split("-")
                    if len(years) == 2:
                        start_year = int(years[0].strip())
                        end_year = int(years[1].strip())
                except:
                    pass

            # 提取 latest request 判断
            is_latest_request = self._extract_tag(extracted_responses[self.ARXIV_LATEST_INDEX],
                                                  "is_latest_request").lower() == "true"

            # 如果是最新论文请求，将查询类型改为 "latest"
            if is_latest_request:
                query_type = "latest"

            # 提取论文标识信息
            paper_source = self._extract_tag(extracted_responses[self.PAPER_IDENTIFY_INDEX], "paper_source")
            paper_id = self._extract_tag(extracted_responses[self.PAPER_IDENTIFY_INDEX], "paper_id")
            paper_title = self._extract_tag(extracted_responses[self.PAPER_IDENTIFY_INDEX], "paper_title")
            if start_year > end_year:
                start_year, end_year = end_year, start_year
            # 更新返回的 SearchCriteria
            return SearchCriteria(
                query_type=query_type,
                main_topic=main_topic,
                sub_topics=sub_topics,
                start_year=start_year,
                end_year=end_year,
                arxiv_params=arxiv_params,
                semantic_params=semantic_params,
                pubmed_params=pubmed_params,
                crossref_params=crossref_params,
                paper_id=paper_id,
                paper_title=paper_title,
                paper_source=paper_source,
                original_query=query,
                adsabs_params=adsabs_params
            )

        except Exception as e:
            raise Exception(f"Failed to analyze query: {str(e)}")

    def _normalize_query_type(self, query_type: str, query: str) -> str:
        """规范化查询类型"""
        if query_type in ["review", "recommend", "qa", "paper"]:
            return query_type

        query_lower = query.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return type_name

        query_type_lower = query_type.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_type_lower:
                    return type_name

        return "qa"  # 默认返回qa类型

    def _extract_tag(self, text: str, tag: str) -> str:
        """提取标记内容"""
        if not text:
            return ""

        # 1. 标准XML格式（处理多行和特殊字符）
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # 2. 处理特定标签的复杂内容
        if tag == "categories":
            # 处理arXiv类别
            patterns = [
                # 标准格式：<categories>cs.CL, cs.AI, cs.LG</categories>
                r"<categories>\s*((?:(?:cs|stat|math|physics|q-bio|q-fin|nlin|astro-ph|cond-mat|gr-qc|hep-[a-z]+|math-ph|nucl-[a-z]+|quant-ph)\.[A-Z]+(?:\s*,\s*)?)+)\s*</categories>",
                # 简单列表格式：cs.CL, cs.AI, cs.LG
                r"(?:^|\s)((?:(?:cs|stat|math|physics|q-bio|q-fin|nlin|astro-ph|cond-mat|gr-qc|hep-[a-z]+|math-ph|nucl-[a-z]+|quant-ph)\.[A-Z]+(?:\s*,\s*)?)+)(?:\s|$)",
                # 单个类别格式：cs.AI
                r"(?:^|\s)((?:cs|stat|math|physics|q-bio|q-fin|nlin|astro-ph|cond-mat|gr-qc|hep-[a-z]+|math-ph|nucl-[a-z]+|quant-ph)\.[A-Z]+)(?:\s|$)"
            ]

        elif tag == "query":
            # 处理搜索查询
            patterns = [
                # 完整的查询格式：<query>complex query</query>
                r"<query>\s*((?:(?:ti|abs|au|cat):[^\n]*?|(?:AND|OR|NOT|\(|\)|\d{4}|year:\d{4}|[\"'][^\"']*[\"']|\s+))+)\s*</query>",
                # 简单的关键词列表：keyword1, keyword2
                r"(?:^|\s)((?:\"[^\"]*\"|'[^']*'|[^\s,]+)(?:\s*,\s*(?:\"[^\"]*\"|'[^']*'|[^\s,]+))*)",
                # 字段搜索格式：field:value
                r"((?:ti|abs|au|cat):\s*(?:\"[^\"]*\"|'[^']*'|[^\s]+))"
            ]

        elif tag == "fields":
            # 处理字段列表
            patterns = [
                # 标准格式：<fields>field1, field2</fields>
                r"<fields>\s*([\w\s,]+)\s*</fields>",
                # 简单列表格式：field1, field2
                r"(?:^|\s)([\w]+(?:\s*,\s*[\w]+)*)",
            ]

        elif tag == "sort_by":
            # 处理排序字段
            patterns = [
                # 标准格式：<sort_by>value</sort_by>
                r"<sort_by>\s*(relevance|date|citations|submittedDate|year)\s*</sort_by>",
                # 简单值格式：relevance
                r"(?:^|\s)(relevance|date|citations|submittedDate|year)(?:\s|$)"
            ]

        else:
            # 通用模式
            patterns = [
                f"<{tag}>\s*([\s\S]*?)\s*</{tag}>",  # 标准XML格式
                f"<{tag}>([\s\S]*?)(?:</{tag}>|$)",  # 未闭合的标签
                f"[{tag}]([\s\S]*?)[/{tag}]",  # 方括号格式
                f"{tag}:\s*(.*?)(?=\n\w|$)",  # 冒号格式
                f"<{tag}>\s*(.*?)(?=<|$)"  # 部分闭合
            ]

        # 3. 尝试所有模式
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:  # 确保提取的内容不为空
                    return content

        # 4. 如果所有模式都失败，返回空字符串
        return ""
