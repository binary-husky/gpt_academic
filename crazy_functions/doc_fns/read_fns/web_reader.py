from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Union
from urllib.parse import urlparse
import logging
import trafilatura
import requests
from pathlib import Path


@dataclass
class WebExtractorConfig:
    """网页内容提取器配置类

    Attributes:
        extract_comments: 是否提取评论
        extract_tables: 是否提取表格
        extract_links: 是否保留链接信息
        paragraph_separator: 段落分隔符
        timeout: 网络请求超时时间(秒)
        max_retries: 最大重试次数
        user_agent: 自定义User-Agent
        text_cleanup: 文本清理选项
    """
    extract_comments: bool = False
    extract_tables: bool = True
    extract_links: bool = False
    paragraph_separator: str = '\n\n'
    timeout: int = 10
    max_retries: int = 3
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': True,
        'remove_special_chars': False,
        'lowercase': False
    })


class WebTextExtractor:
    """网页文本内容提取器

    使用trafilatura库提取网页中的主要文本内容，去除广告、导航等无关内容。
    """

    def __init__(self, config: Optional[WebExtractorConfig] = None):
        """初始化提取器

        Args:
            config: 提取器配置对象，如果为None则使用默认配置
        """
        self.config = config or WebExtractorConfig()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 添加文件处理器
        fh = logging.FileHandler('web_extractor.log')
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

    def _validate_url(self, url: str) -> bool:
        """验证URL格式是否有效

        Args:
            url: 网页URL

        Returns:
            bool: URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _download_webpage(self, url: str) -> Optional[str]:
        """下载网页内容

        Args:
            url: 网页URL

        Returns:
            Optional[str]: 网页HTML内容，失败返回None

        Raises:
            Exception: 下载失败时抛出异常
        """
        headers = {'User-Agent': self.config.user_agent}

        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"Failed to download webpage after {self.config.max_retries} attempts: {e}")
        return None

    def _cleanup_text(self, text: str) -> str:
        """清理文本

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""

        if self.config.text_cleanup['remove_extra_spaces']:
            text = ' '.join(text.split())

        if self.config.text_cleanup['normalize_whitespace']:
            text = text.replace('\t', ' ').replace('\r', '\n')

        if self.config.text_cleanup['lowercase']:
            text = text.lower()

        return text.strip()

    def extract_text(self, url: str) -> str:
        """提取网页文本内容

        Args:
            url: 网页URL

        Returns:
            str: 提取的文本内容

        Raises:
            ValueError: URL无效时抛出
            Exception: 提取失败时抛出
        """
        try:
            if not self._validate_url(url):
                raise ValueError(f"Invalid URL: {url}")

            self.logger.info(f"Processing URL: {url}")

            # 下载网页
            html_content = self._download_webpage(url)
            if not html_content:
                raise Exception("Failed to download webpage")

            # 配置trafilatura提取选项
            extract_config = {
                'include_comments': self.config.extract_comments,
                'include_tables': self.config.extract_tables,
                'include_links': self.config.extract_links,
                'no_fallback': False,  # 允许使用后备提取器
            }

            # 提取文本
            extracted_text = trafilatura.extract(
                html_content,
                **extract_config
            )

            if not extracted_text:
                raise Exception("No content could be extracted")

            # 清理文本
            cleaned_text = self._cleanup_text(extracted_text)

            return cleaned_text

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise


def main():
    """主函数：演示用法"""
    # 配置
    config = WebExtractorConfig(
        extract_comments=False,
        extract_tables=True,
        extract_links=False,
        timeout=10,
        text_cleanup={
            'remove_extra_spaces': True,
            'normalize_whitespace': True,
            'remove_special_chars': False,
            'lowercase': False
        }
    )

    # 创建提取器
    extractor = WebTextExtractor(config)

    # 使用示例
    try:
        # 替换为实际的URL
        sample_url = 'https://arxiv.org/abs/2412.00036'
        text = extractor.extract_text(sample_url)
        print("提取的文本:")
        print(text)

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
