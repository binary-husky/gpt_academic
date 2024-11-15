import re
import os
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional, Callable
from crazy_functions.rag_fns.arxiv_fns.arxiv_fragment import ArxivFragment
from crazy_functions.rag_fns.arxiv_fns.latex_patterns import LaTeXPatterns

class TexProcessor:
    """TeX文档处理器类"""

    def __init__(self, char_range: Tuple[int, int]):
        """
        初始化TeX处理器

        Args:
            char_range: 字符数范围(最小值, 最大值)
        """
        self.min_chars, self.max_chars = char_range
        self.logger = logging.getLogger(__name__)

        # 初始化LaTeX环境和命令模式
        self._init_patterns()
        self.latex_only_patterns = LaTeXPatterns.latex_only_patterns
        # 初始化合并规则列表，每个规则是(priority, rule_func)元组
        self.merge_rules = []
        # 注册默认规则
        self.register_merge_rule(self._merge_short_segments, priority=90)
        self.register_merge_rule(self._merge_clauses, priority=100)

    def is_latex_commands_only(self, content: str) -> bool:
        """
        检查内容是否仅包含LaTeX命令

        Args:
            content: 要检查的内容

        Returns:
            bool: 如果内容仅包含LaTeX命令返回True，否则返回False
        """
        # 预处理：移除空白字符
        content = content.strip()
        if not content:
            return True

        # 移除注释
        content = re.sub(r'(?m)%.*$', '', content)
        content = content.strip()

        # 移除所有已知的LaTeX命令模式
        for pattern in self.latex_only_patterns:
            content = re.sub(pattern, '', content)

        # 移除常见的LaTeX控制序列
        content = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', content)

        # 移除剩余的空白字符
        content = re.sub(r'\s+', '', content)

        # 检查是否还有实质性内容
        # 如果长度为0或者只包含花括号、方括号等LaTeX标记，则认为是纯LaTeX命令
        remaining_chars = re.sub(r'[\{\}\[\]\(\)\,\\\s]', '', content)
        return len(remaining_chars) == 0

    def has_meaningful_content(self, content: str, min_text_ratio: float = 0.1) -> bool:
        """
        检查内容是否包含足够的有意义文本

        Args:
            content: 要检查的内容
            min_text_ratio: 最小文本比例（默认0.1，表示至少10%是文本）

        Returns:
            bool: 如果内容包含足够的有意义文本返回True，否则返回False
        """
        # 移除注释和空白字符
        content = re.sub(r'(?m)%.*$', '', content)
        content = content.strip()

        # 计算总长度
        total_length = len(content)
        if total_length == 0:
            return False

        # 移除所有LaTeX命令和环境
        for pattern in self.latex_only_patterns:
            content = re.sub(pattern, '', content)
        content = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', content)

        # 计算剩余文本长度（移除剩余的LaTeX标记）
        remaining_text = re.sub(r'[\{\}\[\]\(\)\,\\\s]', '', content)
        text_ratio = len(remaining_text) / total_length

        return text_ratio >= min_text_ratio

    def filter_fragments(self, fragments,
                         min_text_ratio: float = 0.1):
        """
        过滤fragment列表，移除仅包含LaTeX命令的片段,并合并相邻的片段

        Args:
            fragments: ArxivFragment列表
            min_text_ratio: 最小文本比例

        Returns:
            List[ArxivFragment]: 过滤后的fragment列表
        """
        filtered_fragments = []
        total_count = len(fragments)
        filtered_count = 0

        for fragment in fragments:
            if self.has_meaningful_content(fragment.content, min_text_ratio):
                filtered_fragments.append(fragment)
            else:
                filtered_count += 1
                self.logger.debug(f"Filtered out latex-only fragment: {fragment.content[:100]}...")

        # 记录过滤统计
        if filtered_count > 0:
            self.logger.info(f"Filtered out {filtered_count}/{total_count} latex-only fragments")

        # 重新计算索引
        for i, fragment in enumerate(filtered_fragments):
            fragment.segment_index = i
            fragment.total_segments = len(filtered_fragments)


        filtered_fragments = self.merge_segments(filtered_fragments)

        # 重新计算索引
        for i, fragment in enumerate(filtered_fragments):
            fragment.segment_index = i
            fragment.total_segments = len(filtered_fragments)

        return filtered_fragments
    def _is_special_environment(self, content: str) -> bool:
        """
        检查内容是否属于特殊环境

        Args:
            content: 要检查的内容

        Returns:
            bool: 如果内容属于特殊环境返回True，否则返回False
        """
        for env_patterns in self.special_envs.values():
            for pattern in env_patterns:
                if re.search(pattern, content, re.DOTALL):
                    return True
        return False

    def _init_patterns(self):
        """初始化LaTeX模式匹配规则"""
        # 特殊环境模式
        self.special_envs = LaTeXPatterns.special_envs
        # 章节模式
        self.section_patterns = LaTeXPatterns.section_patterns
        # 包含模式
        self.include_patterns = LaTeXPatterns.include_patterns
        # 元数据模式
        self.metadata_patterns = LaTeXPatterns.metadata_patterns

    def read_file(self, file_path: str) -> Optional[str]:
        """
        读取TeX文件内容，支持多种编码

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 文件内容或None
        """
        encodings = ['utf-8', 'latin1', 'gbk', 'gb2312', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        self.logger.warning(f"Failed to read {file_path} with all encodings")
        return None

    def find_main_tex_file(self, directory: str) -> Optional[str]:
        """
        查找主TeX文件

        Args:
            directory: 目录路径

        Returns:
            Optional[str]: 主文件路径或None
        """
        tex_files = list(Path(directory).rglob("*.tex"))
        if not tex_files:
            return None

        # 按优先级查找
        for tex_file in tex_files:
            content = self.read_file(str(tex_file))
            if content:
                if r'\documentclass' in content:
                    return str(tex_file)
                if tex_file.name.lower() == 'main.tex':
                    return str(tex_file)

        # 返回最大的tex文件
        return str(max(tex_files, key=lambda x: x.stat().st_size))

    def resolve_includes(self, tex_file: str, processed: Set[str] = None) -> List[str]:
        """
        解析TeX文件中的include引用

        Args:
            tex_file: TeX文件路径
            processed: 已处理的文件集合

        Returns:
            List[str]: 相关文件路径列表
        """
        if processed is None:
            processed = set()

        if tex_file in processed:
            return []

        processed.add(tex_file)
        result = [tex_file]
        content = self.read_file(tex_file)

        if not content:
            return result

        base_dir = Path(tex_file).parent
        for pattern in self.include_patterns:
            for match in re.finditer(pattern, content):
                included_file = match.group(2)
                if not included_file.endswith('.tex'):
                    included_file += '.tex'

                full_path = str(base_dir / included_file)
                if os.path.exists(full_path) and full_path not in processed:
                    result.extend(self.resolve_includes(full_path, processed))

        return result


    def _preprocess_content(self, content: str) -> str:
        """预处理TeX内容"""
        # 移除注释
        content = re.sub(r'(?m)%.*$', '', content)
        # 规范化空白字符
        # content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()

    def _protect_special_environments(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """保护特殊环境内容"""
        for env_patterns in self.special_envs.values():
            for pattern in env_patterns:
                content = re.sub(
                    pattern,
                    lambda m: self._store_protected_block(m.group(0), protected_blocks),
                    content,
                    flags=re.DOTALL
                )
        return content

    def _store_protected_block(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """存储保护块"""
        placeholder = f"__PROTECTED_{len(protected_blocks)}__"
        protected_blocks[placeholder] = content
        return placeholder

    def _restore_special_environments(self, content: str, protected_blocks: Dict[str, str]) -> str:
        """恢复特殊环境内容"""
        for placeholder, original in protected_blocks.items():
            content = content.replace(placeholder, original)
        return content

    def _get_section_info(self, para: str, content: str) -> Optional[Tuple[str, bool]]:
        """获取章节信息"""
        # 检查是否是附录
        is_appendix = bool(re.search(r'\\appendix', content))

        # 提取章节标题
        for pattern in self.section_patterns:
            match = re.search(pattern, para)
            if match:
                section_title = match.group(1)
                # 清理LaTeX命令
                section_title = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?{(.+?)}', r'\1', section_title)
                return section_title, is_appendix

        return None

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割长段落"""
        parts = []
        current_part = []
        current_length = 0

        sentences = re.split(r'(?<=[.!?。！？])\s+', paragraph)
        for sentence in sentences:
            sent_length = len(sentence)

            if current_length + sent_length <= self.max_chars:
                current_part.append(sentence)
                current_length += sent_length
            else:
                if current_part:
                    parts.append(' '.join(current_part))
                current_part = [sentence]
                current_length = sent_length

        if current_part:
            parts.append(' '.join(current_part))

        return parts

    def extract_metadata(self, content: str) -> Tuple[str, str]:
        """
        提取文档元数据

        Args:
            content: TeX内容

        Returns:
            Tuple[str, str]: (标题, 摘要)
        """
        title = ""
        abstract = ""

        # 提取标题
        for pattern in self.metadata_patterns['title']:
            match = re.search(pattern, content)
            if match:
                title = match.group(1)
                # 清理LaTeX命令
                title = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?{(.+?)}', r'\1', title)
                break

        # 提取摘要
        for pattern in self.metadata_patterns['abstract']:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                abstract = match.group(1)
                # 清理LaTeX命令
                abstract = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?{(.+?)}', r'\1', abstract)
                break

        return title.strip(), abstract.strip()

    def detect_segment_type(self, content: str) -> str:
        """
        检测片段类型

        Args:
            content: 内容片段

        Returns:
            str: 片段类型
        """
        for env_type, patterns in self.special_envs.items():
            for pattern in patterns:
                if re.search(pattern, content, re.DOTALL):
                    return env_type
        return 'text'

    def calculate_importance(self, content: str, segment_type: str, is_main: bool) -> float:
        """
        计算内容重要性得分

        Args:
            content: 内容片段
            segment_type: 片段类型
            is_main: 是否在主文件中

        Returns:
            float: 重要性得分 (0-1)
        """
        score = 0.5  # 基础分

        # 根据片段类型调整得分
        type_weights = {
            'text': 0.5,
            'math': 0.7,
            'table': 0.8,
            'figure': 0.6,
            'algorithm': 0.8
        }
        score += type_weights.get(segment_type, 0)

        # 根据位置调整得分
        if is_main:
            score += 0.2

        # 根据内容特征调整得分
        if re.search(r'\\label{', content):
            score += 0.1
        if re.search(r'\\cite{', content):
            score += 0.1
        if re.search(r'\\ref{', content):
            score += 0.1

        # 规范化得分到0-1范围
        return min(1.0, max(0.0, score))



    def split_content(self, content: str) -> List[Tuple[str, str, bool]]:
        """
        按段落分割TeX内容,对超长段落按换行符分割

        Args:
            content: TeX文档内容

        Returns:
            List[Tuple[str, str, bool]]: [(段落内容, 章节名, 是否附录)]
        """
        content = self._preprocess_content(content)
        segments = []
        current_section = "未命名章节"
        is_appendix = False

        # 保护特殊环境
        protected_blocks = {}
        # content = self._protect_special_environments(content, protected_blocks)

        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', content)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 恢复特殊环境
            para = self._restore_special_environments(para, protected_blocks)

            # 检查章节变化
            section_info = self._get_section_info(para, content)
            if section_info:
                current_section, is_appendix = section_info
                continue

            # 处理特殊环境
            if self._is_special_environment(para):
                # 特殊环境超长时分割
                if len(para) > self.max_chars:
                    split_parts = self._split_special_environment(para)
                    segments.extend((part, current_section, is_appendix) for part in split_parts)
                else:
                    segments.append((para, current_section, is_appendix))
                continue

            # 处理普通段落
            if len(para) > self.max_chars:
                # 按换行符分割超长段落
                split_parts = [p.strip() for p in para.split('\n') if p.strip()]
                segments.extend((part, current_section, is_appendix) for part in split_parts)
            else:
                segments.append((para, current_section, is_appendix))

        return segments

    def _is_complete_env(self, content: str) -> bool:
        """
        检查是否是完整的LaTeX环境

        Args:
            content: 要检查的内容

        Returns:
            bool: 是否是完整环境
        """
        try:
            # 检查基本数学环境配对
            env_pairs = [
                (r'\\begin{(equation\*?)}', r'\\end{equation\*?}'),
                (r'\\begin{(align\*?)}', r'\\end{align\*?}'),
                (r'\\begin{(gather\*?)}', r'\\end{gather\*?}'),
                (r'\\begin{(multline\*?)}', r'\\end{multline\*?}'),
                (r'\$\$', r'\$\$'),  # 行间数学
                (r'\$', r'\$'),  # 行内数学
                (r'\\[', r'\\]'),  # 显示数学
                (r'\\(', r'\\)'),  # 行内数学
                (r'\\begin{', r'\\end{')  # 通用环境
            ]

            # 检查所有环境配对
            for begin_pattern, end_pattern in env_pairs:
                if isinstance(begin_pattern, tuple):
                    begin_pattern, end_pattern = begin_pattern
                begin_count = len(re.findall(begin_pattern, content))
                end_count = len(re.findall(end_pattern, content))
                if begin_count != end_count:
                    return False

            # 检查括号配对
            brackets = {'{': '}', '[': ']', '(': ')'}
            bracket_count = {k: 0 for k in brackets.keys() | brackets.values()}

            for char in content:
                if char in bracket_count:
                    bracket_count[char] += 1

            for open_bracket, close_bracket in brackets.items():
                if bracket_count[open_bracket] != bracket_count[close_bracket]:
                    return False

            return True

        except Exception as e:
            self.logger.warning(f"Error checking environment completeness: {str(e)}")
            return False
    def _split_special_environment(self, content: str) -> List[str]:
        """
        分割特殊环境内容，确保环境的完整性

        Args:
            content: 特殊环境内容

        Returns:
            List[str]: 分割后的内容列表
        """
        env_type = self.detect_segment_type(content)

        # 如果内容已经在允许的长度范围内，且是完整的环境，直接返回
        try:
            if len(content) <= self.max_chars:
                if self._is_complete_env(content):
                    return [content]
        except Exception as e:
            self.logger.warning(f"Error checking environment in split_special_environment: {str(e)}")

        # 根据不同环境类型选择不同的分割策略
        if env_type == 'math':
            return self._split_math_content(content)
        elif env_type == 'table':
            return self._split_table_content(content)
        else:
            # 对于其他类型的环境
            parts = []
            current_part = ""

            # 按行分割并尝试保持环境完整性
            lines = content.split('\n')
            for line in lines:
                line_with_newline = line + '\n'

                # 检查是否添加当前行会超出长度限制
                if len(current_part) + len(line_with_newline) <= self.max_chars:
                    current_part += line_with_newline
                else:
                    # 如果当前部分不为空，进行处理
                    if current_part:
                        try:
                            # 尝试找到一个完整的环境结束点
                            if self._is_complete_env(current_part):
                                parts.append(current_part)
                                current_part = line_with_newline
                            else:
                                # 如果当前部分不是完整环境，继续添加
                                if len(current_part) + len(line_with_newline) <= self.max_chars * 1.5:  # 允许一定程度的超出
                                    current_part += line_with_newline
                                else:
                                    # 如果实在太长，强制分割
                                    parts.append(current_part)
                                    current_part = line_with_newline
                        except Exception as e:
                            self.logger.warning(f"Error processing environment part: {str(e)}")
                            parts.append(current_part)
                            current_part = line_with_newline
                    else:
                        # 如果当前行本身就超过长度限制
                        parts.append(line_with_newline)

            # 处理最后剩余的部分
            if current_part:
                parts.append(current_part)

            # 清理并返回非空片段
            return [p.strip() for p in parts if p.strip()]
    def _split_math_content(self, content: str) -> List[str]:
        """
        分割数学公式内容，确保公式环境的完整性

        Args:
            content: 数学公式内容

        Returns:
            List[str]: 分割后的公式列表
        """
        # 首先识别完整的数学环境
        math_envs = LaTeXPatterns.math_envs

        # 提取所有完整的数学环境
        parts = []
        last_end = 0
        math_blocks = []

        for pattern, env_type in math_envs:
            for match in re.finditer(pattern, content, re.DOTALL):
                math_blocks.append((match.start(), match.end(), match.group(0)))

        # 按照位置排序
        math_blocks.sort(key=lambda x: x[0])

        # 保持数学环境的完整性
        if not math_blocks:
            # 如果没有识别到完整的数学环境，作为单个块处理
            return [content] if len(content) <= self.max_chars else self._basic_content_split(content)

        current_part = ""
        for start, end, block in math_blocks:
            # 添加数学环境之前的文本
            if start > last_end:
                text_before = content[last_end:start]
                if text_before.strip():
                    current_part += text_before

            # 处理数学环境
            if len(block) > self.max_chars:
                # 如果当前部分已经有内容，先保存
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # 将过长的数学环境作为独立部分
                parts.append(block)
            else:
                # 如果添加当前数学环境会导致超出长度限制
                if current_part and len(current_part) + len(block) > self.max_chars:
                    parts.append(current_part)
                    current_part = block
                else:
                    current_part += block

            last_end = end

        # 处理最后的文本部分
        if last_end < len(content):
            remaining = content[last_end:]
            if remaining.strip():
                if current_part and len(current_part) + len(remaining) > self.max_chars:
                    parts.append(current_part)
                    current_part = remaining
                else:
                    current_part += remaining

        if current_part:
            parts.append(current_part)

        return parts


    def _split_table_content(self, content: str) -> List[str]:
        """
        分割表格内容

        Args:
            content: 表格内容

        Returns:
            List[str]: 分割后的表格部分列表
        """
        # 在表格行之间分割
        rows = re.split(r'(\\\\|\\hline)', content)
        result = []
        current_part = ""
        header = self._extract_table_header(content)

        for row in rows:
            if len(current_part + row) <= self.max_chars:
                current_part += row
            else:
                if current_part:
                    # 确保每个部分都是完整的表格结构
                    result.append(self._wrap_table_content(current_part, header))
                current_part = header + row if header else row

        if current_part:
            result.append(self._wrap_table_content(current_part, header))

        return result

    def _extract_table_header(self, content: str) -> str:
        """
        提取表格头部

        Args:
            content: 表格内容

        Returns:
            str: 表格头部
        """
        # 提取表格环境声明和列格式
        header_match = re.match(r'(\\begin{(?:table|tabular|longtable)\*?}.*?\\hline)', content, re.DOTALL)
        return header_match.group(1) if header_match else ""

    def _wrap_table_content(self, content: str, header: str) -> str:
        """
        包装表格内容为完整结构

        Args:
            content: 表格内容
            header: 表格头部

        Returns:
            str: 完整的表格结构
        """
        # 确保表格有正确的开始和结束标签
        env_match = re.search(r'\\begin{(table|tabular|longtable)\*?}', header or content)
        if env_match:
            env_type = env_match.group(1)
            if not content.startswith('\\begin'):
                content = f"{header}\n{content}" if header else content
            if not content.endswith(f'\\end{{{env_type}}}'):
                content = f"{content}\n\\end{{{env_type}}}"
        return content

    def _basic_content_split(self, content: str) -> List[str]:
        """
        基本的内容分割策略

        Args:
            content: 要分割的内容

        Returns:
            List[str]: 分割后的内容列表
        """
        parts = []
        while content:
            if len(content) <= self.max_chars:
                parts.append(content)
                break

            # 尝试在最后一个完整行处分割
            split_pos = content[:self.max_chars].rfind('\n')
            if split_pos == -1:  # 如果找不到换行符，则在最后一个空格处分割
                split_pos = content[:self.max_chars].rfind(' ')
            if split_pos == -1:  # 如果仍然找不到分割点，则强制分割
                split_pos = self.max_chars

            parts.append(content[:split_pos])
            content = content[split_pos:].strip()

        return parts

    def _ensure_segment_lengths(self, segments: List[Tuple[str, str, bool]]) -> List[Tuple[str, str, bool]]:
        """
        确保所有片段都在指定的长度范围内

        Args:
            segments: 原始片段列表

        Returns:
            List[Tuple[str, str, bool]]: 处理后的片段列表
        """
        result = []
        for content, section, is_appendix in segments:
            if len(content) <= self.max_chars:
                result.append((content, section, is_appendix))
            else:
                # 根据内容类型选择合适的分割方法
                if self._is_special_environment(content):
                    split_parts = self._split_special_environment(content)
                else:
                    split_parts = self._split_long_paragraph(content)

                result.extend((part, section, is_appendix) for part in split_parts)

        return result

    def register_merge_rule(self, rule_func: Callable[[List['ArxivFragment']], List['ArxivFragment']],
                            priority: int = 0) -> None:
        """
        注册新的合并规则

        Args:
            rule_func: 合并规则函数，接收fragment列表返回处理后的列表
            priority: 规则优先级，数字越大优先级越高
        """
        self.merge_rules.append((priority, rule_func))
        # 按优先级排序，保证高优先级规则先执行
        self.merge_rules.sort(reverse=True, key=lambda x: x[0])


    def _merge_segments(self, seg1: 'ArxivFragment', seg2: 'ArxivFragment') -> 'ArxivFragment':
        """
        合并两个片段的通用方法

        Args:
            seg1: 第一个片段
            seg2: 第二个片段

        Returns:
            ArxivFragment: 合并后的片段
        """
        return ArxivFragment(
            file_path=seg1.file_path,
            content=f"{seg1.content}\n{seg2.content}",
            segment_index=seg1.segment_index,
            total_segments=seg1.total_segments - 1,
            rel_path=seg1.rel_path,
            segment_type=self._merge_segment_type(seg1.segment_type, seg2.segment_type),
            title=seg1.title,
            abstract=seg1.abstract,
            section=seg1.section,
            is_appendix=seg1.is_appendix,
            importance=max(seg1.importance, seg2.importance)
        )

    def _merge_segment_type(self, type1: str, type2: str) -> str:
        """
        确定合并后片段的类型

        Args:
            type1: 第一个片段的类型
            type2: 第二个片段的类型

        Returns:
            str: 合并后的类型
        """
        # 如果类型相同，保持不变
        if type1 == type2:
            return type1
        # 如果其中之一是文本，返回非文本的类型
        if type1 == 'text':
            return type2
        if type2 == 'text':
            return type1
        # 如果是不同的特殊类型，返回 mixed
        return 'mixed'

    def _merge_short_segments(self, fragments: List['ArxivFragment']) -> List['ArxivFragment']:
        """
        合并短片段规则

        Args:
            fragments: 片段列表

        Returns:
            List[ArxivFragment]: 处理后的片段列表
        """
        if not fragments:
            return fragments

        # 持续合并直到没有可以合并的片段
        need_merge = True
        current_fragments = fragments
        max_iterations = len(fragments) * 2  # 设置最大迭代次数防止意外情况
        iteration_count = 0

        while need_merge and iteration_count < max_iterations:
            need_merge = False
            iteration_count += 1
            result = []
            i = 0

            while i < len(current_fragments):
                current = current_fragments[i]
                current_len = len(current.content)

                # 如果当前片段长度足够或是最后一个片段
                if current_len >= self.min_chars or i == len(current_fragments) - 1:
                    result.append(current)
                    i += 1
                    continue

                # 查找最适合合并的相邻片段
                best_target_idx = -1
                min_combined_length = float('inf')

                # 检查前后片段，选择合并后总长度最小的
                for idx in [i - 1, i + 1]:
                    if 0 <= idx < len(current_fragments):
                        target = current_fragments[idx]
                        target_len = len(target.content)
                        combined_len = current_len + target_len

                        # 更新最佳合并目标
                        if combined_len < min_combined_length and (
                                target_len < self.min_chars or  # 目标也是短片段
                                current_len < target_len  # 或当前片段更短
                        ):
                            min_combined_length = combined_len
                            best_target_idx = idx

                # 执行合并
                if best_target_idx != -1:
                    if best_target_idx < i:  # 与前一个片段合并
                        result.pop()  # 移除之前添加的片段
                        merged = self._merge_segments(current_fragments[best_target_idx], current)
                        result.append(merged)
                    else:  # 与后一个片段合并
                        merged = self._merge_segments(current, current_fragments[best_target_idx])
                        result.append(merged)
                        i += 1  # 跳过下一个片段
                    need_merge = True  # 标记发生了合并，需要继续检查
                    i += 1
                else:
                    # 如果没找到合适的合并目标，保留当前片段
                    result.append(current)
                    i += 1

            # 更新当前片段列表
            current_fragments = result

            # 检查是否还需要继续合并
            if not need_merge:
                # 最后检查一遍是否还有短片段
                has_short = any(len(f.content) < self.min_chars for f in result)
                need_merge = has_short and len(result) > 1

        # 如果达到最大迭代次数，记录警告
        if iteration_count >= max_iterations:
            self.logger.warning(f"Reached maximum iterations ({max_iterations}) in merge_short_segments")

        return current_fragments

    def _merge_where_clauses(self, fragments: List['ArxivFragment']) -> List['ArxivFragment']:
        """
        合并 where 子句规则

        Args:
            fragments: 片段列表

        Returns:
            List[ArxivFragment]: 处理后的片段列表
        """
        if not fragments:
            return fragments

        result = []
        i = 0
        while i < len(fragments):
            current = fragments[i]

            # 检查是否是 where 子句
            if current.content.strip().lower().startswith('where'):
                if result:  # 确保有前一个片段可以合并
                    merged = self._merge_segments(result.pop(), current)
                    result.append(merged)
                else:
                    result.append(current)
            else:
                result.append(current)
            i += 1

        return result

    def _merge_clauses(self, fragments: List['ArxivFragment']) -> List['ArxivFragment']:
        """
        合并从句和连接词规则，确保句子的完整性

        处理以下情况：
        1. where/which/that等从句
        2. 连接词(such that, so that等)
        3. 条件句(if, when等)
        4. 其他常见的数学论文连接词

        Args:
            fragments: 片段列表

        Returns:
            List[ArxivFragment]: 处理后的片段列表
        """
        if not fragments:
            return fragments

        # 需要合并的从句和连接词模式
        clause_patterns = [
            # 从句引导词
            r'^(?:where|which|that|whose|when)\b',
            # 数学中的连接词
            r'^(?:such\s+that|so\s+that|in\s+which|for\s+which)\b',
            # 条件引导词
            r'^(?:if|unless|provided|assuming)\b',
            # 其他常见数学连接词
            r'^(?:therefore|thus|hence|consequently|furthermore|moreover)\b',
            # 并列连接词
            r'^(?:and|or|but|while|whereas)\b',
            # 因果关系词
            r'^(?:because|since|as)\b',
            # 时序关系词
            r'^(?:after|before|until|whenever)\b',
            # 让步关系词
            r'^(?:although|though|even\s+if|even\s+though)\b',
            # 比较关系词
            r'^(?:than|as\s+[.\w]+\s+as)\b',
            # 目的关系词
            r'^(?:in\s+order\s+to|so\s+as\s+to)\b',
            # 条件关系词组
            r'^(?:on\s+condition\s+that|given\s+that|suppose\s+that)\b',
            # 常见数学术语
            r'^(?:denoted\s+by|defined\s+as|written\s+as|expressed\s+as)\b'
        ]
        # 编译正则表达式模式
        clause_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in clause_patterns]

        def is_clause_start(text: str) -> bool:
            """检查文本是否以从句或连接词开始"""
            text = text.strip()
            return any(pattern.search(text) for pattern in clause_patterns)

        def is_sentence_complete(text: str) -> bool:
            """检查句子是否完整（基于简单的标点符号检查）"""
            # 检查常见的句子结束符号
            end_markers = ['.', '。', '!', '?', '！', '？']
            # 排除可能的小数点和缩写
            text = text.strip()
            if not text:
                return False
            last_char = text[-1]
            if last_char in end_markers:
                # 确保不是小数点
                if last_char == '.' and re.search(r'\d\.$', text):
                    return False
                return True
            return False

        def should_merge(prev: ArxivFragment, curr: ArxivFragment) -> bool:
            """判断两个片段是否应该合并"""
            # 检查当前片段是否以从句开始
            if is_clause_start(curr.content):
                return True

            # 检查前一个片段是否句子完整
            if not is_sentence_complete(prev.content):
                # 如果前一个片段以数学公式结束，检查当前片段是否是其补充说明
                if re.search(r'[\$\)]\\?$', prev.content.strip()):
                    return True

            # 检查是否存在被截断的括号对
            brackets = {
                '(': ')', '[': ']', '{': '}',
                r'\{': r'\}', r'\[': r'\]', r'\(': r'\)'
            }
            for open_b, close_b in brackets.items():
                open_count = prev.content.count(open_b)
                close_count = prev.content.count(close_b)
                if open_count > close_count:
                    return True

            return False

        result = []
        i = 0
        while i < len(fragments):
            current = fragments[i]
            if "which means that the graph convolution adds up all atom features" in current.content:
                print("find here")
            if not result:
                result.append(current)
                i += 1
                continue

            prev = result[-1]
            if should_merge(prev, current):
                # 合并片段，确保不超过最大长度限制
                merged_content = f"{prev.content}\n{current.content}"
                if len(current.content) <= self.min_chars:
                    merged = self._merge_segments(prev, current)
                    result.pop()  # 移除前一个片段
                    result.append(merged)  # 添加合并后的片段
                else:
                    # 如果合并后超过长度限制，保持分开
                    result.append(current)
            else:
                result.append(current)
            i += 1

        return result

    # 在TexProcessor类中更新merge_segments方法
    def merge_segments(self, fragments: List['ArxivFragment']) -> List['ArxivFragment']:
        """
        按注册的规则合并片段

        Args:
            fragments: 要合并的片段列表

        Returns:
            List[ArxivFragment]: 合并后的片段列表
        """
        result = fragments

        # 首先处理从句和连接词
        result = self._merge_clauses(result)

        # 然后执行其他合并规则
        for _, rule_func in self.merge_rules:
            if rule_func != self._merge_where_clauses:  # 跳过旧的where从句处理
                result = rule_func(result)

        return result

