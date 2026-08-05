from typing import List, Optional
from datetime import datetime
from crazy_functions.review_fns.data_sources.base_source import DataSource, PaperMetadata
import random

class SemanticScholarSource(DataSource):
    """Semantic Scholar API实现,使用官方Python包"""

    def __init__(self, api_key: str = None):
        """初始化

        Args:
            api_key: Semantic Scholar API密钥(可选)
        """
        self.api_key = api_key
        self._initialize()  # 调用初始化方法

    def _initialize(self) -> None:
        """初始化API客户端"""
        if not self.api_key:
            # 默认API密钥列表
            default_api_keys = [
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            ]
            self.api_key = random.choice(default_api_keys)

        self.client = None  # 延迟初始化
        self.fields = [
            "title",
            "authors",
            "abstract",
            "year",
            "externalIds",
            "citationCount",
            "venue",
            "openAccessPdf",
            "publicationVenue"
        ]

    async def _ensure_client(self):
        """确保客户端已初始化"""
        if self.client is None:
            from semanticscholar import AsyncSemanticScholar
            self.client = AsyncSemanticScholar(api_key=self.api_key)

    async def search(
        self,
        query: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文"""
        try:
            await self._ensure_client()

            # 如果指定了起始年份，添加到查询中
            if start_year:
                query = f"{query} year>={start_year}"

            # 直接使用 search_paper 的结果
            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/paper/search",
                f"query={query}&limit={min(limit, 100)}&fields={','.join(self.fields)}",
                self.client.auth_header
            )
            papers = response.get('data', [])
            return [self._parse_paper_data(paper) for paper in papers]
        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    async def get_paper_details(self, doi: str) -> Optional[PaperMetadata]:
        """获取指定DOI的论文详情"""
        try:
            await self._ensure_client()
            paper = await self.client.get_paper(f"DOI:{doi}", fields=self.fields)
            return self._parse_paper_data(paper)
        except Exception as e:
            print(f"获取论文详情时发生错误: {str(e)}")
            return None

    async def get_citations(
        self,
        doi: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """获取引用指定DOI论文的文献列表"""
        try:
            await self._ensure_client()
            # 构建查询参数
            fields_param = f"fields={','.join(self.fields)}"
            limit_param = f"limit={limit}"
            year_param = f"year>={start_year}" if start_year else ""
            params = "&".join(filter(None, [fields_param, limit_param, year_param]))

            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/paper/DOI:{doi}/citations",
                params,
                self.client.auth_header
            )
            citations = response.get('data', [])
            return [self._parse_paper_data(citation.get('citingPaper', {})) for citation in citations]
        except Exception as e:
            print(f"获取引用列表时发生错误: {str(e)}")
            return []

    async def get_references(
        self,
        doi: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """获取指定DOI论文的参考文献列表"""
        try:
            await self._ensure_client()
            # 构建查询参数
            fields_param = f"fields={','.join(self.fields)}"
            limit_param = f"limit={limit}"
            year_param = f"year>={start_year}" if start_year else ""
            params = "&".join(filter(None, [fields_param, limit_param, year_param]))

            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/paper/DOI:{doi}/references",
                params,
                self.client.auth_header
            )
            references = response.get('data', [])
            return [self._parse_paper_data(reference.get('citedPaper', {})) for reference in references]
        except Exception as e:
            print(f"获取参考文献列表时发生错误: {str(e)}")
            return []

    async def get_recommended_papers(self, doi: str, limit: int = 100) -> List[PaperMetadata]:
        """获取论文推荐

        根据一篇论文获取相关的推荐论文

        Args:
            doi: 论文的DOI
            limit: 返回结果数量限制，最大500

        Returns:
            推荐论文列表
        """
        try:
            await self._ensure_client()
            papers = await self.client.get_recommended_papers(
                f"DOI:{doi}",
                fields=self.fields,
                limit=min(limit, 500)
            )
            return [self._parse_paper_data(paper) for paper in papers]
        except Exception as e:
            print(f"获取论文推荐时发生错误: {str(e)}")
            return []

    async def get_recommended_papers_from_lists(
        self,
        positive_dois: List[str],
        negative_dois: List[str] = None,
        limit: int = 100
    ) -> List[PaperMetadata]:
        """基于正负例论文列表获取推荐

        Args:
            positive_dois: 正例论文DOI列表（想要获取类似的论文）
            negative_dois: 负例论文DOI列表（不想要类似的论文）
            limit: 返回结果数量限制，最大500

        Returns:
            推荐论文列表
        """
        try:
            await self._ensure_client()
            positive_ids = [f"DOI:{doi}" for doi in positive_dois]
            negative_ids = [f"DOI:{doi}" for doi in negative_dois] if negative_dois else None

            papers = await self.client.get_recommended_papers_from_lists(
                positive_paper_ids=positive_ids,
                negative_paper_ids=negative_ids,
                fields=self.fields,
                limit=min(limit, 500)
            )
            return [self._parse_paper_data(paper) for paper in papers]
        except Exception as e:
            print(f"获取论文推荐列表时发生错误: {str(e)}")
            return []

    async def search_author(self, query: str, limit: int = 100) -> List[dict]:
        """搜索作者"""
        try:
            await self._ensure_client()
            # 直接使用 API 请求而不是 search_author 方法
            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/author/search",
                f"query={query}&fields=name,paperCount,citationCount&limit={min(limit, 1000)}",
                self.client.auth_header
            )
            authors = response.get('data', [])
            return [
                {
                    'author_id': author.get('authorId'),
                    'name': author.get('name'),
                    'paper_count': author.get('paperCount'),
                    'citation_count': author.get('citationCount'),
                }
                for author in authors
            ]
        except Exception as e:
            print(f"搜索作者时发生错误: {str(e)}")
            return []

    async def get_author_details(self, author_id: str) -> Optional[dict]:
        """获取作者详细信息"""
        try:
            await self._ensure_client()
            # 直接使用 API 请求
            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/author/{author_id}",
                "fields=name,paperCount,citationCount,hIndex",
                self.client.auth_header
            )
            return {
                'author_id': response.get('authorId'),
                'name': response.get('name'),
                'paper_count': response.get('paperCount'),
                'citation_count': response.get('citationCount'),
                'h_index': response.get('hIndex'),
            }
        except Exception as e:
            print(f"获取作者详情时发生错误: {str(e)}")
            return None

    async def get_author_papers(self, author_id: str, limit: int = 100) -> List[PaperMetadata]:
        """获取作者的论文列表"""
        try:
            await self._ensure_client()
            # 直接使用 API 请求
            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/author/{author_id}/papers",
                f"fields={','.join(self.fields)}&limit={min(limit, 1000)}",
                self.client.auth_header
            )
            papers = response.get('data', [])
            return [self._parse_paper_data(paper) for paper in papers]
        except Exception as e:
            print(f"获取作者论文列表时发生错误: {str(e)}")
            return []

    async def get_paper_autocomplete(self, query: str) -> List[dict]:
        """论文标题自动补全"""
        try:
            await self._ensure_client()
            # 直接使用 API 请求
            response = await self.client._requester.get_data_async(
                f"{self.client.api_url}{self.client.BASE_PATH_GRAPH}/paper/autocomplete",
                f"query={query}",
                self.client.auth_header
            )
            suggestions = response.get('matches', [])
            return [
                {
                    'title': suggestion.get('title'),
                    'paper_id': suggestion.get('paperId'),
                    'year': suggestion.get('year'),
                    'venue': suggestion.get('venue'),
                }
                for suggestion in suggestions
            ]
        except Exception as e:
            print(f"获取标题自动补全时发生错误: {str(e)}")
            return []

    def _parse_paper_data(self, paper) -> PaperMetadata:
        """解析论文数据"""
        # 获取DOI
        doi = None
        external_ids = paper.get('externalIds', {}) if isinstance(paper, dict) else paper.externalIds
        if external_ids:
            if isinstance(external_ids, dict):
                doi = external_ids.get('DOI')
                if not doi and 'ArXiv' in external_ids:
                    doi = f"10.48550/arXiv.{external_ids['ArXiv']}"
            else:
                doi = external_ids.DOI if hasattr(external_ids, 'DOI') else None
                if not doi and hasattr(external_ids, 'ArXiv'):
                    doi = f"10.48550/arXiv.{external_ids.ArXiv}"

        # 获取PDF URL
        pdf_url = None
        pdf_info = paper.get('openAccessPdf', {}) if isinstance(paper, dict) else paper.openAccessPdf
        if pdf_info:
            pdf_url = pdf_info.get('url') if isinstance(pdf_info, dict) else pdf_info.url

        # 获取发表场所详细信息
        venue_type = None
        venue_name = None
        venue_info = {}

        venue = paper.get('publicationVenue', {}) if isinstance(paper, dict) else paper.publicationVenue
        if venue:
            if isinstance(venue, dict):
                venue_name = venue.get('name')
                venue_type = venue.get('type')
                # 提取更多venue信息
                venue_info = {
                    'issn': venue.get('issn'),
                    'publisher': venue.get('publisher'),
                    'url': venue.get('url'),
                    'alternate_names': venue.get('alternate_names', [])
                }
            else:
                venue_name = venue.name if hasattr(venue, 'name') else None
                venue_type = venue.type if hasattr(venue, 'type') else None
                venue_info = {
                    'issn': getattr(venue, 'issn', None),
                    'publisher': getattr(venue, 'publisher', None),
                    'url': getattr(venue, 'url', None),
                    'alternate_names': getattr(venue, 'alternate_names', [])
                }

        # 获取标题
        title = paper.get('title', '') if isinstance(paper, dict) else getattr(paper, 'title', '')

        # 获取作者
        authors = paper.get('authors', []) if isinstance(paper, dict) else getattr(paper, 'authors', [])
        author_names = []
        for author in authors:
            if isinstance(author, dict):
                author_names.append(author.get('name', ''))
            else:
                author_names.append(author.name if hasattr(author, 'name') else str(author))

        # 获取摘要
        abstract = paper.get('abstract', '') if isinstance(paper, dict) else getattr(paper, 'abstract', '')

        # 获取年份
        year = paper.get('year') if isinstance(paper, dict) else getattr(paper, 'year', None)

        # 获取引用次数
        citations = paper.get('citationCount') if isinstance(paper, dict) else getattr(paper, 'citationCount', None)

        return PaperMetadata(
            title=title,
            authors=author_names,
            abstract=abstract,
            year=year,
            doi=doi,
            url=pdf_url or (f"https://doi.org/{doi}" if doi else None),
            citations=citations,
            venue=venue_name,
            institutions=[],
            venue_type=venue_type,
            venue_name=venue_name,
            venue_info=venue_info,
            source='semantic'  # 添加来源标记
        )

async def example_usage():
    """SemanticScholarSource使用示例"""
    semantic = SemanticScholarSource()

    try:
        # 示例1：使用DOI直接获取论文
        print("\n=== 示例1：通过DOI获取论文 ===")
        doi = "10.18653/v1/N19-1423"  # BERT论文
        print(f"获取DOI为 {doi} 的论文信息...")

        paper = await semantic.get_paper_details(doi)
        if paper:
            print("\n--- 论文信息 ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"URL: {paper.url}")
            if paper.abstract:
                print(f"\n摘要:")
                print(paper.abstract)
            print(f"\n引用次数: {paper.citations}")
            print(f"发表venue: {paper.venue}")

        # 示例2：搜索论文
        print("\n=== 示例2：搜索论文 ===")
        query = "BERT pre-training"
        print(f"搜索关键词 '{query}' 相关的论文...")
        papers = await semantic.search(query=query, limit=3)

        for i, paper in enumerate(papers, 1):
            print(f"\n--- 搜索结果 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            if paper.abstract:
                print(f"\n摘要:")
                print(paper.abstract)
            print(f"\nDOI: {paper.doi}")
            print(f"引用次数: {paper.citations}")

        # 示例3：获取论文推荐
        print("\n=== 示例3：获取论文推荐 ===")
        print(f"获取与论文 {doi} 相关的推荐论文...")
        recommendations = await semantic.get_recommended_papers(doi, limit=3)
        for i, paper in enumerate(recommendations, 1):
            print(f"\n--- 推荐论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")

        # 示例4：基于多篇论文的推荐
        print("\n=== 示例4：基于多篇论文的推荐 ===")
        positive_dois = ["10.18653/v1/N19-1423", "10.18653/v1/P19-1285"]
        print(f"基于 {len(positive_dois)} 篇论文获取推荐...")
        multi_recommendations = await semantic.get_recommended_papers_from_lists(
            positive_dois=positive_dois,
            limit=3
        )
        for i, paper in enumerate(multi_recommendations, 1):
            print(f"\n--- 推荐论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")

        # 示例5：搜索作者
        print("\n=== 示例5：搜索作者 ===")
        author_query = "Yann LeCun"
        print(f"搜索作者: '{author_query}'")
        authors = await semantic.search_author(author_query, limit=3)
        for i, author in enumerate(authors, 1):
            print(f"\n--- 作者 {i} ---")
            print(f"姓名: {author['name']}")
            print(f"论文数量: {author['paper_count']}")
            print(f"总引用次数: {author['citation_count']}")

        # 示例6：获取作者详情
        print("\n=== 示例6：获取作者详情 ===")
        if authors:  # 使用第一个搜索结果的作者ID
            author_id = authors[0]['author_id']
            print(f"获取作者ID {author_id} 的详细信息...")
            author_details = await semantic.get_author_details(author_id)
            if author_details:
                print(f"姓名: {author_details['name']}")
                print(f"H指数: {author_details['h_index']}")
                print(f"总引用次数: {author_details['citation_count']}")
                print(f"发表论文数: {author_details['paper_count']}")

        # 示例7：获取作者论文
        print("\n=== 示例7：获取作者论文 ===")
        if authors:  # 使用第一个搜索结果的作者ID
            author_id = authors[0]['author_id']
            print(f"获取作者 {authors[0]['name']} 的论文列表...")
            author_papers = await semantic.get_author_papers(author_id, limit=3)
            for i, paper in enumerate(author_papers, 1):
                print(f"\n--- 论文 {i} ---")
                print(f"标题: {paper.title}")
                print(f"发表年份: {paper.year}")
                print(f"引用次数: {paper.citations}")

        # 示例8：论文标题自动补全
        print("\n=== 示例8：论文标题自动补全 ===")
        title_query = "Attention is all"
        print(f"搜索标题: '{title_query}'")
        suggestions = await semantic.get_paper_autocomplete(title_query)
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"\n--- 建议 {i} ---")
            print(f"标题: {suggestion['title']}")
            print(f"发表年份: {suggestion['year']}")
            print(f"发表venue: {suggestion['venue']}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
