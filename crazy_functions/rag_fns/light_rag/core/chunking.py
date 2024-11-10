from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import re
from loguru import logger
import tiktoken
from abc import ABC, abstractmethod
import numpy as np


@dataclass
class ChunkingConfig:
    """文档分块配置

    Attributes:
        chunk_size: 每个块的目标大小(tokens)
        chunk_overlap: 相邻块之间的重叠大小(tokens)
        model_name: 使用的tokenizer模型名称
        min_chunk_chars: 最小块大小(字符)
        max_chunk_chars: 最大块大小(字符)
    """
    chunk_size: int = 1000
    chunk_overlap: int = 200
    model_name: str = "gpt-3.5-turbo"
    min_chunk_chars: int = 100  # 最小块字符数
    max_chunk_chars: int = 2000  # 最大块字符数
    chunk_size_buffer: int = 50  # chunk大小的容差范围

    def __post_init__(self):
        """验证配置参数"""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        if self.min_chunk_chars >= self.max_chunk_chars:
            raise ValueError("min_chunk_chars must be smaller than max_chunk_chars")


class TextChunker:
    """基于tiktoken的文本分块器"""

    def __init__(self, config: ChunkingConfig = None):
        """初始化分块器

        Args:
            config: 分块配置，如果不提供则使用默认配置
        """
        self.config = config or ChunkingConfig()
        self._init_tokenizer()

    def _init_tokenizer(self):
        """初始化tokenizer"""
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.config.model_name)
            logger.info(f"Using tokenizer for model: {self.config.model_name}")
        except Exception as e:
            logger.warning(f"Fallback to cl100k_base tokenizer: {e}")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def get_token_count(self, text: str) -> int:
        """计算文本的token数量

        Args:
            text: 输入文本

        Returns:
            token数量
        """
        if not text.strip():
            return 0
        return len(self.tokenizer.encode(text))

    def split_text(self, text: str) -> List[str]:
        """将文本分割为chunks

        Args:
            text: 输入文本

        Returns:
            文本块列表
        """
        if not text.strip():
            return []

        try:
            # 首先按段落分割
            paragraphs = self._split_into_paragraphs(text)

            # 处理每个段落
            chunks = []
            current_chunk = []
            current_length = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # 计算段落token数
                para_length = self.get_token_count(para)

                # 如果段落太长，需要进一步分割
                if para_length > self.config.chunk_size:
                    # 先处理当前累积的chunk
                    if current_chunk:
                        chunks.append(self._join_text_with_newlines(current_chunk))
                        current_chunk = []
                        current_length = 0
                    # 分割长段落
                    para_chunks = self._split_long_paragraph(para)
                    chunks.extend(para_chunks)
                    continue

                # 检查是否需要开始新的chunk
                if (current_length + para_length > self.config.chunk_size and
                        current_chunk):
                    chunks.append(self._join_text_with_newlines(current_chunk))

                    # 保持重叠
                    if len(current_chunk) > 1:
                        # 保留最后一段作为重叠
                        current_chunk = [current_chunk[-1]]
                        current_length = self.get_token_count(current_chunk[-1])
                    else:
                        current_chunk = []
                        current_length = 0

                current_chunk.append(para)
                current_length += para_length

            # 处理最后一个chunk
            if current_chunk:
                chunks.append(self._join_text_with_newlines(current_chunk))

            # 后处理确保chunk大小合适
            return self._post_process_chunks(chunks)

        except Exception as e:
            logger.error(f"Error in splitting text: {e}")
            # 如果发生错误，返回原文本作为单个chunk
            return [text] if text.strip() else []

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本

        Args:
            text: 输入文本

        Returns:
            段落列表
        """
        # 处理多种换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 分割成段落
        paragraphs = [p.strip() for p in text.split('\n')]

        # 移除空段落
        return [p for p in paragraphs if p]

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割过长的段落

        Args:
            paragraph: 需要分割的段落

        Returns:
            分割后的文本块列表
        """
        # 首先尝试按句子分割
        sentences = self._split_into_sentences(paragraph)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = self.get_token_count(sentence)

            # 如果单个句子超过chunk大小
            if sentence_length > self.config.chunk_size:
                # 处理当前累积的chunk
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # 对长句子进行硬分割
                chunks.extend(self._split_by_tokens(sentence))
                continue

            # 检查是否需要开始新的chunk
            if current_length + sentence_length > self.config.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_length

        # 处理最后一个chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割为句子

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        # 句子分隔符模式
        pattern = r'(?<=[。！？.!?])\s+'

        # 分割文本
        sentences = re.split(pattern, text)

        # 确保每个句子都以句号结尾
        sentences = [s + '。' if not s.strip().endswith(('。', '！', '？', '.', '!', '?'))
                     else s for s in sentences]

        return [s.strip() for s in sentences if s.strip()]

    def _split_by_tokens(self, text: str) -> List[str]:
        """按token数量硬分割文本

        Args:
            text: 输入文本

        Returns:
            分割后的文本块列表
        """
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.config.chunk_size):
            chunk_tokens = tokens[i:i + self.config.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks

    def _join_text_with_newlines(self, text_list: List[str]) -> str:
        """用换行符连接文本列表

        Args:
            text_list: 文本列表

        Returns:
            连接后的文本
        """
        return '\n'.join(text_list)

    def _post_process_chunks(self, chunks: List[str]) -> List[str]:
        """对分割后的chunks进行后处理

        Args:
            chunks: 初始chunks列表

        Returns:
            处理后的chunks列表
        """
        processed_chunks = []

        for chunk in chunks:
            # 移除空白chunk
            if not chunk.strip():
                continue

            # 检查chunk大小
            chunk_length = len(chunk)
            if chunk_length < self.config.min_chunk_chars:
                logger.debug(f"Chunk too small ({chunk_length} chars), skipping")
                continue

            if chunk_length > self.config.max_chunk_chars:
                logger.debug(f"Chunk too large ({chunk_length} chars), splitting")
                sub_chunks = self._split_by_tokens(chunk)
                processed_chunks.extend(sub_chunks)
            else:
                processed_chunks.append(chunk)

        return processed_chunks


def chunk_document(
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        model_name: str = "gpt-3.5-turbo",
        **kwargs
) -> List[str]:
    """文档分块的便捷函数

    Args:
        text: 输入文本
        chunk_size: 每个块的目标大小(tokens)
        chunk_overlap: 相邻块之间的重叠大小(tokens)
        model_name: 使用的tokenizer模型名称
        **kwargs: 其他分块配置参数

    Returns:
        分块后的文本列表
    """
    config = ChunkingConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        model_name=model_name,
        **{k: v for k, v in kwargs.items() if hasattr(ChunkingConfig, k)}
    )

    chunker = TextChunker(config)
    return chunker.split_text(text)