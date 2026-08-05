class MarkdownFormatter:
    """Markdown格式文档生成器 - 用于生成对话记录的markdown文档"""

    def __init__(self):
        self.content = []

    def _add_content(self, text: str):
        """添加正文内容"""
        if text:
            self.content.append(f"\n{text}\n")

    def create_document(self, question: str, answer: str, ranked_papers: list = None) -> str:
        """创建完整的Markdown文档
        Args:
            question: str, 用户问题
            answer: str, AI回答
            ranked_papers: list, 排序后的论文列表
        Returns:
            str: 生成的Markdown文本
        """
        content = []

        # 添加问答部分
        content.append("## 问题")
        content.append(question)
        content.append("\n## 回答")
        content.append(answer)

        # 添加参考文献
        if ranked_papers:
            content.append("\n## 参考文献")
            for idx, paper in enumerate(ranked_papers, 1):
                authors = ', '.join(paper.authors[:3])
                if len(paper.authors) > 3:
                    authors += ' et al.'

                ref = f"[{idx}] {authors}. *{paper.title}*"
                if paper.venue_name:
                    ref += f". {paper.venue_name}"
                if paper.year:
                    ref += f", {paper.year}"
                if paper.doi:
                    ref += f". [DOI: {paper.doi}](https://doi.org/{paper.doi})"

                content.append(ref)

        return "\n\n".join(content)
