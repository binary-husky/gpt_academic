from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
import os
import re


@dataclass
class SectionFragment:
    """Arxiv论文片段数据类"""
    title: str
    authors: str
    abstract: str
    catalogs: str
    arxiv_id: str = ""
    current_section: str = "Introduction"
    content: str = ''
    bibliography: str = ''


class PaperHtmlFormatter:
    """HTML格式论文文档生成器"""

    def __init__(self, fragments: List[SectionFragment], output_dir: Path):
        self.fragments = fragments
        self.output_dir = output_dir
        self.css_styles = """
        :root {
            --primary-color: #1a73e8;
            --secondary-color: #34495e;
            --background-color: #f8f9fa;
            --text-color: #2c3e50;
            --border-color: #e0e0e0;
            --code-bg-color: #f6f8fa;
        }

        body {
            font-family: "Source Serif Pro", "Times New Roman", serif;
            line-height: 1.8;
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
            color: var(--text-color);
            background-color: var(--background-color);
            font-size: 16px;
        }

        .container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }

        h1 {
            color: var(--primary-color);
            font-size: 2.2em;
            text-align: center;
            margin: 1.5rem 0;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--primary-color);
        }

        h2 {
            color: var(--secondary-color);
            font-size: 1.8em;
            margin-top: 2rem;
            padding-left: 1rem;
            border-left: 4px solid var(--primary-color);
        }

        h3 {
            color: var(--text-color);
            font-size: 1.5em;
            margin-top: 1.5rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5rem;
        }

        .authors {
            text-align: center;
            color: var(--secondary-color);
            font-size: 1.1em;
            margin: 1rem 0 2rem;
        }

        .abstract-container {
            background: var(--background-color);
            padding: 1.5rem;
            border-radius: 6px;
            margin: 2rem 0;
        }

        .abstract-title {
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }

        .abstract-content {
            font-style: italic;
            line-height: 1.7;
        }

        .toc {
            background: white;
            padding: 1.5rem;
            border-radius: 6px;
            margin: 2rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .toc-title {
            color: var(--primary-color);
            font-size: 1.4em;
            margin-bottom: 1rem;
        }

        .section-content {
            background: white;
            padding: 1.5rem;
            border-radius: 6px;
            margin: 1.5rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        .fragment {
            margin: 2rem 0;
            padding-left: 1rem;
            border-left: 3px solid var(--border-color);
        }

        .fragment:hover {
            border-left-color: var(--primary-color);
        }

        .bibliography {
            background: var(--code-bg-color);
            padding: 1rem;
            border-radius: 4px;
            font-family: "Source Code Pro", monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            margin-top: 1rem;
        }

        pre {
            background: var(--code-bg-color);
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            font-family: "Source Code Pro", monospace;
        }

        .paper-info {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin: 2rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .arxiv-id {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin: 1rem 0;
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--secondary-color);
        }

        .section-icon {
            color: var(--primary-color);
        }

        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
        }
        """

    def _sanitize_html(self, text: str) -> str:
        """清理HTML特殊字符"""
        if not text:
            return ""

        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _create_section_id(self, section: str) -> str:
        """创建section的ID"""
        section = section.strip() or "uncategorized"
        # 移除特殊字符,转换为小写并用连字符替换空格
        section_id = re.sub(r'[^\w\s-]', '', section.lower())
        return section_id.replace(' ', '-')

    def format_paper_info(self) -> str:
        """格式化论文基本信息"""
        if not self.fragments:
            return ""

        first_fragment = self.fragments[0]
        paper_info = ['<div class="paper-info">']

        # 添加标题
        if first_fragment.title:
            paper_info.append(f'<h1>{self._sanitize_html(first_fragment.title)}</h1>')

        # 添加arXiv ID
        if first_fragment.arxiv_id:
            paper_info.append(f'<div class="arxiv-id">arXiv: {self._sanitize_html(first_fragment.arxiv_id)}</div>')

        # 添加作者
        if first_fragment.authors:
            paper_info.append(f'<div class="authors">{self._sanitize_html(first_fragment.authors)}</div>')

        # 添加摘要
        if first_fragment.abstract:
            paper_info.append('<div class="abstract-container">')
            paper_info.append('<div class="abstract-title">Abstract</div>')
            paper_info.append(f'<div class="abstract-content">{self._sanitize_html(first_fragment.abstract)}</div>')
            paper_info.append('</div>')

        # 添加目录结构
        if first_fragment.catalogs:
            paper_info.append('<h2>Document Structure</h2>')
            paper_info.append('<pre>')
            paper_info.append(self._sanitize_html(first_fragment.catalogs))
            paper_info.append('</pre>')

        paper_info.append('</div>')
        return '\n'.join(paper_info)

    def format_table_of_contents(self, sections: Dict[str, List[SectionFragment]]) -> str:
        """生成目录"""
        toc = ['<div class="toc">']
        toc.append('<div class="toc-title">Table of Contents</div>')
        toc.append('<nav>')

        for section in sections:
            section_id = self._create_section_id(section)
            clean_section = section.strip() or "Uncategorized"
            toc.append(f'<div><a href="#{section_id}">{self._sanitize_html(clean_section)} '
                       f'</a></div>')

        toc.append('</nav>')
        toc.append('</div>')
        return '\n'.join(toc)

    def format_sections(self) -> str:
        """格式化论文各部分内容"""
        sections = {}
        for fragment in self.fragments:
            section = fragment.current_section or "Uncategorized"
            if section not in sections:
                sections[section] = []
            sections[section].append(fragment)

        formatted_html = ['<div class="content">']
        formatted_html.append(self.format_table_of_contents(sections))

        # 生成各部分内容
        for section, fragments in sections.items():
            section_id = self._create_section_id(section)
            formatted_html.append(f'<h2 id="{section_id}">')
            formatted_html.append(f'<span class="section-title">')
            formatted_html.append(f'<span class="section-icon">§</span>')
            formatted_html.append(f'{self._sanitize_html(section)}')
            formatted_html.append('</span>')
            formatted_html.append('</h2>')

            formatted_html.append('<div class="section-content">')

            for i, fragment in enumerate(fragments, 1):
                formatted_html.append('<div class="fragment">')

                # 添加内容
                if fragment.content:
                    formatted_html.append(
                        f'<div class="fragment-content">{self._sanitize_html(fragment.content)}</div>'
                    )

                # 添加参考文献
                if fragment.bibliography:
                    formatted_html.append('<div class="bibliography">')
                    formatted_html.append(f'{self._sanitize_html(fragment.bibliography)}')
                    formatted_html.append('</div>')

                formatted_html.append('</div>')

            formatted_html.append('</div>')

        formatted_html.append('</div>')
        return '\n'.join(formatted_html)

    def save_html(self) -> Path:
        """保存HTML文档"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"paper_content_{timestamp}.html"
            file_path = self.output_dir / filename

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>{self._sanitize_html(self.fragments[0].title if self.fragments else 'Paper Content')}</title>
                <style>
                {self.css_styles}
                </style>
            </head>
            <body>
                <div class="container">
                    {self.format_paper_info()}
                    {self.format_sections()}
                </div>
            </body>
            </html>
            """

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"HTML document saved to: {file_path}")
            return file_path

        except Exception as e:
            print(f"Error saving HTML document: {str(e)}")
            raise

# 使用示例：
# formatter = PaperHtmlFormatter(fragments, output_dir)
# output_path = formatter.save_html()