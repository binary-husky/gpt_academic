
import re


def convert_markdown_to_txt(markdown_text):
    """Convert markdown text to plain text while preserving formatting"""
    # Standardize line endings
    markdown_text = markdown_text.replace('\r\n', '\n').replace('\r', '\n')

    # 1. Handle headers but keep their formatting instead of removing them
    markdown_text = re.sub(r'^#\s+(.+)$', r'# \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^##\s+(.+)$', r'## \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^###\s+(.+)$', r'### \1', markdown_text, flags=re.MULTILINE)

    # 2. Handle bold and italic - simply remove markers
    markdown_text = re.sub(r'\*\*(.+?)\*\*', r'\1', markdown_text)
    markdown_text = re.sub(r'\*(.+?)\*', r'\1', markdown_text)

    # 3. Handle lists but preserve formatting
    markdown_text = re.sub(r'^\s*[-*+]\s+(.+?)(?=\n|$)', r'• \1', markdown_text, flags=re.MULTILINE)

    # 4. Handle links - keep only the text
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', markdown_text)

    # 5. Handle HTML links - convert to user-friendly format
    markdown_text = re.sub(r'<a href=[\'"]([^\'"]+)[\'"](?:\s+target=[\'"][^\'"]+[\'"])?>([^<]+)</a>', r'\2 (\1)',
                           markdown_text)

    # 6. Preserve paragraph breaks
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)  # normalize multiple newlines to double newlines

    # 7. Clean up extra spaces but maintain indentation
    markdown_text = re.sub(r' +', ' ', markdown_text)

    return markdown_text.strip()


class TxtFormatter:
    """Chat history TXT document generator"""

    def __init__(self):
        self.content = []
        self._setup_document()

    def _setup_document(self):
        """Initialize document with header"""
        self.content.append("=" * 50)
        self.content.append("GPT-Academic对话记录".center(48))
        self.content.append("=" * 50)

    def _format_header(self):
        """Create document header with current date"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y年%m月%d日')
        return [
            date_str.center(48),
            "\n"  # Add blank line after date
        ]

    def create_document(self, history):
        """Generate document from chat history"""
        # Add header with date
        self.content.extend(self._format_header())

        # Add conversation content
        for i in range(0, len(history), 2):
            question = history[i]
            answer = convert_markdown_to_txt(history[i + 1]) if i + 1 < len(history) else ""

            if question:
                self.content.append(f"问题 {i // 2 + 1}：{str(question)}")
                self.content.append("")  # Add blank line

            if answer:
                self.content.append(f"回答 {i // 2 + 1}：{str(answer)}")
                self.content.append("")  # Add blank line

        # Join all content with newlines
        return "\n".join(self.content)
