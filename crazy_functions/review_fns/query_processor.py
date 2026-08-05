from typing import List, Dict, Any
from .query_analyzer import QueryAnalyzer, SearchCriteria
from .data_sources.arxiv_source import ArxivSource
from .data_sources.semantic_source import SemanticScholarSource
from .handlers.review_handler import 文献综述功能
from .handlers.recommend_handler import 论文推荐功能
from .handlers.qa_handler import 学术问答功能
from .handlers.paper_handler import 单篇论文分析功能

class QueryProcessor:
    """查询处理器"""

    def __init__(self):
        self.analyzer = QueryAnalyzer()
        self.arxiv = ArxivSource()
        self.semantic = SemanticScholarSource()

        # 初始化各种处理器
        self.handlers = {
            "review": 文献综述功能(self.arxiv, self.semantic),
            "recommend": 论文推荐功能(self.arxiv, self.semantic),
            "qa": 学术问答功能(self.arxiv, self.semantic),
            "paper": 单篇论文分析功能(self.arxiv, self.semantic)
        }

    async def process_query(
        self,
        query: str,
        chatbot: List[List[str]],
        history: List[List[str]],
        system_prompt: str,
        llm_kwargs: Dict[str, Any],
        plugin_kwargs: Dict[str, Any],
    ) -> List[List[str]]:
        """处理用户查询"""

        # 设置默认的插件参数
        default_plugin_kwargs = {
            'max_papers': 20,  # 最大论文数量
            'min_year': 2015,   # 最早年份
            'search_multiplier': 3,  # 检索倍数
        }
        # 更新插件参数
        plugin_kwargs.update({k: v for k, v in default_plugin_kwargs.items() if k not in plugin_kwargs})

        # 1. 分析查询意图
        criteria = self.analyzer.analyze_query(query, chatbot, llm_kwargs)

        # 2. 根据查询类型选择处理器
        handler = self.handlers.get(criteria.query_type)
        if not handler:
            handler = self.handlers["qa"]  # 默认使用QA处理器

        # 3. 处理查询
        response = await handler.handle(
            criteria,
            chatbot,
            history,
            system_prompt,
            llm_kwargs,
            plugin_kwargs
        )

        return response
