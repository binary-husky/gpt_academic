class HtmlFormatter:
    """HTML格式文档生成器 - 保留原始文档结构"""

    def __init__(self, processing_type="文本处理"):
        self.processing_type = processing_type
        self.css_styles = """
        :root {
            --primary-color: #2563eb;
            --primary-light: #eff6ff;
            --secondary-color: #1e293b;
            --background-color: #f8fafc;
            --text-color: #334155;
            --border-color: #e2e8f0;
            --card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 2rem;
            color: var(--text-color);
            background-color: var(--background-color);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: var(--card-shadow);
        }
        ::selection {
            background: var(--primary-light);
            color: var(--primary-color);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .container {
            animation: fadeIn 0.6s ease-out;
        }

        .document-title {
            color: var(--primary-color);
            font-size: 2em;
            text-align: center;
            margin: 1rem 0 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--primary-color);
        }

        .document-body {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .document-header {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 2rem;
        }

        .processing-type {
            color: var(--secondary-color);
            font-size: 1.2em;
            margin: 0.5rem 0;
        }

        .processing-date {
            color: var(--text-color);
            font-size: 0.9em;
            opacity: 0.8;
        }

        .document-content {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* 保留文档结构的样式 */
        h1, h2, h3, h4, h5, h6 {
            color: var(--secondary-color);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }

        h1 { font-size: 1.8em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.3em; }
        h4 { font-size: 1.1em; }

        p {
            margin: 0.8em 0;
        }

        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }

        li {
            margin: 0.5em 0;
        }

        blockquote {
            margin: 1em 0;
            padding: 0.5em 1em;
            border-left: 4px solid var(--primary-light);
            background: rgba(0,0,0,0.02);
        }

        code {
            font-family: monospace;
            background: rgba(0,0,0,0.05);
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }

        pre {
            background: rgba(0,0,0,0.05);
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }

        pre code {
            background: transparent;
            padding: 0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #0f172a;
                --text-color: #e2e8f0;
                --border-color: #1e293b;
            }

            .container, .document-content {
                background: #1e293b;
            }

            blockquote {
                background: rgba(255,255,255,0.05);
            }

            code, pre {
                background: rgba(255,255,255,0.05);
            }
        }
        """

    def _escape_html(self, text):
        """转义HTML特殊字符"""
        import html
        return html.escape(text)

    def _markdown_to_html(self, text):
        """将Markdown格式转换为HTML格式，保留文档结构"""
        try:
            import markdown
            # 使用Python-Markdown库将markdown转换为HTML，启用更多扩展以支持嵌套列表
            return markdown.markdown(text, extensions=['tables', 'fenced_code', 'codehilite', 'nl2br', 'sane_lists', 'smarty', 'extra'])
        except ImportError:
            # 如果没有markdown库，使用更复杂的替换来处理嵌套列表
            import re

            # 替换标题
            text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
            text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
            text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)

            # 预处理列表 - 在列表项之间添加空行以正确分隔
            # 处理编号列表
            text = re.sub(r'(\n\d+\.\s.+)(\n\d+\.\s)', r'\1\n\2', text)
            # 处理项目符号列表
            text = re.sub(r'(\n•\s.+)(\n•\s)', r'\1\n\2', text)
            text = re.sub(r'(\n\*\s.+)(\n\*\s)', r'\1\n\2', text)
            text = re.sub(r'(\n-\s.+)(\n-\s)', r'\1\n\2', text)

            # 处理嵌套列表 - 确保正确的缩进和结构
            lines = text.split('\n')
            in_list = False
            list_type = None  # 'ol' 或 'ul'
            list_html = []
            normal_lines = []

            i = 0
            while i < len(lines):
                line = lines[i]

                # 匹配编号列表项
                numbered_match = re.match(r'^(\d+)\.\s+(.+)$', line)
                # 匹配项目符号列表项
                bullet_match = re.match(r'^[•\*-]\s+(.+)$', line)

                if numbered_match:
                    if not in_list or list_type != 'ol':
                        # 开始新的编号列表
                        if in_list:
                            # 关闭前一个列表
                            list_html.append(f'</{list_type}>')
                        list_html.append('<ol>')
                        in_list = True
                        list_type = 'ol'

                    num, content = numbered_match.groups()
                    list_html.append(f'<li>{content}</li>')

                elif bullet_match:
                    if not in_list or list_type != 'ul':
                        # 开始新的项目符号列表
                        if in_list:
                            # 关闭前一个列表
                            list_html.append(f'</{list_type}>')
                        list_html.append('<ul>')
                        in_list = True
                        list_type = 'ul'

                    content = bullet_match.group(1)
                    list_html.append(f'<li>{content}</li>')

                else:
                    if in_list:
                        # 结束当前列表
                        list_html.append(f'</{list_type}>')
                        in_list = False
                        # 将完成的列表添加到正常行中
                        normal_lines.append(''.join(list_html))
                        list_html = []

                    normal_lines.append(line)

                i += 1

            # 如果最后还在列表中，确保关闭列表
            if in_list:
                list_html.append(f'</{list_type}>')
                normal_lines.append(''.join(list_html))

            # 重建文本
            text = '\n'.join(normal_lines)

            # 替换段落，但避免处理已经是HTML标签的部分
            paragraphs = text.split('\n\n')
            for i, p in enumerate(paragraphs):
                # 如果不是以HTML标签开始且不为空
                if not (p.strip().startswith('<') and p.strip().endswith('>')) and p.strip() != '':
                    paragraphs[i] = f'<p>{p}</p>'

            return '\n'.join(paragraphs)

    def create_document(self, content: str) -> str:
        """生成完整的HTML文档，保留原始文档结构

        Args:
            content: 处理后的文档内容

        Returns:
            str: 完整的HTML文档字符串
        """
        from datetime import datetime

        # 将markdown内容转换为HTML
        html_content = self._markdown_to_html(content)

        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>文档处理结果</title>
            <style>{self.css_styles}</style>
        </head>
        <body>
            <div class="container">
                <h1 class="document-title">文档处理结果</h1>

                <div class="document-header">
                    <div class="processing-type">处理方式: {self._escape_html(self.processing_type)}</div>
                    <div class="processing-date">处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>

                <div class="document-content">
                    {html_content}
                </div>
            </div>
        </body>
        </html>
        """
