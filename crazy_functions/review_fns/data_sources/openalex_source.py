import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from .base_source import DataSource, PaperMetadata
import os
from urllib.parse import quote

class OpenAlexSource(DataSource):
    """OpenAlex API实现"""

    def _initialize(self) -> None:
        self.base_url = "https://api.openalex.org"
        self.mailto = "xxxxxxxxxxxxxxxxxxxxxxxx@163.com"  # 直接写入邮件地址

    async def search(self, query: str, limit: int = 100) -> List[PaperMetadata]:
        params = {"mailto": self.mailto} if self.mailto else {}
        params.update({
            "filter": f"title.search:{query}",
            "per-page": limit
        })

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/works",
                params=params
            ) as response:
                try:
                    response.raise_for_status()
                    data = await response.json()
                    results = data.get("results", [])
                    return [self._parse_work(work) for work in results]
                except Exception as e:
                    print(f"搜索出错: {str(e)}")
                    return []

    def _parse_work(self, work: Dict) -> PaperMetadata:
        """解析OpenAlex返回的数据"""
        # 获取作者信息
        raw_author_names = [
            authorship.get("raw_author_name", "")
            for authorship in work.get("authorships", [])
            if authorship
        ]
        # 处理作者名字格式
        authors = [
            self._reformat_name(author)
            for author in raw_author_names
        ]

        # 获取机构信息
        institutions = [
            inst.get("display_name", "")
            for authorship in work.get("authorships", [])
            for inst in authorship.get("institutions", [])
            if inst
        ]

        # 获取主要发表位置信息
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        venue = source.get("display_name")

        # 获取发表日期
        year = work.get("publication_year")

        return PaperMetadata(
            title=work.get("title", ""),
            authors=authors,
            institutions=institutions,
            abstract=work.get("abstract", ""),
            year=year,
            doi=work.get("doi"),
            url=work.get("doi"),  # OpenAlex 使用 DOI 作为 URL
            citations=work.get("cited_by_count"),
            venue=venue
        )

    def _reformat_name(self, name: str) -> str:
        """重新格式化作者名字"""
        if "," not in name:
            return name
        family, given_names = (x.strip() for x in name.split(",", maxsplit=1))
        return f"{given_names} {family}"

    async def get_paper_details(self, doi: str) -> PaperMetadata:
        """获取指定DOI的论文详情"""
        params = {"mailto": self.mailto} if self.mailto else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/works/https://doi.org/{quote(doi, safe='')}",
                params=params
            ) as response:
                data = await response.json()
                return self._parse_work(data)

    async def get_references(self, doi: str) -> List[PaperMetadata]:
        """获取指定DOI论文的参考文献列表"""
        params = {"mailto": self.mailto} if self.mailto else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/works/https://doi.org/{quote(doi, safe='')}/references",
                params=params
            ) as response:
                data = await response.json()
                return [self._parse_work(work) for work in data.get("results", [])]

    async def get_citations(self, doi: str) -> List[PaperMetadata]:
        """获取引用指定DOI论文的文献列表"""
        params = {"mailto": self.mailto} if self.mailto else {}
        params.update({
            "filter": f"cites:doi:{doi}",
            "per-page": 100
        })

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/works",
                params=params
            ) as response:
                data = await response.json()
                return [self._parse_work(work) for work in data.get("results", [])]

async def example_usage():
    """OpenAlexSource使用示例"""
    # 初始化OpenAlexSource
    openalex = OpenAlexSource()

    try:
        print("正在搜索论文...")
        # 搜索与"artificial intelligence"相关的论文，限制返回5篇
        papers = await openalex.search(query="artificial intelligence", limit=5)

        if not papers:
            print("未获取到任何论文信息")
            return

        print(f"找到 {len(papers)} 篇论文")

        # 打印搜索结果
        for i, paper in enumerate(papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors) if paper.authors else '未知'}")
            if paper.institutions:
                print(f"机构: {', '.join(paper.institutions)}")
            print(f"发表年份: {paper.year if paper.year else '未知'}")
            print(f"DOI: {paper.doi if paper.doi else '未知'}")
            print(f"URL: {paper.url if paper.url else '未知'}")
            if paper.abstract:
                print(f"摘要: {paper.abstract[:200]}...")
            print(f"引用次数: {paper.citations if paper.citations is not None else '未知'}")
            print(f"发表venue: {paper.venue if paper.venue else '未知'}")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

# 如果直接运行此文件，执行示例代码
if __name__ == "__main__":
    import asyncio

    # 运行示例
    asyncio.run(example_usage())
