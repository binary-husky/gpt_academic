from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Dict, Union, List
from dataclasses import dataclass, field
import logging
import os
import re
import subprocess
import tempfile
import shutil

@dataclass
class MarkdownConverterConfig:
    """PDF 到 Markdown 转换器配置类

    Attributes:
        extract_images: 是否提取图片
        extract_tables: 是否尝试保留表格结构
        extract_code_blocks: 是否识别代码块
        extract_math: 是否转换数学公式
        output_dir: 输出目录路径
        image_dir: 图片保存目录路径
        paragraph_separator: 段落之间的分隔符
        text_cleanup: 文本清理选项字典
        docintel_endpoint: Document Intelligence端点URL (可选)
        enable_plugins: 是否启用插件
        llm_client: LLM客户端对象 (例如OpenAI client)
        llm_model: 要使用的LLM模型名称
    """
    extract_images: bool = True
    extract_tables: bool = True
    extract_code_blocks: bool = True
    extract_math: bool = True
    output_dir: str = ""
    image_dir: str = "images"
    paragraph_separator: str = '\n\n'
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': True,
        'remove_special_chars': False,
        'lowercase': False
    })
    docintel_endpoint: str = ""
    enable_plugins: bool = False
    llm_client: Optional[object] = None
    llm_model: str = ""


class MarkdownConverter:
    """PDF 到 Markdown 转换器

    使用 markitdown 库实现 PDF 到 Markdown 的转换，支持多种配置选项。
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        '.pdf',
    }

    def __init__(self, config: Optional[MarkdownConverterConfig] = None):
        """初始化转换器

        Args:
            config: 转换器配置对象，如果为None则使用默认配置
        """
        self.config = config or MarkdownConverterConfig()
        self._setup_logging()

        # 检查是否安装了 markitdown
        self._check_markitdown_installation()

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 添加文件处理器
        fh = logging.FileHandler('markdown_converter.log')
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

    def _check_markitdown_installation(self) -> None:
        """检查是否安装了 markitdown"""
        try:
            # 尝试导入 markitdown 库
            from markitdown import MarkItDown
            self.logger.info("markitdown 库已安装")
        except ImportError:
            self.logger.warning("markitdown 库未安装，尝试安装...")
            try:
                subprocess.check_call(["pip", "install", "markitdown"])
                self.logger.info("markitdown 库安装成功")
                from markitdown import MarkItDown
            except (subprocess.SubprocessError, ImportError):
                self.logger.error("无法安装 markitdown 库，请手动安装")
                self.markitdown_available = False
                return

        self.markitdown_available = True

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
            raise ValueError(f"不是一个文件: {path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"没有读取权限: {path}")

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(
                f"文件大小 ({file_size_mb:.1f}MB) 超过限制 {max_size_mb}MB"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"不支持的格式: {path.suffix}. "
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
        return sorted(MarkdownConverter.SUPPORTED_EXTENSIONS)

    def convert_to_markdown(
            self,
            file_path: Union[str, Path],
            output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """将 PDF 转换为 Markdown

        Args:
            file_path: PDF 文件路径
            output_path: 输出 Markdown 文件路径，如果为 None 则返回内容而不保存

        Returns:
            str: 转换后的 Markdown 内容

        Raises:
            Exception: 转换过程中的错误
        """
        try:
            path = self._validate_file(file_path)
            self.logger.info(f"处理: {path}")

            if not self.markitdown_available:
                raise ImportError("markitdown 库未安装，无法进行转换")

            # 导入 markitdown 库
            from markitdown import MarkItDown

            # 准备输出目录
            if output_path:
                output_path = Path(output_path)
                output_dir = output_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                # 创建临时目录作为输出目录
                temp_dir = tempfile.mkdtemp()
                output_dir = Path(temp_dir)
                output_path = output_dir / f"{path.stem}.md"

            # 图片目录
            image_dir = output_dir / self.config.image_dir
            image_dir.mkdir(parents=True, exist_ok=True)

            # 创建 MarkItDown 实例并进行转换
            if self.config.docintel_endpoint:
                md = MarkItDown(docintel_endpoint=self.config.docintel_endpoint)
            elif self.config.llm_client and self.config.llm_model:
                md = MarkItDown(
                    enable_plugins=self.config.enable_plugins,
                    llm_client=self.config.llm_client,
                    llm_model=self.config.llm_model
                )
            else:
                md = MarkItDown(enable_plugins=self.config.enable_plugins)

            # 执行转换
            result = md.convert(str(path))
            markdown_content = result.text_content

            # 清理文本
            markdown_content = self._cleanup_text(markdown_content)

            # 如果需要保存到文件
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                self.logger.info(f"转换成功，输出到: {output_path}")

            return markdown_content

        except Exception as e:
            self.logger.error(f"转换失败: {e}")
            raise
        finally:
            # 如果使用了临时目录且没有指定输出路径，则清理临时目录
            if 'temp_dir' in locals() and not output_path:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def convert_to_markdown_and_save(
            self,
            file_path: Union[str, Path],
            output_path: Union[str, Path]
    ) -> Path:
        """将 PDF 转换为 Markdown 并保存到指定路径

        Args:
            file_path: PDF 文件路径
            output_path: 输出 Markdown 文件路径

        Returns:
            Path: 输出文件的 Path 对象

        Raises:
            Exception: 转换过程中的错误
        """
        self.convert_to_markdown(file_path, output_path)
        return Path(output_path)

    def batch_convert(
            self,
            file_paths: List[Union[str, Path]],
            output_dir: Union[str, Path]
    ) -> List[Path]:
        """批量转换多个 PDF 文件为 Markdown

        Args:
            file_paths: PDF 文件路径列表
            output_dir: 输出目录路径

        Returns:
            List[Path]: 输出文件路径列表

        Raises:
            Exception: 转换过程中的错误
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_paths = []
        for file_path in file_paths:
            path = Path(file_path)
            output_path = output_dir / f"{path.stem}.md"

            try:
                self.convert_to_markdown(file_path, output_path)
                output_paths.append(output_path)
                self.logger.info(f"成功转换: {path} -> {output_path}")
            except Exception as e:
                self.logger.error(f"转换失败 {path}: {e}")

        return output_paths


def main():
    """主函数：演示用法"""
    # 配置
    config = MarkdownConverterConfig(
        extract_images=True,
        extract_tables=True,
        extract_code_blocks=True,
        extract_math=True,
        enable_plugins=False,
        text_cleanup={
            'remove_extra_spaces': True,
            'normalize_whitespace': True,
            'remove_special_chars': False,
            'lowercase': False
        }
    )

    # 创建转换器
    converter = MarkdownConverter(config)

    # 使用示例
    try:
        # 替换为实际的文件路径
        sample_file = './crazy_functions/doc_fns/read_fns/paper/2501.12599v1.pdf'
        if Path(sample_file).exists():
            # 转换为 Markdown 并打印内容
            markdown_content = converter.convert_to_markdown(sample_file)
            print("转换后的 Markdown 内容:")
            print(markdown_content[:500] + "...")  # 只打印前500个字符

            # 转换并保存到文件
            output_file = f"./output_{Path(sample_file).stem}.md"
            output_path = converter.convert_to_markdown_and_save(sample_file, output_file)
            print(f"\n已保存到: {output_path}")

            # 使用LLM增强的示例 (需要添加相应的导入和配置)
            # try:
            #     from openai import OpenAI
            #     client = OpenAI()
            #     llm_config = MarkdownConverterConfig(
            #         llm_client=client,
            #         llm_model="gpt-4o"
            #     )
            #     llm_converter = MarkdownConverter(llm_config)
            #     llm_result = llm_converter.convert_to_markdown("example.jpg")
            #     print("LLM增强的结果:")
            #     print(llm_result[:500] + "...")
            # except ImportError:
            #     print("未安装OpenAI库，跳过LLM示例")
        else:
            print(f"示例文件 {sample_file} 不存在")

        print("\n支持的格式:", converter.get_supported_formats())

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
