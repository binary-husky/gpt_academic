class MarkdownFormatter:
    """Markdown格式文档生成器 - 保留原始文档结构"""

    def __init__(self):
        self.content = []

    def _add_content(self, text: str):
        """添加正文内容"""
        if text:
            self.content.append(f"\n{text}\n")

    def create_document(self, content: str, processing_type: str = "文本处理") -> str:
        """
        创建完整的Markdown文档，保留原始文档结构
        Args:
            content: 处理后的文档内容
            processing_type: 处理类型（润色、翻译等）
        Returns:
            str: 生成的Markdown文本
        """
        self.content = []

        # 添加标题和说明
        self.content.append(f"# 文档处理结果\n")
        self.content.append(f"## 处理方式: {processing_type}\n")

        # 添加处理时间
        from datetime import datetime
        self.content.append(f"*处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # 添加分隔线
        self.content.append("---\n")

        # 添加原始内容，保留结构
        self.content.append(content)

        # 添加结尾分隔线
        self.content.append("\n---\n")

        return "\n".join(self.content)
