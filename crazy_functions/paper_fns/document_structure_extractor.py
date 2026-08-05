from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import os
import re
import logging

from crazy_functions.doc_fns.read_fns.unstructured_all.paper_structure_extractor import (
    PaperStructureExtractor, PaperSection, StructuredPaper
)
from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Text, Title, NarrativeText, ListItem, Table,
    Footer, Header, PageBreak, Image, Address
)

@dataclass
class DocumentSection:
    """通用文档章节数据类"""
    title: str  # 章节标题，如果没有标题则为空字符串
    content: str  # 章节内容
    level: int = 0  # 标题级别，0为主标题，1为一级标题，以此类推
    section_type: str = "content"  # 章节类型
    is_heading_only: bool = False  # 是否仅包含标题
    subsections: List['DocumentSection'] = field(default_factory=list)  # 子章节列表


@dataclass
class StructuredDocument:
    """结构化文档数据类"""
    title: str = ""  # 文档标题
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    sections: List[DocumentSection] = field(default_factory=list)  # 章节列表
    full_text: str = ""  # 完整文本
    is_paper: bool = False  # 是否为学术论文


class GenericDocumentStructureExtractor:
    """通用文档结构提取器

    可以从各种文档格式中提取结构信息，包括标题和内容。
    支持论文、报告、文章和一般文本文档。
    """

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = [
        '.pdf', '.docx', '.doc', '.pptx', '.ppt',
        '.txt', '.md', '.html', '.htm', '.xml',
        '.rtf', '.odt', '.epub', '.msg', '.eml'
    ]

    # 常见的标题前缀模式
    HEADING_PATTERNS = [
        # 数字标题 (1., 1.1., etc.)
        r'^\s*(\d+\.)+\s+',
        # 中文数字标题 (一、, 二、, etc.)
        r'^\s*[一二三四五六七八九十]+[、：:]\s+',
        # 带括号的数字标题 ((1), (2), etc.)
        r'^\s*\(\s*\d+\s*\)\s+',
        # 特定标记的标题 (Chapter 1, Section 1, etc.)
        r'^\s*(chapter|section|part|附录|章|节)\s+\d+[\.:：]\s+',
    ]

    # 常见的文档分段标记词
    SECTION_MARKERS = {
        'introduction': ['简介', '导言', '引言', 'introduction', '概述', 'overview'],
        'background': ['背景', '现状', 'background', '理论基础', '相关工作'],
        'main_content': ['主要内容', '正文', 'main content', '分析', '讨论'],
        'conclusion': ['结论', '总结', 'conclusion', '结语', '小结', 'summary'],
        'reference': ['参考', '参考文献', 'references', '文献', 'bibliography'],
        'appendix': ['附录', 'appendix', '补充资料', 'supplementary']
    }

    def __init__(self):
        """初始化提取器"""
        self.paper_extractor = PaperStructureExtractor()  # 论文专用提取器
        self._setup_logging()

    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def extract_document_structure(self, file_path: str, strategy: str = "fast") -> StructuredDocument:
        """提取文档结构

        Args:
            file_path: 文件路径
            strategy: 提取策略 ("fast" 或 "accurate")

        Returns:
            StructuredDocument: 结构化文档对象
        """
        try:
            self.logger.info(f"正在处理文档结构: {file_path}")

            # 1. 首先尝试使用论文提取器
            try:
                paper_result = self.paper_extractor.extract_paper_structure(file_path)
                if paper_result and len(paper_result.sections) > 2:  # 如果成功识别为论文结构
                    self.logger.info(f"成功识别为学术论文: {file_path}")
                    # 将论文结构转换为通用文档结构
                    return self._convert_paper_to_document(paper_result)
            except Exception as e:
                self.logger.debug(f"论文结构提取失败，将尝试通用提取: {str(e)}")

            # 2. 使用通用方法提取文档结构
            elements = partition(
                str(file_path),
                strategy=strategy,
                include_metadata=True,
                nlp=False
            )

            # 3. 使用通用提取器处理
            doc = self._extract_generic_structure(elements)
            return doc

        except Exception as e:
            self.logger.error(f"文档结构提取失败: {str(e)}")
            # 返回一个空的结构化文档
            return StructuredDocument(
                title="未能提取文档标题",
                sections=[DocumentSection(
                    title="",
                    content="",
                    level=0,
                    section_type="content"
                )]
            )

    def _convert_paper_to_document(self, paper: StructuredPaper) -> StructuredDocument:
        """将论文结构转换为通用文档结构

        Args:
            paper: 结构化论文对象

        Returns:
            StructuredDocument: 转换后的通用文档结构
        """
        doc = StructuredDocument(
            title=paper.metadata.title,
            is_paper=True,
            full_text=paper.full_text
        )

        # 转换元数据
        doc.metadata = {
            'title': paper.metadata.title,
            'authors': paper.metadata.authors,
            'keywords': paper.keywords,
            'abstract': paper.metadata.abstract if hasattr(paper.metadata, 'abstract') else "",
            'is_paper': True
        }

        # 转换章节结构
        doc.sections = self._convert_paper_sections(paper.sections)

        return doc

    def _convert_paper_sections(self, paper_sections: List[PaperSection], level: int = 0) -> List[DocumentSection]:
        """递归转换论文章节为通用文档章节

        Args:
            paper_sections: 论文章节列表
            level: 当前章节级别

        Returns:
            List[DocumentSection]: 通用文档章节列表
        """
        doc_sections = []

        for section in paper_sections:
            doc_section = DocumentSection(
                title=section.title,
                content=section.content,
                level=section.level,
                section_type=section.section_type,
                is_heading_only=False if section.content else True
            )

            # 递归处理子章节
            if section.subsections:
                doc_section.subsections = self._convert_paper_sections(
                    section.subsections, level + 1
                )

            doc_sections.append(doc_section)

        return doc_sections

    def _extract_generic_structure(self, elements) -> StructuredDocument:
        """从元素列表中提取通用文档结构

        Args:
            elements: 文档元素列表

        Returns:
            StructuredDocument: 结构化文档对象
        """
        # 创建结构化文档对象
        doc = StructuredDocument(full_text="")

        # 1. 提取文档标题
        title_candidates = []
        for i, element in enumerate(elements[:5]):  # 只检查前5个元素
            if isinstance(element, Title):
                title_text = str(element).strip()
                title_candidates.append((i, title_text))

        if title_candidates:
            # 使用第一个标题作为文档标题
            doc.title = title_candidates[0][1]

        # 2. 识别所有标题元素和内容
        title_elements = []

        # 2.1 首先识别所有标题
        for i, element in enumerate(elements):
            is_heading = False
            title_text = ""
            level = 0

            # 检查元素类型
            if isinstance(element, Title):
                is_heading = True
                title_text = str(element).strip()

                # 进一步检查是否为真正的标题
                if self._is_likely_heading(title_text, element, i, elements):
                    level = self._estimate_heading_level(title_text, element)
                else:
                    is_heading = False

            # 也检查格式像标题的普通文本
            elif isinstance(element, (Text, NarrativeText)) and i > 0:
                text = str(element).strip()
                # 检查是否匹配标题模式
                if any(re.match(pattern, text) for pattern in self.HEADING_PATTERNS):
                    # 检查长度和后续内容以确认是否为标题
                    if len(text) < 100 and self._has_sufficient_following_content(i, elements):
                        is_heading = True
                        title_text = text
                        level = self._estimate_heading_level(title_text, element)

            if is_heading:
                section_type = self._identify_section_type(title_text)
                title_elements.append((i, title_text, level, section_type))

        # 2.2 为每个标题提取内容
        sections = []

        for i, (index, title_text, level, section_type) in enumerate(title_elements):
            # 确定内容范围
            content_start = index + 1
            content_end = elements[-1]  # 默认到文档结束

            # 如果有下一个标题，内容到下一个标题开始
            if i < len(title_elements) - 1:
                content_end = title_elements[i+1][0]
            else:
                content_end = len(elements)

            # 提取内容
            content = self._extract_content_between(elements, content_start, content_end)

            # 创建章节
            section = DocumentSection(
                title=title_text,
                content=content,
                level=level,
                section_type=section_type,
                is_heading_only=False if content.strip() else True
            )

            sections.append(section)

        # 3. 如果没有识别到任何章节，创建一个默认章节
        if not sections:
            all_content = self._extract_content_between(elements, 0, len(elements))

            # 尝试从内容中提取标题
            first_line = all_content.split('\n')[0] if all_content else ""
            if first_line and len(first_line) < 100:
                doc.title = first_line
                all_content = '\n'.join(all_content.split('\n')[1:])

            default_section = DocumentSection(
                title="",
                content=all_content,
                level=0,
                section_type="content"
            )
            sections.append(default_section)

        # 4. 构建层次结构
        doc.sections = self._build_section_hierarchy(sections)

        # 5. 提取完整文本
        doc.full_text = "\n\n".join([str(element) for element in elements if isinstance(element, (Text, NarrativeText, Title, ListItem))])

        return doc

    def _build_section_hierarchy(self, sections: List[DocumentSection]) -> List[DocumentSection]:
        """构建章节层次结构

        Args:
            sections: 章节列表

        Returns:
            List[DocumentSection]: 具有层次结构的章节列表
        """
        if not sections:
            return []

        # 按层级排序
        top_level_sections = []
        current_parents = {0: None}  # 每个层级的当前父节点

        for section in sections:
            # 找到当前节点的父节点
            parent_level = None
            for level in sorted([k for k in current_parents.keys() if k < section.level], reverse=True):
                parent_level = level
                break

            if parent_level is None:
                # 顶级章节
                top_level_sections.append(section)
            else:
                # 子章节
                parent = current_parents[parent_level]
                if parent:
                    parent.subsections.append(section)
                else:
                    top_level_sections.append(section)

            # 更新当前层级的父节点
            current_parents[section.level] = section

            # 清除所有更深层级的父节点缓存
            deeper_levels = [k for k in current_parents.keys() if k > section.level]
            for level in deeper_levels:
                current_parents.pop(level, None)

        return top_level_sections

    def _is_likely_heading(self, text: str, element, index: int, elements) -> bool:
        """判断文本是否可能是标题

        Args:
            text: 文本内容
            element: 元素对象
            index: 元素索引
            elements: 所有元素列表

        Returns:
            bool: 是否可能是标题
        """
        # 1. 检查文本长度 - 标题通常不会太长
        if len(text) > 150:  # 标题通常不超过150个字符
            return False

        # 2. 检查是否匹配标题的数字编号模式
        if any(re.match(pattern, text) for pattern in self.HEADING_PATTERNS):
            return True

        # 3. 检查是否包含常见章节标记词
        lower_text = text.lower()
        for markers in self.SECTION_MARKERS.values():
            if any(marker.lower() in lower_text for marker in markers):
                return True

        # 4. 检查后续内容数量 - 标题后通常有足够多的内容
        if not self._has_sufficient_following_content(index, elements, min_chars=100):
            # 但如果文本很短且以特定格式开头，仍可能是标题
            if len(text) < 50 and (text.endswith(':') or text.endswith('：')):
                return True
            return False

        # 5. 检查格式特征
        # 标题通常是元素的开头，不在段落中间
        if len(text.split('\n')) > 1:
            # 多行文本不太可能是标题
            return False

        # 如果有元数据，检查字体特征（字体大小等）
        if hasattr(element, 'metadata') and element.metadata:
            try:
                font_size = getattr(element.metadata, 'font_size', None)
                is_bold = getattr(element.metadata, 'is_bold', False)

                # 字体较大或加粗的文本更可能是标题
                if font_size and font_size > 12:
                    return True
                if is_bold:
                    return True
            except (AttributeError, TypeError):
                pass

        # 默认返回True，因为元素已被识别为Title类型
        return True

    def _estimate_heading_level(self, text: str, element) -> int:
        """估计标题的层级

        Args:
            text: 标题文本
            element: 元素对象

        Returns:
            int: 标题层级 (0为主标题，1为一级标题, 等等)
        """
        # 1. 通过编号模式判断层级
        for pattern, level in [
            (r'^\s*\d+\.\s+', 1),  # 1. 开头 (一级标题)
            (r'^\s*\d+\.\d+\.\s+', 2),  # 1.1. 开头 (二级标题)
            (r'^\s*\d+\.\d+\.\d+\.\s+', 3),  # 1.1.1. 开头 (三级标题)
            (r'^\s*\d+\.\d+\.\d+\.\d+\.\s+', 4),  # 1.1.1.1. 开头 (四级标题)
        ]:
            if re.match(pattern, text):
                return level

        # 2. 检查是否是常见的主要章节标题
        lower_text = text.lower()
        main_sections = [
            'abstract', 'introduction', 'background', 'methodology',
            'results', 'discussion', 'conclusion', 'references'
        ]
        for section in main_sections:
            if section in lower_text:
                return 1  # 主要章节为一级标题

        # 3. 根据文本特征判断
        if text.isupper():  # 全大写文本可能是章标题
            return 1

        # 4. 通过元数据判断层级
        if hasattr(element, 'metadata') and element.metadata:
            try:
                # 根据字体大小判断层级
                font_size = getattr(element.metadata, 'font_size', None)
                if font_size is not None:
                    if font_size > 18:  # 假设主标题字体最大
                        return 0
                    elif font_size > 16:
                        return 1
                    elif font_size > 14:
                        return 2
                    else:
                        return 3
            except (AttributeError, TypeError):
                pass

        # 默认为二级标题
        return 2

    def _identify_section_type(self, title_text: str) -> str:
        """识别章节类型，包括参考文献部分"""
        lower_text = title_text.lower()

        # 特别检查是否为参考文献部分
        references_patterns = [
            r'references', r'参考文献', r'bibliography', r'引用文献',
            r'literature cited', r'^cited\s+literature', r'^文献$', r'^引用$'
        ]

        for pattern in references_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                return "references"

        # 检查是否匹配其他常见章节类型
        for section_type, markers in self.SECTION_MARKERS.items():
            if any(marker.lower() in lower_text for marker in markers):
                return section_type

        # 检查带编号的章节
        if re.match(r'^\d+\.', lower_text):
            return "content"

        # 默认为内容章节
        return "content"

    def _has_sufficient_following_content(self, index: int, elements, min_chars: int = 150) -> bool:
        """检查元素后是否有足够的内容

        Args:
            index: 当前元素索引
            elements: 所有元素列表
            min_chars: 最小字符数要求

        Returns:
            bool: 是否有足够的内容
        """
        total_chars = 0
        for i in range(index + 1, min(index + 5, len(elements))):
            if isinstance(elements[i], Title):
                # 如果紧接着是标题，就停止检查
                break
            if isinstance(elements[i], (Text, NarrativeText, ListItem, Table)):
                total_chars += len(str(elements[i]))
                if total_chars >= min_chars:
                    return True

        return total_chars >= min_chars

    def _extract_content_between(self, elements, start_index: int, end_index: int) -> str:
        """提取指定范围内的内容文本

        Args:
            elements: 元素列表
            start_index: 开始索引
            end_index: 结束索引

        Returns:
            str: 提取的内容文本
        """
        content_parts = []

        for i in range(start_index, end_index):
            if isinstance(elements[i], (Text, NarrativeText, ListItem, Table)):
                content_parts.append(str(elements[i]).strip())

        return "\n\n".join([part for part in content_parts if part])

    def generate_markdown(self, doc: StructuredDocument) -> str:
        """将结构化文档转换为Markdown格式

        Args:
            doc: 结构化文档对象

        Returns:
            str: Markdown格式文本
        """
        md_parts = []

        # 添加标题
        if doc.title:
            md_parts.append(f"# {doc.title}\n")

        # 添加元数据
        if doc.is_paper:
            # 作者信息
            if 'authors' in doc.metadata and doc.metadata['authors']:
                authors_str = ", ".join(doc.metadata['authors'])
                md_parts.append(f"**作者:** {authors_str}\n")

            # 关键词
            if 'keywords' in doc.metadata and doc.metadata['keywords']:
                keywords_str = ", ".join(doc.metadata['keywords'])
                md_parts.append(f"**关键词:** {keywords_str}\n")

            # 摘要
            if 'abstract' in doc.metadata and doc.metadata['abstract']:
                md_parts.append(f"## 摘要\n\n{doc.metadata['abstract']}\n")

        # 添加章节内容
        md_parts.append(self._format_sections_markdown(doc.sections))

        return "\n".join(md_parts)

    def _format_sections_markdown(self, sections: List[DocumentSection], base_level: int = 0) -> str:
        """递归格式化章节为Markdown

        Args:
            sections: 章节列表
            base_level: 基础层级

        Returns:
            str: Markdown格式文本
        """
        md_parts = []

        for section in sections:
            # 计算标题级别 (确保不超过6级)
            header_level = min(section.level + base_level + 1, 6)

            # 添加标题和内容
            if section.title:
                md_parts.append(f"{'#' * header_level} {section.title}\n")

            if section.content:
                md_parts.append(f"{section.content}\n")

            # 递归处理子章节
            if section.subsections:
                md_parts.append(self._format_sections_markdown(
                    section.subsections, base_level
                ))

        return "\n".join(md_parts)
