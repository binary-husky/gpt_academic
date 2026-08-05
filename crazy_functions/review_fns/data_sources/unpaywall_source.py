import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from .base_source import DataSource, PaperMetadata

class UnpaywallSource(DataSource):
    """Unpaywall API实现"""

    def _initialize(self) -> None:
        self.base_url = "https://api.unpaywall.org/v2"
        self.email = self.api_key  # Unpaywall使用email作为API key

    async def search(self, query: str, limit: int = 100) -> List[PaperMetadata]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search",
                params={
                    "query": query,
                    "email": self.email,
                    "limit": limit
                }
            ) as response:
                data = await response.json()
                return [self._parse_response(item.response)
                        for item in data.get("results", [])]

    def _parse_response(self, data: Dict) -> PaperMetadata:
        """解析Unpaywall返回的数据"""
        return PaperMetadata(
            title=data.get("title", ""),
            authors=[
                f"{author.get('given', '')} {author.get('family', '')}"
                for author in data.get("z_authors", [])
            ],
            institutions=[
                aff.get("name", "")
                for author in data.get("z_authors", [])
                for aff in author.get("affiliation", [])
            ],
            abstract="",  # Unpaywall不提供摘要
            year=data.get("year"),
            doi=data.get("doi"),
            url=data.get("doi_url"),
            citations=None,  # Unpaywall不提供引用计数
            venue=data.get("journal_name")
        )
