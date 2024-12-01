"""
LaTeX Document Parser

This module provides functionality for parsing and extracting structured information from LaTeX documents,
including metadata, document structure, and content. It uses modular design and clean architecture principles.
"""

import re
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from copy import deepcopy
from crazy_functions.rag_fns.arxiv_fns.latex_cleaner import clean_latex_commands
from crazy_functions.rag_fns.arxiv_fns.section_extractor import Section, SectionLevel, EnhancedSectionExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_tex_file(file_path):
    encodings = ['utf-8', 'latin1', 'gbk', 'gb2312', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

@dataclass
class DocumentStructure:
    title: str = ''
    abstract: str = ''
    toc: List[Section] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def merge(self, other: 'DocumentStructure', strategy: str = 'smart') -> 'DocumentStructure':
        """
        Merge this document structure with another one.

        Args:
            other: Another DocumentStructure to merge with
            strategy: Merge strategy - 'smart' (default) or 'append'
                     'smart' - Intelligently merge sections with same titles
                     'append' - Simply append sections from other document
        """
        merged = deepcopy(self)

        # Merge title if needed
        if not merged.title and other.title:
            merged.title = other.title

        # Merge abstract
        merged.abstract = self._merge_abstract(merged.abstract, other.abstract)

        # Merge metadata
        merged.metadata.update(other.metadata)

        if strategy == 'append':
            merged.toc.extend(deepcopy(other.toc))
        else:  # smart merge
            # Create sections lookup for efficient merging
            sections_map = {s.title: s for s in merged.toc}

            for other_section in other.toc:
                if other_section.title in sections_map:
                    # Merge existing section
                    idx = next(i for i, s in enumerate(merged.toc)
                             if s.title == other_section.title)
                    merged.toc[idx] = merged.toc[idx].merge(other_section)
                else:
                    # Add new section
                    merged.toc.append(deepcopy(other_section))

        return merged

    @staticmethod
    def _merge_abstract(abstract1: str, abstract2: str) -> str:
        """Merge abstracts intelligently."""
        if not abstract1:
            return abstract2
        if not abstract2:
            return abstract1
        # Combine non-empty abstracts with a separator
        return f"{abstract1}\n\n{abstract2}"

    def generate_toc_tree(self, indent_char: str = "  ", abstract_preview_length: int = 0) -> str:
        """
        Generate a tree-like string representation of the table of contents including abstract.

        Args:
            indent_char: Character(s) used for indentation. Default is two spaces.
            abstract_preview_length: Maximum length of abstract preview. Default is 200 characters.

        Returns:
            str: A formatted string showing the hierarchical document structure with abstract
        """

        def _format_section(section: Section, level: int = 0) -> str:
            # Create the current section line with proper indentation
            current_line = f"{indent_char * level}{'•' if level > 0 else '○'} {section.title}\n"

            # Recursively process subsections
            subsections = ""
            if section.subsections:
                subsections = "".join(_format_section(subsec, level + 1)
                                      for subsec in section.subsections)

            return current_line + subsections

        result = []

        # Add document title if it exists
        if self.title:
            result.append(f"《{self.title}》\n")

        # Add abstract if it exists
        if self.abstract:
            result.append("\n□ Abstract:")
            # Format abstract content with word wrap
            abstract_preview = self.abstract[:abstract_preview_length]
            if len(self.abstract) > abstract_preview_length:
                abstract_preview += "..."

            # Split abstract into lines and indent them
            wrapped_lines = []
            current_line = ""
            for word in abstract_preview.split():
                if len(current_line) + len(word) + 1 <= 80:  # 80 characters per line
                    current_line = (current_line + " " + word).strip()
                else:
                    wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)

            # Add formatted abstract lines
            for line in wrapped_lines:
                result.append(f"\n{indent_char}{line}")
            result.append("\n")  # Add extra newline after abstract

        # Add table of contents header if there are sections
        if self.toc:
            result.append("\n◈ Table of Contents:\n")

            # Add all top-level sections and their subsections
            result.extend(_format_section(section, 0) for section in self.toc)

        return "".join(result)
class BaseExtractor(ABC):
    """Base class for LaTeX content extractors."""

    @abstractmethod
    def extract(self, content: str) -> str:
        """Extract specific content from LaTeX document."""
        pass

class TitleExtractor(BaseExtractor):
    """Extracts title from LaTeX document."""

    PATTERNS = [
        r'\\title{(.+?)}',
        r'\\title\[.*?\]{(.+?)}',
        r'\\Title{(.+?)}',
        r'\\TITLE{(.+?)}',
        r'\\begin{document}\s*\\section[*]?{(.+?)}',
        r'\\maketitle\s*\\section[*]?{(.+?)}',
        r'\\chapter[*]?{(.+?)}'
    ]

    def extract(self, content: str) -> str:
        """Extract title using defined patterns."""
        for pattern in self.PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
            for match in matches:
                title = match.group(1).strip()
                if title:
                    return clean_latex_commands(title)
        return ''

class AbstractExtractor(BaseExtractor):
    """Extracts abstract from LaTeX document."""

    PATTERNS = [
        r'\\begin{abstract}(.*?)\\end{abstract}',
        r'\\abstract{(.*?)}',
        r'\\ABSTRACT{(.*?)}',
        r'\\Abstract{(.*?)}',
        r'\\begin{Abstract}(.*?)\\end{Abstract}',
        r'\\section[*]?{(?:Abstract|ABSTRACT)}\s*(.*?)(?:\\section|\Z)',
        r'\\chapter[*]?{(?:Abstract|ABSTRACT)}\s*(.*?)(?:\\chapter|\Z)'
    ]

    def extract(self, content: str) -> str:
        """Extract abstract using defined patterns."""
        for pattern in self.PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
            for match in matches:
                abstract = match.group(1).strip()
                if abstract:
                    return clean_latex_commands(abstract)
        return ''

class EssayStructureParser:
    """Main class for parsing LaTeX documents."""

    def __init__(self):
        self.title_extractor = TitleExtractor()
        self.abstract_extractor = AbstractExtractor()
        self.section_extractor = EnhancedSectionExtractor()  # Using the enhanced extractor

    def parse(self, content: str) -> DocumentStructure:
        """Parse LaTeX document and extract structured information."""
        try:
            content = self._preprocess_content(content)

            return DocumentStructure(
                title=self.title_extractor.extract(content),
                abstract=self.abstract_extractor.extract(content),
                toc=self.section_extractor.extract(content)
            )
        except Exception as e:
            logger.error(f"Error parsing LaTeX document: {str(e)}")
            raise

    def _preprocess_content(self, content: str) -> str:
        """Preprocess LaTeX content for parsing."""
        # Remove comments
        content = re.sub(r'(?<!\\)%.*$', '', content, flags=re.MULTILINE)
        return content

def pretty_print_structure(doc: DocumentStructure, max_content_length: int = 100):
    """Print document structure in a readable format."""
    print(f"Title: {doc.title}\n")
    print(f"Abstract: {doc.abstract}\n")
    print("Table of Contents:")

    def print_section(section: Section, indent: int = 0):
        print("  " * indent + f"- {section.title}")
        if section.content:
            preview = section.content[:max_content_length]
            if len(section.content) > max_content_length:
                preview += "..."
            print("  " * (indent + 1) + f"Content: {preview}")
        for subsection in section.subsections:
            print_section(subsection, indent + 1)

    for section in doc.toc:
        print_section(section)

# Example usage:
if __name__ == "__main__":


    # Test with a file
    file_path = 'test_cache/2411.03663/neurips_2024.tex'
    main_tex = read_tex_file(file_path)

    # Parse main file
    parser = EssayStructureParser()
    main_doc = parser.parse(main_tex)

    # Merge other documents
    file_path_list = [
        "test_cache/2411.03663/1_intro.tex",
        "test_cache/2411.03663/0_abstract.tex",
        "test_cache/2411.03663/2_pre.tex",
        "test_cache/2411.03663/3_method.tex",
        "test_cache/2411.03663/4_experiment.tex",
        "test_cache/2411.03663/5_related_work.tex",
        "test_cache/2411.03663/6_conclu.tex",
        "test_cache/2411.03663/reference.bib"
    ]
    for file_path in file_path_list:
        tex_content = read_tex_file(file_path)
        additional_doc = parser.parse(tex_content)
        main_doc = main_doc.merge(additional_doc)

    tree= main_doc.generate_toc_tree()
    pretty_print_structure(main_doc)