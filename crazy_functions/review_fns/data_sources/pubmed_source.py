from typing import List, Optional, Dict, Union
from datetime import datetime
import aiohttp
import asyncio
from crazy_functions.review_fns.data_sources.base_source import DataSource, PaperMetadata
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json
from tqdm import tqdm
import random

class PubMedSource(DataSource):
    """PubMed API实现"""

    # 定义API密钥列表
    API_KEYS = [
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ]

    def __init__(self, api_key: str = None):
        """初始化

        Args:
            api_key: PubMed API密钥，如果不提供则从预定义列表中随机选择
        """
        self.api_key = api_key or random.choice(self.API_KEYS)  # 随机选择一个API密钥
        self._initialize()

    def _initialize(self) -> None:
        """初始化基础URL和请求头"""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.headers = {
            "User-Agent": "Mozilla/5.0 PubMedDataSource/1.0",
            "Accept": "application/json"
        }

    async def _make_request(self, url: str) -> Optional[str]:
        """发送HTTP请求

        Args:
            url: 请求URL

        Returns:
            响应内容
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"请求失败: {response.status}")
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
            # 添加年份过滤
            if start_year:
                query = f"{query} AND {start_year}:3000[dp]"

            # 构建搜索URL
            search_url = (
                f"{self.base_url}/esearch.fcgi?"
                f"db=pubmed&term={quote(query)}&retmax={limit}"
                f"&usehistory=y&api_key={self.api_key}"
            )

            if sort_by == "date":
                search_url += "&sort=date"

            # 获取搜索结果
            response = await self._make_request(search_url)
            if not response:
                return []

            # 解析XML响应
            root = ET.fromstring(response)
            id_list = root.findall(".//Id")
            pmids = [id_elem.text for id_elem in id_list]

            if not pmids:
                return []

            # 批量获取论文详情
            papers = []
            batch_size = 50
            for i in range(0, len(pmids), batch_size):
                batch = pmids[i:i + batch_size]
                batch_papers = await self._fetch_papers_batch(batch)
                papers.extend(batch_papers)

            return papers

        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    async def _fetch_papers_batch(self, pmids: List[str]) -> List[PaperMetadata]:
        """批量获取论文详情

        Args:
            pmids: PubMed ID列表

        Returns:
            论文详情列表
        """
        try:
            # 构建批量获取URL
            fetch_url = (
                f"{self.base_url}/efetch.fcgi?"
                f"db=pubmed&id={','.join(pmids)}"
                f"&retmode=xml&api_key={self.api_key}"
            )

            response = await self._make_request(fetch_url)
            if not response:
                return []

            # 解析XML响应
            root = ET.fromstring(response)
            articles = root.findall(".//PubmedArticle")

            return [self._parse_article(article) for article in articles]

        except Exception as e:
            print(f"获取论文批次时发生错误: {str(e)}")
            return []

    def _parse_article(self, article: ET.Element) -> PaperMetadata:
        """解析PubMed文章XML

        Args:
            article: XML元素

        Returns:
            解析后的论文数据
        """
        try:
            # 提取基本信息
            pmid = article.find(".//PMID").text
            article_meta = article.find(".//Article")

            # 获取标题
            title = article_meta.find(".//ArticleTitle")
            title = title.text if title is not None else ""

            # 获取作者列表
            authors = []
            author_list = article_meta.findall(".//Author")
            for author in author_list:
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                if last_name is not None and fore_name is not None:
                    authors.append(f"{fore_name.text} {last_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)

            # 获取摘要
            abstract = article_meta.find(".//Abstract/AbstractText")
            abstract = abstract.text if abstract is not None else ""

            # 获取发表年份
            pub_date = article_meta.find(".//PubDate/Year")
            year = int(pub_date.text) if pub_date is not None else None

            # 获取DOI
            doi = article.find(".//ELocationID[@EIdType='doi']")
            doi = doi.text if doi is not None else None

            # 获取期刊信息
            journal = article_meta.find(".//Journal")
            if journal is not None:
                journal_title = journal.find(".//Title")
                venue = journal_title.text if journal_title is not None else None

                # 获取期刊详细信息
                venue_info = {
                    'issn': journal.findtext(".//ISSN"),
                    'volume': journal.findtext(".//Volume"),
                    'issue': journal.findtext(".//Issue"),
                    'pub_date': journal.findtext(".//PubDate/MedlineDate") or
                               f"{journal.findtext('.//PubDate/Year', '')}-{journal.findtext('.//PubDate/Month', '')}"
                }
            else:
                venue = None
                venue_info = {}

            # 获取机构信息
            institutions = []
            affiliations = article_meta.findall(".//Affiliation")
            for affiliation in affiliations:
                if affiliation is not None and affiliation.text:
                    institutions.append(affiliation.text)

            return PaperMetadata(
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                citations=None,  # PubMed API不直接提供引用数据
                venue=venue,
                institutions=institutions,
                venue_type="journal",
                venue_name=venue,
                venue_info=venue_info,
                source='pubmed'  # 添加来源标记
            )

        except Exception as e:
            print(f"解析文章时发生错误: {str(e)}")
            return None

    async def get_paper_details(self, pmid: str) -> Optional[PaperMetadata]:
        """获取指定PMID的论文详情"""
        papers = await self._fetch_papers_batch([pmid])
        return papers[0] if papers else None

    async def get_related_papers(self, pmid: str, limit: int = 100) -> List[PaperMetadata]:
        """获取相关论文

        使用PubMed的相关文章功能

        Args:
            pmid: PubMed ID
            limit: 返回结果数量限制

        Returns:
            相关论文列表
        """
        try:
            # 构建相关文章URL
            link_url = (
                f"{self.base_url}/elink.fcgi?"
                f"db=pubmed&id={pmid}&cmd=neighbor&api_key={self.api_key}"
            )

            response = await self._make_request(link_url)
            if not response:
                return []

            # 解析XML响应
            root = ET.fromstring(response)
            related_ids = root.findall(".//Link/Id")
            pmids = [id_elem.text for id_elem in related_ids][:limit]

            if not pmids:
                return []

            # 获取相关论文详情
            return await self._fetch_papers_batch(pmids)

        except Exception as e:
            print(f"获取相关论文时发生错误: {str(e)}")
            return []

    async def search_by_author(
        self,
        author: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = f"{author}[Author]"
        if start_year:
            query += f" AND {start_year}:3000[dp]"
        return await self.search(query, limit=limit)

    async def search_by_journal(
        self,
        journal: str,
        limit: int = 100,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按期刊搜索论文"""
        query = f"{journal}[Journal]"
        if start_year:
            query += f" AND {start_year}:3000[dp]"
        return await self.search(query, limit=limit)

    async def get_latest_papers(
        self,
        days: int = 7,
        limit: int = 100
    ) -> List[PaperMetadata]:
        """获取最新论文

        Args:
            days: 最近几天的论文
            limit: 返回结果数量限制

        Returns:
            最新论文列表
        """
        query = f"last {days} days[dp]"
        return await self.search(query, limit=limit, sort_by="date")

    async def get_citations(self, paper_id: str) -> List[PaperMetadata]:
        """获取引用该论文的文献

        注意：PubMed API本身不提供引用数据，此方法将返回空列表
        未来可以考虑集成其他数据源(如CrossRef)来获取引用信息

        Args:
            paper_id: PubMed ID

        Returns:
            空列表，因为PubMed不提供引用数据
        """
        return []

    async def get_references(self, paper_id: str) -> List[PaperMetadata]:
        """获取该论文引用的文献

        从PubMed文章的参考文献列表获取引用的文献

        Args:
            paper_id: PubMed ID

        Returns:
            引用的文献列表
        """
        try:
            # 构建获取参考文献的URL
            refs_url = (
                f"{self.base_url}/elink.fcgi?"
                f"dbfrom=pubmed&db=pubmed&id={paper_id}"
                f"&cmd=neighbor_history&linkname=pubmed_pubmed_refs"
                f"&api_key={self.api_key}"
            )

            response = await self._make_request(refs_url)
            if not response:
                return []

            # 解析XML响应
            root = ET.fromstring(response)
            ref_ids = root.findall(".//Link/Id")
            pmids = [id_elem.text for id_elem in ref_ids]

            if not pmids:
                return []

            # 获取参考文献详情
            return await self._fetch_papers_batch(pmids)

        except Exception as e:
            print(f"获取参考文献时发生错误: {str(e)}")
            return []

async def example_usage():
    """PubMedSource使用示例"""
    pubmed = PubMedSource()

    try:
        # 示例1：基本搜索
        print("\n=== 示例1：搜索COVID-19相关论文 ===")
        papers = await pubmed.search("COVID-19", limit=3)
        for i, paper in enumerate(papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            if paper.abstract:
                print(f"摘要: {paper.abstract[:200]}...")

        # 示例2：获取论文详情
        if papers:
            print("\n=== 示例2：获取论文详情 ===")
            paper_id = papers[0].url.split("/")[-2]
            paper = await pubmed.get_paper_details(paper_id)
            if paper:
                print(f"标题: {paper.title}")
                print(f"期刊: {paper.venue}")
                print(f"机构: {', '.join(paper.institutions)}")

        # 示例3：获取相关论文
        if papers:
            print("\n=== 示例3：获取相关论文 ===")
            related = await pubmed.get_related_papers(paper_id, limit=3)
            for i, paper in enumerate(related, 1):
                print(f"\n--- 相关论文 {i} ---")
                print(f"标题: {paper.title}")
                print(f"作者: {', '.join(paper.authors)}")

        # 示例4：按作者搜索
        print("\n=== 示例4：按作者搜索 ===")
        author_papers = await pubmed.search_by_author("Fauci AS", limit=3)
        for i, paper in enumerate(author_papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"发表年份: {paper.year}")

        # 示例5：按期刊搜索
        print("\n=== 示例5：按期刊搜索 ===")
        journal_papers = await pubmed.search_by_journal("Nature", limit=3)
        for i, paper in enumerate(journal_papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"发表年份: {paper.year}")

        # 示例6：获取最新论文
        print("\n=== 示例6：获取最新论文 ===")
        latest = await pubmed.get_latest_papers(days=7, limit=3)
        for i, paper in enumerate(latest, 1):
            print(f"\n--- 最新论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"发表日期: {paper.venue_info.get('pub_date')}")

        # 示例7：获取论文的参考文献
        if papers:
            print("\n=== 示例7：获取论文的参考文献 ===")
            paper_id = papers[0].url.split("/")[-2]
            references = await pubmed.get_references(paper_id)
            for i, paper in enumerate(references[:3], 1):
                print(f"\n--- 参考文献 {i} ---")
                print(f"标题: {paper.title}")
                print(f"作者: {', '.join(paper.authors)}")
                print(f"发表年份: {paper.year}")

        # 示例8：尝试获取引用信息（将返回空列表）
        if papers:
            print("\n=== 示例8：获取论文的引用信息 ===")
            paper_id = papers[0].url.split("/")[-2]
            citations = await pubmed.get_citations(paper_id)
            print(f"引用数据：{len(citations)} (PubMed API不提供引用信息)")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(example_usage())
