from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Dict, Union, List, Tuple, Any
from dataclasses import dataclass, field
import logging
import os
import re

from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Text, Title, NarrativeText, ListItem, Table,
    Footer, Header, PageBreak, Image, Address
)

# 引入元数据提取器
from crazy_functions.doc_fns.read_fns.unstructured_all.paper_metadata_extractor import PaperMetadata, PaperMetadataExtractor


@dataclass
class PaperSection:
    """论文章节数据类"""
    section_type: str  # 章节类型，如"abstract", "introduction", "method", "result", "discussion", "conclusion", "references"等
    title: str  # 章节标题
    content: str  # 章节内容
    level: int = 0  # 标题级别，0为主标题，1为一级标题，以此类推
    subsections: List['PaperSection'] = field(default_factory=list)  # 子章节列表


@dataclass
class Figure:
    """论文图表数据类"""
    id: str  # 图表ID，如"Figure 1"
    caption: str  # 图表标题
    content: str  # 图表描述内容
    position: int  # 在文档中的位置索引


@dataclass
class Formula:
    """论文公式数据类"""
    id: str  # 公式ID，如"(1)"
    content: str  # 公式内容
    position: int  # 在文档中的位置索引


@dataclass
class Reference:
    """参考文献数据类"""
    id: str = ""  # 引用编号，如"[1]"
    text: str = ""  # 完整引用文本
    title: str = ""  # 文献标题
    authors: List[str] = field(default_factory=list)  # 作者列表
    year: str = ""  # 出版年份
    source: str = ""  # 来源（期刊、会议等）


@dataclass
class StructuredPaper:
    """结构化论文数据类"""
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    sections: List[PaperSection] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
    tables: List[Figure] = field(default_factory=list)
    formulas: List[Formula] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    full_text: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class ExtractorConfig:
    """提取器配置类"""
    extract_figures: bool = True
    extract_tables: bool = True
    extract_formulas: bool = True
    extract_references: bool = True
    paragraph_separator: str = '\n\n'
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': True,
        'remove_special_chars': False,
        'lowercase': False
    })


class PaperStructureExtractor:
    """论文结构提取器

    从各种文档格式中提取论文的完整结构化信息，包括元数据、章节结构、图表、公式、参考文献等。
    """

    # 定义论文各部分的关键词模式
    PAPER_SECTION_PATTERNS = {
        'abstract': r'\b(摘要|abstract|summary|概要|résumé|zusammenfassung|аннотация)\b',
        'keywords': r'\b(关键词|keywords|key\s+words|关键字|mots[- ]clés|schlüsselwörter|ключевые слова)\b',
        'introduction': r'\b(引言|介绍|绪论|introduction|background|引言：|概述|einleitung|введение)\b',
        'related_work': r'\b(相关工作|related\s+work|literature\s+review|研究现状|prior\s+work|verwandte arbeiten|предыдущие работы)\b',
        'method': r'\b(方法|材料与方法|methodology|materials\s+and\s+methods|methods|approach|experimental|实验|算法|algorithm|方法：|研究方法|methoden|методы)\b',
        'result': r'\b(结果|results|findings|observations|实验结果|结果与分析|ergebnisse|результаты)\b',
        'discussion': r'\b(讨论|discussion|analysis|interpretation|分析|讨论与分析|diskussion|обсуждение)\b',
        'conclusion': r'\b(结论|总结|conclusion|summary|concluding\s+remarks|结语|总结与展望|schlussfolgerung|заключение)\b',
        'references': r'\b(参考文献|references|bibliography|引用|citation|文献|literatur|литература)\b',
        'acknowledgement': r'\b(致谢|acknowledgement|acknowledgment|鸣谢|acknowledgements|danksagung|благодарности)\b',
        'appendix': r'\b(附录|appendix|supplementary|补充材料|appendices|anhang|приложение)\b',
        'table': r'\b(表\s*\d+|table\s*\d+|tabelle\s*\d+|таблица\s*\d+)\b',
        'figure': r'\b(图\s*\d+|figure\s*\d+|fig.\s*\d+|abbildung\s*\d+|рисунок\s*\d+)\b'
    }

    SUPPORTED_EXTENSIONS = PaperMetadataExtractor.SUPPORTED_EXTENSIONS

    def __init__(self, config: Optional[ExtractorConfig] = None):
        """初始化提取器

        Args:
            config: 提取器配置对象，如果为None则使用默认配置
        """
        self.config = config or ExtractorConfig()
        self.metadata_extractor = PaperMetadataExtractor()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 添加文件处理器
        fh = logging.FileHandler('paper_structure_extractor.log')
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

    def _cleanup_text(self, text: str) -> str:
        """清理文本

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        if self.config.text_cleanup['remove_extra_spaces']:
            text = ' '.join(text.split())

        if self.config.text_cleanup['normalize_whitespace']:
            text = text.replace('\t', ' ').replace('\r', '\n')

        if self.config.text_cleanup['remove_special_chars']:
            # 只保留字母、数字、基本标点和中文字符
            text = re.sub(r'[^\w\s.,;:!?，。；：！？、\u4e00-\u9fff]', '', text)

        if self.config.text_cleanup['lowercase']:
            text = text.lower()

        return text.strip()

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式列表"""
        return sorted(PaperStructureExtractor.SUPPORTED_EXTENSIONS)

    def extract_paper_structure(self, file_path: Union[str, Path], strategy: str = "fast") -> StructuredPaper:
        """提取论文的完整结构化信息

        Args:
            file_path: 文件路径
            strategy: 提取策略 ("fast" 或 "accurate")

        Returns:
            StructuredPaper: 结构化的论文数据

        Raises:
            Exception: 提取过程中的错误
        """
        try:
            path = Path(file_path).resolve()
            self.logger.info(f"正在处理论文结构: {path}")

            # 创建结构化论文对象
            paper = StructuredPaper()

            # 提取元数据
            paper.metadata = self.metadata_extractor.extract_metadata(path, strategy)

            # 使用unstructured库分解文档
            elements = partition(
                str(path),
                strategy=strategy,
                include_metadata=True,
                nlp=False,
            )

            # 提取关键词
            paper.keywords = paper.metadata.keywords

            # 提取章节结构
            paper.sections = self._extract_sections(elements)

            # 提取图表
            if self.config.extract_figures:
                paper.figures, paper.tables = self._extract_figures_and_tables(elements)

            # 提取公式
            if self.config.extract_formulas:
                paper.formulas = self._extract_formulas(elements)

            # 提取参考文献
            if self.config.extract_references:
                paper.references = self._extract_references(elements)

            # 提取完整文本
            paper.full_text = self._extract_full_text(elements)

            return paper

        except Exception as e:
            self.logger.error(f"结构提取失败: {e}")
            raise

    def _extract_sections(self, elements) -> List[PaperSection]:
        """提取论文的章节结构

        Args:
            elements: 文档元素列表

        Returns:
            List[PaperSection]: 章节列表
        """
        # 第一遍：识别所有标题元素
        title_elements = []
        for i, element in enumerate(elements):
            if isinstance(element, Title):
                title_text = str(element).strip()

                # 添加过滤条件，排除非章节标题
                if self._is_likely_section_title(title_text, element, i, elements):
                    section_type = self._identify_section_type(title_text)
                    level = self._estimate_title_level(element, elements)
                    title_elements.append((i, title_text, section_type, level, element))

        # 按层级排序，确保层级低的（数字大的）在后面
        title_elements.sort(key=lambda x: (x[0], x[3]))

        # 第二遍：创建章节内容
        sections = []
        for i, (index, title_text, section_type, level, element) in enumerate(title_elements):
            # 提取章节内容
            content = ""
            if i < len(title_elements) - 1:
                # 提取到下一章节开始
                next_index = title_elements[i+1][0]
                content = self._extract_content_between_indices(elements, index+1, next_index)
            else:
                # 提取到文档结束
                content = self._extract_content_after_index(elements, index+1)

            # 创建章节对象
            section = PaperSection(
                section_type=section_type,
                title=title_text,
                content=content,
                level=level,
                subsections=[]
            )
            sections.append(section)

        # 构建章节层次结构
        hierarchical_sections = self._build_section_hierarchy(sections)
        return hierarchical_sections

    def _is_likely_section_title(self, title_text: str, element, index: int, elements) -> bool:
        """判断标题是否可能是章节标题"""
        title_lower = title_text.lower()

        # 首先检查是否在参考文献部分
        if self._is_in_references_section(index, elements):
            # 参考文献部分的标题处理策略：
            # 1. 只有特定格式的标题才被接受
            # 2. 通常参考文献中的内容不应被识别为标题

            # 检查是否是有效的参考文献标题格式
            valid_ref_title_patterns = [
                r'^references$',
                r'^bibliography$',
                r'^参考文献$',
                r'^\d+\.\s*references$',
                r'^文献$',
                r'^引用文献$'
            ]

            is_valid_ref_title = any(re.match(pattern, title_lower) for pattern in valid_ref_title_patterns)

            # 在参考文献部分，除非是明确的子分类标题，否则都不认为是标题
            if not is_valid_ref_title:
                # 检查特定格式：常见的参考文献子类别
                ref_subcategory_patterns = [
                    r'^primary\s+sources$',
                    r'^secondary\s+sources$',
                    r'^books$',
                    r'^journals$',
                    r'^conference\s+papers$',
                    r'^web\s+sources$',
                    r'^further\s+reading$',
                    r'^monographs$'
                ]

                is_ref_subcategory = any(re.match(pattern, title_lower) for pattern in ref_subcategory_patterns)

                # 如果不是子类别标题，在参考文献部分很可能不是标题
                if not is_ref_subcategory:
                    # 检查是否包含出版物特征（会议、期刊、年份等）
                    pub_features = [
                        r'conference', r'proceedings', r'journal', r'transactions',
                        r'symposium', r'workshop', r'international', r'annual',
                        r'\d{4}', r'pp\.', r'vol\.', r'pages', r'ieee', r'acm'
                    ]

                    has_pub_features = any(re.search(pattern, title_lower) for pattern in pub_features)

                    if has_pub_features:
                        return False

                    # 检查文本长度和格式特征
                    if len(title_text) > 50 or title_text.count(' ') > 10:
                        return False

                    # 检查是否包含DOI、arXiv等标识
                    if re.search(r'doi|arxiv|http|url|issn|isbn', title_lower):
                        return False

        # 检查是否为数学表达式（例如"max θ"）- 保留现有的模式检测
        math_expr_patterns = [
            r'^(max|min|sup|inf|lim|arg\s*max|arg\s*min)\s+[a-zA-Z\u0370-\u03FF\u0400-\u04FF θΘ]+$',
            r'^E\s*\(',  # 期望值表达式开头
            r'^∑|∏|∫|∂|∇|∆',  # 以数学符号开头
            r'^\s*\([a-zA-Z0-9]\)\s*$',  # 如 (a), (1) 等单个字母/数字的标识
        ]

        # 如果匹配任何数学表达式模式，不太可能是章节标题
        for pattern in math_expr_patterns:
            if re.search(pattern, title_text):
                return False

        # 检查标题文本本身是否过短（短标题通常不是章节标题，除非是明确的关键词）
        if len(title_text) < 4 and not re.match(r'^(abstract|introduction|methods?|results?|discussion|conclusion|references)$', title_lower, re.IGNORECASE):
            return False

        # 标题中包含括号、大量符号等可能是公式
        if re.search(r'[)}]n$|[([{)\]}].*[([{)\]}]|\d+[=><≥≤]|[a-z]\s*=', title_text):
            return False

        # =================== 增强后续内容长度检查 ===================
        # 查找下一个非空元素
        next_elements = []
        total_followup_content = ""
        next_title_index = -1

        # 收集标题后的内容，直到遇到另一个标题或超过限制
        for i in range(index+1, min(index+10, len(elements))):
            if str(elements[i]).strip():
                next_elements.append(elements[i])
                if not isinstance(elements[i], Title):
                    total_followup_content += str(elements[i])
                else:
                    next_title_index = i
                    break

        # 核心检查：标题后内容长度判断
        # 1. 如果后面没有内容，这不太可能是标题
        if not next_elements:
            return False

        # 2. 如果后面第一个元素不是标题但内容很短(少于100字符)
        if next_elements and not isinstance(next_elements[0], Title):
            first_element_length = len(str(next_elements[0]))
            # 检查是否存在第二个非标题元素，如果没有或内容同样很短
            if (len(next_elements) == 1 or
                (len(next_elements) > 1 and not isinstance(next_elements[1], Title) and
                 len(str(next_elements[1])) < 50)):
                # 如果后续内容总长度小于阈值，可能不是真正的标题
                if first_element_length < 100 and len(total_followup_content) < 150:
                    # 只有常见章节标题可以例外
                    section_type = self._identify_section_type(title_text)
                    main_sections = ['abstract', 'introduction', 'method', 'result',
                                   'discussion', 'conclusion', 'references', 'acknowledgement']
                    if section_type not in main_sections:
                        # 额外检查：如果紧接着的内容包含数学符号，更可能是公式的一部分
                        if re.search(r'[+\-*/=<>≤≥≈≠∑∏∫∂√∞∝∇≡∀∃∄⊂⊃∈∉]|i\s*=|x\s*[ij]|y\s*[ij*]|\(\d+\)', str(next_elements[0])):
                            return False
                        # 检查标题文本是否包含可疑的数学符号或编号
                        if re.search(r'[(){}\[\]∑∏∫i]|^\w{1,2}$', title_text):
                            return False

                        # 最后根据总体内容长度判断
                        if len(total_followup_content) < 150:
                            return False

        # 3. 如果后面第一个元素是标题，检查级别关系
        elif next_elements and isinstance(next_elements[0], Title):
            # 获取当前和下一个标题的级别
            current_level = self._estimate_title_level(element, elements)
            next_level = self._estimate_title_level(next_elements[0], elements)

            # 如果下一个标题级别不是子标题(级别更大)，当前标题可能是有问题的
            if next_level <= current_level:
                # 检查前后是否有更多数学内容
                if self._surrounding_has_math_symbols(index, elements):
                    return False

                # 对于非主要章节标题特别严格
                section_type = self._identify_section_type(title_text)
                if section_type not in ['abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references']:
                    # 检查标题文本是否匹配常见章节编号模式
                    if not re.match(r'^\d+(\.\d+)*\.\s+', title_text):
                        return False

        # 定义明确的非章节标题模式
        non_section_patterns = [
            r'received|accepted|submitted|revised|published',
            r'key\s*words|keywords',
            r'^(table|表)\s*\d+',
            r'^(figure|fig\.|图)\s*\d+',
            r'^p[- ]value',  # P值通常不是章节
            r'^(age|sex|gender|stage)(\s+|:)',  # 表格中的变量名
            r'male\s+female',  # 表格内容
            r'≤|≥',  # 表格中的比较符号
            r'^not applicable\.?$',  # "Not applicable" 文本
            r'^[t](\d+)',  # T1, T2等肿瘤分期不是章节
            r'^[nm](\d+)',  # N0, M1等肿瘤分期不是章节
        ]

        # 如果匹配任何非章节模式，返回False
        for pattern in non_section_patterns:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return False

        # 检查是否为表格内容的更强化逻辑

        # 1. 检查前后文本模式 - 表格行通常有一定的模式

        # 检查前面的元素 - 如果前面几个元素都是Title且长度相似，可能是表格
        similar_title_count = 0
        if index > 1:
            for i in range(max(0, index-5), index):
                if isinstance(elements[i], Title):
                    prev_title_text = str(elements[i]).strip()
                    # 检查长度是否相似
                    if 0.7 <= len(prev_title_text) / len(title_text) <= 1.3:
                        similar_title_count += 1
                    # 检查格式是否相似(例如都是由空格分隔的几个词)
                    if len(prev_title_text.split()) == len(title_text.split()):
                        similar_title_count += 1

        # 检查后面的元素 - 如果后面几个元素都是Title且长度相似，可能是表格
        if index < len(elements) - 1:
            for i in range(index+1, min(index+5, len(elements))):
                if isinstance(elements[i], Title):
                    next_title_text = str(elements[i]).strip()
                    # 检查长度是否相似
                    if 0.7 <= len(next_title_text) / len(title_text) <= 1.3:
                        similar_title_count += 1
                    # 检查格式是否相似
                    if len(next_title_text.split()) == len(title_text.split()):
                        similar_title_count += 1

        # 如果周围有多个相似的Title元素，可能是表格内容
        if similar_title_count >= 4:
            return False

        # 2. 检查内容特征 - 表格行通常有特定的特征

        # 检查是否像表格数据行
        if len(title_text) < 40:  # 表格行通常不会太长
            words = title_text.split()

            # 表格可能格式: "项目 数值 数值" 或 "组别 n 百分比" 等
            if 2 <= len(words) <= 6:
                # 检查是否包含数字或百分比 - 表格行特征
                has_numbers = any(re.search(r'\d', word) for word in words)
                has_percentages = '%' in title_text

                # 检查短词占比 - 表格行通常是短词
                short_words_ratio = sum(1 for word in words if len(word) <= 5) / len(words)

                # 综合判断
                if (has_numbers or has_percentages) and short_words_ratio > 0.6:
                    # 再检查内容长度 - 表格行后通常没有长内容
                    followup_content_length = self._calculate_followup_content_length(index, elements, max_elements=3)
                    if followup_content_length < 100:
                        return False

        # 3. 检查前后内容长度

        # 计算前面内容长度
        preceding_content_length = 0
        for i in range(max(0, index-3), index):
            if isinstance(elements[i], (Text, NarrativeText)):
                preceding_content_length += len(str(elements[i]))

        # 计算后面内容长度
        followup_content_length = self._calculate_followup_content_length(index, elements)

        # 真正的章节标题前面通常是另一章节的结尾(有少量文本)或文档开始，后面有大量文本
        if preceding_content_length > 200 and followup_content_length < 150:
            # 如果前面有大量文本，后面文本很少，可能不是章节标题
            return False

        # 标题应该有足够长的后续内容(除非是参考文献等特殊章节)
        section_type = self._identify_section_type(title_text)
        main_sections = ['abstract', 'introduction', 'method', 'result',
                        'discussion', 'conclusion', 'references', 'acknowledgement']

        if section_type in ['references', 'acknowledgement']:
            return True  # 特殊章节不需要内容长度检查

        # 其他章节，根据章节类型和编号情况进行判断
        if section_type in main_sections:
            return followup_content_length >= 200  # 主要章节要求200字符以上
        elif re.match(r'^\d+(\.\d+)*\.?\s+', title_text):  # 带编号的章节
            return followup_content_length >= 150  # 编号章节要求150字符以上
        else:
            return followup_content_length >= 300  # 其他可能章节要求300字符以上

    def _calculate_followup_content_length(self, index: int, elements, max_elements: int = 10) -> int:
        """计算标题后面的内容长度

        Args:
            index: 标题在元素列表中的索引
            elements: 所有元素列表
            max_elements: 最多检查后续多少个元素

        Returns:
            int: 内容长度
        """
        content_length = 0
        for i in range(index + 1, min(index + max_elements + 1, len(elements))):
            if isinstance(elements[i], Title):
                # 如果遇到另一个标题，停止计算
                break
            if isinstance(elements[i], (Text, NarrativeText)):
                content_length += len(str(elements[i]))
        return content_length

    def _identify_section_type(self, title_text: str) -> str:
        """根据标题文本识别章节类型"""
        title_lower = title_text.lower()

        for section_type, pattern in self.PAPER_SECTION_PATTERNS.items():
            if re.search(pattern, title_lower):
                return section_type

        # 尝试识别编号章节
        if re.match(r'^(\d+\.|\d+\s+)', title_lower):
            # 如果是数字开头，可能是正文章节
            return "content"

        return "other"

    def _estimate_title_level(self, title_element, all_elements) -> int:
        """估计标题的层级"""
        title_text = str(title_element).strip()

        # 通过标题文本中的编号格式判断层级
        # 查找诸如 "1."、"1.1"、"1.1.1" 等模式
        level_patterns = [
            (r'^(\d+\.?\s+)', 1),  # 1. 或 1 开头为一级标题
            (r'^(\d+\.\d+\.?\s+)', 2),  # 1.1. 或 1.1 开头为二级标题
            (r'^(\d+\.\d+\.\d+\.?\s+)', 3),  # 1.1.1. 或 1.1.1 开头为三级标题
            (r'^(\d+\.\d+\.\d+\.\d+\.?\s+)', 4),  # 1.1.1.1. 或 1.1.1.1 开头为四级标题
        ]

        for pattern, level in level_patterns:
            if re.match(pattern, title_text):
                return level

        # 检查标题是否是常见的主要章节标题
        main_sections = {'abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references'}
        if self._identify_section_type(title_text) in main_sections:
            return 1

        # 检查字体大小（如果元数据中有）
        if hasattr(title_element, 'metadata') and title_element.metadata:
            try:
                # 尝试获取字体大小信息
                font_size = getattr(title_element.metadata, 'font_size', None)
                if font_size is not None:
                    # 根据字体大小确定层级（较大字体为较低层级）
                    if font_size > 16:
                        return 1
                    elif font_size > 14:
                        return 2
                    else:
                        return 3
            except (AttributeError, TypeError):
                pass

        # 默认为1级标题
        return 1

    def _extract_content_between_indices(self, elements, start_index: int, end_index: int) -> str:
        """提取指定索引范围内的内容"""
        content_parts = []

        for i in range(start_index, end_index):
            element = elements[i]
            if isinstance(element, (Text, NarrativeText, ListItem, Table)):
                content_parts.append(self._cleanup_text(str(element)))

        return self.config.paragraph_separator.join(content_parts)

    def _extract_content_after_index(self, elements, start_index: int) -> str:
        """提取从指定索引到文档结束的内容"""
        content_parts = []

        for i in range(start_index, len(elements)):
            element = elements[i]
            if isinstance(element, (Text, NarrativeText, ListItem, Table)):
                content_parts.append(self._cleanup_text(str(element)))

        return self.config.paragraph_separator.join(content_parts)

    def _build_section_hierarchy(self, sections: List[PaperSection]) -> List[PaperSection]:
        """构建章节的层次结构"""
        if not sections:
            return []

        # 按层级排序
        root_sections = []
        current_parents = {0: None}  # 每个层级的当前父节点

        for section in sections:
            # 找到当前节点的父节点
            parent_level = None
            for level in sorted([k for k in current_parents.keys() if k < section.level], reverse=True):
                parent_level = level
                break

            if parent_level is None:
                # 顶级节点
                root_sections.append(section)
            else:
                # 添加为子节点
                parent = current_parents[parent_level]
                if parent:
                    parent.subsections.append(section)
                else:
                    root_sections.append(section)

            # 更新当前层级的父节点
            current_parents[section.level] = section

            # 清除所有更深层级的父节点缓存
            deeper_levels = [k for k in current_parents.keys() if k > section.level]
            for level in deeper_levels:
                current_parents.pop(level, None)

        return root_sections

    def _extract_figures_and_tables(self, elements) -> Tuple[List[Figure], List[Figure]]:
        """提取文档中的图表信息"""
        figures = []
        tables = []

        for i, element in enumerate(elements):
            element_text = str(element).strip()

            # 查找图表标识
            fig_match = re.match(r'^(figure|fig\.|图)\s*(\d+)[.:](.*)', element_text, re.IGNORECASE)
            table_match = re.match(r'^(table|表)\s*(\d+)[.:](.*)', element_text, re.IGNORECASE)

            if fig_match:
                fig_id = f"{fig_match.group(1)} {fig_match.group(2)}"
                caption = fig_match.group(3).strip()

                # 查找图表描述（通常在图表标识下方）
                description = ""
                for j in range(i+1, min(i+5, len(elements))):
                    next_text = str(elements[j]).strip()
                    if isinstance(elements[j], (Title, Table)) or re.match(r'^(figure|fig\.|table|图|表)\s*\d+', next_text, re.IGNORECASE):
                        break
                    description += next_text + " "

                figures.append(Figure(
                    id=fig_id,
                    caption=caption,
                    content=description.strip(),
                    position=i
                ))

            elif table_match:
                table_id = f"{table_match.group(1)} {table_match.group(2)}"
                caption = table_match.group(3).strip()

                # 对于表格，尝试获取表格内容
                table_content = ""
                if i+1 < len(elements) and isinstance(elements[i+1], Table):
                    table_content = str(elements[i+1])

                tables.append(Figure(
                    id=table_id,
                    caption=caption,
                    content=table_content,
                    position=i
                ))

            # 检查元素本身是否为表格
            elif isinstance(element, Table):
                # 查找表格标题（通常在表格之前）
                caption = ""
                if i > 0:
                    prev_text = str(elements[i-1]).strip()
                    if re.match(r'^(table|表)\s*\d+', prev_text, re.IGNORECASE):
                        caption = prev_text

                if not caption:
                    caption = f"Table {len(tables) + 1}"

                tables.append(Figure(
                    id=f"Table {len(tables) + 1}",
                    caption=caption,
                    content=element_text,
                    position=i
                ))

            # 检查元素本身是否为图片
            elif isinstance(element, Image):
                # 查找图片标题（通常在图片之前或之后）
                caption = ""
                for j in range(max(0, i-2), min(i+3, len(elements))):
                    if j != i:
                        j_text = str(elements[j]).strip()
                        if re.match(r'^(figure|fig\.|图)\s*\d+', j_text, re.IGNORECASE):
                            caption = j_text
                            break

                if not caption:
                    caption = f"Figure {len(figures) + 1}"

                figures.append(Figure(
                    id=f"Figure {len(figures) + 1}",
                    caption=caption,
                    content="[Image]",
                    position=i
                ))

        return figures, tables

    def _surrounding_has_math_symbols(self, index: int, elements, window: int = 3) -> bool:
        """检查周围元素是否包含较多数学符号

        Args:
            index: 当前元素索引
            elements: 所有元素
            window: 检查的窗口大小

        Returns:
            bool: 是否包含较多数学符号
        """
        math_symbols = r'[+\-*/=<>≤≥≈≠∑∏∫∂√∞∝∇≡∀∃∄⊂⊃∈∉θΘαβγδ\[\]\{\}]'

        # 检查前后各window个元素
        start = max(0, index - window)
        end = min(len(elements), index + window + 1)

        math_symbol_count = 0
        total_text = ""

        for i in range(start, end):
            if i == index:
                continue  # 跳过当前元素

            if isinstance(elements[i], (Text, NarrativeText, Title)):
                text = str(elements[i])
                total_text += text
                math_symbol_count += len(re.findall(math_symbols, text))

        # 计算数学符号密度
        if total_text:
            density = math_symbol_count / len(total_text)
            return density > 0.05  # 如果密度超过5%，认为是数学内容

        return False

    def _extract_formulas(self, elements) -> List[Formula]:
        """提取文档中的公式"""
        formulas = []
        formula_pattern = r'^\s*\((\d+)\)\s*'

        # 标记可能是标题但实际是公式的索引
        formula_title_indices = set()

        # 第一遍：识别可能被误解为标题的公式
        for i, element in enumerate(elements):
            if isinstance(element, Title):
                title_text = str(element).strip()

                # 检查是否符合数学表达式模式
                math_expr_patterns = [
                    r'^(max|min|sup|inf|lim|arg\s*max|arg\s*min)\s+[a-zA-Z\u0370-\u03FF\u0400-\u04FF θΘ]+$',
                    r'^E\s*\(',  # 期望值表达式
                    r'^∑|∏|∫|∂|∇|∆',  # 以数学符号开头
                ]

                is_math_expr = any(re.search(pattern, title_text) for pattern in math_expr_patterns)

                if is_math_expr:
                    # 判断是否是真正的标题
                    # 1. 检查后面元素的长度
                    next_is_short = False
                    for j in range(i+1, min(i+3, len(elements))):
                        if isinstance(elements[j], (Text, NarrativeText)) and len(str(elements[j])) < 50:
                            next_is_short = True
                            break

                    # 2. 检查周围是否有数学符号
                    surrounding_has_math = self._surrounding_has_math_symbols(i, elements)

                    if next_is_short or surrounding_has_math:
                        formula_title_indices.add(i)

        # 第二遍：提取所有公式，包括被误识别为标题的公式
        for i, element in enumerate(elements):
            element_text = str(element).strip()
            is_formula = False
            formula_id = ""

            # 处理被误识别为标题的公式
            if i in formula_title_indices:
                is_formula = True
                formula_id = f"Formula-{len(formulas)+1}"
            else:
                # 常规公式识别逻辑，与之前相同
                formula_match = re.match(formula_pattern, element_text)

                if formula_match:
                    formula_id = f"({formula_match.group(1)})"
                    # 移除公式编号
                    element_text = re.sub(formula_pattern, '', element_text)
                    is_formula = True

            if is_formula:
                # 检查后续元素是否需要合并（例如，如果标题是"max θ"，后面元素通常是公式的其余部分）
                merged_content = element_text
                j = i + 1
                while j < min(i+3, len(elements)):
                    next_elem = elements[j]
                    next_text = str(next_elem).strip()

                    # 如果下一个元素很短且包含数学符号，可能是公式的一部分
                    if len(next_text) < 50 and re.search(r'[+\-*/=<>≤≥≈≠∑∏∫∂√∞∝∇≡]', next_text):
                        merged_content += " " + next_text
                        j += 1
                    else:
                        break

                formulas.append(Formula(
                    id=formula_id,
                    content=merged_content,
                    position=i
                ))

        return formulas

    def _extract_references(self, elements) -> List[Reference]:
        """提取文档中的参考文献"""
        references = []

        # 首先找到参考文献部分
        ref_section_start = -1
        for i, element in enumerate(elements):
            if isinstance(element, Title) and re.search(self.PAPER_SECTION_PATTERNS['references'], str(element), re.IGNORECASE):
                ref_section_start = i
                break

        if ref_section_start == -1:
            # 没有找到明确的参考文献部分，尝试在文档末尾寻找
            # 参考文献通常在文档的最后20%
            start_pos = int(len(elements) * 0.8)
            for i in range(start_pos, len(elements)):
                element_text = str(elements[i]).strip()
                # 常见的参考文献格式特征
                if re.match(r'^\[\d+\]|\(\d+\)|^\d+\.\s+[A-Z]', element_text):
                    ref_section_start = i
                    break

        if ref_section_start != -1:
            # 提取参考文献列表
            current_ref = None
            inside_ref = False  # 标记是否在一个参考文献项内

            for i in range(ref_section_start + 1, len(elements)):
                element = elements[i]

                # 忽略标题元素 - 这些可能是错误识别的参考文献部分
                if isinstance(element, Title):
                    # 检查是否是真正的参考文献部分结束标题
                    title_text = str(element).lower().strip()
                    if re.search(r'^(appendix|appendices|supplementary|acknowledgements?|附录|致谢)$', title_text):
                        # 遇到下一个主要章节，结束参考文献提取
                        break

                    # 对于可能是参考文献一部分的标题，将其内容合并到当前参考文献
                    if current_ref and inside_ref:
                        current_ref.text += " " + str(element)
                        continue

                element_text = str(element).strip()
                if not element_text:
                    continue

                # 检查是否是新的参考文献条目
                ref_start_match = re.match(r'^\[(\d+)\]|\((\d+)\)|^(\d+)\.\s+', element_text)

                if ref_start_match:
                    # 如果已有参考文献，保存它
                    if current_ref and current_ref.text:
                        references.append(current_ref)
                        inside_ref = False

                    # 提取引用ID
                    ref_id = ""
                    if ref_start_match.group(1):  # [1] 格式
                        ref_id = f"[{ref_start_match.group(1)}]"
                        # 移除ID前缀
                        element_text = re.sub(r'^\[\d+\]\s*', '', element_text)
                    elif ref_start_match.group(2):  # (1) 格式
                        ref_id = f"({ref_start_match.group(2)})"
                        # 移除ID前缀
                        element_text = re.sub(r'^\(\d+\)\s*', '', element_text)
                    elif ref_start_match.group(3):  # 1. 格式
                        ref_id = f"{ref_start_match.group(3)}."
                        # 移除ID前缀
                        element_text = re.sub(r'^\d+\.\s+', '', element_text)

                    # 创建新的参考文献
                    current_ref = Reference(id=ref_id, text=element_text)
                    inside_ref = True

                    # 尝试提取作者和年份
                    author_year_match = re.match(r'^([^,]+),\s*(?:\()?(\d{4})(?:\))?', element_text)
                    if author_year_match:
                        authors_text = author_year_match.group(1).strip()
                        # 尝试分割多个作者
                        authors = [a.strip() for a in re.split(r',|and|&|；|、|等', authors_text) if a.strip()]
                        current_ref.authors = authors
                        current_ref.year = author_year_match.group(2)

                elif current_ref and inside_ref:
                    # 继续当前参考文献
                    current_ref.text += " " + element_text

            # 添加最后一个参考文献
            if current_ref and current_ref.text:
                references.append(current_ref)

        return references

    def _extract_full_text(self, elements) -> str:
        """提取文档的完整文本"""
        text_parts = []

        for element in elements:
            if isinstance(element, (Text, NarrativeText, Title, ListItem, Table)):
                text = str(element).strip()
                if text:
                    text_parts.append(self._cleanup_text(text))

        return self.config.paragraph_separator.join(text_parts)

    def generate_markdown(self, paper: StructuredPaper) -> str:
        """将论文结构化数据转换为Markdown格式

        Args:
            paper: 结构化论文数据对象

        Returns:
            str: 完整的Markdown格式论文文本
        """
        md_parts = []

        # 标题和作者信息
        md_parts.append(f"# {paper.metadata.title}\n")

        if paper.metadata.authors:
            authors_str = ", ".join(paper.metadata.authors)
            md_parts.append(f"**作者:** {authors_str}\n")

        # 发表信息
        pub_info = []
        if hasattr(paper.metadata, 'journal') and paper.metadata.journal:
            pub_info.append(paper.metadata.journal)
        if hasattr(paper.metadata, 'publication_date') and paper.metadata.publication_date:
            pub_info.append(paper.metadata.publication_date)
        elif hasattr(paper.metadata, 'date') and paper.metadata.date:
            pub_info.append(paper.metadata.date)
        elif hasattr(paper.metadata, 'year') and paper.metadata.year:
            pub_info.append(paper.metadata.year)

        if pub_info:
            md_parts.append(f"**发表信息:** {', '.join(pub_info)}\n")

        # DOI和URL
        if hasattr(paper.metadata, 'doi') and paper.metadata.doi:
            md_parts.append(f"**DOI:** {paper.metadata.doi}\n")
        if hasattr(paper.metadata, 'url') and paper.metadata.url:
            md_parts.append(f"**URL:** {paper.metadata.url}\n")

        # 摘要
        abstract_section = next((s for s in paper.sections if s.section_type == 'abstract'), None)
        if abstract_section:
            md_parts.append(f"## 摘要\n\n{abstract_section.content}\n")
        elif hasattr(paper.metadata, 'abstract') and paper.metadata.abstract:
            md_parts.append(f"## 摘要\n\n{paper.metadata.abstract}\n")

        # 关键词
        if paper.keywords:
            md_parts.append(f"**关键词:** {', '.join(paper.keywords)}\n")

        # 章节内容
        md_parts.append(self._format_sections_markdown(paper.sections))

        # 图表
        if paper.figures:
            md_parts.append("## 图\n")
            for fig in paper.figures:
                md_parts.append(f"### {fig.id}: {fig.caption}\n\n{fig.content}\n")

        if paper.tables:
            md_parts.append("## 表\n")
            for table in paper.tables:
                md_parts.append(f"### {table.id}: {table.caption}\n\n{table.content}\n")

        # 公式
        if paper.formulas:
            md_parts.append("## 公式\n")
            for formula in paper.formulas:
                # 使用代码块包装公式内容，而不是作为标题
                formatted_content = self._format_formula_content(formula.content)
                md_parts.append(f"**{formula.id}**\n\n```math\n{formatted_content}\n```\n")

        # 参考文献
        if paper.references:
            md_parts.append("## 参考文献\n")
            for ref in paper.references:
                md_parts.append(f"{ref.id} {ref.text}\n")

        return "\n".join(md_parts)

    def _format_sections_markdown(self, sections: List[PaperSection], level: int = 0) -> str:
        """递归格式化章节内容为Markdown

        Args:
            sections: 章节列表
            level: 当前章节级别

        Returns:
            str: 格式化后的Markdown文本
        """
        if not sections:
            return ""

        md_parts = []
        for section in sections:
            # 计算标题级别（注意Markdown最多支持6级标题）
            header_level = min(section.level + 2, 6)  # +2是因为文章标题是h1，摘要是h2
            header_marks = '#' * header_level

            # 忽略已经作为摘要处理的部分
            if level == 0 and section.section_type == 'abstract':
                continue

            # 添加章节标题和内容
            md_parts.append(f"{header_marks} {section.title}\n")
            if section.content:
                md_parts.append(f"{section.content}\n")

            # 递归处理子章节
            if section.subsections:
                md_parts.append(self._format_sections_markdown(
                    section.subsections, level + 1))

        return "\n".join(md_parts)

    def _format_formula_content(self, content: str) -> str:
        """
        格式化公式内容，确保不会被误解为Markdown语法

        Args:
            content: 原始公式内容

        Returns:
            str: 格式化后的公式内容
        """
        # 移除可能导致Markdown格式错误的前缀
        content = re.sub(r'^#+\s*', '', content)

        # 清理(cid:X)这样的特殊字符序列，这些通常是PDF解析错误
        content = re.sub(r'\(cid:\d+\)', '', content)

        # 将多行公式合并成单行（如果需要）
        content = re.sub(r'\s*\n\s*', ' ', content)

        # 如果公式包含"max"、"min"等关键字，确保它们不被分割
        # 这里特别处理类似"max θ"的情况
        content = re.sub(r'(max|min|sup|inf|lim|arg\s*max|arg\s*min)\s+([a-zA-Z\u0370-\u03FF\u0400-\u04FF]+)', r'\1_{\2}', content)

        return content.strip()

    def _is_in_references_section(self, index: int, elements) -> bool:
        """判断元素是否位于参考文献部分

        Args:
            index: 当前元素索引
            elements: 所有元素列表

        Returns:
            bool: 是否在参考文献部分
        """
        # 方法1：查找前面是否有明确的参考文献标题
        for i in range(index-1, max(0, index-100), -1):
            if isinstance(elements[i], Title):
                title_text = str(elements[i]).lower().strip()
                if re.search(r'^(references|bibliography|参考文献|引用|文献)(\s|$)', title_text):
                    return True
                # 检查编号形式
                if re.match(r'^\d+\.\s*(references|bibliography|参考文献)', title_text):
                    return True

        # 方法2：基于位置启发式（通常参考文献在论文末尾）
        if index > len(elements) * 0.75:  # 如果在文档后四分之一
            # 搜索前后文本是否包含参考文献特征
            ref_features = 0
            window = 20  # 查看周围20个元素

            start = max(0, index - window)
            end = min(len(elements), index + window)

            for i in range(start, end):
                if i == index:
                    continue

                text = str(elements[i]).lower()

                # 检查参考文献特征
                if re.search(r'\[\d+\]|\(\d{4}\)|et\s+al\.', text):
                    ref_features += 1
                if re.search(r'proceedings|journal|conference|transactions|vol\.|pp\.', text):
                    ref_features += 1
                if re.search(r'doi:|arxiv:|https?://|ieee|acm|springer', text):
                    ref_features += 1

            # 如果周围文本具有足够的参考文献特征
            if ref_features >= 5:
                return True

        return False


def main():
    """主函数：演示用法"""
    # 创建提取器
    extractor = PaperStructureExtractor()

    # 使用示例
    try:
        # 替换为实际的文件路径
        sample_file = '/Users/boyin.liu/Documents/示例文档/论文/3.pdf'
        if Path(sample_file).exists():
            paper = extractor.extract_paper_structure(sample_file)

            print("\n===== 论文结构化信息 =====")
            print(f"标题: {paper.metadata.title}")
            print(f"作者: {', '.join(paper.metadata.authors)}")

            print("\n--- 章节结构 ---")
            for i, section in enumerate(paper.sections):
                print(f"{i+1}. {section.title} ({section.section_type})")
                if section.subsections:
                    for j, subsection in enumerate(section.subsections):
                        print(f"   {i+1}.{j+1} {subsection.title}")

            print("\n--- 图表 ---")
            print(f"图: {len(paper.figures)}")
            for i, fig in enumerate(paper.figures[:3]):
                print(f"图 {i+1}: {fig.caption[:50]}...")

            print(f"\n表: {len(paper.tables)}")
            for i, table in enumerate(paper.tables[:3]):
                print(f"表 {i+1}: {table.caption[:50]}...")

            print(f"\n--- 公式: {len(paper.formulas)} ---")
            for i, formula in enumerate(paper.formulas[:3]):
                print(f"公式 {formula.id}: {formula.content[:30]}...")

            print(f"\n--- 参考文献: {len(paper.references)} ---")
            for i, ref in enumerate(paper.references[:5]):
                print(f"{ref.id} {ref.text[:50]}...")

            print("\n--- 摘要 ---")
            abstract_section = next((s for s in paper.sections if s.section_type == 'abstract'), None)
            if abstract_section:
                print(abstract_section.content[:200] + "...")
            else:
                print(paper.metadata.abstract[:200] + "...")

        else:
            print(f"示例文件 {sample_file} 不存在")

        print("\n支持的格式:", extractor.get_supported_formats())

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
