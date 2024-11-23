from dataclasses import dataclass, field
from typing import Set, Dict, Pattern, Optional, List, Tuple
import re
from enum import Enum
import logging
from functools import lru_cache


class EnvType(Enum):
    """Environment classification types."""
    PRESERVE = "preserve"  # Preserve complete environment including commands
    REMOVE = "remove"  # Remove environment completely
    EXTRACT = "extract"  # Extract and clean content


@dataclass
class LatexConfig:
    """Configuration for LaTeX processing."""
    preserve_envs: Set[str] = field(default_factory=lambda: {
        # Math environments - preserve complete content
        'equation', 'equation*', 'align', 'align*', 'displaymath',
        'math', 'eqnarray', 'eqnarray*', 'gather', 'gather*',
        'multline', 'multline*', 'flalign', 'flalign*',
        'alignat', 'alignat*', 'cases', 'split', 'aligned',
        # Tables and figures - preserve structure and content
        'table', 'table*', 'tabular', 'tabularx', 'array', 'matrix',
        'figure', 'figure*', 'subfigure', 'wrapfigure',
        'minipage', 'tabbing', 'verbatim', 'longtable',
        'sidewaystable', 'sidewaysfigure', 'floatrow',
        # Arrays and matrices
        'pmatrix', 'bmatrix', 'Bmatrix', 'vmatrix', 'Vmatrix',
        'smallmatrix', 'array', 'matrix*', 'pmatrix*', 'bmatrix*',
        # Algorithms and code
        'algorithm', 'algorithmic', 'lstlisting', 'verbatim',
        'minted', 'listing', 'algorithmic*', 'algorithm2e',
        # Theorems and proofs
        'theorem', 'proof', 'definition', 'lemma', 'corollary',
        'proposition', 'example', 'remark', 'note', 'claim',
        'axiom', 'property', 'assumption', 'conjecture', 'observation',
        # Bibliography
        'thebibliography', 'bibliography', 'references'
    })

    # 引用类命令的特殊处理配置
    citation_commands: Set[str] = field(default_factory=lambda: {
        # Basic citations
        'cite', 'citep', 'citet', 'citeyear', 'citeauthor',
        'citeyearpar', 'citetext', 'citenum',
        # Natbib citations
        'citefullauthor', 'citealp', 'citealt', 'citename',
        'citepalias', 'citetalias', 'citetext',
        # Cross-references
        'ref', 'eqref', 'pageref', 'autoref', 'nameref', 'cref',
        'Cref', 'vref', 'Vref', 'fref', 'pref',
        # Hyperref
        'hyperref', 'href', 'url',
        # Labels
        'label', 'tag'
    })

    preserve_commands: Set[str] = field(default_factory=lambda: {
        # Text formatting
        'emph', 'textbf', 'textit', 'underline', 'texttt', 'footnote',
        'section', 'subsection', 'subsubsection', 'paragraph', 'part',
        'chapter', 'title', 'author', 'date', 'thanks',
        # Math operators and symbols
        'frac', 'sum', 'int', 'prod', 'lim', 'sup', 'inf',
        'partial', 'nabla', 'implies', 'iff', 'therefore',
        'exists', 'forall', 'in', 'subset', 'subseteq',
        # Greek letters and math symbols
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta',
        'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu',
        'nu', 'xi', 'pi', 'rho', 'sigma', 'tau',
        'upsilon', 'phi', 'chi', 'psi', 'omega',
        'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi',
        'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega',
        # Math commands
        'left', 'right', 'big', 'Big', 'bigg', 'Bigg',
        'mathbf', 'mathit', 'mathsf', 'mathtt', 'mathbb',
        'mathcal', 'mathfrak', 'mathscr', 'mathrm', 'mathop',
        'operatorname', 'overline', 'underline', 'overbrace',
        'underbrace', 'overset', 'underset', 'stackrel',
        # Spacing and alignment
        'quad', 'qquad', 'hspace', 'vspace', 'medskip',
        'bigskip', 'smallskip', 'hfill', 'vfill', 'centering',
        'raggedright', 'raggedleft'
    })

    remove_commands: Set[str] = field(default_factory=lambda: {
        # Document setup
        'documentclass', 'usepackage', 'input', 'include', 'includeonly',
        'bibliographystyle', 'frontmatter', 'mainmatter',
        'newtheorem', 'theoremstyle', 'proofname',
        'newcommand', 'renewcommand', 'providecommand', 'DeclareMathOperator',
        'newenvironment',
        # Layout and spacing
        'pagestyle', 'thispagestyle', 'newpage', 'clearpage',
        'pagebreak', 'linebreak', 'newline', 'setlength',
        'setcounter', 'addtocounter', 'makeatletter',
        'makeatother', 'pagenumbering'
    })

    latex_chars: Dict[str, str] = field(default_factory=lambda: {
        '~': ' ', '\\&': '&', '\\%': '%', '\\_': '_', '\\$': '$',
        '\\#': '#', '\\{': '{', '\\}': '}', '``': '"', "''": '"',
        '\\textbackslash': '\\', '\\ldots': '...', '\\dots': '...',
        '\\textasciitilde': '~', '\\textasciicircum': '^'
    })

    # 保留原始格式的特殊命令模式
    special_command_patterns: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r'\\cite\*?(?:\[[^\]]*\])?{([^}]+)}', r'\\cite{\1}'),
        (r'\\ref\*?{([^}]+)}', r'\\ref{\1}'),
        (r'\\label{([^}]+)}', r'\\label{\1}'),
        (r'\\eqref{([^}]+)}', r'\\eqref{\1}'),
        (r'\\autoref{([^}]+)}', r'\\autoref{\1}'),
        (r'\\url{([^}]+)}', r'\\url{\1}'),
        (r'\\href{([^}]+)}{([^}]+)}', r'\\href{\1}{\2}')
    ])


class LatexCleaner:
    """Enhanced LaTeX text cleaner that preserves mathematical content and citations."""

    def __init__(self, config: Optional[LatexConfig] = None):
        self.config = config or LatexConfig()
        self.logger = logging.getLogger(__name__)
        # 初始化正则表达式缓存
        self._regex_cache = {}

    @lru_cache(maxsize=128)
    def _get_env_pattern(self, env_name: str) -> Pattern:
        """Get cached regex pattern for environment matching."""
        return re.compile(fr'\\begin{{{env_name}}}(.*?)\\end{{{env_name}}}', re.DOTALL)

    def _get_env_type(self, env_name: str) -> EnvType:
        """Determine environment processing type."""
        if env_name.rstrip('*') in {name.rstrip('*') for name in self.config.preserve_envs}:
            return EnvType.PRESERVE
        elif env_name in {'comment'}:
            return EnvType.REMOVE
        return EnvType.EXTRACT

    def _preserve_special_commands(self, text: str) -> str:
        """Preserve special commands like citations and references with their complete structure."""
        for pattern, replacement in self.config.special_command_patterns:
            if pattern not in self._regex_cache:
                self._regex_cache[pattern] = re.compile(pattern)

            def replace_func(match):
                # 保持原始命令格式
                return match.group(0)

            text = self._regex_cache[pattern].sub(replace_func, text)
        return text

    def _process_environment(self, match: re.Match) -> str:
        """Process LaTeX environments while preserving complete content for special environments."""
        try:
            env_name = match.group(1)
            content = match.group(2)
            env_type = self._get_env_type(env_name)

            if env_type == EnvType.PRESERVE:
                # 完整保留环境内容
                complete_env = match.group(0)
                return f"\n[BEGIN_{env_name}]\n{complete_env}\n[END_{env_name}]\n"
            elif env_type == EnvType.REMOVE:
                return ' '
            else:
                # 处理嵌套环境
                return self._clean_nested_environments(content)
        except Exception as e:
            self.logger.error(f"Error processing environment {match.group(1) if match else 'unknown'}: {e}")
            return match.group(0)

    def _preserve_inline_math(self, text: str) -> str:
        """Preserve complete inline math content."""

        def preserve_math(match):
            return f" {match.group(0)} "

        patterns = [
            (r'\$[^$]+\$', preserve_math),
            (r'\\[\(\[].*?\\[\)\]]', preserve_math),
            (r'\\begin{math}.*?\\end{math}', preserve_math)
        ]

        for pattern, handler in patterns:
            if pattern not in self._regex_cache:
                self._regex_cache[pattern] = re.compile(pattern, re.DOTALL)
            text = self._regex_cache[pattern].sub(handler, text)

        return text

    def _clean_nested_environments(self, text: str) -> str:
        """Process nested environments recursively."""
        pattern = r'\\begin{(\w+)}(.*?)\\end{\1}'
        if pattern not in self._regex_cache:
            self._regex_cache[pattern] = re.compile(pattern, re.DOTALL)

        return self._regex_cache[pattern].sub(self._process_environment, text)

    def _clean_commands(self, text: str) -> str:
        """Clean LaTeX commands while preserving important content."""
        # 首先处理特殊命令
        text = self._preserve_special_commands(text)

        # 保留内联数学
        text = self._preserve_inline_math(text)

        # 移除指定的命令
        for cmd in self.config.remove_commands:
            if cmd not in self._regex_cache:
                self._regex_cache[cmd] = re.compile(
                    fr'\\{cmd}\*?(?:\[.*?\])?(?:{{.*?}})*'
                )
            text = self._regex_cache[cmd].sub('', text)

        # 处理带内容的命令
        def handle_command(match: re.Match) -> str:
            cmd = match.group(1).rstrip('*')
            if cmd in self.config.preserve_commands or cmd in self.config.citation_commands:
                return match.group(0)  # 完整保留命令和内容
            return ' '

        if 'command_pattern' not in self._regex_cache:
            self._regex_cache['command_pattern'] = re.compile(
                r'\\(\w+)\*?(?:\[.*?\])?{(.*?)}'
            )

        text = self._regex_cache['command_pattern'].sub(handle_command, text)
        return text

    def _normalize_text(self, text: str) -> str:
        """Normalize text while preserving special content markers."""
        # 替换特殊字符
        for char, replacement in self.config.latex_chars.items():
            text = text.replace(char, replacement)

        # 清理空白字符，同时保留环境标记
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*\[BEGIN_(\w+)\]\s*', r'\n[BEGIN_\1]\n', text)
        text = re.sub(r'\s*\[END_(\w+)\]\s*', r'\n[END_\1]\n', text)

        # 保持块级环境之间的分隔
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def clean_text(self, text: str) -> str:
        """Clean LaTeX text while preserving mathematical content, citations, and special environments."""
        if not text:
            return ""

        try:
            # 移除注释
            text = re.sub(r'(?<!\\)%.*?(?=\n|$)', '', text, flags=re.MULTILINE)

            # 处理环境
            text = self._clean_nested_environments(text)

            # 清理命令并规范化
            text = self._clean_commands(text)
            text = self._normalize_text(text)

            return text

        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text  # 发生错误时返回原始文本


def clean_latex_commands(text: str) -> str:
    """Convenience function for quick text cleaning with default config."""
    cleaner = LatexCleaner()
    return cleaner.clean_text(text)


# Example usage:
if __name__ == "__main__":
    text = r"""
    \documentclass{article}
    \begin{document}

    \section{Introduction}
    This is a reference to \cite{smith2020} and equation \eqref{eq:main}.

    \begin{equation}\label{eq:main}
    E = mc^2 \times \sum_{i=1}^{n} x_i
    \end{equation}

    See Figure \ref{fig:example} for details.

    \begin{figure}
    \includegraphics{image.png}
    \caption{Example figure\label
    \textbf{Important} result: $E=mc^2$ and
    \begin{equation}
    F = ma
    \end{equation}
    \label{sec:intro}
    """

    # Custom configuration
    config = LatexConfig(
        preserve_envs={},
        preserve_commands={'textbf', 'emph'},
        latex_chars={'~': ' ', '\\&': '&'}
    )


    def read_tex_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return "文件未找到，请检查路径是否正确。"
        except Exception as e:
            return f"读取文件时发生错误: {e}"


    # 使用函数
    file_path = 'test_cache/2411.03663/neurips_2024.tex'
    content = read_tex_file(file_path)
    cleaner = LatexCleaner(config)
    text = cleaner.clean_text(text)
    print(text)