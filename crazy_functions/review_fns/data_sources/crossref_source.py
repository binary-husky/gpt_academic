import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from crazy_functions.review_fns.data_sources.base_source import DataSource, PaperMetadata
import random

class CrossrefSource(DataSource):
    """Crossref API实现"""

    CONTACT_EMAILS = [
        "gpt_abc_academic@163.com",
        "gpt_abc_newapi@163.com",
        "gpt_abc_academic_pwd@163.com"
    ]

    def _initialize(self) -> None:
        """初始化客户端，设置默认参数"""
        self.base_url = "https://api.crossref.org"
        # 随机选择一个邮箱
        contact_email = random.choice(self.CONTACT_EMAILS)
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"Mozilla/5.0 (compatible; PythonScript/1.0; mailto:{contact_email})",
        }
        if self.api_key:
            self.headers["Crossref-Plus-API-Token"] = f"Bearer {self.api_key}"

    async def search(
        self,
        query: str,
        limit: int = 100,
        sort_by: str = None,
        sort_order: str = None,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            sort_by: 排序字段
            sort_order: 排序顺序
            start_year: 起始年份
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # 请求更多的结果以补偿可能被过滤掉的文章
            adjusted_limit = min(limit * 3, 1000)  # 设置上限以避免请求过多
            params = {
                "query": query,
                "rows": adjusted_limit,
                "select": (
                    "DOI,title,author,published-print,abstract,reference,"
                    "container-title,is-referenced-by-count,type,"
                    "publisher,ISSN,ISBN,issue,volume,page"
                )
            }

            # 添加年份过滤
            if start_year:
                params["filter"] = f"from-pub-date:{start_year}"

            # 添加排序
            if sort_by:
                params["sort"] = sort_by
                if sort_order:
                    params["order"] = sort_order

            async with session.get(
                f"{self.base_url}/works",
                params=params
            ) as response:
                if response.status != 200:
                    print(f"API请求失败: HTTP {response.status}")
                    print(f"响应内容: {await response.text()}")
                    return []

                data = await response.json()
                items = data.get("message", {}).get("items", [])
                if not items:
                    print(f"未找到相关论文")
                    return []

                # 过滤掉没有摘要的文章
                papers = []
                filtered_count = 0
                for work in items:
                    paper = self._parse_work(work)
                    if paper.abstract and paper.abstract.strip():
                        papers.append(paper)
                        if len(papers) >= limit:  # 达到原始请求的限制后停止
                            break
                    else:
                        filtered_count += 1

                print(f"找到 {len(items)} 篇相关论文，其中 {filtered_count} 篇因缺少摘要被过滤")
                print(f"返回 {len(papers)} 篇包含摘要的论文")
                return papers

    async def get_paper_details(self, doi: str) -> PaperMetadata:
        """获取指定DOI的论文详情"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/works/{doi}",
                params={
                    "select": (
                        "DOI,title,author,published-print,abstract,reference,"
                        "container-title,is-referenced-by-count,type,"
                        "publisher,ISSN,ISBN,issue,volume,page"
                    )
                }
            ) as response:
                if response.status != 200:
                    print(f"获取论文详情失败: HTTP {response.status}")
                    print(f"响应内容: {await response.text()}")
                    return None

                try:
                    data = await response.json()
                    return self._parse_work(data.get("message", {}))
                except Exception as e:
                    print(f"解析论文详情时发生错误: {str(e)}")
                    return None

    async def get_references(self, doi: str) -> List[PaperMetadata]:
        """获取指定DOI论文的参考文献列表"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/works/{doi}",
                params={"select": "reference"}
            ) as response:
                if response.status != 200:
                    print(f"获取参考文献失败: HTTP {response.status}")
                    return []

                try:
                    data = await response.json()
                    # 确保我们正确处理返回的数据结构
                    if not isinstance(data, dict):
                        print(f"API返回了意外的数据格式: {type(data)}")
                        return []

                    references = data.get("message", {}).get("reference", [])
                    if not references:
                        print(f"未找到参考文献")
                        return []

                    return [
                        PaperMetadata(
                            title=ref.get("article-title", ""),
                            authors=[ref.get("author", "")],
                            year=ref.get("year"),
                            doi=ref.get("DOI"),
                            url=f"https://doi.org/{ref.get('DOI')}" if ref.get("DOI") else None,
                            abstract="",
                            citations=None,
                            venue=ref.get("journal-title", ""),
                            institutions=[]
                        )
                        for ref in references
                    ]
                except Exception as e:
                    print(f"解析参考文献数据时发生错误: {str(e)}")
                    return []

    async def get_citations(self, doi: str) -> List[PaperMetadata]:
        """获取引用指定DOI论文的文献列表"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/works",
                params={
                    "filter": f"reference.DOI:{doi}",
                    "select": "DOI,title,author,published-print,abstract"
                }
            ) as response:
                if response.status != 200:
                    print(f"获取引用信息失败: HTTP {response.status}")
                    print(f"响应内容: {await response.text()}")
                    return []

                try:
                    data = await response.json()
                    # 检查返回的数据结构
                    if isinstance(data, dict):
                        items = data.get("message", {}).get("items", [])
                        return [self._parse_work(work) for work in items]
                    else:
                        print(f"API返回了意外的数据格式: {type(data)}")
                        return []
                except Exception as e:
                    print(f"解析引用数据时发生错误: {str(e)}")
                    return []

    def _parse_work(self, work: Dict) -> PaperMetadata:
        """解析Crossref返回的数据"""
        # 获取摘要 - 处理可能的不同格式
        abstract = ""
        if isinstance(work.get("abstract"), str):
            abstract = work.get("abstract", "")
        elif isinstance(work.get("abstract"), dict):
            abstract = work.get("abstract", {}).get("value", "")

        if not abstract:
            print(f"警告: 论文 '{work.get('title', [''])[0]}' 没有可用的摘要")

        # 获取机构信息
        institutions = []
        for author in work.get("author", []):
            if "affiliation" in author:
                for affiliation in author["affiliation"]:
                    if "name" in affiliation and affiliation["name"] not in institutions:
                        institutions.append(affiliation["name"])

        # 获取venue信息
        venue_name = work.get("container-title", [None])[0]
        venue_type = work.get("type", "unknown")  # 文献类型
        venue_info = {
            "publisher": work.get("publisher"),
            "issn": work.get("ISSN", []),
            "isbn": work.get("ISBN", []),
            "issue": work.get("issue"),
            "volume": work.get("volume"),
            "page": work.get("page")
        }

        return PaperMetadata(
            title=work.get("title", [None])[0] or "",
            authors=[
                author.get("given", "") + " " + author.get("family", "")
                for author in work.get("author", [])
            ],
            institutions=institutions,  # 添加机构信息
            abstract=abstract,
            year=work.get("published-print", {}).get("date-parts", [[None]])[0][0],
            doi=work.get("DOI"),
            url=f"https://doi.org/{work.get('DOI')}" if work.get("DOI") else None,
            citations=work.get("is-referenced-by-count"),
            venue=venue_name,
            venue_type=venue_type,  # 添加venue类型
            venue_name=venue_name,  # 添加venue名称
            venue_info=venue_info,  # 添加venue详细信息
            source='crossref'  # 添加来源标记
        )

    async def search_by_authors(
        self,
        authors: List[str],
        limit: int = 100,
        sort_by: str = None,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = " ".join([f"author:\"{author}\"" for author in authors])
        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by,
            start_year=start_year
        )

    async def search_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        sort_by: str = None,
        sort_order: str = None
    ) -> List[PaperMetadata]:
        """按日期范围搜索论文"""
        query = f"from-pub-date:{start_date.strftime('%Y-%m-%d')} until-pub-date:{end_date.strftime('%Y-%m-%d')}"
        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

async def example_usage():
    """CrossrefSource使用示例"""
    crossref = CrossrefSource(api_key=None)

    try:
        # 示例1：基本搜索，使用不同的排序方式
        print("\n=== 示例1：搜索最新的机器学习论文 ===")
        papers = await crossref.search(
            query="machine learning",
            limit=3,
            sort_by="published",
            sort_order="desc",
            start_year=2023
        )

        for i, paper in enumerate(papers, 1):
            print(f"\n--- 论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"URL: {paper.url}")
            if paper.abstract:
                print(f"摘要: {paper.abstract[:200]}...")
            if paper.institutions:
                print(f"机构: {', '.join(paper.institutions)}")
            print(f"引用次数: {paper.citations}")
            print(f"发表venue: {paper.venue}")
            print(f"venue类型: {paper.venue_type}")
            if paper.venue_info:
                print("Venue详细信息:")
                for key, value in paper.venue_info.items():
                    if value:
                        print(f"  - {key}: {value}")

        # 示例2：按DOI获取论文详情
        print("\n=== 示例2：获取特定论文详情 ===")
        # 使用BERT论文的DOI
        doi = "10.18653/v1/N19-1423"
        paper = await crossref.get_paper_details(doi)
        if paper:
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            if paper.abstract:
                print(f"摘要: {paper.abstract[:200]}...")
            print(f"引用次数: {paper.citations}")

        # 示例3：按作者搜索
        print("\n=== 示例3：搜索特定作者的论文 ===")
        author_papers = await crossref.search_by_authors(
            authors=["Yoshua Bengio"],
            limit=3,
            sort_by="published",
            start_year=2020
        )
        for i, paper in enumerate(author_papers, 1):
            print(f"\n--- {i}. {paper.title} ---")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")
            print(f"引用次数: {paper.citations}")

        # 示例4：按日期范围搜索
        print("\n=== 示例4：搜索特定日期范围的论文 ===")
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # 最近一个月
        recent_papers = await crossref.search_by_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=3,
            sort_by="published",
            sort_order="desc"
        )
        for i, paper in enumerate(recent_papers, 1):
            print(f"\n--- 最近发表的论文 {i} ---")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")
            print(f"DOI: {paper.doi}")

        # 示例5：获取论文引用信息
        print("\n=== 示例5：获取论文引用信息 ===")
        if paper:  # 使用之前获取的BERT论文
            print("\n获取引用该论文的文献:")
            citations = await crossref.get_citations(paper.doi)
            for i, citing_paper in enumerate(citations[:3], 1):
                print(f"\n--- 引用论文 {i} ---")
                print(f"标题: {citing_paper.title}")
                print(f"作者: {', '.join(citing_paper.authors)}")
                print(f"发表年份: {citing_paper.year}")

            print("\n获取该论文引用的参考文献:")
            references = await crossref.get_references(paper.doi)
            for i, ref_paper in enumerate(references[:3], 1):
                print(f"\n--- 参考文献 {i} ---")
                print(f"标题: {ref_paper.title}")
                print(f"作者: {', '.join(ref_paper.authors)}")
                print(f"发表年份: {ref_paper.year if ref_paper.year else '未知'}")

        # 示例6：展示venue信息的使用
        print("\n=== 示例6：展示期刊/会议详细信息 ===")
        if papers:
            paper = papers[0]
            print(f"文献类型: {paper.venue_type}")
            print(f"发表venue: {paper.venue_name}")
            if paper.venue_info:
                print("Venue详细信息:")
                for key, value in paper.venue_info.items():
                    if value:
                        print(f"  - {key}: {value}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio

    # 运行示例
    asyncio.run(example_usage())
