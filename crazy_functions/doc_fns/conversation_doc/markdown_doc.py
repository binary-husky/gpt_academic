
class MarkdownFormatter:
    """Markdown格式文档生成器 - 用于生成对话记录的markdown文档"""

    def __init__(self):
        self.content = []

    def _add_content(self, text: str):
        """添加正文内容"""
        if text:
            self.content.append(f"\n{text}\n")

    def create_document(self, history: list) -> str:
        """
        创建完整的Markdown文档
        Args:
            history: 历史记录列表，偶数位置为问题，奇数位置为答案
        Returns:
            str: 生成的Markdown文本
        """
        self.content = []

        # 处理问答对
        for i in range(0, len(history), 2):
            question = history[i]
            answer = history[i + 1]

            # 添加问题
            self.content.append(f"\n### 问题 {i//2 + 1}")
            self._add_content(question)

            # 添加回答
            self.content.append(f"\n### 回答 {i//2 + 1}")
            self._add_content(answer)

            # 添加分隔线
            self.content.append("\n---\n")

        return "\n".join(self.content)
