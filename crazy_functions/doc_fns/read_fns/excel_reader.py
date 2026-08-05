from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Set, Dict, Union, Iterator, Tuple
from dataclasses import dataclass, field
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import chardet
from functools import lru_cache
import os


@dataclass
class ExtractorConfig:
    """提取器配置类"""
    encoding: str = 'auto'
    na_filter: bool = True
    skip_blank_lines: bool = True
    chunk_size: int = 10000
    max_workers: int = 4
    preserve_format: bool = True
    read_all_sheets: bool = True  # 新增：是否读取所有工作表
    text_cleanup: Dict[str, bool] = field(default_factory=lambda: {
        'remove_extra_spaces': True,
        'normalize_whitespace': False,
        'remove_special_chars': False,
        'lowercase': False
    })


class ExcelTextExtractor:
    """增强的Excel格式文件文本内容提取器"""

    SUPPORTED_EXTENSIONS: Set[str] = {
        '.xlsx', '.xls', '.csv', '.tsv', '.xlsm', '.xltx', '.xltm', '.ods'
    }

    def __init__(self, config: Optional[ExtractorConfig] = None):
        self.config = config or ExtractorConfig()
        self._setup_logging()
        self._detect_encoding = lru_cache(maxsize=128)(self._detect_encoding)

    def _setup_logging(self) -> None:
        """配置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        fh = logging.FileHandler('excel_extractor.log')
        fh.setLevel(logging.ERROR)
        self.logger.addHandler(fh)

    def _detect_encoding(self, file_path: Path) -> str:
        if self.config.encoding != 'auto':
            return self.config.encoding

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            self.logger.warning(f"Encoding detection failed: {e}. Using utf-8")
            return 'utf-8'

    def _validate_file(self, file_path: Union[str, Path]) -> Path:
        path = Path(file_path).resolve()

        if not path.exists():
            raise ValueError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {path}")

        if not os.access(path, os.R_OK):
            raise PermissionError(f"No read permission: {path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {path.suffix}. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        return path

    def _format_value(self, value: Any) -> str:
        if pd.isna(value) or value is None:
            return ''
        if isinstance(value, (int, float)):
            return str(value)
        return str(value).strip()

    def _process_chunk(self, chunk: pd.DataFrame, columns: Optional[List[str]] = None, sheet_name: str = '') -> str:
        """处理数据块，新增sheet_name参数"""
        try:
            if columns:
                chunk = chunk[columns]

            if self.config.preserve_format:
                formatted_chunk = chunk.applymap(self._format_value)
                rows = []

                # 添加工作表名称作为标题
                if sheet_name:
                    rows.append(f"[Sheet: {sheet_name}]")

                # 添加表头
                headers = [str(col) for col in formatted_chunk.columns]
                rows.append('\t'.join(headers))

                # 添加数据行
                for _, row in formatted_chunk.iterrows():
                    rows.append('\t'.join(row.values))

                return '\n'.join(rows)
            else:
                flat_values = (
                    chunk.astype(str)
                    .replace({'nan': '', 'None': '', 'NaN': ''})
                    .values.flatten()
                )
                return ' '.join(v for v in flat_values if v)

        except Exception as e:
            self.logger.error(f"Error processing chunk: {e}")
            raise

    def _read_file(self, file_path: Path) -> Union[pd.DataFrame, Iterator[pd.DataFrame], Dict[str, pd.DataFrame]]:
        """读取文件，支持多工作表"""
        try:
            encoding = self._detect_encoding(file_path)

            if file_path.suffix.lower() in {'.csv', '.tsv'}:
                sep = '\t' if file_path.suffix.lower() == '.tsv' else ','

                # 对大文件使用分块读取
                if file_path.stat().st_size > self.config.chunk_size * 1024:
                    return pd.read_csv(
                        file_path,
                        encoding=encoding,
                        na_filter=self.config.na_filter,
                        skip_blank_lines=self.config.skip_blank_lines,
                        sep=sep,
                        chunksize=self.config.chunk_size,
                        on_bad_lines='warn'
                    )
                else:
                    return pd.read_csv(
                        file_path,
                        encoding=encoding,
                        na_filter=self.config.na_filter,
                        skip_blank_lines=self.config.skip_blank_lines,
                        sep=sep
                    )
            else:
                # Excel文件处理，支持多工作表
                if self.config.read_all_sheets:
                    # 读取所有工作表
                    return pd.read_excel(
                        file_path,
                        na_filter=self.config.na_filter,
                        keep_default_na=self.config.na_filter,
                        engine='openpyxl',
                        sheet_name=None  # None表示读取所有工作表
                    )
                else:
                    # 只读取第一个工作表
                    return pd.read_excel(
                        file_path,
                        na_filter=self.config.na_filter,
                        keep_default_na=self.config.na_filter,
                        engine='openpyxl',
                        sheet_name=0  # 读取第一个工作表
                    )

        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise

    def extract_text(
            self,
            file_path: Union[str, Path],
            columns: Optional[List[str]] = None,
            separator: str = '\n'
    ) -> str:
        """提取文本，支持多工作表"""
        try:
            path = self._validate_file(file_path)
            self.logger.info(f"Processing: {path}")

            reader = self._read_file(path)
            texts = []

            # 处理Excel多工作表
            if isinstance(reader, dict):
                for sheet_name, df in reader.items():
                    sheet_text = self._process_chunk(df, columns, sheet_name)
                    if sheet_text:
                        texts.append(sheet_text)
                return separator.join(texts)

            # 处理单个DataFrame
            elif isinstance(reader, pd.DataFrame):
                return self._process_chunk(reader, columns)

            # 处理DataFrame迭代器
            else:
                with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                    futures = {
                        executor.submit(self._process_chunk, chunk, columns): i
                        for i, chunk in enumerate(reader)
                    }

                    chunk_texts = []
                    for future in as_completed(futures):
                        try:
                            text = future.result()
                            if text:
                                chunk_texts.append((futures[future], text))
                        except Exception as e:
                            self.logger.error(f"Error in chunk {futures[future]}: {e}")

                    # 按块的顺序排序
                    chunk_texts.sort(key=lambda x: x[0])
                    texts = [text for _, text in chunk_texts]

                # 合并文本，保留格式
                if texts and self.config.preserve_format:
                    result = texts[0]  # 第一块包含表头
                    if len(texts) > 1:
                        # 跳过后续块的表头行
                        for text in texts[1:]:
                            result += '\n' + '\n'.join(text.split('\n')[1:])
                    return result
                else:
                    return separator.join(texts)

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式列表"""
        return sorted(ExcelTextExtractor.SUPPORTED_EXTENSIONS)


def main():
    """主函数：演示用法"""
    config = ExtractorConfig(
        encoding='auto',
        preserve_format=True,
        read_all_sheets=True,  # 启用多工作表读取
        text_cleanup={
            'remove_extra_spaces': True,
            'normalize_whitespace': False,
            'remove_special_chars': False,
            'lowercase': False
        }
    )

    extractor = ExcelTextExtractor(config)

    try:
        sample_file = 'example.xlsx'
        if Path(sample_file).exists():
            text = extractor.extract_text(
                sample_file,
                columns=['title', 'content']
            )
            print("提取的文本:")
            print(text)
        else:
            print(f"示例文件 {sample_file} 不存在")

        print("\n支持的格式:", extractor.get_supported_formats())

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
