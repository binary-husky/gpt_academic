import asyncio
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from crazy_functions.review_fns.query_analyzer import SearchCriteria
from crazy_functions.review_fns.data_sources.arxiv_source import ArxivSource
from crazy_functions.review_fns.data_sources.semantic_source import SemanticScholarSource
from crazy_functions.review_fns.data_sources.pubmed_source import PubMedSource
from crazy_functions.review_fns.paper_processor.paper_llm_ranker import PaperLLMRanker
from crazy_functions.pdf_fns.breakdown_pdf_txt import cut_from_end_to_satisfy_token_limit
from request_llms.bridge_all import model_info
from crazy_functions.review_fns.data_sources.crossref_source import CrossrefSource
from crazy_functions.review_fns.data_sources.adsabs_source import AdsabsSource
from toolbox import get_conf


class BaseHandler(ABC):
    """处理器基类"""

    def __init__(self, arxiv: ArxivSource, semantic: SemanticScholarSource, llm_kwargs: Dict = None):
        self.arxiv = arxiv
        self.semantic = semantic
        self.pubmed = PubMedSource()
        self.crossref = CrossrefSource()  # 添加 Crossref 实例
        self.adsabs = AdsabsSource()  # 添加 ADS 实例
        self.paper_ranker = PaperLLMRanker(llm_kwargs=llm_kwargs)
        self.ranked_papers = []  # 存储排序后的论文列表
        self.llm_kwargs = llm_kwargs or {}  # 保存llm_kwargs

    def _get_search_params(self, plugin_kwargs: Dict) -> Dict:
        """获取搜索参数"""
        return {
            'max_papers': plugin_kwargs.get('max_papers', 100),  # 最大论文数量
            'min_year': plugin_kwargs.get('min_year', 2015),  # 最早年份
            'search_multiplier': plugin_kwargs.get('search_multiplier', 3),  # 检索倍数
        }

    @abstractmethod
    async def handle(
            self,
            criteria: SearchCriteria,
            chatbot: List[List[str]],
            history: List[List[str]],
            system_prompt: str,
            llm_kwargs: Dict[str, Any],
            plugin_kwargs: Dict[str, Any],
    ) -> List[List[str]]:
        """处理查询"""
        pass

    async def _search_arxiv(self, params: Dict, limit_multiplier: int = 1, min_year: int = 2015) -> List:
        """使用arXiv专用参数搜索"""
        try:
            original_limit = params.get("limit", 20)
            params["limit"] = original_limit * limit_multiplier
            papers = []

            # 首先尝试基础搜索
            query = params.get("query", "")
            if query:
                papers = await self.arxiv.search(
                    query,
                    limit=params["limit"],
                    sort_by=params.get("sort_by", "relevance"),
                    sort_order=params.get("sort_order", "descending"),
                    start_year=min_year
                )

            # 如果基础搜索没有结果，尝试分类搜索
            if not papers:
                categories = params.get("categories", [])
                for category in categories:
                    category_papers = await self.arxiv.search_by_category(
                        category,
                        limit=params["limit"],
                        sort_by=params.get("sort_by", "relevance"),
                        sort_order=params.get("sort_order", "descending"),
                    )
                    if category_papers:
                        papers.extend(category_papers)

            return papers or []

        except Exception as e:
            print(f"arXiv搜索出错: {str(e)}")
            return []

    async def _search_semantic(self, params: Dict, limit_multiplier: int = 1, min_year: int = 2015) -> List:
        """使用Semantic Scholar专用参数搜索"""
        try:
            original_limit = params.get("limit", 20)
            params["limit"] = original_limit * limit_multiplier

            # 只使用基本的搜索参数
            papers = await self.semantic.search(
                query=params.get("query", ""),
                limit=params["limit"]
            )

            # 在内存中进行过滤
            if papers and min_year:
                papers = [p for p in papers if getattr(p, 'year', 0) and p.year >= min_year]

            return papers or []

        except Exception as e:
            print(f"Semantic Scholar搜索出错: {str(e)}")
            return []

    async def _search_pubmed(self, params: Dict, limit_multiplier: int = 1, min_year: int = 2015) -> List:
        """使用PubMed专用参数搜索"""
        try:
            # 如果不需要PubMed搜索，直接返回空列表
            if params.get("search_type") == "none":
                return []

            original_limit = params.get("limit", 20)
            params["limit"] = original_limit * limit_multiplier
            papers = []

            # 根据搜索类型选择搜索方法
            if params.get("search_type") == "basic":
                papers = await self.pubmed.search(
                    query=params.get("query", ""),
                    limit=params["limit"],
                    start_year=min_year
                )
            elif params.get("search_type") == "author":
                papers = await self.pubmed.search_by_author(
                    author=params.get("query", ""),
                    limit=params["limit"],
                    start_year=min_year
                )
            elif params.get("search_type") == "journal":
                papers = await self.pubmed.search_by_journal(
                    journal=params.get("query", ""),
                    limit=params["limit"],
                    start_year=min_year
                )

            return papers or []

        except Exception as e:
            print(f"PubMed搜索出错: {str(e)}")
            return []

    async def _search_crossref(self, params: Dict, limit_multiplier: int = 1, min_year: int = 2015) -> List:
        """使用Crossref专用参数搜索"""
        try:
            original_limit = params.get("limit", 20)
            params["limit"] = original_limit * limit_multiplier
            papers = []

            # 根据搜索类型选择搜索方法
            if params.get("search_type") == "basic":
                papers = await self.crossref.search(
                    query=params.get("query", ""),
                    limit=params["limit"],
                    start_year=min_year
                )
            elif params.get("search_type") == "author":
                papers = await self.crossref.search_by_authors(
                    authors=[params.get("query", "")],
                    limit=params["limit"],
                    start_year=min_year
                )
            elif params.get("search_type") == "journal":
                # 实现期刊搜索逻辑
                pass

            return papers or []

        except Exception as e:
            print(f"Crossref搜索出错: {str(e)}")
            return []

    async def _search_adsabs(self, params: Dict, limit_multiplier: int = 1, min_year: int = 2015) -> List:
        """使用ADS专用参数搜索"""
        try:
            original_limit = params.get("limit", 20)
            params["limit"] = original_limit * limit_multiplier
            papers = []

            # 执行搜索
            if params.get("search_type") == "basic":
                papers = await self.adsabs.search(
                    query=params.get("query", ""),
                    limit=params["limit"],
                    start_year=min_year
                )

            return papers or []

        except Exception as e:
            print(f"ADS搜索出错: {str(e)}")
            return []

    async def _search_all_sources(self, criteria: SearchCriteria, search_params: Dict) -> List:
        """从所有数据源搜索论文"""
        search_tasks = []

        # # 检查是否需要执行PubMed搜索
        # is_using_pubmed = criteria.pubmed_params.get("search_type") != "none" and criteria.pubmed_params.get("query") != "none"
        is_using_pubmed = False # 开源版本不再搜索pubmed

        # 如果使用PubMed，则只执行PubMed和Semantic Scholar搜索
        if is_using_pubmed:
            search_tasks.append(
                self._search_pubmed(
                    criteria.pubmed_params,
                    limit_multiplier=search_params['search_multiplier'],
                    min_year=criteria.start_year
                )
            )

            # Semantic Scholar总是执行搜索
            search_tasks.append(
                self._search_semantic(
                    criteria.semantic_params,
                    limit_multiplier=search_params['search_multiplier'],
                    min_year=criteria.start_year
                )
            )
        else:

            # 如果不使用ADS，则执行Crossref搜索
            if criteria.crossref_params.get("search_type") != "none" and criteria.crossref_params.get("query") != "none":
                search_tasks.append(
                    self._search_crossref(
                        criteria.crossref_params,
                        limit_multiplier=search_params['search_multiplier'],
                        min_year=criteria.start_year
                    )
                )

            search_tasks.append(
                self._search_arxiv(
                    criteria.arxiv_params,
                    limit_multiplier=search_params['search_multiplier'],
                    min_year=criteria.start_year
                )
            )
            if get_conf("SEMANTIC_SCHOLAR_KEY"):
                search_tasks.append(
                    self._search_semantic(
                        criteria.semantic_params,
                        limit_multiplier=search_params['search_multiplier'],
                        min_year=criteria.start_year
                    )
                )

        # 执行所有需要的搜索任务
        papers = await asyncio.gather(*search_tasks)

        # 合并所有来源的论文并统计各来源的数量
        all_papers = []
        source_counts = {
            'arxiv': 0,
            'semantic': 0,
            'pubmed': 0,
            'crossref': 0,
            'adsabs': 0
        }

        for source_papers in papers:
            if source_papers:
                for paper in source_papers:
                    source = getattr(paper, 'source', 'unknown')
                    if source in source_counts:
                        source_counts[source] += 1
                all_papers.extend(source_papers)

        # 打印各来源的论文数量
        print("\n=== 各数据源找到的论文数量 ===")
        for source, count in source_counts.items():
            if count > 0:  # 只打印有论文的来源
                print(f"{source.capitalize()}: {count} 篇")
        print(f"总计: {len(all_papers)} 篇")
        print("===========================\n")

        return all_papers

    def _format_paper_time(self, paper) -> str:
        """格式化论文时间信息"""
        year = getattr(paper, 'year', None)
        if not year:
            return ""

        # 如果有具体的发表日期，使用具体日期
        if hasattr(paper, 'published') and paper.published:
            return f"(发表于 {paper.published.strftime('%Y-%m')})"
        # 如果只有年份，只显示年份
        return f"({year})"

    def _format_papers(self, papers: List) -> str:
        """格式化论文列表，使用token限制控制长度"""
        formatted = []

        for i, paper in enumerate(papers, 1):
            # 只保留前三个作者
            authors = paper.authors[:3]
            if len(paper.authors) > 3:
                authors.append("et al.")

            # 构建所有可能的下载链接
            download_links = []

            # 添加arXiv链接
            if hasattr(paper, 'doi') and paper.doi:
                if paper.doi.startswith("10.48550/arXiv."):
                    # 从DOI中提取完整的arXiv ID
                    arxiv_id = paper.doi.split("arXiv.")[-1]
                    # 移除多余的点号并确保格式正确
                    arxiv_id = arxiv_id.replace("..", ".")  # 移除重复的点号
                    if arxiv_id.startswith("."):  # 移除开头的点号
                        arxiv_id = arxiv_id[1:]
                    if arxiv_id.endswith("."):  # 移除结尾的点号
                        arxiv_id = arxiv_id[:-1]

                    download_links.append(f"[arXiv PDF](https://arxiv.org/pdf/{arxiv_id}.pdf)")
                    download_links.append(f"[arXiv Page](https://arxiv.org/abs/{arxiv_id})")
                elif "arxiv.org/abs/" in paper.doi:
                    # 直接从URL中提取arXiv ID
                    arxiv_id = paper.doi.split("arxiv.org/abs/")[-1]
                    if "v" in arxiv_id:  # 移除版本号
                        arxiv_id = arxiv_id.split("v")[0]

                    download_links.append(f"[arXiv PDF](https://arxiv.org/pdf/{arxiv_id}.pdf)")
                    download_links.append(f"[arXiv Page](https://arxiv.org/abs/{arxiv_id})")
                else:
                    download_links.append(f"[DOI](https://doi.org/{paper.doi})")

            # 添加直接URL链接（如果存在且不同于前面的链接）
            if hasattr(paper, 'url') and paper.url:
                if not any(paper.url in link for link in download_links):
                    download_links.append(f"[Source]({paper.url})")

            # 构建下载链接字符串
            download_section = " | ".join(download_links) if download_links else "No direct download link available"

            # 构建来源信息
            source_info = []
            if hasattr(paper, 'venue_type') and paper.venue_type and paper.venue_type != 'preprint':
                source_info.append(f"Type: {paper.venue_type}")
            if hasattr(paper, 'venue_name') and paper.venue_name:
                source_info.append(f"Venue: {paper.venue_name}")

            # 添加IF指数和分区信息
            if hasattr(paper, 'if_factor') and paper.if_factor:
                source_info.append(f"IF: {paper.if_factor}")
            if hasattr(paper, 'cas_division') and paper.cas_division:
                source_info.append(f"中科院分区: {paper.cas_division}")
            if hasattr(paper, 'jcr_division') and paper.jcr_division:
                source_info.append(f"JCR分区: {paper.jcr_division}")

            if hasattr(paper, 'venue_info') and paper.venue_info:
                if paper.venue_info.get('journal_ref'):
                    source_info.append(f"Journal Reference: {paper.venue_info['journal_ref']}")
                if paper.venue_info.get('publisher'):
                    source_info.append(f"Publisher: {paper.venue_info['publisher']}")

            # 构建当前论文的格式化文本
            paper_text = (
                    f"{i}. **{paper.title}**\n" +
                    f"   Authors: {', '.join(authors)}\n" +
                    f"   Year: {paper.year}\n" +
                    f"   Citations: {paper.citations if paper.citations else 'N/A'}\n" +
                    (f"   Source: {'; '.join(source_info)}\n" if source_info else "") +
                    # 添加PubMed特有信息
                    (f"   MeSH Terms: {'; '.join(paper.mesh_terms)}\n" if hasattr(paper,
                                                                                  'mesh_terms') and paper.mesh_terms else "") +
                    f"   📥 PDF Downloads: {download_section}\n" +
                    f"   Abstract: {paper.abstract}\n"
            )

            formatted.append(paper_text)

        full_text = "\n".join(formatted)

        # 根据不同模型设置不同的token限制
        model_name = getattr(self, 'llm_kwargs', {}).get('llm_model', 'gpt-3.5-turbo')

        token_limit = model_info[model_name]['max_token'] * 3 // 4
        # 使用token限制控制长度
        return cut_from_end_to_satisfy_token_limit(full_text, limit=token_limit, reserve_token=0, llm_model=model_name)

    def _get_current_time(self) -> str:
        """获取当前时间信息"""
        now = datetime.now()
        return now.strftime("%Y年%m月%d日")

    def _generate_apology_prompt(self, criteria: SearchCriteria) -> str:
        """生成道歉提示"""
        return f"""很抱歉，我们未能找到与"{criteria.main_topic}"相关的有效文献。

可能的原因：
1. 搜索词过于具体或专业
2. 时间范围限制过严

建议解决方案：
   1. 尝试使用更通用的关键词
   2. 扩大搜索时间范围
   3. 使用同义词或相关术语
请根据以上建议调整后重试。"""

    def get_ranked_papers(self) -> str:
        """获取排序后的论文列表的格式化字符串"""
        return self._format_papers(self.ranked_papers) if self.ranked_papers else ""

    def _is_pubmed_paper(self, paper) -> bool:
        """判断是否为PubMed论文"""
        return (paper.url and 'pubmed.ncbi.nlm.nih.gov' in paper.url)
