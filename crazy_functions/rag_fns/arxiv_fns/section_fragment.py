from dataclasses import dataclass

@dataclass
class SectionFragment:
    """Arxiv论文片段数据类"""
    title: str  # 文件路径
    abstract: str  # 论文摘要
    catalogs: str # 文章各章节的目录结构
    arxiv_id: str = ""  # 添加 arxiv_id 属性
    current_section: str = "Introduction" # 当前片段所属的section或者subsection或者孙subsubsection名字
    content: str = '' #当前片段的内容
    bibliography: str = '' #当前片段的参考文献






