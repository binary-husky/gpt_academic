from typing import List, Optional, Dict, Union
from datetime import datetime
import aiohttp
import asyncio
from crazy_functions.review_fns.data_sources.base_source import DataSource, PaperMetadata
import json
from tqdm import tqdm
import random

class AdsabsSource(DataSource):
    """ADS (Astrophysics Data System) API实现"""

    # 定义API密钥列表
    API_KEYS = [
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ]

    def __init__(self, api_key: str = None):
        """初始化

        Args:
            api_key: ADS API密钥，如果不提供则从预定义列表中随机选择
        """
        self.api_key = api_key or random.choice(self.API_KEYS)  # 随机选择一个API密钥
        self._initialize()

    def _initialize(self) -> None:
        """初始化基础URL和请求头"""
        self.base_url = "https://api.adsabs.harvard.edu/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, url: str, method: str = "GET", data: dict = None) -> Optional[dict]:
        """发送HTTP请求

        Args:
            url: 请求URL
            method: HTTP方法
            data: POST请求数据

        Returns:
            响应内容
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None

    def _parse_paper(self, doc: dict) -> PaperMetadata:
        """解析ADS文献数据

        Args:
            doc: ADS文献数据

        Returns:
            解析后的论文数据
        """
        try:
            return PaperMetadata(
                title=doc.get('title', [''])[0] if doc.get('title') else '',
                authors=doc.get('author', []),
                abstract=doc.get('abstract', ''),
                year=doc.get('year'),
                doi=doc.get('doi', [''])[0] if doc.get('doi') else None,
                url=f"https://ui.adsabs.harvard.edu/abs/{doc.get('bibcode')}/abstract" if doc.get('bibcode') else None,
                citations=doc.get('citation_count'),
                venue=doc.get('pub', ''),
                institutions=doc.get('aff', []),
                venue_type="journal",
                venue_name=doc.get('pub', ''),
                venue_info={
                    'volume': doc.get('volume'),
                    'issue': doc.get('issue'),
                    'pub_date': doc.get('pubdate', '')
                },
                source='adsabs'
            )
        except Exception as e:
            print(f"解析文章时发生错误: {str(e)}")
            return None

    async def search(
        self,
        query: str,
        limit: int = 100,
        sort_by: str = "relevance",
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            sort_by: 排序方式 ('relevance', 'date', 'citations')
            start_year: 起始年份

        Returns:
            论文列表
        """
        try:
            # 构建查询
            if start_year:
                query = f"{query} year:{start_year}-"

            # 设置排序
            sort_mapping = {
                'relevance': 'score desc',
                'date': 'date desc',
                'citations': 'citation_count desc'
            }
            sort = sort_mapping.get(sort_by, 'score desc')

            # 构建搜索请求
            search_url = f"{self.base_url}/search/query"
            params = {
                "q": query,
                "rows": limit,
                "sort": sort,
                "fl": "title,author,abstract,year,doi,bibcode,citation_count,pub,aff,volume,issue,pubdate"
            }

            response = await self._make_request(f"{search_url}?{self._build_query_string(params)}")
            if not response or 'response' not in response:
                return []

            # 解析结果
            papers = []
            for doc in response['response']['docs']:
                paper = self._parse_paper(doc)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    def _build_query_string(self, params: dict) -> str:
        """构建查询字符串"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    async def get_paper_details(self, bibcode: str) -> Optional[PaperMetadata]:
        """获取指定bibcode的论文详情"""
        search_url = f"{self.base_url}/search/query"
        params = {
            "q": f"identifier:{bibcode}",
            "fl": "title,author,abstract,year,doi,bibcode,citation_count,pub,aff,volume,issue,pubdate"
        }

        response = await self._make_request(f"{search_url}?{self._build_query_string(params)}")
        if response and 'response' in response and response['response']['docs']:
            return self._parse_paper(response['response']['docs'][0])
        return None

    async def get_related_papers(self, bibcode: str, limit: int = 100) -> List[PaperMetadata]:
        """获取相关论文"""
        url = f"{self.base_url}/search/query"
        params = {
            "q": f"citations(identifier:{bibcode}) OR references(identifier:{bibcode})",
            "rows": limit,
            "fl": "title,author,abstract,year,doi,bibcode,citation_count,pub,aff,volume,issue,pubdate"
        }

        response = await self._make_request(f"{url}?{self._build_query_string(params)}")
        if not response or 'response' not in response:
            return []

        papers = []
        for doc in response['response']['docs']:
            paper = self._parse_paper(doc)
            if paper:
                papers.append(paper)
        return papers

    async def search_by_author(
        self,
        author: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = f"author:\"{author}\""
        return await self.search(query, limit=limit, start_year=start_year)

    async def search_by_journal(
        self,
        journal: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按期刊搜索论文"""
        query = f"pub:\"{journal}\""
        return await self.search(query, limit=limit, start_year=start_year)

    async def get_latest_papers(
        self,
        days: int = 7,
        limit: int = 100
    ) -> List[PaperMetadata]:
        """获取最新论文"""
        query = f"entdate:[NOW-{days}DAYS TO NOW]"
        return await self.search(query, limit=limit, sort_by="date")

    async def get_citations(self, bibcode: str) -> List[PaperMetadata]:
        """获取引用该论文的文献"""
        url = f"{self.base_url}/search/query"
        params = {
            "q": f"citations(identifier:{bibcode})",
            "fl": "title,author,abstract,year,doi,bibcode,citation_count,pub,aff,volume,issue,pubdate"
        }

        response = await self._make_request(f"{url}?{self._build_query_string(params)}")
        if not response or 'response' not in response:
            return []

        papers = []
        for doc in response['response']['docs']:
            paper = self._parse_paper(doc)
            if paper:
                papers.append(paper)
        return papers

    async def get_references(self, bibcode: str) -> List[PaperMetadata]:
        """获取该论文引用的文献"""
        url = f"{self.base_url}/search/query"
        params = {
            "q": f"references(identifier:{bibcode})",
            "fl": "title,author,abstract,year,doi,bibcode,citation_count,pub,aff,volume,issue,pubdate"
        }

        response = await self._make_request(f"{url}?{self._build_query_string(params)}")
        if not response or 'response' not in response:
            return []

        papers = []
        for doc in response['response']['docs']:
            paper = self._parse_paper(doc)
            if paper:
                papers.append(paper)
        return papers

async def example_usage():
    """AdsabsSource使用示例"""
    ads = AdsabsSource()

    try:
        # 示例1：基本搜索
        print("\n=== 示例1：搜索黑洞相关论文 ===")
        papers = await ads.search("black hole", limit=3)
        for i, paper in enumerate(papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")

        # 其他示例...

    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # python -m crazy_functions.review_fns.data_sources.adsabs_source
    asyncio.run(example_usage())
