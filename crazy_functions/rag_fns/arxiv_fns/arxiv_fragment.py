from dataclasses import dataclass

@dataclass
class ArxivFragment:
    """Arxiv论文片段数据类"""
    file_path: str  # 文件路径
    content: str  # 内容
    segment_index: int  # 片段索引
    total_segments: int  # 总片段数
    rel_path: str  # 相对路径
    segment_type: str  # 片段类型(text/math/table/figure等)
    title: str  # 论文标题
    abstract: str  # 论文摘要
    section: str  # 所属章节
    is_appendix: bool  # 是否是附录
    importance: float = 1.0  # 重要性得分
    arxiv_id: str = ""  # 添加 arxiv_id 属性

    @staticmethod
    def merge_segments(seg1: 'ArxivFragment', seg2: 'ArxivFragment') -> 'ArxivFragment':
        """
        合并两个片段的静态方法

        Args:
            seg1: 第一个片段
            seg2: 第二个片段

        Returns:
            ArxivFragment: 合并后的片段
        """
        # 合并内容
        merged_content = f"{seg1.content}\n{seg2.content}"

        # 确定合并后的类型
        def _merge_segment_type(type1: str, type2: str) -> str:
            if type1 == type2:
                return type1
            if type1 == 'text':
                return type2
            if type2 == 'text':
                return type1
            return 'mixed'

        return ArxivFragment(
            file_path=seg1.file_path,
            content=merged_content,
            segment_index=seg1.segment_index,
            total_segments=seg1.total_segments - 1,
            rel_path=seg1.rel_path,
            segment_type=_merge_segment_type(seg1.segment_type, seg2.segment_type),
            title=seg1.title,
            abstract=seg1.abstract,
            section=seg1.section,
            is_appendix=seg1.is_appendix,
            importance=max(seg1.importance, seg2.importance)
        )