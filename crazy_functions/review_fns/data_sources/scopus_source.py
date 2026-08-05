from typing import List, Optional, Dict, Union
from datetime import datetime
import aiohttp
import random
from .base_source import DataSource, PaperMetadata
from tqdm import tqdm

class ScopusSource(DataSource):
    """Scopus API实现"""

    # 定义API密钥列表
    API_KEYS = [
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ]

    def __init__(self, api_key: str = None):
        """初始化

        Args:
            api_key: Scopus API密钥，如果不提供则从预定义列表中随机选择
        """
        self.api_key = api_key or random.choice(self.API_KEYS)
        self._initialize()

    def _initialize(self) -> None:
        """初始化基础URL和请求头"""
        self.base_url = "https://api.elsevier.com/content"
        self.headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }

    async def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """发送HTTP请求

        Args:
            url: 请求URL
            params: 查询参数

        Returns:
            响应JSON数据
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"请求失败: {response.status}")
                        return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None

    def _parse_paper_data(self, data: Dict) -> PaperMetadata:
        """解析Scopus API返回的数据

        Args:
            data: Scopus API返回的论文数据

        Returns:
            解析后的论文元数据
        """
        try:
            # 提取基本信息
            title = data.get("dc:title", "")

            # 提取作者信息
            authors = []
            if "author" in data:
                if isinstance(data["author"], list):
                    for author in data["author"]:
                        if "given-name" in author and "surname" in author:
                            authors.append(f"{author['given-name']} {author['surname']}")
                        elif "indexed-name" in author:
                            authors.append(author["indexed-name"])
                elif isinstance(data["author"], dict):
                    if "given-name" in data["author"] and "surname" in data["author"]:
                        authors.append(f"{data['author']['given-name']} {data['author']['surname']}")
                    elif "indexed-name" in data["author"]:
                        authors.append(data["author"]["indexed-name"])

            # 提取摘要
            abstract = data.get("dc:description", "")

            # 提取年份
            year = None
            if "prism:coverDate" in data:
                try:
                    year = int(data["prism:coverDate"][:4])
                except:
                    pass

            # 提取DOI
            doi = data.get("prism:doi")

            # 提取引用次数
            citations = data.get("citedby-count")
            if citations:
                try:
                    citations = int(citations)
                except:
                    citations = None

            # 提取期刊信息
            venue = data.get("prism:publicationName")

            # 提取机构信息
            institutions = []
            if "affiliation" in data:
                if isinstance(data["affiliation"], list):
                    for aff in data["affiliation"]:
                        if "affilname" in aff:
                            institutions.append(aff["affilname"])
                elif isinstance(data["affiliation"], dict):
                    if "affilname" in data["affiliation"]:
                        institutions.append(data["affiliation"]["affilname"])

            # 构建venue信息
            venue_info = {
                "issn": data.get("prism:issn"),
                "eissn": data.get("prism:eIssn"),
                "volume": data.get("prism:volume"),
                "issue": data.get("prism:issueIdentifier"),
                "page_range": data.get("prism:pageRange"),
                "article_number": data.get("article-number"),
                "publication_date": data.get("prism:coverDate")
            }

            return PaperMetadata(
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                doi=doi,
                url=data.get("link", [{}])[0].get("@href"),
                citations=citations,
                venue=venue,
                institutions=institutions,
                venue_type="journal",
                venue_name=venue,
                venue_info=venue_info
            )

        except Exception as e:
            print(f"解析论文数据时发生错误: {str(e)}")
            return None

    async def search(
        self,
        query: str,
        limit: int = 100,
        sort_by: str = None,
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
            # 构建查询参数
            params = {
                "query": query,
                "count": min(limit, 100),  # Scopus API单次请求限制
                "start": 0
            }

            # 添加年份过滤
            if start_year:
                params["date"] = f"{start_year}-present"

            # 添加排序
            if sort_by:
                sort_map = {
                    "relevance": "-score",
                    "date": "-coverDate",
                    "citations": "-citedby-count"
                }
                if sort_by in sort_map:
                    params["sort"] = sort_map[sort_by]

            # 发送请求
            url = f"{self.base_url}/search/scopus"
            response = await self._make_request(url, params)

            if not response or "search-results" not in response:
                return []

            # 解析结果
            results = response["search-results"].get("entry", [])
            papers = []

            for result in results:
                paper = self._parse_paper_data(result)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    async def get_paper_details(self, paper_id: str) -> Optional[PaperMetadata]:
        """获取论文详情

        Args:
            paper_id: Scopus ID或DOI

        Returns:
            论文详情
        """
        try:
            # 判断是否为DOI
            if "/" in paper_id:
                url = f"{self.base_url}/article/doi/{paper_id}"
            else:
                url = f"{self.base_url}/abstract/scopus_id/{paper_id}"

            response = await self._make_request(url)

            if not response or "abstracts-retrieval-response" not in response:
                return None

            data = response["abstracts-retrieval-response"]
            return self._parse_paper_data(data)

        except Exception as e:
            print(f"获取论文详情时发生错误: {str(e)}")
            return None

    async def get_citations(self, paper_id: str) -> List[PaperMetadata]:
        """获取引用该论文的文献

        Args:
            paper_id: Scopus ID

        Returns:
            引用论文列表
        """
        try:
            url = f"{self.base_url}/abstract/citations/{paper_id}"
            response = await self._make_request(url)

            if not response or "citing-papers" not in response:
                return []

            results = response["citing-papers"].get("papers", [])
            papers = []

            for result in results:
                paper = self._parse_paper_data(result)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"获取引用信息时发生错误: {str(e)}")
            return []

    async def get_references(self, paper_id: str) -> List[PaperMetadata]:
        """获取该论文引用的文献

        Args:
            paper_id: Scopus ID

        Returns:
            参考文献列表
        """
        try:
            url = f"{self.base_url}/abstract/references/{paper_id}"
            response = await self._make_request(url)

            if not response or "references" not in response:
                return []

            results = response["references"].get("reference", [])
            papers = []

            for result in results:
                paper = self._parse_paper_data(result)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"获取参考文献时发生错误: {str(e)}")
            return []

    async def search_by_author(
        self,
        author: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = f"AUTHOR-NAME({author})"
        if start_year:
            query += f" AND PUBYEAR > {start_year}"
        return await self.search(query, limit=limit)

    async def search_by_journal(
        self,
        journal: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按期刊搜索论文"""
        query = f"SRCTITLE({journal})"
        if start_year:
            query += f" AND PUBYEAR > {start_year}"
        return await self.search(query, limit=limit)

    async def get_latest_papers(
        self,
        days: int = 7,
        limit: int = 100
    ) -> List[PaperMetadata]:
        """获取最新论文"""
        query = f"LOAD-DATE > NOW() - {days}d"
        return await self.search(query, limit=limit, sort_by="date")

async def example_usage():
    """ScopusSource使用示例"""
    scopus = ScopusSource()

    try:
        # 示例1：基本搜索
        print("\n=== 示例1：搜索机器学习相关论文 ===")
        papers = await scopus.search("machine learning", limit=3)
        print(f"\n找到 {len(papers)} 篇相关论文:")
        for i, paper in enumerate(papers, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"发表期刊: {paper.venue}")
            print(f"引用次数: {paper.citations}")
            print(f"DOI: {paper.doi}")
            if paper.abstract:
                print(f"摘要:\n{paper.abstract}")
            print("-" * 80)

        # 示例2：按作者搜索
        print("\n=== 示例2：搜索特定作者的论文 ===")
        author_papers = await scopus.search_by_author("Hinton G.", limit=3)
        print(f"\n找到 {len(author_papers)} 篇 Hinton 的论文:")
        for i, paper in enumerate(author_papers, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"发表期刊: {paper.venue}")
            print(f"引用次数: {paper.citations}")
            print(f"DOI: {paper.doi}")
            if paper.abstract:
                print(f"摘要:\n{paper.abstract}")
            print("-" * 80)

        # 示例3：根据关键词搜索相关论文
        print("\n=== 示例3：搜索人工智能相关论文 ===")
        keywords = "artificial intelligence AND deep learning"
        papers = await scopus.search(
            query=keywords,
            limit=5,
            sort_by="citations",  # 按引用次数排序
            start_year=2020  # 只搜索2020年之后的论文
        )

        print(f"\n找到 {len(papers)} 篇相关论文:")
        for i, paper in enumerate(papers, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"发表期刊: {paper.venue}")
            print(f"引用次数: {paper.citations}")
            print(f"DOI: {paper.doi}")
            if paper.abstract:
                print(f"摘要:\n{paper.abstract}")
            print("-" * 80)

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
