from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Dict, Union, List
from dataclasses import dataclass, field
import logging
import os
import re

from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Text, Title, NarrativeText, ListItem, Table,
    Footer, Header, PageBreak, Image, Address
)


@dataclass
class PaperMetadata:
    """论文元数据类"""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    journal: str = ""
    volume: str = ""
    issue: str = ""
    year: str = ""
    doi: str = ""
    date: str = ""
    publisher: str = ""
    conference: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class ExtractorConfig:
    """元数据提取器配置类"""
    paragraph_separator: str = '\n\n'
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': True,
        'remove_special_chars': False,
        'lowercase': False
    })


class PaperMetadataExtractor:
    """论文元数据提取器

    使用unstructured库从多种文档格式中提取论文的标题、作者、摘要等元数据信息。
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        '.pdf', '.docx', '.doc', '.txt', '.ppt', '.pptx',
        '.xlsx', '.xls', '.md', '.org', '.odt', '.rst',
        '.rtf', '.epub', '.html', '.xml', '.json'
    }

    # 定义论文各部分的关键词模式
    SECTION_PATTERNS = {
        'abstract': r'\b(摘要|abstract|summary|概要|résumé|zusammenfassung|аннотация)\b',
        'keywords': r'\b(关键词|keywords|key\s+words|关键字|mots[- ]clés|schlüsselwörter|ключевые слова)\b',
    }

    def __init__(self, config: Optional[ExtractorConfig] = None):
        """初始化提取器

        Args:
            config: 提取器配置对象，如果为None则使用默认配置
        """
        self.config = config or ExtractorConfig()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 添加文件处理器
        fh = logging.FileHandler('paper_metadata_extractor.log')
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

    def _validate_file(self, file_path: Union[str, Path], max_size_mb: int = 100) -> Path:
        """验证文件

        Args:
            file_path: 文件路径
            max_size_mb: 允许的最大文件大小(MB)

        Returns:
            Path: 验证后的Path对象

        Raises:
            ValueError: 文件不存在、格式不支持或大小超限
            PermissionError: 没有读取权限
        """
        path = Path(file_path).resolve()

        if not path.exists():
            raise ValueError(f"文件不存在: {path}")

        if not path.is_file():
            raise ValueError(f"不是文件: {path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"没有读取权限: {path}")

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(
                f"文件大小 ({file_size_mb:.1f}MB) 超过限制 {max_size_mb}MB"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"不支持的文件格式: {path.suffix}. "
                f"支持的格式: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        return path

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

        if self.config.text_cleanup['lowercase']:
            text = text.lower()

        return text.strip()

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式列表"""
        return sorted(PaperMetadataExtractor.SUPPORTED_EXTENSIONS)

    def extract_metadata(self, file_path: Union[str, Path], strategy: str = "fast") -> PaperMetadata:
        """提取论文元数据

        Args:
            file_path: 文件路径
            strategy: 提取策略 ("fast" 或 "accurate")

        Returns:
            PaperMetadata: 提取的论文元数据

        Raises:
            Exception: 提取过程中的错误
        """
        try:
            path = self._validate_file(file_path)
            self.logger.info(f"正在处理: {path}")

            # 使用unstructured库分解文档
            elements = partition(
                str(path),
                strategy=strategy,
                include_metadata=True,
                nlp=False,
            )

            # 提取元数据
            metadata = PaperMetadata()

            # 提取标题和作者
            self._extract_title_and_authors(elements, metadata)

            # 提取摘要和关键词
            self._extract_abstract_and_keywords(elements, metadata)

            # 提取其他元数据
            self._extract_additional_metadata(elements, metadata)

            return metadata

        except Exception as e:
            self.logger.error(f"元数据提取失败: {e}")
            raise

    def _extract_title_and_authors(self, elements, metadata: PaperMetadata) -> None:
        """从文档中提取标题和作者信息 - 改进版"""
        # 收集所有潜在的标题候选
        title_candidates = []
        all_text = []
        raw_text = []

        # 首先收集文档前30个元素的文本，用于辅助判断
        for i, element in enumerate(elements[:30]):
            if isinstance(element, (Text, Title, NarrativeText)):
                text = str(element).strip()
                if text:
                    all_text.append(text)
                    raw_text.append(text)

        # 打印出原始文本，用于调试
        print("原始文本前10行:")
        for i, text in enumerate(raw_text[:10]):
            print(f"{i}: {text}")

        # 1. 尝试查找连续的标题片段并合并它们
        i = 0
        while i < len(all_text) - 1:
            current = all_text[i]
            next_text = all_text[i + 1]

            # 检查是否存在标题分割情况：一行以冒号结尾，下一行像是标题的延续
            if current.endswith(':') and len(current) < 50 and len(next_text) > 5 and next_text[0].isupper():
                # 合并这两行文本
                combined_title = f"{current} {next_text}"
                # 查找合并前的文本并替换
                all_text[i] = combined_title
                all_text.pop(i + 1)
                # 给合并后的标题很高的分数
                title_candidates.append((combined_title, 15, i))
            else:
                i += 1

        # 2. 首先尝试从标题元素中查找
        for i, element in enumerate(elements[:15]):  # 只检查前15个元素
            if isinstance(element, Title):
                title_text = str(element).strip()
                # 排除常见的非标题内容
                if title_text.lower() not in ['abstract', '摘要', 'introduction', '引言']:
                    # 计算标题分数（越高越可能是真正的标题）
                    score = self._evaluate_title_candidate(title_text, i, element)
                    title_candidates.append((title_text, score, i))

        # 3. 特别处理常见的论文标题格式
        for i, text in enumerate(all_text[:15]):
            # 特别检查"KIMI K1.5:"类型的前缀标题
            if re.match(r'^[A-Z][A-Z0-9\s\.]+(\s+K\d+(\.\d+)?)?:', text):
                score = 12  # 给予很高的分数
                title_candidates.append((text, score, i))

                # 如果下一行也是全大写，很可能是标题的延续
                if i+1 < len(all_text) and all_text[i+1].isupper() and len(all_text[i+1]) > 10:
                    combined_title = f"{text} {all_text[i+1]}"
                    title_candidates.append((combined_title, 15, i))  # 给合并标题更高分数

            # 匹配全大写的标题行
            elif text.isupper() and len(text) > 10 and len(text) < 100:
                score = 10 - i * 0.5  # 越靠前越可能是标题
                title_candidates.append((text, score, i))

        # 对标题候选按分数排序并选取最佳候选
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            metadata.title = title_candidates[0][0]
            title_position = title_candidates[0][2]
            print(f"所有标题候选: {title_candidates[:3]}")
        else:
            # 如果没有找到合适的标题，使用一个备选策略
            for text in all_text[:10]:
                if text.isupper() and len(text) > 10 and len(text) < 200:  # 大写且适当长度的文本
                    metadata.title = text
                    break
            title_position = 0

        # 提取作者信息 - 改进后的作者提取逻辑
        author_candidates = []

        # 1. 特别处理"TECHNICAL REPORT OF"之后的行，通常是作者或团队
        for i, text in enumerate(all_text):
            if "TECHNICAL REPORT" in text.upper() and i+1 < len(all_text):
                team_text = all_text[i+1].strip()
                if re.search(r'\b(team|group|lab)\b', team_text, re.IGNORECASE):
                    author_candidates.append((team_text, 15))

        # 2. 查找包含Team的文本
        for text in all_text[:20]:
            if "Team" in text and len(text) < 30:
                # 这很可能是团队名
                author_candidates.append((text, 12))

        # 添加作者到元数据
        if author_candidates:
            # 按分数排序
            author_candidates.sort(key=lambda x: x[1], reverse=True)

            # 去重
            seen_authors = set()
            for author, _ in author_candidates:
                if author.lower() not in seen_authors and not author.isdigit():
                    seen_authors.add(author.lower())
                    metadata.authors.append(author)

        # 如果没有找到作者，尝试查找隶属机构信息中的团队名称
        if not metadata.authors:
            for text in all_text[:20]:
                if re.search(r'\b(team|group|lab|laboratory|研究组|团队)\b', text, re.IGNORECASE):
                    if len(text) < 50:  # 避免太长的文本
                        metadata.authors.append(text.strip())
                        break

        # 提取隶属机构信息
        for i, element in enumerate(elements[:30]):
            element_text = str(element).strip()
            if re.search(r'(university|institute|department|school|laboratory|college|center|centre|\d{5,}|^[a-zA-Z]+@|学院|大学|研究所|研究院)', element_text, re.IGNORECASE):
                # 可能是隶属机构
                if element_text not in metadata.affiliations and len(element_text) > 10:
                    metadata.affiliations.append(element_text)

    def _evaluate_title_candidate(self, text, position, element):
        """评估标题候选项的可能性分数"""
        score = 0

        # 位置因素：越靠前越可能是标题
        score += max(0, 10 - position) * 0.5

        # 长度因素：标题通常不会太短也不会太长
        if 10 <= len(text) <= 150:
            score += 3
        elif len(text) < 10:
            score -= 2
        elif len(text) > 150:
            score -= 3

        # 格式因素
        if text.isupper():  # 全大写可能是标题
            score += 2
        if re.match(r'^[A-Z]', text):  # 首字母大写
            score += 1
        if ':' in text:  # 标题常包含冒号
            score += 1.5

        # 内容因素
        if re.search(r'\b(scaling|learning|model|approach|method|system|framework|analysis)\b', text.lower()):
            score += 2  # 包含常见的学术论文关键词

        # 避免误判
        if re.match(r'^\d+$', text):  # 纯数字
            score -= 10
        if re.search(r'^(http|www|doi)', text.lower()):  # URL或DOI
            score -= 5
        if len(text.split()) <= 2 and len(text) < 15:  # 太短的短语
            score -= 3

        # 元数据因素(如果有)
        if hasattr(element, 'metadata') and element.metadata:
            # 修复：正确处理ElementMetadata对象
            try:
                # 尝试通过getattr安全地获取属性
                font_size = getattr(element.metadata, 'font_size', None)
                if font_size is not None and font_size > 14:  # 假设标准字体大小是12
                    score += 3

                font_weight = getattr(element.metadata, 'font_weight', None)
                if font_weight == 'bold':
                    score += 2  # 粗体加分
            except (AttributeError, TypeError):
                # 如果metadata的访问方式不正确，尝试其他可能的访问方式
                try:
                    metadata_dict = element.metadata.__dict__ if hasattr(element.metadata, '__dict__') else {}
                    if 'font_size' in metadata_dict and metadata_dict['font_size'] > 14:
                        score += 3
                    if 'font_weight' in metadata_dict and metadata_dict['font_weight'] == 'bold':
                        score += 2
                except Exception:
                    # 如果所有尝试都失败，忽略元数据处理
                    pass

        return score

    def _extract_abstract_and_keywords(self, elements, metadata: PaperMetadata) -> None:
        """从文档中提取摘要和关键词"""
        abstract_found = False
        keywords_found = False
        abstract_text = []

        for i, element in enumerate(elements):
            element_text = str(element).strip().lower()

            # 寻找摘要部分
            if not abstract_found and (
                isinstance(element, Title) and
                re.search(self.SECTION_PATTERNS['abstract'], element_text, re.IGNORECASE)
            ):
                abstract_found = True
                continue

            # 如果找到摘要部分，收集内容直到遇到关键词部分或新章节
            if abstract_found and not keywords_found:
                # 检查是否遇到关键词部分或新章节
                if (
                    isinstance(element, Title) or
                    re.search(self.SECTION_PATTERNS['keywords'], element_text, re.IGNORECASE) or
                    re.match(r'\b(introduction|引言|method|方法)\b', element_text, re.IGNORECASE)
                ):
                    keywords_found = re.search(self.SECTION_PATTERNS['keywords'], element_text, re.IGNORECASE)
                    abstract_found = False  # 停止收集摘要
                else:
                    # 收集摘要文本
                    if isinstance(element, (Text, NarrativeText)) and element_text:
                        abstract_text.append(element_text)

            # 如果找到关键词部分，提取关键词
            if keywords_found and not abstract_found and not metadata.keywords:
                if isinstance(element, (Text, NarrativeText)):
                    # 清除可能的"关键词:"/"Keywords:"前缀
                    cleaned_text = re.sub(r'^\s*(关键词|keywords|key\s+words)\s*[：:]\s*', '', element_text, flags=re.IGNORECASE)

                    # 尝试按不同分隔符分割
                    for separator in [';', '；', ',', '，']:
                        if separator in cleaned_text:
                            metadata.keywords = [k.strip() for k in cleaned_text.split(separator) if k.strip()]
                            break

                    # 如果未能分割，将整个文本作为一个关键词
                    if not metadata.keywords and cleaned_text:
                        metadata.keywords = [cleaned_text]

                    keywords_found = False  # 已提取关键词，停止处理

        # 设置摘要文本
        if abstract_text:
            metadata.abstract = self.config.paragraph_separator.join(abstract_text)

    def _extract_additional_metadata(self, elements, metadata: PaperMetadata) -> None:
        """提取其他元数据信息"""
        for element in elements[:30]:  # 只检查文档前部分
            element_text = str(element).strip()

            # 尝试匹配DOI
            doi_match = re.search(r'(doi|DOI):\s*(10\.\d{4,}\/[a-zA-Z0-9.-]+)', element_text)
            if doi_match and not metadata.doi:
                metadata.doi = doi_match.group(2)

            # 尝试匹配日期
            date_match = re.search(r'(published|received|accepted|submitted):\s*(\d{1,2}\s+[a-zA-Z]+\s+\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})', element_text, re.IGNORECASE)
            if date_match and not metadata.date:
                metadata.date = date_match.group(2)

            # 尝试匹配年份
            year_match = re.search(r'\b(19|20)\d{2}\b', element_text)
            if year_match and not metadata.year:
                metadata.year = year_match.group(0)

            # 尝试匹配期刊/会议名称
            journal_match = re.search(r'(journal|conference):\s*([^,;.]+)', element_text, re.IGNORECASE)
            if journal_match:
                if "journal" in journal_match.group(1).lower() and not metadata.journal:
                    metadata.journal = journal_match.group(2).strip()
                elif not metadata.conference:
                    metadata.conference = journal_match.group(2).strip()


def main():
    """主函数：演示用法"""
    # 创建提取器
    extractor = PaperMetadataExtractor()

    # 使用示例
    try:
        # 替换为实际的文件路径
        sample_file = '/Users/boyin.liu/Documents/示例文档/论文/3.pdf'
        if Path(sample_file).exists():
            metadata = extractor.extract_metadata(sample_file)
            print("提取的元数据:")
            print(f"标题: {metadata.title}")
            print(f"作者: {', '.join(metadata.authors)}")
            print(f"机构: {', '.join(metadata.affiliations)}")
            print(f"摘要: {metadata.abstract[:200]}...")
            print(f"关键词: {', '.join(metadata.keywords)}")
            print(f"DOI: {metadata.doi}")
            print(f"日期: {metadata.date}")
            print(f"年份: {metadata.year}")
            print(f"期刊: {metadata.journal}")
            print(f"会议: {metadata.conference}")
        else:
            print(f"示例文件 {sample_file} 不存在")

        print("\n支持的格式:", extractor.get_supported_formats())

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
