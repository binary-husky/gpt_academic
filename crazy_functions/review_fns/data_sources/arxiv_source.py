import arxiv
from typing import List, Optional, Union, Literal, Dict
from datetime import datetime
from .base_source import DataSource, PaperMetadata
import os
from urllib.request import urlretrieve
import feedparser
from tqdm import tqdm

class ArxivSource(DataSource):
    """arXiv API实现"""

    CATEGORIES = {
        # 物理学
        "Physics": {
            "astro-ph": "天体物理学",
            "cond-mat": "凝聚态物理",
            "gr-qc": "广义相对论与量子宇宙学",
            "hep-ex": "高能物理实验",
            "hep-lat": "格点场论",
            "hep-ph": "高能物理理论",
            "hep-th": "高能物理理论",
            "math-ph": "数学物理",
            "nlin": "非线性科学",
            "nucl-ex": "核实验",
            "nucl-th": "核理论",
            "physics": "物理学",
            "quant-ph": "量子物理",
        },

        # 数学
        "Mathematics": {
            "math.AG": "代数几何",
            "math.AT": "代数拓扑",
            "math.AP": "分析与偏微分方程",
            "math.CT": "范畴论",
            "math.CA": "复分析",
            "math.CO": "组合数学",
            "math.AC": "交换代数",
            "math.CV": "复变函数",
            "math.DG": "微分几何",
            "math.DS": "动力系统",
            "math.FA": "泛函分析",
            "math.GM": "一般数学",
            "math.GN": "一般拓扑",
            "math.GT": "几何拓扑",
            "math.GR": "群论",
            "math.HO": "数学史与数学概述",
            "math.IT": "信息论",
            "math.KT": "K理论与同调",
            "math.LO": "逻辑",
            "math.MP": "数学物理",
            "math.MG": "度量几何",
            "math.NT": "数论",
            "math.NA": "数值分析",
            "math.OA": "算子代数",
            "math.OC": "最优化与控制",
            "math.PR": "概率论",
            "math.QA": "量子代数",
            "math.RT": "表示论",
            "math.RA": "环与代数",
            "math.SP": "谱理论",
            "math.ST": "统计理论",
            "math.SG": "辛几何",
        },

        # 计算机科学
        "Computer Science": {
            "cs.AI": "人工智能",
            "cs.CL": "计算语言学",
            "cs.CC": "计算复杂性",
            "cs.CE": "计算工程",
            "cs.CG": "计算几何",
            "cs.GT": "计算机博弈论",
            "cs.CV": "计算机视觉",
            "cs.CY": "计算机与社会",
            "cs.CR": "密码学与安全",
            "cs.DS": "数据结构与算法",
            "cs.DB": "数据库",
            "cs.DL": "数字图书馆",
            "cs.DM": "离散数学",
            "cs.DC": "分布式计算",
            "cs.ET": "新兴技术",
            "cs.FL": "形式语言与自动机理论",
            "cs.GL": "一般文献",
            "cs.GR": "图形学",
            "cs.AR": "硬件架构",
            "cs.HC": "人机交互",
            "cs.IR": "信息检索",
            "cs.IT": "信息论",
            "cs.LG": "机器学习",
            "cs.LO": "逻辑与计算机",
            "cs.MS": "数学软件",
            "cs.MA": "多智能体系统",
            "cs.MM": "多媒体",
            "cs.NI": "网络与互联网架构",
            "cs.NE": "神经与进化计算",
            "cs.NA": "数值分析",
            "cs.OS": "操作系统",
            "cs.OH": "其他计算机科学",
            "cs.PF": "性能评估",
            "cs.PL": "编程语言",
            "cs.RO": "机器人学",
            "cs.SI": "社会与信息网络",
            "cs.SE": "软件工程",
            "cs.SD": "声音",
            "cs.SC": "符号计算",
            "cs.SY": "系统与控制",
        },

        # 定量生物学
        "Quantitative Biology": {
            "q-bio.BM": "生物分子",
            "q-bio.CB": "细胞行为",
            "q-bio.GN": "基因组学",
            "q-bio.MN": "分子网络",
            "q-bio.NC": "神经计算",
            "q-bio.OT": "其他",
            "q-bio.PE": "群体与进化",
            "q-bio.QM": "定量方法",
            "q-bio.SC": "亚细胞过程",
            "q-bio.TO": "组织与器官",
        },

        # 定量金融
        "Quantitative Finance": {
            "q-fin.CP": "计算金融",
            "q-fin.EC": "经济学",
            "q-fin.GN": "一般金融",
            "q-fin.MF": "数学金融",
            "q-fin.PM": "投资组合管理",
            "q-fin.PR": "定价理论",
            "q-fin.RM": "风险管理",
            "q-fin.ST": "统计金融",
            "q-fin.TR": "交易与市场微观结构",
        },

        # 统计学
        "Statistics": {
            "stat.AP": "应用统计",
            "stat.CO": "计算统计",
            "stat.ML": "机器学习",
            "stat.ME": "方法论",
            "stat.OT": "其他统计",
            "stat.TH": "统计理论",
        },

        # 电气工程与系统科学
        "Electrical Engineering and Systems Science": {
            "eess.AS": "音频与语音处理",
            "eess.IV": "图像与视频处理",
            "eess.SP": "信号处理",
            "eess.SY": "系统与控制",
        },

        # 经济学
        "Economics": {
            "econ.EM": "计量经济学",
            "econ.GN": "一般经济学",
            "econ.TH": "理论经济学",
        }
    }

    def __init__(self):
        """初始化"""
        self._initialize()  # 调用初始化方法
        # 修改排序选项映射
        self.sort_options = {
            'relevance': arxiv.SortCriterion.Relevance,  # arXiv的相关性排序
            'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,  # 最后更新日期
            'submittedDate': arxiv.SortCriterion.SubmittedDate,  # 提交日期
        }

        self.sort_order_options = {
            'ascending': arxiv.SortOrder.Ascending,
            'descending': arxiv.SortOrder.Descending
        }

        self.default_sort = 'lastUpdatedDate'
        self.default_order = 'descending'

    def _initialize(self) -> None:
        """初始化客户端，设置默认参数"""
        self.client = arxiv.Client()

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = None,
        sort_order: str = None,
        start_year: int = None
    ) -> List[Dict]:
        """搜索论文"""
        try:
            # 使用默认排序如果提供的排序选项无效
            if not sort_by or sort_by not in self.sort_options:
                sort_by = self.default_sort

            # 使用默认排序顺序如果提供的顺序无效
            if not sort_order or sort_order not in self.sort_order_options:
                sort_order = self.default_order

            # 如果指定了起始年份，添加到查询中
            if start_year:
                query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"

            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=self.sort_options[sort_by],
                sort_order=self.sort_order_options[sort_order]
            )

            results = list(self.client.results(search))
            return [self._parse_paper_data(result) for result in results]
        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    async def search_by_id(self, paper_id: Union[str, List[str]]) -> List[PaperMetadata]:
        """按ID搜索论文

        Args:
            paper_id: 单个arXiv ID或ID列表，例如：'2005.14165' 或 ['2005.14165', '2103.14030']
        """
        if isinstance(paper_id, str):
            paper_id = [paper_id]

        search = arxiv.Search(
            id_list=paper_id,
            max_results=len(paper_id)
        )
        results = list(self.client.results(search))
        return [self._parse_paper_data(result) for result in results]

    async def search_by_category(
        self,
        category: str,
        limit: int = 100,
        sort_by: str = 'relevance',
        sort_order: str = 'descending',
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按类别搜索论文"""
        query = f"cat:{category}"

        # 如果指定了起始年份，添加到查询中
        if start_year:
            query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"

        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def search_by_authors(
        self,
        authors: List[str],
        limit: int = 100,
        sort_by: str = 'relevance',
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = " AND ".join([f"au:\"{author}\"" for author in authors])

        # 如果指定了起始年份，添加到查询中
        if start_year:
            query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"

        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by
        )

    async def search_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        sort_by: Literal['relevance', 'updated', 'submitted'] = 'submitted',
        sort_order: Literal['ascending', 'descending'] = 'descending'
    ) -> List[PaperMetadata]:
        """按日期范围搜索论文"""
        query = f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
        return await self.search(
            query,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def download_pdf(self, paper_id: str, dirpath: str = "./", filename: str = "") -> str:
        """下载论文PDF

        Args:
            paper_id: arXiv ID
            dirpath: 保存目录
            filename: 文件名，如果为空则使用默认格式：{paper_id}_{标题}.pdf

        Returns:
            保存的文件路径
        """
        papers = await self.search_by_id(paper_id)
        if not papers:
            raise ValueError(f"未找到ID为 {paper_id} 的论文")
        paper = papers[0]

        if not filename:
            # 清理标题中的非法字符
            safe_title = "".join(c if c.isalnum() else "_" for c in paper.title)
            filename = f"{paper_id}_{safe_title}.pdf"

        filepath = os.path.join(dirpath, filename)
        urlretrieve(paper.url, filepath)
        return filepath

    async def download_source(self, paper_id: str, dirpath: str = "./", filename: str = "") -> str:
        """下载论文源文件（通常是LaTeX源码）

        Args:
            paper_id: arXiv ID
            dirpath: 保存目录
            filename: 文件名，如果为空则使用默认格式：{paper_id}_{标题}.tar.gz

        Returns:
            保存的文件路径
        """
        papers = await self.search_by_id(paper_id)
        if not papers:
            raise ValueError(f"未找到ID为 {paper_id} 的论文")
        paper = papers[0]

        if not filename:
            safe_title = "".join(c if c.isalnum() else "_" for c in paper.title)
            filename = f"{paper_id}_{safe_title}.tar.gz"

        filepath = os.path.join(dirpath, filename)
        source_url = paper.url.replace("/pdf/", "/src/")
        urlretrieve(source_url, filepath)
        return filepath

    async def get_citations(self, paper_id: str) -> List[PaperMetadata]:
        # arXiv API不直接提供引用信息
        return []

    async def get_references(self, paper_id: str) -> List[PaperMetadata]:
        # arXiv API不直接提供引用信息
        return []

    async def get_paper_details(self, paper_id: str) -> Optional[PaperMetadata]:
        """获取论文详情

        Args:
            paper_id: arXiv ID 或 DOI

        Returns:
            论文详细信息，如果未找到返回 None
        """
        try:
            # 如果是完整的 arXiv URL，提取 ID
            if "arxiv.org" in paper_id:
                paper_id = paper_id.split("/")[-1]
            # 如果是 DOI 格式且是 arXiv 论文，提取 ID
            elif paper_id.startswith("10.48550/arXiv."):
                paper_id = paper_id.split(".")[-1]

            papers = await self.search_by_id(paper_id)
            return papers[0] if papers else None
        except Exception as e:
            print(f"获取论文详情时发生错误: {str(e)}")
            return None

    def _parse_paper_data(self, result: arxiv.Result) -> PaperMetadata:
        """解析arXiv API返回的数据"""
        # 解析主要类别和次要类别
        primary_category = result.primary_category
        categories = result.categories

        # 构建venue信息
        venue_info = {
            'primary_category': primary_category,
            'categories': categories,
            'comments': getattr(result, 'comment', None),
            'journal_ref': getattr(result, 'journal_ref', None)
        }

        return PaperMetadata(
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            year=result.published.year,
            doi=result.entry_id,
            url=result.pdf_url,
            citations=None,
            venue=f"arXiv:{primary_category}",
            institutions=[],
            venue_type='preprint',  # arXiv论文都是预印本
            venue_name='arXiv',
            venue_info=venue_info,
            source='arxiv'  # 添加来源标记
        )

    async def get_latest_papers(
        self,
        category: str,
        debug: bool = False,
        batch_size: int = 50
    ) -> List[PaperMetadata]:
        """获取指定类别的最新论文

        通过 RSS feed 获取最新发布的论文，然后批量获取详细信息

        Args:
            category: arXiv类别，例如：
                     - 整个领域: 'cs'
                     - 具体方向: 'cs.AI'
                     - 多个类别: 'cs.AI+q-bio.NC'
            debug: 是否为调试模式，如果为True则只返回5篇最新论文
            batch_size: 批量获取论文的数量，默认50

        Returns:
            论文列表

        Raises:
            ValueError: 如果类别无效
        """
        try:
            # 处理类别格式
            # 1. 转换为小写
            # 2. 确保多个类别之间使用+连接
            category = category.lower().replace(' ', '+')

            # 构建RSS feed URL
            feed_url = f"https://rss.arxiv.org/rss/{category}"
            print(f"正在获取RSS feed: {feed_url}")  # 添加调试信息

            feed = feedparser.parse(feed_url)

            # 检查feed是否有效
            if hasattr(feed, 'status') and feed.status != 200:
                raise ValueError(f"获取RSS feed失败，状态码: {feed.status}")

            if not feed.entries:
                print(f"警告：未在feed中找到任何条目")  # 添加调试信息
                print(f"Feed标题: {feed.feed.title if hasattr(feed, 'feed') else '无标题'}")
                raise ValueError(f"无效的arXiv类别或未找到论文: {category}")

            if debug:
                # 调试模式：只获取5篇最新论文
                search = arxiv.Search(
                    query=f'cat:{category}',
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                    max_results=5
                )
                results = list(self.client.results(search))
                return [self._parse_paper_data(result) for result in results]

            # 正常模式：获取所有新论文
            # 从RSS条目中提取arXiv ID
            paper_ids = []
            for entry in feed.entries:
                try:
                    # RSS链接格式可能是以下几种：
                    # - http://arxiv.org/abs/2403.xxxxx
                    # - http://arxiv.org/pdf/2403.xxxxx
                    # - https://arxiv.org/abs/2403.xxxxx
                    link = entry.link or entry.id
                    arxiv_id = link.split('/')[-1].replace('.pdf', '')
                    if arxiv_id:
                        paper_ids.append(arxiv_id)
                except Exception as e:
                    print(f"警告：处理条目时出错: {str(e)}")  # 添加调试信息
                    continue

            if not paper_ids:
                print("未能从feed中提取到任何论文ID")  # 添加调试信息
                return []

            print(f"成功提取到 {len(paper_ids)} 个论文ID")  # 添加调试信息

            # 批量获取论文详情
            papers = []
            with tqdm(total=len(paper_ids), desc="获取arXiv论文") as pbar:
                for i in range(0, len(paper_ids), batch_size):
                    batch_ids = paper_ids[i:i + batch_size]
                    search = arxiv.Search(
                        id_list=batch_ids,
                        max_results=len(batch_ids)
                    )
                    batch_results = list(self.client.results(search))
                    papers.extend([self._parse_paper_data(result) for result in batch_results])
                    pbar.update(len(batch_results))

            return papers

        except Exception as e:
            print(f"获取最新论文时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())  # 添加完整的错误追踪
            return []

async def example_usage():
    """ArxivSource使用示例"""
    arxiv_source = ArxivSource()

    try:
        # 示例1：基本搜索，使用不同的排序方式
        # print("\n=== 示例1：搜索最新的机器学习论文（按提交时间排序）===")
        # papers = await arxiv_source.search(
        #     "ti:\"machine learning\"",
        #     limit=3,
        #     sort_by='submitted',
        #     sort_order='descending'
        # )
        # print(f"找到 {len(papers)} 篇论文")

        # for i, paper in enumerate(papers, 1):
        #     print(f"\n--- 论文 {i} ---")
        #     print(f"标题: {paper.title}")
        #     print(f"作者: {', '.join(paper.authors)}")
        #     print(f"发表年份: {paper.year}")
        #     print(f"arXiv ID: {paper.doi}")
        #     print(f"PDF URL: {paper.url}")
        #     if paper.abstract:
        #         print(f"\n摘要:")
        #         print(paper.abstract)
        #     print(f"发表venue: {paper.venue}")

        # # 示例2：按ID搜索
        # print("\n=== 示例2：按ID搜索论文 ===")
        # paper_id = "2005.14165"  # GPT-3论文
        # papers = await arxiv_source.search_by_id(paper_id)
        # if papers:
        #     paper = papers[0]
        #     print(f"标题: {paper.title}")
        #     print(f"作者: {', '.join(paper.authors)}")
        #     print(f"发表年份: {paper.year}")

        # # 示例3：按类别搜索
        # print("\n=== 示例3：搜索人工智能领域最新论文 ===")
        # ai_papers = await arxiv_source.search_by_category(
        #     "cs.AI",
        #     limit=2,
        #     sort_by='updated',
        #     sort_order='descending'
        # )
        # for i, paper in enumerate(ai_papers, 1):
        #     print(f"\n--- AI论文 {i} ---")
        #     print(f"标题: {paper.title}")
        #     print(f"作者: {', '.join(paper.authors)}")
        #     print(f"发表venue: {paper.venue}")

        # # 示例4：按作者搜索
        # print("\n=== 示例4：搜索特定作者的论文 ===")
        # author_papers = await arxiv_source.search_by_authors(
        #     ["Bengio"],
        #     limit=2,
        #     sort_by='relevance'
        # )
        # for i, paper in enumerate(author_papers, 1):
        #     print(f"\n--- Bengio的论文 {i} ---")
        #     print(f"标题: {paper.title}")
        #     print(f"作者: {', '.join(paper.authors)}")
        #     print(f"发表venue: {paper.venue}")

        # # 示例5：按日期范围搜索
        # print("\n=== 示例5：搜索特定日期范围的论文 ===")
        # from datetime import datetime, timedelta
        # end_date = datetime.now()
        # start_date = end_date - timedelta(days=7)  # 最近一周
        # recent_papers = await arxiv_source.search_by_date_range(
        #     start_date,
        #     end_date,
        #     limit=2
        # )
        # for i, paper in enumerate(recent_papers, 1):
        #     print(f"\n--- 最近论文 {i} ---")
        #     print(f"标题: {paper.title}")
        #     print(f"作者: {', '.join(paper.authors)}")
        #     print(f"发表年份: {paper.year}")

        # # 示例6：下载PDF
        # print("\n=== 示例6：下载论文PDF ===")
        # if papers:  # 使用之前搜索到的GPT-3论文
        #     pdf_path = await arxiv_source.download_pdf(paper_id)
        #     print(f"PDF已下载到: {pdf_path}")

        # # 示例7：下载源文件
        # print("\n=== 示例7：下载论文源文件 ===")
        # if papers:
        #     source_path = await arxiv_source.download_source(paper_id)
        #     print(f"源文件已下载到: {source_path}")

        # 示例6：获取最新论文
        print("\n=== 示例8：获取最新论文 ===")

        # 获取CS.AI领域的最新论文
        print("\n--- 获取AI领域最新论文 ---")
        ai_latest = await arxiv_source.get_latest_papers("cs.AI", debug=True)
        for i, paper in enumerate(ai_latest, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")

        # 获取整个计算机科学领域的最新论文
        print("\n--- 获取整个CS领域最新论文 ---")
        cs_latest = await arxiv_source.get_latest_papers("cs", debug=True)
        for i, paper in enumerate(cs_latest, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")

        # 获取多个类别的最新论文
        print("\n--- 获取AI和机器学习领域最新论文 ---")
        multi_latest = await arxiv_source.get_latest_papers("cs.AI+cs.LG", debug=True)
        for i, paper in enumerate(multi_latest, 1):
            print(f"\n论文 {i}:")
            print(f"标题: {paper.title}")
            print(f"作者: {', '.join(paper.authors)}")
            print(f"发表年份: {paper.year}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
