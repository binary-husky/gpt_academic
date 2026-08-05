from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Dict, Union, List
from dataclasses import dataclass, field
import logging
import os

from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Text, Title, NarrativeText, ListItem, Table,
    Footer, Header, PageBreak, Image, Address
)


@dataclass
class TextExtractorConfig:
    """通用文档提取器配置类

    Attributes:
        extract_headers_footers: 是否提取页眉页脚
        extract_tables: 是否提取表格内容
        extract_lists: 是否提取列表内容
        extract_titles: 是否提取标题
        paragraph_separator: 段落之间的分隔符
        text_cleanup: 文本清理选项字典
    """
    extract_headers_footers: bool = False
    extract_tables: bool = True
    extract_lists: bool = True
    extract_titles: bool = True
    paragraph_separator: str = '\n\n'
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': True,
        'remove_special_chars': False,
        'lowercase': False
    })


class UnstructuredTextExtractor:
    """通用文档文本内容提取器

    使用 unstructured 库支持多种文档格式的文本提取，提供统一的接口和配置选项。
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        # 文档格式
        '.pdf', '.docx', '.doc', '.txt',
        # 演示文稿
        '.ppt', '.pptx',
        # 电子表格
        '.xlsx', '.xls', '.csv',
        # 图片
        '.png', '.jpg', '.jpeg', '.tiff',
        # 邮件
        '.eml', '.msg', '.p7s',
        # Markdown
        ".md",
        # Org Mode
        ".org",
        # Open Office
        ".odt",
        # reStructured Text
        ".rst",
        # Rich Text
        ".rtf",
        # TSV
        ".tsv",
        # EPUB
        '.epub',
        # 其他格式
        '.html', '.xml',  '.json',
    }

    def __init__(self, config: Optional[TextExtractorConfig] = None):
        """初始化提取器

        Args:
            config: 提取器配置对象，如果为None则使用默认配置
        """
        self.config = config or TextExtractorConfig()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 添加文件处理器
        fh = logging.FileHandler('text_extractor.log')
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
            raise ValueError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"No read permission: {path}")

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f}MB) exceeds limit of {max_size_mb}MB"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {path.suffix}. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
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

    def _should_extract_element(self, element) -> bool:
        """判断是否应该提取某个元素

        Args:
            element: 文档元素

        Returns:
            bool: 是否应该提取
        """
        if isinstance(element, (Text, NarrativeText)):
            return True

        if isinstance(element, Title) and self.config.extract_titles:
            return True

        if isinstance(element, ListItem) and self.config.extract_lists:
            return True

        if isinstance(element, Table) and self.config.extract_tables:
            return True

        if isinstance(element, (Header, Footer)) and self.config.extract_headers_footers:
            return True

        return False

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式列表"""
        return sorted(UnstructuredTextExtractor.SUPPORTED_EXTENSIONS)

    def extract_text(
            self,
            file_path: Union[str, Path],
            strategy: str = "fast"
    ) -> str:
        """提取文本

        Args:
            file_path: 文件路径
            strategy: 提取策略 ("fast" 或 "accurate")

        Returns:
            str: 提取的文本内容

        Raises:
            Exception: 提取过程中的错误
        """
        try:
            path = self._validate_file(file_path)
            self.logger.info(f"Processing: {path}")

            # 修改这里：添加 nlp=False 参数来禁用 NLTK
            elements = partition(
                str(path),
                strategy=strategy,
                include_metadata=True,
                nlp=True,
            )

            # 其余代码保持不变
            text_parts = []
            for element in elements:
                if self._should_extract_element(element):
                    text = str(element)
                    cleaned_text = self._cleanup_text(text)
                    if cleaned_text:
                        if isinstance(element, (Header, Footer)):
                            prefix = "[Header] " if isinstance(element, Header) else "[Footer] "
                            text_parts.append(f"{prefix}{cleaned_text}")
                        else:
                            text_parts.append(cleaned_text)

            return self.config.paragraph_separator.join(text_parts)

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise



def main():
    """主函数：演示用法"""
    # 配置
    config = TextExtractorConfig(
        extract_headers_footers=True,
        extract_tables=True,
        extract_lists=True,
        extract_titles=True,
        text_cleanup={
            'remove_extra_spaces': True,
            'normalize_whitespace': True,
            'remove_special_chars': False,
            'lowercase': False
        }
    )

    # 创建提取器
    extractor = UnstructuredTextExtractor(config)

    # 使用示例
    try:
        # 替换为实际的文件路径
        sample_file = './crazy_functions/doc_fns/read_fns/paper/2501.12599v1.pdf'
        if Path(sample_file).exists() or True:
            text = extractor.extract_text(sample_file)
            print("提取的文本:")
            print(text)
        else:
            print(f"示例文件 {sample_file} 不存在")

        print("\n支持的格式:", extractor.get_supported_formats())

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
