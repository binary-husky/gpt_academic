"""
LaTeX Document Parser

This module provides functionality for parsing and extracting structured information from LaTeX documents,
including metadata, document structure, and content. It uses modular design and clean architecture principles.
"""


import re
from abc import ABC, abstractmethod
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import logging
from copy import deepcopy
from crazy_functions.rag_fns.arxiv_fns.latex_cleaner import clean_latex_commands

logger = logging.getLogger(__name__)


class SectionLevel(Enum):
    CHAPTER = 0
    SECTION = 1
    SUBSECTION = 2
    SUBSUBSECTION = 3
    PARAGRAPH = 4
    SUBPARAGRAPH = 5


@dataclass
class Section:
    level: SectionLevel
    title: str
    content: str = ''
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


class SectionExtractor:
    """Extracts document structure including sections and their content."""

    def __init__(self):
        self.section_pattern = self._compile_section_pattern()

    def _compile_section_pattern(self) -> str:
        """Create pattern for matching section commands."""
        section_types = '|'.join(level.name.lower() for level in SectionLevel)
        return fr'\\({section_types})\*?(?:\[.*?\])?\{{(.*?)\}}'

    def extract(self, content: str) -> List[Section]:
        """Extract sections and build document hierarchy."""
        sections = []
        section_stack = []
        matches = list(re.finditer(self.section_pattern, content, re.IGNORECASE))

        for i, match in enumerate(matches):
            cmd_type = match.group(1).lower()
            section_title = match.group(2)
            level = SectionLevel[cmd_type.upper()]

            content = self._extract_section_content(content, match,
                                                    matches[i + 1] if i < len(matches) - 1 else None)

            new_section = Section(
                level=level,
                title=clean_latex_commands(section_title),
                content=clean_latex_commands(content)
            )

            self._update_section_hierarchy(sections, section_stack, new_section)

        return sections

    def _extract_section_content(self, content: str, current_match: re.Match,
                                 next_match: Optional[re.Match]) -> str:
        """Extract content between current section and next section."""
        start_pos = current_match.end()
        end_pos = next_match.start() if next_match else len(content)
        return content[start_pos:end_pos].strip()

    def _update_section_hierarchy(self, sections: List[Section],
                                  stack: List[Section], new_section: Section):
        """Update section hierarchy based on section levels."""
        while stack and stack[-1].level.value >= new_section.level.value:
            stack.pop()

        if stack:
            stack[-1].subsections.append(new_section)
        else:
            sections.append(new_section)

        stack.append(new_section)


class EssayStructureParser:
    """Main class for parsing LaTeX documents."""

    def __init__(self):
        self.title_extractor = TitleExtractor()
        self.abstract_extractor = AbstractExtractor()
        self.section_extractor = SectionExtractor()

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

        # # Handle input/include commands
        # content = re.sub(r'\\(?:input|include){.*?}', '', content)
        #
        # # Normalize newlines and whitespace
        # content = re.sub(r'\r\n?', '\n', content)
        # content = re.sub(r'\n\s*\n', '\n', content)

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
    # Sample main.tex
    main_tex = r"""
    \documentclass{article}
    \title{Research Paper}
    \begin{document}
    \begin{abstract}
    Main abstract introducing the research.
    \end{abstract}
    \section{Introduction}
    Overview of the topic...
    \section{Background}
    Part 1 of background...
    \end{document}
    """

    # Sample background.tex
    background_tex = r"""
    \section{Background}
    Part 2 of background...
    \subsection{Related Work}
    Discussion of related work...
    \section{Methodology}
    Research methods...
    """

    # Parse both files
    parser = EssayStructureParser()  # Assuming LaTeXParser class from previous code
    main_doc = parser.parse(main_tex)
    background_doc = parser.parse(background_tex)

    # Merge documents using smart strategy
    merged_doc = main_doc.merge(background_doc)

    # Example of how sections are merged:
    print("Original Background section content:",
          [s for s in main_doc.toc if s.title == "Background"][0].content)
    print("\nMerged Background section content:",
          [s for s in merged_doc.toc if s.title == "Background"][0].content)
    print("\nMerged structure:")
    pretty_print_structure(merged_doc)  # Assuming pretty_print_structure from previous code

    # Example of appending sections
    appended_doc = main_doc.merge(background_doc, strategy='append')
    print("\nAppended structure (may have duplicate sections):")
    pretty_print_structure(appended_doc)