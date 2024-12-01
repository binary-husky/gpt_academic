import re
from typing import Optional


class LatexAuthorExtractor:
    def __init__(self):
        # Patterns for matching author blocks with balanced braces
        self.author_block_patterns = [
            # Standard LaTeX patterns with optional arguments
            r'\\author(?:\s*\[[^\]]*\])?\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\(?:title)?author[s]?\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\name[s]?\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\Author[s]?\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\AUTHOR[S]?\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            # Conference and journal specific patterns
            r'\\addauthor\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\IEEEauthor\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\speaker\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\authorrunning\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            # Academic publisher specific patterns
            r'\\alignauthor\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\spauthor\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
            r'\\authors\s*\{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)\}',
        ]

        # Cleaning patterns for LaTeX commands and formatting
        self.cleaning_patterns = [
            # Text formatting commands - preserve content
            (r'\\textbf\{([^}]+)\}', r'\1'),
            (r'\\textit\{([^}]+)\}', r'\1'),
            (r'\\emph\{([^}]+)\}', r'\1'),
            (r'\\texttt\{([^}]+)\}', r'\1'),
            (r'\\textrm\{([^}]+)\}', r'\1'),
            (r'\\text\{([^}]+)\}', r'\1'),

            # Affiliation and footnote markers
            (r'\$\^{[^}]+}\$', ''),
            (r'\^{[^}]+}', ''),
            (r'\\thanks\{[^}]+\}', ''),
            (r'\\footnote\{[^}]+\}', ''),

            # Email and contact formatting
            (r'\\email\{([^}]+)\}', r'\1'),
            (r'\\href\{[^}]+\}\{([^}]+)\}', r'\1'),

            # Institution formatting
            (r'\\inst\{[^}]+\}', ''),
            (r'\\affil\{[^}]+\}', ''),

            # Special characters and symbols
            (r'\\&', '&'),
            (r'\\\\\s*', ' '),
            (r'\\,', ' '),
            (r'\\;', ' '),
            (r'\\quad', ' '),
            (r'\\qquad', ' '),

            # Math mode content
            (r'\$[^$]+\$', ''),

            # Common symbols
            (r'\\dagger', '†'),
            (r'\\ddagger', '‡'),
            (r'\\ast', '*'),
            (r'\\star', '★'),

            # Remove remaining LaTeX commands
            (r'\\[a-zA-Z]+', ''),

            # Clean up remaining special characters
            (r'[\\{}]', '')
        ]

    def extract_author_block(self, text: str) -> Optional[str]:
        """
        Extract the complete author block from LaTeX text.

        Args:
            text (str): Input LaTeX text

        Returns:
            Optional[str]: Extracted author block or None if not found
        """
        try:
            if not text:
                return None

            for pattern in self.author_block_patterns:
                match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
                if match:
                    return match.group(1).strip()
            return None

        except (AttributeError, IndexError) as e:
            print(f"Error extracting author block: {e}")
            return None

    def clean_tex_commands(self, text: str) -> str:
        """
        Remove LaTeX commands and formatting from text while preserving content.

        Args:
            text (str): Text containing LaTeX commands

        Returns:
            str: Cleaned text with commands removed
        """
        if not text:
            return ""

        cleaned_text = text

        # Apply cleaning patterns
        for pattern, replacement in self.cleaning_patterns:
            cleaned_text = re.sub(pattern, replacement, cleaned_text)

        # Clean up whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def extract_authors(self, text: str) -> Optional[str]:
        """
        Extract and clean author information from LaTeX text.

        Args:
            text (str): Input LaTeX text

        Returns:
            Optional[str]: Cleaned author information or None if extraction fails
        """
        try:
            if not text:
                return None

            # Extract author block
            author_block = self.extract_author_block(text)
            if not author_block:
                return None

            # Clean LaTeX commands
            cleaned_authors = self.clean_tex_commands(author_block)
            return cleaned_authors or None

        except Exception as e:
            print(f"Error processing text: {e}")
            return None


def test_author_extractor():
    """Test the LatexAuthorExtractor with sample inputs."""
    test_cases = [
        # Basic test case
        (r"\author{John Doe}", "John Doe"),

        # Test with multiple authors
        (r"\author{Alice Smith \and Bob Jones}", "Alice Smith and Bob Jones"),

        # Test with affiliations
        (r"\author[1]{John Smith}\affil[1]{University}", "John Smith"),

    ]

    extractor = LatexAuthorExtractor()

    for i, (input_tex, expected) in enumerate(test_cases, 1):
        result = extractor.extract_authors(input_tex)
    print(f"\nTest case {i}:")
    print(f"Input: {input_tex[:50]}...")
    print(f"Expected: {expected[:50]}...")
    print(f"Got: {result[:50]}...")
    print(f"Pass: {bool(result and result.strip() == expected.strip())}")


if __name__ == "__main__":
    test_author_extractor()
