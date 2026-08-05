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
    markdown_text = re.sub(r'<a href=[\'"]([^\'"]+)[\'"](?:\s+target=[\'"][^\'"]+[\'"])?>([^<]+)</a>', r'\2 (\1)', markdown_text)

    # 6. Preserve paragraph breaks
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)  # normalize multiple newlines to double newlines

    # 7. Clean up extra spaces but maintain indentation
    markdown_text = re.sub(r' +', ' ', markdown_text)

    return markdown_text.strip()


class TxtFormatter:
    """文本格式化器 - 保留原始文档结构"""

    def __init__(self):
        self.content = []
        self._setup_document()

    def _setup_document(self):
        """初始化文档标题"""
        self.content.append("=" * 50)
        self.content.append("处理后文档".center(48))
        self.content.append("=" * 50)

    def _format_header(self):
        """创建文档头部信息"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y年%m月%d日')
        return [
            date_str.center(48),
            "\n"  # 添加空行
        ]

    def create_document(self, content):
        """生成保留原始结构的文档"""
        # 添加头部信息
        self.content.extend(self._format_header())

        # 处理内容，保留原始结构
        processed_content = convert_markdown_to_txt(content)

        # 添加处理后的内容
        self.content.append(processed_content)

        # 合并所有内容
        return "\n".join(self.content)
