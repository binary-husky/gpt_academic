import os
import re
import time
import aiohttp
import asyncio
import requests
import tarfile
import logging
from pathlib import Path
from typing import Generator, List, Tuple, Optional, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from crazy_functions.rag_fns.arxiv_fns.tex_processor import TexProcessor
from crazy_functions.rag_fns.arxiv_fns.arxiv_fragment import ArxivFragment



def save_fragments_to_file(fragments, output_dir: str = "fragment_outputs"):
        """
        将所有fragments保存为单个结构化markdown文件

        Args:
            fragments: fragment列表
            output_dir: 输出目录
        """
        from datetime import datetime
        from pathlib import Path
        import re

        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        filename = f"fragments_{timestamp}.md"
        file_path = output_path / filename

        current_section = ""
        section_count = {}  # 用于跟踪每个章节的片段数量

        with open(file_path, "w", encoding="utf-8") as f:
            # 写入文档头部
            f.write("# Document Fragments Analysis\n\n")
            f.write("## Overview\n")
            f.write(f"- Total Fragments: {len(fragments)}\n")
            f.write(f"- Generated Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            # 如果有标题和摘要，添加到开头
            if fragments and (fragments[0].title or fragments[0].abstract):
                f.write("\n## Paper Information\n")
                if fragments[0].title:
                    f.write(f"### Title\n{fragments[0].title}\n")
                if fragments[0].abstract:
                    f.write(f"\n### Abstract\n{fragments[0].abstract}\n")

            # 生成目录
            f.write("\n## Table of Contents\n")

            # 首先收集所有章节信息
            sections = {}
            for fragment in fragments:
                section = fragment.section or "Uncategorized"
                if section not in sections:
                    sections[section] = []
                sections[section].append(fragment)

            # 写入目录
            for section, section_fragments in sections.items():
                clean_section = section.strip()
                if not clean_section:
                    clean_section = "Uncategorized"
                f.write(
                    f"- [{clean_section}](#{clean_section.lower().replace(' ', '-')}) ({len(section_fragments)} fragments)\n")

            # 写入正文内容
            f.write("\n## Content\n")

            # 按章节组织内容
            for section, section_fragments in sections.items():
                clean_section = section.strip() or "Uncategorized"
                f.write(f"\n### {clean_section}\n")

                # 写入每个fragment
                for i, fragment in enumerate(section_fragments, 1):
                    f.write(f"\n#### Fragment {i} ({fragment.segment_type})\n")

                    # 元数据
                    f.write("**Metadata:**\n")
                    f.write(f"- Type: {fragment.segment_type}\n")
                    f.write(f"- Length: {len(fragment.content)} chars\n")
                    f.write(f"- Importance: {fragment.importance:.2f}\n")
                    f.write(f"- Is Appendix: {fragment.is_appendix}\n")
                    f.write(f"- File: {fragment.rel_path}\n")

                    # 内容
                    f.write("\n**Content:**\n")
                    f.write("```tex\n")
                    f.write(fragment.content)
                    f.write("\n```\n")

                    # 添加分隔线
                    if i < len(section_fragments):
                        f.write("\n---\n")

            # 添加统计信息
            f.write("\n## Statistics\n")
            f.write("\n### Fragment Type Distribution\n")
            type_stats = {}
            for fragment in fragments:
                type_stats[fragment.segment_type] = type_stats.get(fragment.segment_type, 0) + 1

            for ftype, count in type_stats.items():
                percentage = (count / len(fragments)) * 100
                f.write(f"- {ftype}: {count} ({percentage:.1f}%)\n")

            # 长度分布
            f.write("\n### Length Distribution\n")
            lengths = [len(f.content) for f in fragments]
            f.write(f"- Minimum: {min(lengths)} chars\n")
            f.write(f"- Maximum: {max(lengths)} chars\n")
            f.write(f"- Average: {sum(lengths) / len(lengths):.1f} chars\n")

        print(f"Fragments saved to: {file_path}")
        return file_path



class ArxivSplitter:
    """Arxiv论文智能分割器"""

    def __init__(self,
                 char_range: Tuple[int, int],
                 root_dir: str = "gpt_log/arxiv_cache",
                 proxies: Optional[Dict[str, str]] = None,
                 cache_ttl: int = 7 * 24 * 60 * 60):
        """
        初始化分割器

        Args:
            char_range: 字符数范围(最小值, 最大值)
            root_dir: 缓存根目录
            proxies: 代理设置
            cache_ttl: 缓存过期时间(秒)
        """
        self.min_chars, self.max_chars = char_range
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.proxies = proxies or {}
        self.cache_ttl = cache_ttl

        # 动态计算最优线程数
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        # 根据CPU核心数动态设置，但设置上限防止过度并发
        self.max_workers = min(32, cpu_count * 2)

        # 初始化TeX处理器
        self.tex_processor = TexProcessor(char_range)

        # 配置日志
        self._setup_logging()



    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _normalize_arxiv_id(self, input_str: str) -> str:
        """规范化ArXiv ID"""
        if 'arxiv.org/' in input_str.lower():
            # 处理URL格式
            if '/pdf/' in input_str:
                arxiv_id = input_str.split('/pdf/')[-1]
            else:
                arxiv_id = input_str.split('/abs/')[-1]
            # 移除版本号和其他后缀
            return arxiv_id.split('v')[0].strip()
        return input_str.split('v')[0].strip()


    def _check_cache(self, paper_dir: Path) -> bool:
        """
        检查缓存是否有效，包括文件完整性检查

        Args:
            paper_dir: 论文目录路径

        Returns:
            bool: 如果缓存有效返回True，否则返回False
        """
        if not paper_dir.exists():
            return False

        # 检查目录中是否存在必要文件
        has_tex_files = False
        has_main_tex = False

        for file_path in paper_dir.rglob("*"):
            if file_path.suffix == '.tex':
                has_tex_files = True
                content = self.tex_processor.read_file(str(file_path))
                if content and r'\documentclass' in content:
                    has_main_tex = True
                    break

        if not (has_tex_files and has_main_tex):
            return False

        # 检查缓存时间
        cache_time = paper_dir.stat().st_mtime
        if (time.time() - cache_time) < self.cache_ttl:
            self.logger.info(f"Using valid cache for {paper_dir.name}")
            return True

        return False

    async def download_paper(self, arxiv_id: str, paper_dir: Path) -> bool:
        """
        异步下载论文，包含重试机制和临时文件处理

        Args:
            arxiv_id: ArXiv论文ID
            paper_dir: 目标目录路径

        Returns:
            bool: 下载成功返回True，否则返回False
        """
        from crazy_functions.rag_fns.arxiv_fns.arxiv_downloader import ArxivDownloader
        temp_tar_path = paper_dir / f"{arxiv_id}_temp.tar.gz"
        final_tar_path = paper_dir / f"{arxiv_id}.tar.gz"

        # 确保目录存在
        paper_dir.mkdir(parents=True, exist_ok=True)

        # 尝试使用 ArxivDownloader 下载
        try:
            downloader = ArxivDownloader(root_dir=str(paper_dir), proxies=self.proxies)
            downloaded_dir = downloader.download_paper(arxiv_id)
            if downloaded_dir:
                self.logger.info(f"Successfully downloaded using ArxivDownloader to {downloaded_dir}")
                return True
        except Exception as e:
            self.logger.warning(f"ArxivDownloader failed: {str(e)}. Falling back to direct download.")

        # 如果 ArxivDownloader 失败，使用原有的下载方式作为备选
        urls = [
            f"https://arxiv.org/src/{arxiv_id}",
            f"https://arxiv.org/e-print/{arxiv_id}"
        ]

        max_retries = 3
        retry_delay = 1  # 初始重试延迟（秒）

        for url in urls:
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Downloading from {url} (attempt {attempt + 1}/{max_retries})")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, proxy=self.proxies.get('http')) as response:
                            if response.status == 200:
                                content = await response.read()

                                # 写入临时文件
                                temp_tar_path.write_bytes(content)

                                try:
                                    # 验证tar文件完整性并解压
                                    loop = asyncio.get_event_loop()
                                    await loop.run_in_executor(None, self._process_tar_file, temp_tar_path, paper_dir)

                                    # 下载成功后移动临时文件到最终位置
                                    temp_tar_path.rename(final_tar_path)
                                    return True

                                except Exception as e:
                                    self.logger.warning(f"Invalid tar file: {str(e)}")
                                    if temp_tar_path.exists():
                                        temp_tar_path.unlink()

                except Exception as e:
                    self.logger.warning(f"Download attempt {attempt + 1} failed from {url}: {str(e)}")
                    await asyncio.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue

        return False

    def _process_tar_file(self, tar_path: Path, extract_path: Path):
        """处理tar文件的同步操作"""
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.testall()  # 验证文件完整性
            tar.extractall(path=extract_path)  # 解压文件

    def _process_single_tex(self, file_path: str) -> List[ArxivFragment]:
        """处理单个TeX文件"""
        try:
            content = self.tex_processor.read_file(file_path)
            if not content:
                return []

            # 提取元数据
            is_main = r'\documentclass' in content
            title, abstract = "", ""
            if is_main:
                title, abstract = self.tex_processor.extract_metadata(content)

            # 分割内容
            segments = self.tex_processor.split_content(content)
            fragments = []

            for i, (segment_content, section, is_appendix) in enumerate(segments):
                if not segment_content.strip():
                    continue

                segment_type = self.tex_processor.detect_segment_type(segment_content)
                importance = self.tex_processor.calculate_importance(
                    segment_content, segment_type, is_main
                )
                fragments.append(ArxivFragment(
                    file_path=file_path,
                    content=segment_content,
                    segment_index=i,
                    total_segments=len(segments),
                    rel_path=str(Path(file_path).relative_to(self.root_dir)),
                    segment_type=segment_type,
                    title=title,
                    abstract=abstract,
                    section=section,
                    is_appendix=is_appendix,
                    importance=importance
                ))

            return fragments

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return []

    async def process(self, arxiv_id_or_url: str) -> List[ArxivFragment]:
        """处理ArXiv论文"""
        try:
            arxiv_id = self._normalize_arxiv_id(arxiv_id_or_url)
            paper_dir = self.root_dir / arxiv_id

            # 检查缓存
            if not self._check_cache(paper_dir):
                paper_dir.mkdir(exist_ok=True)
                if not await self.download_paper(arxiv_id, paper_dir):
                    raise RuntimeError(f"Failed to download paper {arxiv_id}")

            # 查找主TeX文件
            main_tex = self.tex_processor.find_main_tex_file(str(paper_dir))
            if not main_tex:
                raise RuntimeError(f"No main TeX file found in {paper_dir}")

            # 获取所有相关TeX文件
            tex_files = self.tex_processor.resolve_includes(main_tex)
            if not tex_files:
                raise RuntimeError(f"No valid TeX files found for {arxiv_id}")

            # 并行处理所有TeX文件
            fragments = []
            chunk_size = max(1, len(tex_files) // self.max_workers)  # 计算每个线程处理的文件数
            loop = asyncio.get_event_loop()

            async def process_chunk(chunk_files):
                chunk_fragments = []
                for file_path in chunk_files:
                    try:
                        result = await loop.run_in_executor(None, self._process_single_tex, file_path)
                        chunk_fragments.extend(result)
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {str(e)}")
                return chunk_fragments

            # 将文件分成多个块
            file_chunks = [tex_files[i:i + chunk_size] for i in range(0, len(tex_files), chunk_size)]
            # 异步处理每个块
            chunk_results = await asyncio.gather(*[process_chunk(chunk) for chunk in file_chunks])
            for result in chunk_results:
                fragments.extend(result)
            # 重新计算片段索引并排序
            fragments.sort(key=lambda x: (x.rel_path, x.segment_index))
            total_fragments = len(fragments)

            for i, fragment in enumerate(fragments):
                fragment.segment_index = i
                fragment.total_segments = total_fragments
            # 在返回之前添加过滤
            fragments = self.tex_processor.filter_fragments(fragments)
            return fragments

        except Exception as e:
            self.logger.error(f"Failed to process {arxiv_id_or_url}: {str(e)}")
            raise


async def test_arxiv_splitter():
    """测试ArXiv分割器的功能"""

    # 测试配置
    test_cases = [
        {
            "arxiv_id": "2411.03663",
            "expected_title": "Large Language Models and Simple Scripts",
            "min_fragments": 10,
        },
        # {
        #     "arxiv_id": "1805.10988",
        #     "expected_title": "RAG vs Fine-tuning",
        #     "min_fragments": 15,
        # }
    ]

    # 创建分割器实例
    splitter = ArxivSplitter(
        char_range=(800, 1800),
        root_dir="test_cache"
    )


    for case in test_cases:
        print(f"\nTesting paper: {case['arxiv_id']}")
        try:
            fragments = await splitter.process(case['arxiv_id'])

            # 保存fragments
            output_dir = save_fragments_to_file(fragments,output_dir="crazy_functions/rag_fns/arxiv_fns/gpt_log")
            print(f"Output saved to: {output_dir}")
            # 内容检查
            for fragment in fragments:
                # 长度检查

                print((fragment.content))
                print(len(fragment.content))
                # 类型检查


        except Exception as e:
            print(f"✗ Test failed for {case['arxiv_id']}: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(test_arxiv_splitter())