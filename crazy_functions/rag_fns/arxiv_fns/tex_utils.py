import re
import os
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional, Callable
from crazy_functions.rag_fns.arxiv_fns.latex_patterns import LaTeXPatterns

class TexUtils:
    """TeX文档处理器类"""

    def __init__(self, ):
        """
        初始化TeX处理器

        Args:
            char_range: 字符数范围(最小值, 最大值)
        """
        self.logger = logging.getLogger(__name__)

        # 初始化LaTeX环境和命令模式
        self._init_patterns()
        self.latex_only_patterns = LaTeXPatterns.latex_only_patterns




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

    def resolve_references(self, tex_file: str, path_dir: str = None) -> str:
        """
        解析TeX文件中的参考文献引用，返回所有引用文献的内容，只保留title、author和journal字段。
        如果在tex_file目录下没找到bib文件，会在path_dir中查找。

        Args:
            tex_file: TeX文件路径
            path_dir: 额外的参考文献搜索路径

        Returns:
            str: 所有参考文献内容的字符串，只包含特定字段，不同参考文献之间用空行分隔
        """
        all_references = []  # 存储所有参考文献内容
        content = self.read_file(tex_file)

        if not content:
            return ""

        # 扩展参考文献引用的模式
        bib_patterns = [
            r'\\bibliography\{([^}]+)\}',
            r'\\addbibresource\{([^}]+)\}',
            r'\\bibliographyfile\{([^}]+)\}',
            r'\\begin\{thebibliography\}',
            r'\\bibinput\{([^}]+)\}',
            r'\\newrefsection\{([^}]+)\}'
        ]

        base_dir = Path(tex_file).parent
        found_in_tex_dir = False

        # 首先在tex文件目录下查找显式引用的bib文件
        for pattern in bib_patterns:
            for match in re.finditer(pattern, content):
                if not match.groups():
                    continue

                bib_files = match.group(1).split(',')
                for bib_file in bib_files:
                    bib_file = bib_file.strip()
                    if not bib_file.endswith('.bib'):
                        bib_file += '.bib'

                    full_path = str(base_dir / bib_file)
                    if os.path.exists(full_path):
                        found_in_tex_dir = True
                        bib_content = self.read_file(full_path)
                        if bib_content:
                            processed_refs = self._process_bib_content(bib_content)
                            all_references.extend(processed_refs)

        # 如果在tex文件目录下没找到bib文件，且提供了额外搜索路径
        if not found_in_tex_dir and path_dir:
            search_dir = Path(path_dir)
            try:
                for bib_path in search_dir.glob('**/*.bib'):
                    bib_content = self.read_file(str(bib_path))
                    if bib_content:
                        processed_refs = self._process_bib_content(bib_content)
                        all_references.extend(processed_refs)
            except Exception as e:
                print(f"Error searching in path_dir: {e}")

        # 合并所有参考文献内容，用空行分隔
        return "\n\n".join(all_references)

    def _process_bib_content(self, content: str) -> List[str]:
        """
        处理bib文件内容，提取每个参考文献的特定字段

        Args:
            content: bib文件内容

        Returns:
            List[str]: 处理后的参考文献列表
        """
        processed_refs = []
        # 匹配完整的参考文献条目
        ref_pattern = r'@\w+\{[^@]*\}'
        # 匹配参考文献类型和键值
        entry_start_pattern = r'@(\w+)\{([^,]*?),'
        # 匹配字段
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'

        # 查找所有参考文献条目
        for ref_match in re.finditer(ref_pattern, content, re.DOTALL):
            ref_content = ref_match.group(0)

            # 获取参考文献类型和键值
            entry_match = re.match(entry_start_pattern, ref_content)
            if not entry_match:
                continue

            entry_type, cite_key = entry_match.groups()

            # 提取需要的字段
            needed_fields = {'title': None, 'author': None, 'journal': None}
            for field_match in re.finditer(field_pattern, ref_content):
                field_name, field_value = field_match.groups()
                field_name = field_name.lower()
                if field_name in needed_fields:
                    needed_fields[field_name] = field_value.strip()

            # 构建新的参考文献条目
            if any(needed_fields.values()):  # 如果至少有一个需要的字段
                ref_lines = [f"@{entry_type}{{{cite_key},"]
                for field_name, field_value in needed_fields.items():
                    if field_value:
                        ref_lines.append(f"  {field_name}={{{field_value}}},")
                ref_lines[-1] = ref_lines[-1][:-1]  # 移除最后一个逗号
                ref_lines.append("}")

                processed_refs.append("\n".join(ref_lines))

        return processed_refs
    def _extract_inline_references(self, content: str) -> str:
        """
        从tex文件内容中提取直接写在文件中的参考文献

        Args:
            content: tex文件内容

        Returns:
            str: 提取的参考文献内容，如果没有找到则返回空字符串
        """
        # 查找参考文献环境
        bib_start = r'\\begin\{thebibliography\}'
        bib_end = r'\\end\{thebibliography\}'

        start_match = re.search(bib_start, content)
        end_match = re.search(bib_end, content)

        if start_match and end_match:
            return content[start_match.start():end_match.end()]

        return ""
    def _preprocess_content(self, content: str) -> str:
        """预处理TeX内容"""
        # 移除注释
        content = re.sub(r'(?m)%.*$', '', content)
        # 规范化空白字符
        # content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()






