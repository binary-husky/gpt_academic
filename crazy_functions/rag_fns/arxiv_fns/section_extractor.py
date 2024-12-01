import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SectionLevel(Enum):
    CHAPTER = 0
    SECTION = 1
    SUBSECTION = 2
    SUBSUBSECTION = 3
    PARAGRAPH = 4
    SUBPARAGRAPH = 5

    def __lt__(self, other):
        if not isinstance(other, SectionLevel):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, SectionLevel):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, SectionLevel):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, SectionLevel):
            return NotImplemented
        return self.value >= other.value


@dataclass
class Section:
    level: SectionLevel
    title: str
    content: str = ''
    bibliography: str = ''
    subsections: List['Section'] = field(default_factory=list)

    def merge(self, other: 'Section') -> 'Section':
        """Merge this section with another section."""
        if self.title != other.title or self.level != other.level:
            raise ValueError("Can only merge sections with same title and level")

        merged = deepcopy(self)
        merged.content = self._merge_content(self.content, other.content)

        # Create subsections lookup for efficient merging
        subsections_map = {s.title: s for s in merged.subsections}

        for other_subsection in other.subsections:
            if other_subsection.title in subsections_map:
                # Merge existing subsection
                idx = next(i for i, s in enumerate(merged.subsections)
                           if s.title == other_subsection.title)
                merged.subsections[idx] = merged.subsections[idx].merge(other_subsection)
            else:
                # Add new subsection
                merged.subsections.append(deepcopy(other_subsection))

        return merged

    @staticmethod
    def _merge_content(content1: str, content2: str) -> str:
        """Merge content strings intelligently."""
        if not content1:
            return content2
        if not content2:
            return content1
        # Combine non-empty contents with a separator
        return f"{content1}\n\n{content2}"


@dataclass
class LatexEnvironment:
    """表示LaTeX环境的数据类"""
    name: str
    start: int
    end: int
    content: str
    raw: str


class EnhancedSectionExtractor:
    """Enhanced section extractor with comprehensive content handling and hierarchy management."""

    def __init__(self, preserve_environments: bool = True):
        """
        初始化Section提取器

        Args:
            preserve_environments: 是否保留特定环境（如equation, figure等）的原始LaTeX代码
        """
        self.preserve_environments = preserve_environments

        # Section级别定义
        self.section_levels = {
            'chapter': SectionLevel.CHAPTER,
            'section': SectionLevel.SECTION,
            'subsection': SectionLevel.SUBSECTION,
            'subsubsection': SectionLevel.SUBSUBSECTION,
            'paragraph': SectionLevel.PARAGRAPH,
            'subparagraph': SectionLevel.SUBPARAGRAPH
        }

        # 需要保留的环境类型
        self.important_environments = {
            'equation', 'equation*', 'align', 'align*',
            'figure', 'table', 'algorithm', 'algorithmic',
            'definition', 'theorem', 'lemma', 'proof',
            'itemize', 'enumerate', 'description'
        }

        # 改进的section pattern
        self.section_pattern = (
            r'\\(?P<type>chapter|section|subsection|subsubsection|paragraph|subparagraph)'
            r'\*?'  # Optional star
            r'(?:\[(?P<short>.*?)\])?'  # Optional short title
            r'{(?P<title>(?:[^{}]|\{[^{}]*\})*?)}'  # Main title with nested braces support
        )

        # 环境匹配模式
        self.environment_pattern = (
            r'\\begin{(?P<env_name>[^}]+)}'
            r'(?P<env_content>.*?)'
            r'\\end{(?P=env_name)}'
        )

    def _find_environments(self, content: str) -> List[LatexEnvironment]:
        """
        查找文档中的所有LaTeX环境。
        支持嵌套环境的处理。
        """
        environments = []
        stack = []

        # 使用正则表达式查找所有begin和end标记
        begin_pattern = r'\\begin{([^}]+)}'
        end_pattern = r'\\end{([^}]+)}'

        # 组合模式来同时匹配begin和end
        tokens = []
        for match in re.finditer(fr'({begin_pattern})|({end_pattern})', content):
            if match.group(1):  # begin标记
                tokens.append(('begin', match.group(1), match.start()))
            else:  # end标记
                tokens.append(('end', match.group(2), match.start()))

        # 处理环境嵌套
        for token_type, env_name, pos in tokens:
            if token_type == 'begin':
                stack.append((env_name, pos))
            elif token_type == 'end' and stack:
                if stack[-1][0] == env_name:
                    start_env_name, start_pos = stack.pop()
                    env_content = content[start_pos:pos]
                    raw_content = content[start_pos:pos + len('\\end{' + env_name + '}')]

                    if start_env_name in self.important_environments:
                        environments.append(LatexEnvironment(
                            name=start_env_name,
                            start=start_pos,
                            end=pos + len('\\end{' + env_name + '}'),
                            content=env_content,
                            raw=raw_content
                        ))

        return sorted(environments, key=lambda x: x.start)

    def _protect_environments(self, content: str) -> Tuple[str, Dict[str, str]]:
        """
        保护重要的LaTeX环境，用占位符替换它们。
        返回处理后的内容和恢复映射。
        """
        environments = self._find_environments(content)
        replacements = {}

        # 从后向前替换，避免位置改变的问题
        for env in reversed(environments):
            if env.name in self.important_environments:
                placeholder = f'__ENV_{len(replacements)}__'
                replacements[placeholder] = env.raw
                content = content[:env.start] + placeholder + content[env.end:]

        return content, replacements

    def _restore_environments(self, content: str, replacements: Dict[str, str]) -> str:
        """
        恢复之前保护的环境。
        """
        for placeholder, original in replacements.items():
            content = content.replace(placeholder, original)
        return content

    def extract(self, content: str) -> List[Section]:
        """
        从LaTeX文档中提取sections及其内容。

        Args:
            content: LaTeX文档内容

        Returns:
            List[Section]: 提取的section列表，包含层次结构
        """
        try:
            # 预处理：保护重要环境
            if self.preserve_environments:
                content, env_replacements = self._protect_environments(content)

            # 查找所有sections
            sections = self._find_all_sections(content)
            if not sections:
                return []

            # 处理sections
            root_sections = self._process_sections(content, sections)

            # 如果需要，恢复环境
            if self.preserve_environments:
                for section in self._traverse_sections(root_sections):
                    section.content = self._restore_environments(section.content, env_replacements)

            return root_sections

        except Exception as e:
            logger.error(f"Error extracting sections: {str(e)}")
            raise

    def _find_all_sections(self, content: str) -> List[dict]:
        """查找所有section命令及其位置。"""
        sections = []

        for match in re.finditer(self.section_pattern, content, re.DOTALL | re.MULTILINE):
            section_type = match.group('type').lower()
            if section_type not in self.section_levels:
                continue

            section = {
                'type': section_type,
                'level': self.section_levels[section_type],
                'title': self._clean_title(match.group('title')),
                'start': match.start(),
                'command_end': match.end(),
            }
            sections.append(section)

        return sorted(sections, key=lambda x: x['start'])

    def _process_sections(self, content: str, sections: List[dict]) -> List[Section]:
        """处理sections以构建层次结构和提取内容。"""
        # 计算content范围
        self._calculate_content_ranges(content, sections)

        # 构建层次结构
        root_sections = []
        section_stack = []

        for section_info in sections:
            new_section = Section(
                level=section_info['level'],
                title=section_info['title'],
                content=self._extract_clean_content(content, section_info),
                subsections=[]
            )

            # 调整堆栈以找到正确的父section
            while section_stack and section_stack[-1].level.value >= new_section.level.value:
                section_stack.pop()

            if section_stack:
                section_stack[-1].subsections.append(new_section)
            else:
                root_sections.append(new_section)

            section_stack.append(new_section)

        return root_sections

    def _calculate_content_ranges(self, content: str, sections: List[dict]):
        for i, current in enumerate(sections):
            content_start = current['command_end']

            # 找到下一个section（无论什么级别）
            content_end = len(content)
            for next_section in sections[i + 1:]:
                content_end = next_section['start']
                break

            current['content_range'] = (content_start, content_end)

    def _calculate_content_ranges_with_subsection_content(self, content: str, sections: List[dict]):
        """为每个section计算内容范围。"""
        for i, current in enumerate(sections):
            content_start = current['command_end']

            # 找到下一个同级或更高级的section
            content_end = len(content)
            for next_section in sections[i + 1:]:
                if next_section['level'] <= current['level']:
                    content_end = next_section['start']
                    break

            current['content_range'] = (content_start, content_end)

    def _extract_clean_content(self, content: str, section_info: dict) -> str:
        """提取并清理section内容。"""
        start, end = section_info['content_range']
        raw_content = content[start:end]

        # 清理内容
        clean_content = self._clean_content(raw_content)
        return clean_content

    def _clean_content(self, content: str) -> str:
        """清理LaTeX内容同时保留重要信息。"""
        # 移除注释
        content = re.sub(r'(?<!\\)%.*?\n', '\n', content)

        # LaTeX命令处理规则
        replacements = [
            # 保留引用
            (r'\\cite(?:\[.*?\])?{(.*?)}', r'[cite:\1]'),
            # 保留脚注
            (r'\\footnote{(.*?)}', r'[footnote:\1]'),
            # 处理引用
            (r'\\ref{(.*?)}', r'[ref:\1]'),
            # 保留URL
            (r'\\url{(.*?)}', r'[url:\1]'),
            # 保留超链接
            (r'\\href{(.*?)}{(.*?)}', r'[\2](\1)'),
            # 处理文本格式命令
            (r'\\(?:textbf|textit|emph){(.*?)}', r'\1'),
            # 保留特殊字符
            (r'\\([&%$#_{}])', r'\1'),
        ]

        # 应用所有替换规则
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # 清理多余的空白
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()

    def _clean_title(self, title: str) -> str:
        """清理section标题。"""
        # 处理嵌套的花括号
        while '{' in title:
            title = re.sub(r'{([^{}]*)}', r'\1', title)

        # 处理LaTeX命令
        title = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?{(.*?)}', r'\1', title)
        title = re.sub(r'\\([&%$#_{}])', r'\1', title)

        return title.strip()

    def _traverse_sections(self, sections: List[Section]) -> List[Section]:
        """遍历所有sections（包括子sections）。"""
        result = []
        for section in sections:
            result.append(section)
            result.extend(self._traverse_sections(section.subsections))
        return result


def test_enhanced_extractor():
    """使用复杂的测试用例测试提取器。"""
    test_content = r"""
\section{Complex Examples}
Here's a complex section with various environments.

\begin{equation}
E = mc^2
\end{equation}

\subsection{Nested Environments}
This subsection has nested environments.

\begin{figure}
\begin{equation*}
f(x) = \int_0^x g(t) dt
\end{equation*}
\caption{A nested equation in a figure}
\end{figure}

    """

    extractor = EnhancedSectionExtractor()
    sections = extractor.extract(test_content)

    def print_section(section, level=0):
        print("\n" + "  " * level + f"[{section.level.name}] {section.title}")
        if section.content:
            content_preview = section.content[:150] + "..." if len(section.content) > 150 else section.content
            print("  " * (level + 1) + f"Content: {content_preview}")
        for subsection in section.subsections:
            print_section(subsection, level + 1)

    print("\nExtracted Section Structure:")
    for section in sections:
        print_section(section)


if __name__ == "__main__":
    test_enhanced_extractor()
