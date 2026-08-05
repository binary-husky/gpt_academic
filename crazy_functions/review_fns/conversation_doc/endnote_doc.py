from typing import List
from crazy_functions.review_fns.data_sources.base_source import PaperMetadata

class EndNoteFormatter:
    """EndNote参考文献格式生成器"""

    def __init__(self):
        pass

    def create_document(self, papers: List[PaperMetadata]) -> str:
        """生成EndNote格式的参考文献文本

        Args:
            papers: 论文列表

        Returns:
            str: EndNote格式的参考文献文本
        """
        endnote_text = ""

        for paper in papers:
            # 开始一个新条目
            endnote_text += "%0 Journal Article\n"  # 默认类型为期刊文章

            # 根据venue_type调整条目类型
            if hasattr(paper, 'venue_type') and paper.venue_type:
                if paper.venue_type.lower() == 'conference':
                    endnote_text = endnote_text.replace("Journal Article", "Conference Paper")
                elif paper.venue_type.lower() == 'preprint':
                    endnote_text = endnote_text.replace("Journal Article", "Electronic Article")

            # 添加标题
            endnote_text += f"%T {paper.title}\n"

            # 添加作者
            for author in paper.authors:
                endnote_text += f"%A {author}\n"

            # 添加年份
            if paper.year:
                endnote_text += f"%D {paper.year}\n"

            # 添加期刊/会议名称
            if hasattr(paper, 'venue_name') and paper.venue_name:
                endnote_text += f"%J {paper.venue_name}\n"
            elif paper.venue:
                endnote_text += f"%J {paper.venue}\n"

            # 添加DOI
            if paper.doi:
                endnote_text += f"%R {paper.doi}\n"
                endnote_text += f"%U https://doi.org/{paper.doi}\n"
            elif paper.url:
                endnote_text += f"%U {paper.url}\n"

            # 添加摘要
            if paper.abstract:
                endnote_text += f"%X {paper.abstract}\n"

            # 添加机构
            if hasattr(paper, 'institutions'):
                for institution in paper.institutions:
                    endnote_text += f"%I {institution}\n"

            # 条目之间添加空行
            endnote_text += "\n"

        return endnote_text
