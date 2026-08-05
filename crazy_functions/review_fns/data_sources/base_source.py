from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

class PaperMetadata:
    """论文元数据"""
    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        year: int,
        doi: str = None,
        url: str = None,
        citations: int = None,
        venue: str = None,
        institutions: List[str] = None,
        venue_type: str = None,  # 来源类型(journal/conference/preprint等)
        venue_name: str = None,  # 具体的期刊/会议名称
        venue_info: Dict = None,  # 更多来源详细信息(如影响因子、分区等)
        source: str = None  # 新增: 论文来源标记
    ):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.year = year
        self.doi = doi
        self.url = url
        self.citations = citations
        self.venue = venue
        self.institutions = institutions or []
        self.venue_type = venue_type  # 新增
        self.venue_name = venue_name  # 新增
        self.venue_info = venue_info or {}  # 新增
        self.source = source  # 新增: 存储论文来源

        # 新增：影响因子和分区信息，初始化为None
        self._if_factor = None
        self._cas_division = None
        self._jcr_division = None

    @property
    def if_factor(self) -> Optional[float]:
        """获取影响因子"""
        return self._if_factor

    @if_factor.setter
    def if_factor(self, value: float):
        """设置影响因子"""
        self._if_factor = value

    @property
    def cas_division(self) -> Optional[str]:
        """获取中科院分区"""
        return self._cas_division

    @cas_division.setter
    def cas_division(self, value: str):
        """设置中科院分区"""
        self._cas_division = value

    @property
    def jcr_division(self) -> Optional[str]:
        """获取JCR分区"""
        return self._jcr_division

    @jcr_division.setter
    def jcr_division(self, value: str):
        """设置JCR分区"""
        self._jcr_division = value

class DataSource(ABC):
    """数据源基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._initialize()

    @abstractmethod
    def _initialize(self) -> None:
        """初始化数据源"""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 100) -> List[PaperMetadata]:
        """搜索论文"""
        pass

    @abstractmethod
    async def get_paper_details(self, paper_id: str) -> PaperMetadata:
        """获取论文详细信息"""
        pass

    @abstractmethod
    async def get_citations(self, paper_id: str) -> List[PaperMetadata]:
        """获取引用该论文的文献"""
        pass

    @abstractmethod
    async def get_references(self, paper_id: str) -> List[PaperMetadata]:
        """获取该论文引用的文献"""
        pass
