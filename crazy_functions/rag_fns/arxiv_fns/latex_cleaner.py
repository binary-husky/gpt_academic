from dataclasses import dataclass, field
from typing import Set, Dict, Pattern, Optional
import re
from enum import Enum
import logging
from functools import lru_cache


class EnvType(Enum):
    """Environment classification types."""
    PRESERVE = "preserve"
    REMOVE = "remove"
    EXTRACT = "extract"


@dataclass
class LatexConfig:
    """Configuration for LaTeX processing."""
    preserve_envs: Set[str] = field(default_factory=lambda: {
        # Math environments
        'equation', 'equation*', 'align', 'align*', 'displaymath',
        'math', 'eqnarray', 'gather', 'gather*', 'multline', 'multline*',
        # Tables and figures
        'table', 'table*', 'tabular', 'tabularx', 'array', 'matrix',
        'figure', 'figure*', 'subfigure',
        # Algorithms and code
        'algorithm', 'algorithmic', 'lstlisting',
        # Theorems and proofs
        'theorem', 'proof', 'definition', 'lemma', 'corollary',
        'proposition', 'example', 'remark'
    })

    preserve_commands: Set[str] = field(default_factory=lambda: {
        # Citations and references
        'caption', 'label', 'ref', 'cite', 'citep', 'citet', 'eqref',
        # Text formatting
        'emph', 'textbf', 'textit', 'underline', 'texttt', 'footnote',
        'section', 'subsection', 'subsubsection', 'paragraph',
        # Math operators
        'frac', 'sum', 'int', 'prod', 'lim', 'sup', 'inf'
    })

    remove_commands: Set[str] = field(default_factory=lambda: {
        # Document setup
        'documentclass', 'usepackage', 'input', 'include', 'includeonly',
        'bibliography', 'bibliographystyle', 'frontmatter', 'mainmatter',
        # Layout and spacing
        'pagestyle', 'thispagestyle', 'vspace', 'hspace', 'vfill', 'hfill',
        'newpage', 'clearpage', 'pagebreak', 'linebreak', 'newline',
        'setlength', 'setcounter', 'addtocounter', 'renewcommand',
        'newcommand', 'makeatletter', 'makeatother', 'pagenumbering',
        # Margins and columns
        'marginpar', 'marginparsep', 'columnsep', 'columnseprule',
        'twocolumn', 'onecolumn', 'minipage', 'parbox'
    })

    latex_chars: Dict[str, str] = field(default_factory=lambda: {
        '~': ' ', '\\&': '&', '\\%': '%', '\\_': '_', '\\$': '$',
        '\\#': '#', '\\{': '{', '\\}': '}', '``': '"', "''": '"',
        '\\textbackslash': '\\', '\\ldots': '...', '\\dots': '...',
        '\\textasciitilde': '~', '\\textasciicircum': '^',
        '\\quad': ' ', '\\qquad': ' ', '\\,': '', '\\;': '', '\\:': '',
        '\\!': '', '\\space': ' ', '\\noindent': ''
    })

    inline_math_delimiters: Set[str] = field(default_factory=lambda: {
        '$', '\\(', '\\)', '\\[', '\\]'
    })


class LatexCleaner:
    """Efficient and modular LaTeX text cleaner."""

    def __init__(self, config: Optional[LatexConfig] = None):
        self.config = config or LatexConfig()
        self.logger = logging.getLogger(__name__)

    @lru_cache(maxsize=128)
    def _get_env_pattern(self, env_name: str) -> Pattern:
        return re.compile(fr'\\begin{{{env_name}}}(.*?)\\end{{{env_name}}}', re.DOTALL)

    def _get_env_type(self, env_name: str) -> EnvType:
        """Determine environment processing type."""
        if env_name.rstrip('*') in {name.rstrip('*') for name in self.config.preserve_envs}:
            return EnvType.PRESERVE
        elif env_name in {'verbatim', 'comment'}:
            return EnvType.REMOVE
        return EnvType.EXTRACT

    def _process_environment(self, match: re.Match) -> str:
        try:
            env_name = match.group(1)
            content = match.group(2)
            env_type = self._get_env_type(env_name)

            if env_type == EnvType.PRESERVE:
                # Preserve math content without markers for inline math
                if env_name in {'math', 'displaymath'}:
                    return f" {content} "
                return f" [BEGIN_{env_name}] {content} [END_{env_name}] "
            elif env_type == EnvType.REMOVE:
                return ' '
            # Process nested environments recursively
            return self._clean_nested_environments(content)
        except Exception as e:
            self.logger.error(f"Error processing environment {env_name}: {e}")
            return content

    def _clean_nested_environments(self, text: str) -> str:
        """Process nested environments recursively."""
        return re.sub(
            r'\\begin{(\w+)}(.*?)\\end{\1}',
            self._process_environment,
            text,
            flags=re.DOTALL
        )

    def _clean_commands(self, text: str) -> str:
        """Clean LaTeX commands while preserving specified content."""
        # Remove complete commands
        for cmd in self.config.remove_commands:
            text = re.sub(fr'\\{cmd}\*?(?:\[.*?\])?(?:{{.*?}})*', '', text)

        # Process commands with content
        def handle_command(match: re.Match) -> str:
            cmd = match.group(1).rstrip('*')  # Handle starred versions
            content = match.group(2)

            # Keep math content intact
            if cmd in {'[', ']', '(', ')', '$'} or cmd in self.config.inline_math_delimiters:
                return content

            return content if cmd in self.config.preserve_commands else ' '

        # Handle commands with arguments
        text = re.sub(r'\\(\w+)\*?(?:\[.*?\])?{(.*?)}', handle_command, text)

        # Handle inline math
        text = self._preserve_inline_math(text)

        # Remove remaining standalone commands
        return re.sub(r'\\[a-zA-Z]+\*?(?:\[\])?', '', text)

    def _preserve_inline_math(self, text: str) -> str:
        """Preserve inline math content."""
        # Handle $...$ math
        text = re.sub(r'\$(.+?)\$', r' \1 ', text)
        # Handle \(...\) math
        text = re.sub(r'\\[\(\[](.+?)\\[\)\]]', r' \1 ', text)
        return text

    def _normalize_text(self, text: str) -> str:
        """Normalize special characters and whitespace."""
        # Replace special characters
        for char, replacement in self.config.latex_chars.items():
            text = text.replace(char, replacement)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*\[BEGIN_(\w+)\]\s*', r' [BEGIN_\1] ', text)
        text = re.sub(r'\s*\[END_(\w+)\]\s*', r' [END_\1] ', text)

        # Remove empty brackets and braces
        text = re.sub(r'{\s*}|\[\s*\]|\(\s*\)', '', text)

        return text.strip()

    def clean_text(self, text: str) -> str:
        """Clean LaTeX text while preserving meaningful content."""
        if not text:
            raise ValueError("Input text cannot be empty")

        try:
            # Remove comments not inside environments
            text = re.sub(r'(?<!\\)%.*?(?=\n|$)', '', text, flags=re.MULTILINE)

            # Process environments and their nested contents
            text = self._clean_nested_environments(text)

            # Clean commands and normalize
            text = self._clean_commands(text)
            text = self._normalize_text(text)

            return text

        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            raise


def clean_latex_commands(text: str) -> str:
    """Convenience function for quick text cleaning with default config."""
    config = LatexConfig(
        preserve_envs={'equation', 'theorem'},
        preserve_commands={'textbf', 'emph', "label"},
        latex_chars={'~': ' ', '\\&': '&'}
    )
    return LatexCleaner(config).clean_text(text)


# Example usage:
if __name__ == "__main__":
    # Basic usage with inline math
    text = clean_latex_commands(r"""
    \textbf{Important} result: $E=mc^2$ and
    \begin{equation}
    F = ma
    \end{equation}
    """)
    print(text)

    # Custom configuration
    config = LatexConfig(
        preserve_envs={'equation', 'theorem'},
        preserve_commands={'textbf', 'emph'},
        latex_chars={'~': ' ', '\\&': '&'}
    )
    cleaner = LatexCleaner(config)
    text = cleaner.clean_text(r"\textbf{Custom} cleaning")
    print(text)