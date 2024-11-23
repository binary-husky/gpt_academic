import os
import re
import time
import aiohttp
import asyncio
import requests
import tarfile
import logging
from pathlib import Path
from copy import deepcopy

from typing import Generator, List, Tuple, Optional, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from crazy_functions.rag_fns.arxiv_fns.tex_utils import TexUtils
from crazy_functions.rag_fns.arxiv_fns.section_fragment import SectionFragment
from crazy_functions.rag_fns.arxiv_fns.essay_structure import EssayStructureParser, DocumentStructure, read_tex_file
from crazy_functions.rag_fns.arxiv_fns.section_extractor import Section


def save_fragments_to_file(fragments: List[SectionFragment], output_dir: str = "fragment_outputs") -> Path:
    """
    Save all fragments to a single structured markdown file.

    Args:
        fragments: List of SectionFragment objects
        output_dir: Output directory path

    Returns:
        Path: Path to the generated markdown file
    """
    from datetime import datetime
    from pathlib import Path
    import re

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = f"fragments_{timestamp}.md"
    file_path = output_path / filename

    # Group fragments by section
    sections = {}
    for fragment in fragments:
        section = fragment.current_section or "Uncategorized"
        if section not in sections:
            sections[section] = []
        sections[section].append(fragment)

    with open(file_path, "w", encoding="utf-8") as f:
        # Write document header
        f.write("# Document Fragments Analysis\n\n")
        f.write("## Overview\n")
        f.write(f"- Total Fragments: {len(fragments)}\n")
        f.write(f"- Generated Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Add paper information if available
        if fragments and (fragments[0].title or fragments[0].abstract):
            f.write("\n## Paper Information\n")
            if fragments[0].title:
                f.write(f"### Title\n{fragments[0].title}\n")
            if fragments[0].abstract:
                f.write(f"\n### Abstract\n{fragments[0].abstract}\n")

        # Write section tree if available
        if fragments and fragments[0].section_tree:
            f.write("\n## Section Tree\n")
            f.write(fragments[0].section_tree)

        # Generate table of contents
        f.write("\n## Table of Contents\n")
        for section in sections:
            clean_section = section.strip() or "Uncategorized"
            fragment_count = len(sections[section])
            f.write(f"- [{clean_section}](#{clean_section.lower().replace(' ', '-')}) "
                    f"({fragment_count} fragments)\n")

        # Write content sections
        f.write("\n## Content\n")
        for section, section_fragments in sections.items():
            clean_section = section.strip() or "Uncategorized"
            f.write(f"\n### {clean_section}\n")

            # Write each fragment
            for i, fragment in enumerate(section_fragments, 1):
                f.write(f"\n#### Fragment {i}\n")

                # Metadata
                f.write("**Metadata:**\n")
                metadata = [
                    f"- Section: {fragment.current_section}",
                    f"- Length: {len(fragment.content)} chars",
                    f"- ArXiv ID: {fragment.arxiv_id}" if fragment.arxiv_id else None
                ]
                f.write("\n".join(filter(None, metadata)) + "\n")

                # Content
                f.write("\n**Content:**\n")
                f.write("```tex\n")
                f.write(fragment.content)
                f.write("\n```\n")

                # Bibliography if exists
                if fragment.bibliography:
                    f.write("\n**Bibliography:**\n")
                    f.write("```bibtex\n")
                    f.write(fragment.bibliography)
                    f.write("\n```\n")

                # Add separator
                if i < len(section_fragments):
                    f.write("\n---\n")

        # Add statistics
        f.write("\n## Statistics\n")

        # Length distribution
        lengths = [len(f.content) for f in fragments]
        f.write("\n### Length Distribution\n")
        f.write(f"- Minimum: {min(lengths)} chars\n")
        f.write(f"- Maximum: {max(lengths)} chars\n")
        f.write(f"- Average: {sum(lengths) / len(lengths):.1f} chars\n")

        # Section distribution
        f.write("\n### Section Distribution\n")
        for section, section_fragments in sections.items():
            percentage = (len(section_fragments) / len(fragments)) * 100
            f.write(f"- {section}: {len(section_fragments)} ({percentage:.1f}%)\n")

    print(f"Fragments saved to: {file_path}")
    return file_path

# 定义各种引用命令的模式
CITATION_PATTERNS = [
    # 基本的 \cite{} 格式
    r'\\cite(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    # natbib 格式
    r'\\citep(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\citet(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\citeauthor(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\citeyear(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\citealt(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\citealp(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    # biblatex 格式
    r'\\textcite(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\parencite(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    r'\\autocite(?:\*)?(?:\[[^\]]*\])?{([^}]+)}',
    # 自定义 [cite:...] 格式
    r'\[cite:([^\]]+)\]',
]

# 编译所有模式
COMPILED_PATTERNS = [re.compile(pattern) for pattern in CITATION_PATTERNS]


class ArxivSplitter:
    """Arxiv论文智能分割器"""

    def __init__(self,
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
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.proxies = proxies or {}
        self.cache_ttl = cache_ttl

        # 动态计算最优线程数
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        # 根据CPU核心数动态设置，但设置上限防止过度并发
        self.document_structure = DocumentStructure()
        self.document_parser = EssayStructureParser()

        self.max_workers = min(32, cpu_count * 2)

        # 初始化TeX处理器
        self.tex_processor = TexUtils()

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

    def process_references(self, doc_structure: DocumentStructure, ref_bib: str) -> DocumentStructure:
        """
        Process citations in document structure and add referenced literature for each section

        Args:
            doc_structure: DocumentStructure object
            ref_bib: String containing references separated by newlines

        Returns:
            Updated DocumentStructure object
        """
        try:
            # Create a copy to avoid modifying the original
            doc = deepcopy(doc_structure)

            # Parse references into a mapping
            ref_map = self._parse_references(ref_bib)
            if not ref_map:
                self.logger.warning("No valid references found in ref_bib")
                return doc

            # Process all sections recursively
            self._process_section_references(doc.toc, ref_map)

            return doc

        except Exception as e:
            self.logger.error(f"Error processing references: {str(e)}")
            return doc_structure  # Return original if processing fails

    def _process_section_references(self, sections: List[Section], ref_map: Dict[str, str]) -> None:
        """
        Recursively process sections to add references

        Args:
            sections: List of Section objects
            ref_map: Mapping of citation keys to full references
        """
        for section in sections:
            if section.content:
                # Find citations in current section
                cited_refs = self.find_citations(section.content)

                if cited_refs:
                    # Get full references for citations
                    full_refs = []
                    for ref_key in cited_refs:
                        ref_text = ref_map.get(ref_key)
                        if ref_text:
                            full_refs.append(ref_text)
                        else:
                            self.logger.warning(f"Reference not found for citation key: {ref_key}")

                    # Add references to section content
                    if full_refs:
                        section.bibliography = "\n\n".join(full_refs)

            # Process subsections recursively
            if section.subsections:
                self._process_section_references(section.subsections, ref_map)

    def _parse_references(self, ref_bib: str) -> Dict[str, str]:
        """
        Parse reference string into a mapping of citation keys to full references

        Args:
            ref_bib: Reference string with references separated by newlines

        Returns:
            Dict mapping citation keys to full reference text
        """
        ref_map = {}
        current_ref = []
        current_key = None

        try:
            for line in ref_bib.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # New reference entry
                if line.startswith('@'):
                    # Save previous reference if exists
                    if current_key and current_ref:
                        ref_map[current_key] = '\n'.join(current_ref)
                        current_ref = []

                    # Extract key from new reference
                    key_match = re.search(r'{(.*?),', line)
                    if key_match:
                        current_key = key_match.group(1)
                        current_ref.append(line)
                else:
                    if current_ref is not None:
                        current_ref.append(line)

            # Save last reference
            if current_key and current_ref:
                ref_map[current_key] = '\n'.join(current_ref)

        except Exception as e:
            self.logger.error(f"Error parsing references: {str(e)}")

        return ref_map

    # 编译一次正则表达式以提高效率

    @staticmethod
    def _clean_citation_key(key: str) -> str:
        """Clean individual citation key."""
        return key.strip().strip(',').strip()

    def _extract_keys_from_group(self, keys_str: str) -> Set[str]:
        """Extract and clean individual citation keys from a group."""
        try:
            # 分割多个引用键（支持逗号和分号分隔）
            separators = '[,;]'
            keys = re.split(separators, keys_str)
            # 清理并过滤空键
            return {self._clean_citation_key(k) for k in keys if self._clean_citation_key(k)}
        except Exception as e:
            self.logger.warning(f"Error processing citation group '{keys_str}': {e}")
            return set()

    def find_citations(self, content: str) -> Set[str]:
        """
        Find citation keys in text content in various formats.

        Args:
            content: Text content to search for citations

        Returns:
            Set of unique citation keys

        Examples:
            Supported formats include:
            - \cite{key1,key2}
            - \cite[p. 1]{key}
            - \citep{key}
            - \citet{key}
            - [cite:key1, key2]
            - And many other variants
        """
        citations = set()

        if not content:
            return citations

        try:
            # 对每个编译好的模式进行搜索
            for pattern in COMPILED_PATTERNS:
                matches = pattern.finditer(content)
                for match in matches:
                    # 获取捕获组中的引用键
                    keys_str = match.group(1)
                    if keys_str:
                        # 提取并添加所有引用键
                        new_keys = self._extract_keys_from_group(keys_str)
                        citations.update(new_keys)

        except Exception as e:
            self.logger.error(f"Error finding citations: {str(e)}")

        # 移除明显无效的键
        citations = {key for key in citations
                     if key and not key.startswith(('\\', '{', '}', '[', ']'))}

        return citations

    def get_citation_contexts(self, content: str, context_chars: int = 100) -> dict:
        """
        Find citations and their surrounding context.

        Args:
            content: Text content to search for citations
            context_chars: Number of characters of context to include before/after

        Returns:
            Dict mapping citation keys to lists of context strings
        """
        contexts = {}

        if not content:
            return contexts

        try:
            for pattern in COMPILED_PATTERNS:
                matches = pattern.finditer(content)
                for match in matches:
                    # 获取匹配的位置
                    start = max(0, match.start() - context_chars)
                    end = min(len(content), match.end() + context_chars)

                    # 获取上下文
                    context = content[start:end]

                    # 获取并处理引用键
                    keys_str = match.group(1)
                    keys = self._extract_keys_from_group(keys_str)

                    # 为每个键添加上下文
                    for key in keys:
                        if key not in contexts:
                            contexts[key] = []
                        contexts[key].append(context)

        except Exception as e:
            self.logger.error(f"Error finding citation contexts: {str(e)}")

        return contexts
    async def process(self, arxiv_id_or_url: str) -> List[SectionFragment]:
        """
        Process ArXiv paper and convert to list of SectionFragments.
        Each fragment represents the smallest section unit.

        Args:
            arxiv_id_or_url: ArXiv paper ID or URL

        Returns:
            List[SectionFragment]: List of processed paper fragments
        """
        try:
            arxiv_id = self._normalize_arxiv_id(arxiv_id_or_url)
            paper_dir = self.root_dir / arxiv_id

            # Check if paper directory exists, if not, try to download
            if not paper_dir.exists():
                self.logger.info(f"Downloading paper {arxiv_id}")
                await self.download_paper(arxiv_id, paper_dir)

            # Find main TeX file
            main_tex = self.tex_processor.find_main_tex_file(str(paper_dir))
            if not main_tex:
                raise RuntimeError(f"No main TeX file found in {paper_dir}")

            # Get all related TeX files and references
            tex_files = self.tex_processor.resolve_includes(main_tex)
            ref_bib = self.tex_processor.resolve_references(main_tex, paper_dir)

            if not tex_files:
                raise RuntimeError(f"No valid TeX files found for {arxiv_id}")

            # Reset document structure for new processing
            self.document_structure = DocumentStructure()

            # Process each TeX file
            for file_path in tex_files:
                self.logger.info(f"Processing TeX file: {file_path}")
                tex_content = read_tex_file(file_path)
                if tex_content:
                    additional_doc = self.document_parser.parse(tex_content)
                    self.document_structure = self.document_structure.merge(additional_doc)

            # Process references if available
            if ref_bib:
                self.document_structure = self.process_references(self.document_structure, ref_bib)
                self.logger.info("Successfully processed references")
            else:
                self.logger.info("No references found to process")

            # Generate table of contents once
            section_tree = self.document_structure.generate_toc_tree()

            # Convert DocumentStructure to SectionFragments
            fragments = self._convert_to_fragments(
                doc_structure=self.document_structure,
                arxiv_id=arxiv_id,
                section_tree=section_tree
            )

            return fragments

        except Exception as e:
            self.logger.error(f"Failed to process {arxiv_id_or_url}: {str(e)}")
            raise

    def _convert_to_fragments(self,
                              doc_structure: DocumentStructure,
                              arxiv_id: str,
                              section_tree: str) -> List[SectionFragment]:
        """
        Convert DocumentStructure to list of SectionFragments.
        Creates a fragment for each leaf section in the document hierarchy.

        Args:
            doc_structure: Source DocumentStructure
            arxiv_id: ArXiv paper ID
            section_tree: Pre-generated table of contents tree

        Returns:
            List[SectionFragment]: List of paper fragments
        """
        fragments = []

        # Create a base template for all fragments to avoid repetitive assignments
        base_fragment_template = {
            'title': doc_structure.title,
            'abstract': doc_structure.abstract,
            'section_tree': section_tree,
            'arxiv_id': arxiv_id
        }

        def get_leaf_sections(section: Section, path: List[str] = None) -> None:
            """
            Recursively find all leaf sections and create fragments.
            A leaf section is one that has content but no subsections, or has neither.

            Args:
                section: Current section being processed
                path: List of section titles forming the path to current section
            """
            if path is None:
                path = []

            current_path = path + [section.title]

            if not section.subsections:
                # This is a leaf section, create a fragment if it has content
                if section.content or section.bibliography:
                    fragment = SectionFragment(
                        **base_fragment_template,
                        current_section="/".join(current_path),
                        content=self._clean_content(section.content),
                        bibliography=section.bibliography
                    )
                    if self._validate_fragment(fragment):
                        fragments.append(fragment)
            else:
                # Process each subsection
                for subsection in section.subsections:
                    get_leaf_sections(subsection, current_path)

        # Process all top-level sections
        for section in doc_structure.toc:
            get_leaf_sections(section)

        # Add a fragment for the abstract if it exists
        if doc_structure.abstract:
            abstract_fragment = SectionFragment(
                **base_fragment_template,
                current_section="Abstract",
                content=self._clean_content(doc_structure.abstract)
            )
            if self._validate_fragment(abstract_fragment):
                fragments.insert(0, abstract_fragment)

        self.logger.info(f"Created {len(fragments)} fragments")
        return fragments

    def _validate_fragment(self, fragment: SectionFragment) -> bool:
        """
        Validate if the fragment has all required fields with meaningful content.

        Args:
            fragment: SectionFragment to validate

        Returns:
            bool: True if fragment is valid, False otherwise
        """
        try:
            return all([
                fragment.title.strip(),
                fragment.section_tree.strip(),
                fragment.current_section.strip(),
                fragment.content.strip() or fragment.bibliography.strip()
            ])
        except AttributeError:
            return False

    def _clean_content(self, content: str) -> str:
        """
        Clean and normalize content text.

        Args:
            content: Raw content text

        Returns:
            str: Cleaned content text
        """
        if not content:
            return ""

        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Remove remaining LaTeX artifacts
        content = re.sub(r'\\item\s*', '• ', content)  # Convert \item to bullet points
        content = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', content)  # Remove simple LaTeX commands

        # Clean special characters
        content = content.replace('\\\\', '\n')  # Convert LaTeX newlines to actual newlines
        content = re.sub(r'\s*\n\s*', '\n', content)  # Clean up newlines

        return content.strip()


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