import os
import re
import requests
import tarfile
import logging
from dataclasses import dataclass
from typing import Generator, List, Tuple, Optional, Dict, Set
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class ArxivFragment:
    """Arxiv论文片段数据类"""
    file_path: str
    content: str
    segment_index: int
    total_segments: int
    rel_path: str
    segment_type: str
    title: str
    abstract: str
    section: str
    is_appendix: bool


class SmartArxivSplitter:
    def __init__(self,
                 char_range: Tuple[int, int],
                 root_dir: str = "gpt_log/arxiv_cache",
                 proxies: Optional[Dict[str, str]] = None,
                 max_workers: int = 4):

        self.min_chars, self.max_chars = char_range
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.proxies = proxies or {}
        self.max_workers = max_workers

        # 定义特殊环境模式
        self._init_patterns()

        # 配置日志
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def _init_patterns(self):
        """初始化LaTeX环境和命令模式"""
        self.special_envs = {
            'math': [r'\\begin{(equation|align|gather|eqnarray)\*?}.*?\\end{\1\*?}',
                     r'\$\$.*?\$\$', r'\$[^$]+\$'],
            'table': [r'\\begin{(table|tabular)\*?}.*?\\end{\1\*?}'],
            'figure': [r'\\begin{figure\*?}.*?\\end{figure\*?}'],
            'algorithm': [r'\\begin{(algorithm|algorithmic)}.*?\\end{\1}']
        }

        self.section_patterns = [
            r'\\(sub)*section\{([^}]+)\}',
            r'\\chapter\{([^}]+)\}'
        ]

        self.include_patterns = [
            r'\\(input|include|subfile)\{([^}]+)\}'
        ]

    def _find_main_tex_file(self, directory: str) -> Optional[str]:
        """查找主TEX文件"""
        tex_files = list(Path(directory).rglob("*.tex"))
        if not tex_files:
            return None

        # 按以下优先级查找：
        # 1. 包含documentclass的文件
        # 2. 文件名为main.tex
        # 3. 最大的tex文件
        for tex_file in tex_files:
            try:
                content = self._read_file(str(tex_file))
                if content and r'\documentclass' in content:
                    return str(tex_file)
                if tex_file.name.lower() == 'main.tex':
                    return str(tex_file)
            except Exception:
                continue

        return str(max(tex_files, key=lambda x: x.stat().st_size))

    def _resolve_includes(self, tex_file: str, processed: Set[str] = None) -> List[str]:
        """递归解析tex文件中的include/input命令"""
        if processed is None:
            processed = set()

        if tex_file in processed:
            return []

        processed.add(tex_file)
        result = [tex_file]
        content = self._read_file(tex_file)

        if not content:
            return result

        base_dir = Path(tex_file).parent
        for pattern in self.include_patterns:
            for match in re.finditer(pattern, content):
                included_file = match.group(2)
                if not included_file.endswith('.tex'):
                    included_file += '.tex'

                # 构建完整路径
                full_path = str(base_dir / included_file)
                if os.path.exists(full_path) and full_path not in processed:
                    result.extend(self._resolve_includes(full_path, processed))

        return result

    def _smart_split(self, content: str) -> List[Tuple[str, str, bool]]:
        """智能分割TEX内容，确保在字符范围内并保持语义完整性"""
        content = self._preprocess_content(content)
        segments = []
        current_buffer = []
        current_length = 0
        current_section = "Unknown Section"
        is_appendix = False

        # 保护特殊环境
        protected_blocks = {}
        content = self._protect_special_environments(content, protected_blocks)

        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', content)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 恢复特殊环境
            para = self._restore_special_environments(para, protected_blocks)

            # 更新章节信息
            section_info = self._get_section_info(para, content)
            if section_info:
                current_section, is_appendix = section_info

            # 判断是否是特殊环境
            if self._is_special_environment(para):
                # 处理当前缓冲区
                if current_buffer:
                    segments.append((
                        '\n'.join(current_buffer),
                        current_section,
                        is_appendix
                    ))
                    current_buffer = []
                    current_length = 0

                # 添加特殊环境作为独立片段
                segments.append((para, current_section, is_appendix))
                continue

            # 处理普通段落
            sentences = self._split_into_sentences(para)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sent_length = len(sentence)
                new_length = current_length + sent_length + (1 if current_buffer else 0)

                if new_length <= self.max_chars:
                    current_buffer.append(sentence)
                    current_length = new_length
                else:
                    # 如果当前缓冲区达到最小长度要求
                    if current_length >= self.min_chars:
                        segments.append((
                            '\n'.join(current_buffer),
                            current_section,
                            is_appendix
                        ))
                        current_buffer = [sentence]
                        current_length = sent_length
                    else:
                        # 尝试将过长的句子分割
                        split_sentences = self._split_long_sentence(sentence)
                        for split_sent in split_sentences:
                            if current_length + len(split_sent) <= self.max_chars:
                                current_buffer.append(split_sent)
                                current_length += len(split_sent) + 1
                            else:
                                segments.append((
                                    '\n'.join(current_buffer),
                                    current_section,
                                    is_appendix
                                ))
                                current_buffer = [split_sent]
                                current_length = len(split_sent)

        # 处理剩余的缓冲区
        if current_buffer:
            segments.append((
                '\n'.join(current_buffer),
                current_section,
                is_appendix
            ))

        return segments

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        return re.split(r'(?<=[.!?。！？])\s+', text)

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """智能分割过长的句子"""
        if len(sentence) <= self.max_chars:
            return [sentence]

        result = []
        while sentence:
            # 在最大长度位置寻找合适的分割点
            split_pos = self._find_split_position(sentence[:self.max_chars])
            if split_pos <= 0:
                split_pos = self.max_chars

            result.append(sentence[:split_pos])
            sentence = sentence[split_pos:].strip()

        return result

    def _find_split_position(self, text: str) -> int:
        """找到合适的句子分割位置"""
        # 优先在标点符号处分割
        punctuation_match = re.search(r'[,，;；]\s*', text[::-1])
        if punctuation_match:
            return len(text) - punctuation_match.end()

        # 其次在空白字符处分割
        space_match = re.search(r'\s+', text[::-1])
        if space_match:
            return len(text) - space_match.end()

        return -1

    def _protect_special_environments(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """保护特殊环境内容"""
        for env_type, patterns in self.special_envs.items():
            for pattern in patterns:
                content = re.sub(
                    pattern,
                    lambda m: self._store_protected_block(m.group(0), protected_blocks),
                    content,
                    flags=re.DOTALL
                )
        return content

    def _store_protected_block(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """存储受保护的内容块"""
        placeholder = f"PROTECTED_{len(protected_blocks)}"
        protected_blocks[placeholder] = content
        return placeholder

    def _restore_special_environments(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """恢复特殊环境内容"""
        for placeholder, original in protected_blocks.items():
            content = content.replace(placeholder, original)
        return content

    def _is_special_environment(self, text: str) -> bool:
        """判断是否是特殊环境"""
        for patterns in self.special_envs.values():
            for pattern in patterns:
                if re.search(pattern, text, re.DOTALL):
                    return True
        return False

    def _preprocess_content(self, content: str) -> str:
        """预处理TEX内容"""
        # 移除注释
        content = re.sub(r'(?m)%.*$', '', content)
        # 规范化空白字符
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # 移除不必要的命令
        content = re.sub(r'\\(label|ref|cite)\{[^}]*\}', '', content)
        return content.strip()

    def process(self, arxiv_id_or_url: str) -> Generator[ArxivFragment, None, None]:
        """处理单篇arxiv论文"""
        try:
            arxiv_id = self._normalize_arxiv_id(arxiv_id_or_url)
            paper_dir = self._download_and_extract(arxiv_id)

            # 查找主tex文件
            main_tex = self._find_main_tex_file(paper_dir)
            if not main_tex:
                raise RuntimeError(f"No main tex file found in {paper_dir}")

            # 获取所有相关tex文件
            tex_files = self._resolve_includes(main_tex)

            # 处理所有tex文件
            fragments = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self._process_single_tex, file_path): file_path
                    for file_path in tex_files
                }

                for future in as_completed(future_to_file):
                    try:
                        fragments.extend(future.result())
                    except Exception as e:
                        logging.error(f"Error processing file: {e}")

            # 重新计算片段索引
            fragments.sort(key=lambda x: (x.rel_path, x.segment_index))
            total_fragments = len(fragments)

            for i, fragment in enumerate(fragments):
                fragment.segment_index = i
                fragment.total_segments = total_fragments
                yield fragment

        except Exception as e:
            logging.error(f"Error processing paper {arxiv_id_or_url}: {e}")
            raise RuntimeError(f"Failed to process paper: {str(e)}")

    def _normalize_arxiv_id(self, input_str: str) -> str:
        """规范化arxiv ID"""
        if input_str.startswith('https://arxiv.org/'):
            if '/pdf/' in input_str:
                return input_str.split('/pdf/')[-1].split('v')[0]
            return input_str.split('/abs/')[-1].split('v')[0]
        return input_str.split('v')[0]

    def _download_and_extract(self, arxiv_id: str) -> str:
        """下载并解压arxiv论文源码"""
        paper_dir = self.root_dir / arxiv_id
        tar_path = paper_dir / f"{arxiv_id}.tar.gz"

        # 检查缓存
        if paper_dir.exists() and any(paper_dir.iterdir()):
            logging.info(f"Using cached version for {arxiv_id}")
            return str(paper_dir)

        paper_dir.mkdir(exist_ok=True)

        urls = [
            f"https://arxiv.org/src/{arxiv_id}",
            f"https://arxiv.org/e-print/{arxiv_id}"
        ]

        for url in urls:
            try:
                logging.info(f"Downloading from {url}")
                response = requests.get(url, proxies=self.proxies)
                if response.status_code == 200:
                    tar_path.write_bytes(response.content)
                    with tarfile.open(tar_path, 'r:gz') as tar:
                        tar.extractall(path=paper_dir)
                    return str(paper_dir)
            except Exception as e:
                logging.warning(f"Download failed for {url}: {e}")
                continue

        raise RuntimeError(f"Failed to download paper {arxiv_id}")

    def _read_file(self, file_path: str) -> Optional[str]:
        """使用多种编码尝试读取文件"""
        encodings = ['utf-8', 'latin1', 'gbk', 'gb2312', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        logging.warning(f"Failed to read file {file_path} with all encodings")
        return None

    def _extract_metadata(self, content: str) -> Tuple[str, str]:
        """提取论文标题和摘要"""
        title = ""
        abstract = ""

        # 提取标题
        title_patterns = [
            r'\\title{([^}]*)}',
            r'\\Title{([^}]*)}'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(1)
                title = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', title)
                break

        # 提取摘要
        abstract_patterns = [
            r'\\begin{abstract}(.*?)\\end{abstract}',
            r'\\abstract{([^}]*)}'
        ]
        for pattern in abstract_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                abstract = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', abstract)
                break

        return title.strip(), abstract.strip()

    def _get_section_info(self, para: str, content: str) -> Optional[Tuple[str, bool]]:
        """获取段落所属的章节信息"""
        section = "Unknown Section"
        is_appendix = False

        # 查找所有章节标记
        all_sections = []
        for pattern in self.section_patterns:
            for match in re.finditer(pattern, content):
                all_sections.append((match.start(), match.group(2)))

        # 查找appendix标记
        appendix_pos = content.find(r'\appendix')

        # 确定当前章节
        para_pos = content.find(para)
        if para_pos >= 0:
            current_section = None
            for sec_pos, sec_title in sorted(all_sections):
                if sec_pos > para_pos:
                    break
                current_section = sec_title

            if current_section:
                section = current_section
                is_appendix = appendix_pos >= 0 and para_pos > appendix_pos

            return section, is_appendix

        return None

    def _process_single_tex(self, file_path: str) -> List[ArxivFragment]:
        """处理单个TEX文件"""
        try:
            content = self._read_file(file_path)
            if not content:
                return []

            # 提取元数据
            is_main = r'\documentclass' in content
            title = ""
            abstract = ""
            if is_main:
                title, abstract = self._extract_metadata(content)

            # 智能分割内容
            segments = self._smart_split(content)
            fragments = []

            for i, (segment_content, section, is_appendix) in enumerate(segments):
                if segment_content.strip():
                    segment_type = 'text'
                    for env_type, patterns in self.special_envs.items():
                        if any(re.search(pattern, segment_content, re.DOTALL)
                               for pattern in patterns):
                            segment_type = env_type
                            break

                    fragments.append(ArxivFragment(
                        file_path=file_path,
                        content=segment_content,
                        segment_index=i,
                        total_segments=len(segments),
                        rel_path=os.path.relpath(file_path, str(self.root_dir)),
                        segment_type=segment_type,
                        title=title,
                        abstract=abstract,
                        section=section,
                        is_appendix=is_appendix
                    ))

            return fragments

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return []

def main():
    """使用示例"""
    # 创建分割器实例
    splitter = SmartArxivSplitter(
        char_range=(1000, 1200),
        root_dir="gpt_log/arxiv_cache"
    )

    # 处理论文
    for fragment in splitter.process("2411.03663"):
        print(f"Segment {fragment.segment_index + 1}/{fragment.total_segments}")
        print(f"Length: {len(fragment.content)}")
        print(f"Section: {fragment.section}")
        print(f"Title: {fragment.file_path}")

        print(fragment.content)
        print("-" * 80)


if __name__ == "__main__":
    main()
