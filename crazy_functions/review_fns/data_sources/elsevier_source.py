from typing import List, Optional, Dict, Union
from datetime import datetime
import aiohttp
import asyncio
from crazy_functions.review_fns.data_sources.base_source import DataSource, PaperMetadata
import json
from tqdm import tqdm
import random

class ElsevierSource(DataSource):
    """Elsevier (Scopus) API实现"""

    # 定义API密钥列表
    API_KEYS = [
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ]

    def __init__(self, api_key: str = None):
        """初始化

        Args:
            api_key: Elsevier API密钥，如果不提供则从预定义列表中随机选择
        """
        self.api_key = api_key or random.choice(self.API_KEYS)
        self._initialize()

    def _initialize(self) -> None:
        """初始化基础URL和请求头"""
        self.base_url = "https://api.elsevier.com/content"
        self.headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            # 添加更多必要的头部信息
            "X-ELS-Insttoken": "",  # 如果有机构令牌
        }

    async def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """发送HTTP请求

        Args:
            url: 请求URL
            params: 查询参数

        Returns:
            JSON响应
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        # 添加更详细的错误信息
                        error_text = await response.text()
                        print(f"请求失败: {response.status}")
                        print(f"错误详情: {error_text}")
                        if response.status == 401:
                            print(f"使用的API密钥: {self.api_key}")
                            # 尝试切换到另一个API密钥
                            new_key = random.choice([k for k in self.API_KEYS if k != self.api_key])
                            print(f"尝试切换到新的API密钥: {new_key}")
                            self.api_key = new_key
                            self.headers["X-ELS-APIKey"] = new_key
                            # 重试请求
                            return await self._make_request(url, params)
                        return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None

    async def search(
        self,
        query: str,
        limit: int = 100,
        sort_by: str = "relevance",
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文"""
        try:
            params = {
                "query": query,
                "count": min(limit, 100),
                "view": "STANDARD",
                # 移除dc:description字段，因为它在STANDARD视图中不可用
                "field": "dc:title,dc:creator,prism:doi,prism:coverDate,citedby-count,prism:publicationName"
            }

            # 添加年份过滤
            if start_year:
                params["date"] = f"{start_year}-present"

            # 添加排序
            if sort_by == "date":
                params["sort"] = "-coverDate"
            elif sort_by == "cited":
                params["sort"] = "-citedby-count"

            # 发送搜索请求
            response = await self._make_request(
                f"{self.base_url}/search/scopus",
                params=params
            )

            if not response or "search-results" not in response:
                return []

            # 解析搜索结果
            entries = response["search-results"].get("entry", [])
            papers = [paper for paper in (self._parse_entry(entry) for entry in entries) if paper is not None]

            # 尝试为每篇论文获取摘要
            for paper in papers:
                if paper.doi:
                    paper.abstract = await self.fetch_abstract(paper.doi) or ""

            return papers

        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    def _parse_entry(self, entry: Dict) -> Optional[PaperMetadata]:
        """解析Scopus API返回的条目"""
        try:
            # 获取作者列表
            authors = []
            creator = entry.get("dc:creator")
            if creator:
                authors = [creator]

            # 获取发表年份
            year = None
            if "prism:coverDate" in entry:
                try:
                    year = int(entry["prism:coverDate"][:4])
                except:
                    pass

            # 简化venue信息
            venue_info = {
                'source_id': entry.get("source-id"),
                'issn': entry.get("prism:issn")
            }

            return PaperMetadata(
                title=entry.get("dc:title", ""),
                authors=authors,
                abstract=entry.get("dc:description", ""),  # 从响应中获取摘要
                year=year,
                doi=entry.get("prism:doi"),
                url=entry.get("prism:url"),
                citations=int(entry.get("citedby-count", 0)),
                venue=entry.get("prism:publicationName"),
                institutions=[],  # 移除机构信息
                venue_type="",
                venue_name=entry.get("prism:publicationName"),
                venue_info=venue_info
            )

        except Exception as e:
            print(f"解析条目时发生错误: {str(e)}")
            return None

    async def get_citations(self, doi: str, limit: int = 100) -> List[PaperMetadata]:
        """获取引用该论文的文献"""
        try:
            params = {
                "query": f"REF({doi})",
                "count": min(limit, 100),
                "view": "STANDARD"
            }

            response = await self._make_request(
                f"{self.base_url}/search/scopus",
                params=params
            )

            if not response or "search-results" not in response:
                return []

            entries = response["search-results"].get("entry", [])
            return [self._parse_entry(entry) for entry in entries]

        except Exception as e:
            print(f"获取引用文献时发生错误: {str(e)}")
            return []

    async def get_references(self, doi: str) -> List[PaperMetadata]:
        """获取该论文引用的文献"""
        try:
            response = await self._make_request(
                f"{self.base_url}/abstract/doi/{doi}/references",
                params={"view": "STANDARD"}
            )

            if not response or "references" not in response:
                return []

            references = response["references"].get("reference", [])
            papers = [paper for paper in (self._parse_reference(ref) for ref in references) if paper is not None]
            return papers

        except Exception as e:
            print(f"获取参考文献时发生错误: {str(e)}")
            return []

    def _parse_reference(self, ref: Dict) -> Optional[PaperMetadata]:
        """解析参考文献数据"""
        try:
            authors = []
            if "author-list" in ref:
                author_list = ref["author-list"].get("author", [])
                if isinstance(author_list, list):
                    authors = [f"{author.get('ce:given-name', '')} {author.get('ce:surname', '')}"
                             for author in author_list]
                else:
                    authors = [f"{author_list.get('ce:given-name', '')} {author_list.get('ce:surname', '')}"]

            year = None
            if "prism:coverDate" in ref:
                try:
                    year = int(ref["prism:coverDate"][:4])
                except:
                    pass

            return PaperMetadata(
                title=ref.get("ce:title", ""),
                authors=authors,
                abstract="",  # 参考文献通常不包含摘要
                year=year,
                doi=ref.get("prism:doi"),
                url=None,
                citations=None,
                venue=ref.get("prism:publicationName"),
                institutions=[],
                venue_type="unknown",
                venue_name=ref.get("prism:publicationName"),
                venue_info={}
            )

        except Exception as e:
            print(f"解析参考文献时发生错误: {str(e)}")
            return None

    async def search_by_author(
        self,
        author: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = f"AUTHOR-NAME({author})"
        return await self.search(query, limit=limit, start_year=start_year)

    async def search_by_affiliation(
        self,
        affiliation: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按机构搜索论文"""
        query = f"AF-ID({affiliation})"
        return await self.search(query, limit=limit, start_year=start_year)

    async def search_by_venue(
        self,
        venue: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按期刊/会议搜索论文"""
        query = f"SRCTITLE({venue})"
        return await self.search(query, limit=limit, start_year=start_year)

    async def test_api_access(self):
        """测试API访问权限"""
        print(f"\n测试API密钥: {self.api_key}")

        # 测试1: 基础搜索
        basic_params = {
            "query": "test",
            "count": 1,
            "view": "STANDARD"
        }
        print("\n1. 测试基础搜索...")
        response = await self._make_request(
            f"{self.base_url}/search/scopus",
            params=basic_params
        )
        if response:
            print("基础搜索成功")
            print("可用字段:", list(response.get("search-results", {}).get("entry", [{}])[0].keys()))

        # 测试2: 测试单篇文章访问
        print("\n2. 测试文章详情访问...")
        test_doi = "10.1016/j.artint.2021.103535"  # 一个示例DOI
        response = await self._make_request(
            f"{self.base_url}/abstract/doi/{test_doi}",
            params={"view": "STANDARD"}  # 改为STANDARD视图
        )
        if response:
            print("文章详情访问成功")
        else:
            print("文章详情访问失败")

    async def get_paper_details(self, paper_id: str) -> Optional[PaperMetadata]:
        """获取论文详细信息

        注意：当前API权限不支持获取详细信息，返回None

        Args:
            paper_id: 论文ID

        Returns:
            None，因为当前API权限不支持此功能
        """
        return None

    async def fetch_abstract(self, doi: str) -> Optional[str]:
        """获取论文摘要

        使用Scopus Abstract API获取论文摘要

        Args:
            doi: 论文的DOI

        Returns:
            摘要文本，如果获取失败则返回None
        """
        try:
            # 使用Abstract API而不是Search API
            response = await self._make_request(
                f"{self.base_url}/abstract/doi/{doi}",
                params={
                    "view": "FULL"  # 使用FULL视图
                }
            )

            if response and "abstracts-retrieval-response" in response:
                # 从coredata中获取摘要
                coredata = response["abstracts-retrieval-response"].get("coredata", {})
                return coredata.get("dc:description", "")

            return None

        except Exception as e:
            print(f"获取摘要时发生错误: {str(e)}")
            return None

async def example_usage():
    """ElsevierSource使用示例"""
    elsevier = ElsevierSource()

    try:
        # 首先测试API访问权限
        print("\n=== 测试API访问权限 ===")
        await elsevier.test_api_access()

        # 示例1：基本搜索
        print("\n=== 示例1：搜索机器学习相关论文 ===")
        papers = await elsevier.search("machine learning", limit=3)
        for i, paper in enumerate(papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"URL: {paper.url}")
            print(f"引用次数: {paper.citations}")
            print(f"期刊/会议: {paper.venue}")
            print("期刊信息:")
            for key, value in paper.venue_info.items():
                if value:  # 只打印非空值
                    print(f"  - {key}: {value}")

        # 示例2：获取引用信息
        if papers and papers[0].doi:
            print("\n=== 示例2：获取引用该论文的文献 ===")
            citations = await elsevier.get_citations(papers[0].doi, limit=3)
            for i, paper in enumerate(citations, 1):
                print(f"\n--- 引用论文 {i} ---")
                print(f"标题: {paper.title}")
                print(f"作者: {', '.join(paper.authors)}")
                print(f"发表年份: {paper.year}")
                print(f"DOI: {paper.doi}")
                print(f"引用次数: {paper.citations}")
                print(f"期刊/会议: {paper.venue}")

        # 示例3：获取参考文献
        if papers and papers[0].doi:
            print("\n=== 示例3：获取论文的参考文献 ===")
            references = await elsevier.get_references(papers[0].doi)
            for i, paper in enumerate(references[:3], 1):
                print(f"\n--- 参考文献 {i} ---")
                print(f"标题: {paper.title}")
                print(f"作者: {', '.join(paper.authors)}")
                print(f"发表年份: {paper.year}")
                print(f"DOI: {paper.doi}")
                print(f"期刊/会议: {paper.venue}")

        # 示例4：按作者搜索
        print("\n=== 示例4：按作者搜索 ===")
        author_papers = await elsevier.search_by_author("Hinton G", limit=3)
        for i, paper in enumerate(author_papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"引用次数: {paper.citations}")
            print(f"期刊/会议: {paper.venue}")

        # 示例5：按机构搜索
        print("\n=== 示例5：按机构搜索 ===")
        affiliation_papers = await elsevier.search_by_affiliation("60027950", limit=3)  # MIT的机构ID
        for i, paper in enumerate(affiliation_papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"引用次数: {paper.citations}")
            print(f"期刊/会议: {paper.venue}")

        # 示例6：获取论文摘要
        print("\n=== 示例6：获取论文摘要 ===")
        test_doi = "10.1016/j.artint.2021.103535"
        abstract = await elsevier.fetch_abstract(test_doi)
        if abstract:
            print(f"摘要: {abstract[:200]}...")  # 只显示前200个字符
        else:
            print("无法获取摘要")

        # 在搜索结果中显示摘要
        print("\n=== 示例7：搜索结果中的摘要 ===")
        papers = await elsevier.search("machine learning", limit=1)
        for paper in papers:
            print(f"标题: {paper.title}")
            print(f"摘要: {paper.abstract[:200]}..." if paper.abstract else "摘要: 无")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(example_usage())
