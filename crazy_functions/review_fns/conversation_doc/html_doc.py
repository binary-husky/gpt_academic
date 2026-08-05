class HtmlFormatter:
    """聊天记录HTML格式生成器"""

    def __init__(self):
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

        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .container {
            animation: fadeIn 0.6s ease-out;
        }

        .QaBox {
            animation: slideIn 0.5s ease-out;
            transition: all 0.3s ease;
        }

        .QaBox:hover {
            transform: translateX(5px);
        }
        .Question, .Answer, .historyBox {
            transition: all 0.3s ease;
        }
        .chat-title {
            color: var(--primary-color);
            font-size: 2em;
            text-align: center;
            margin: 1rem 0 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--primary-color);
        }

        .chat-body {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .QaBox {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }

        .Question {
            color: var(--secondary-color);
            font-weight: 500;
            margin-bottom: 1rem;
        }

        .Answer {
            color: var(--text-color);
            background: var(--primary-light);
            padding: 1rem;
            border-radius: 6px;
        }

        .history-section {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border-color);
        }

        .history-title {
            color: var(--secondary-color);
            font-size: 1.5em;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .historyBox {
            background: white;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #0f172a;
                --text-color: #e2e8f0;
                --border-color: #1e293b;
            }

            .container, .QaBox {
                background: #1e293b;
            }
        }
        """

    def create_document(self, question: str, answer: str, ranked_papers: list = None) -> str:
        """生成完整的HTML文档
        Args:
            question: str, 用户问题
            answer: str, AI回答
            ranked_papers: list, 排序后的论文列表
        Returns:
            str: 完整的HTML文档字符串
        """
        chat_content = f'''
        <div class="QaBox">
            <div class="Question">{question}</div>
            <div class="Answer markdown-body" id="answer-content">{answer}</div>
        </div>
        '''

        references_content = ""
        if ranked_papers:
            references_content = '<div class="history-section"><h2 class="history-title">参考文献</h2>'
            for idx, paper in enumerate(ranked_papers, 1):
                authors = ', '.join(paper.authors)

                # 构建引用信息
                citations_info = f"被引用次数：{paper.citations}" if paper.citations is not None else "引用信息未知"

                # 构建下载链接
                download_links = []
                if paper.doi:
                    # 检查是否是arXiv链接
                    if 'arxiv.org' in paper.doi:
                        # 如果DOI中包含完整的arXiv URL，直接使用
                        arxiv_url = paper.doi if paper.doi.startswith('http') else f'http://{paper.doi}'
                        download_links.append(f'<a href="{arxiv_url}">arXiv链接</a>')
                        # 提取arXiv ID并添加PDF链接
                        arxiv_id = arxiv_url.split('abs/')[-1].split('v')[0]
                        download_links.append(f'<a href="https://arxiv.org/pdf/{arxiv_id}.pdf">PDF下载</a>')
                    else:
                        # 非arXiv的DOI使用标准格式
                        download_links.append(f'<a href="https://doi.org/{paper.doi}">DOI: {paper.doi}</a>')

                if hasattr(paper, 'url') and paper.url and 'arxiv.org' not in str(paper.url):
                    # 只有当URL不是arXiv链接时才添加
                    download_links.append(f'<a href="{paper.url}">原文链接</a>')
                download_section = ' | '.join(download_links) if download_links else "无直接下载链接"

                # 构建来源信息
                source_info = []
                if paper.venue_type:
                    source_info.append(f"类型：{paper.venue_type}")
                if paper.venue_name:
                    source_info.append(f"来源：{paper.venue_name}")

                # 添加期刊指标信息
                if hasattr(paper, 'if_factor') and paper.if_factor:
                    source_info.append(f"<span class='journal-metric'>IF: {paper.if_factor}</span>")
                if hasattr(paper, 'jcr_division') and paper.jcr_division:
                    source_info.append(f"<span class='journal-metric'>JCR分区: {paper.jcr_division}</span>")
                if hasattr(paper, 'cas_division') and paper.cas_division:
                    source_info.append(f"<span class='journal-metric'>中科院分区: {paper.cas_division}</span>")

                if hasattr(paper, 'venue_info') and paper.venue_info:
                    if paper.venue_info.get('journal_ref'):
                        source_info.append(f"期刊参考：{paper.venue_info['journal_ref']}")
                    if paper.venue_info.get('publisher'):
                        source_info.append(f"出版商：{paper.venue_info['publisher']}")
                source_section = ' | '.join(source_info) if source_info else ""

                # 构建标准引用格式
                standard_citation = f"[{idx}] "
                # 添加作者（最多3个，超过则添加et al.）
                author_list = paper.authors[:3]
                if len(paper.authors) > 3:
                    author_list.append("et al.")
                standard_citation += ", ".join(author_list) + ". "
                # 添加标题
                standard_citation += f"<i>{paper.title}</i>"
                # 添加期刊/会议名称
                if paper.venue_name:
                    standard_citation += f". {paper.venue_name}"
                # 添加年份
                if paper.year:
                    standard_citation += f", {paper.year}"
                # 添加DOI
                if paper.doi:
                    if 'arxiv.org' in paper.doi:
                        # 如果是arXiv链接，直接使用arXiv URL
                        arxiv_url = paper.doi if paper.doi.startswith('http') else f'http://{paper.doi}'
                        standard_citation += f". {arxiv_url}"
                    else:
                        # 非arXiv的DOI使用标准格式
                        standard_citation += f". DOI: {paper.doi}"
                standard_citation += "."

                references_content += f'''
                <div class="historyBox">
                    <div class="entry">
                        <p class="paper-title"><b>[{idx}]</b> <i>{paper.title}</i></p>
                        <p class="paper-authors">作者：{authors}</p>
                        <p class="paper-year">发表年份：{paper.year if paper.year else "未知"}</p>
                        <p class="paper-citations">{citations_info}</p>
                        {f'<p class="paper-source">{source_section}</p>' if source_section else ""}
                        <p class="paper-abstract">摘要：{paper.abstract if paper.abstract else "无摘要"}</p>
                        <p class="paper-links">链接：{download_section}</p>
                        <div class="standard-citation">
                            <p class="citation-title">标准引用格式：</p>
                            <p class="citation-text">{standard_citation}</p>
                            <button class="copy-btn" onclick="copyToClipboard(this.previousElementSibling)">复制引用格式</button>
                        </div>
                    </div>
                </div>
                '''
            references_content += '</div>'

        # 添加新的CSS样式
        css_additions = """
            .paper-title {
                font-size: 1.1em;
                margin-bottom: 0.5em;
            }
            .paper-authors {
                color: var(--secondary-color);
                margin: 0.3em 0;
            }
            .paper-year, .paper-citations {
                color: var(--text-color);
                margin: 0.3em 0;
            }
            .paper-source {
                color: var(--text-color);
                font-style: italic;
                margin: 0.3em 0;
            }
            .paper-abstract {
                margin: 0.8em 0;
                padding: 0.8em;
                background: var(--primary-light);
                border-radius: 4px;
            }
            .paper-links {
                margin-top: 0.5em;
            }
            .paper-links a {
                color: var(--primary-color);
                text-decoration: none;
                margin-right: 1em;
            }
            .paper-links a:hover {
                text-decoration: underline;
            }
            .standard-citation {
                margin-top: 1em;
                padding: 1em;
                background: #f8fafc;
                border-radius: 4px;
                border: 1px solid var(--border-color);
            }

            .citation-title {
                font-weight: bold;
                margin-bottom: 0.5em;
                color: var(--secondary-color);
            }

            .citation-text {
                font-family: 'Times New Roman', Times, serif;
                line-height: 1.6;
                margin-bottom: 0.5em;
                padding: 0.5em;
                background: white;
                border-radius: 4px;
                border: 1px solid var(--border-color);
            }

            .copy-btn {
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 0.5em 1em;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background-color 0.2s;
            }

            .copy-btn:hover {
                background: #1e40af;
            }

            @media (prefers-color-scheme: dark) {
                .standard-citation {
                    background: #1e293b;
                }
                .citation-text {
                    background: #0f172a;
                }
            }

            /* 添加期刊指标样式 */
            .journal-metric {
                display: inline-block;
                padding: 0.2em 0.6em;
                margin: 0 0.3em;
                background: var(--primary-light);
                border-radius: 4px;
                font-weight: 500;
                color: var(--primary-color);
            }

            @media (prefers-color-scheme: dark) {
                .journal-metric {
                    background: #1e293b;
                    color: #60a5fa;
                }
            }
        """

        # 修改 js_code 部分，添加 markdown 解析功能
        js_code = """
        <script>
        // 复制功能
        function copyToClipboard(element) {
            const text = element.innerText;
            navigator.clipboard.writeText(text).then(function() {
                const btn = element.nextElementSibling;
                const originalText = btn.innerText;
                btn.innerText = '已复制！';
                setTimeout(() => {
                    btn.innerText = originalText;
                }, 2000);
            }).catch(function(err) {
                console.error('复制失败:', err);
            });
        }

        // Markdown解析
        document.addEventListener('DOMContentLoaded', function() {
            const answerContent = document.getElementById('answer-content');
            if (answerContent) {
                const markdown = answerContent.textContent;
                answerContent.innerHTML = marked.parse(markdown);
            }
        });
        </script>
        """

        # 将新的CSS样式添加到现有样式中
        self.css_styles += css_additions

        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>学术对话存档</title>
            <!-- 添加 marked.js -->
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <!-- 添加 GitHub Markdown CSS -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/sindresorhus/github-markdown-css@4.0.0/github-markdown.min.css">
            <style>
                {self.css_styles}
                /* 添加 Markdown 相关样式 */
                .markdown-body {{
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 1rem;
                    background: var(--primary-light);
                    border-radius: 6px;
                }}
                .markdown-body pre {{
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    padding: 16px;
                    overflow: auto;
                }}
                .markdown-body code {{
                    background-color: rgba(175,184,193,0.2);
                    border-radius: 6px;
                    padding: 0.2em 0.4em;
                    font-size: 85%;
                }}
                .markdown-body pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                .markdown-body blockquote {{
                    border-left: 0.25em solid #d0d7de;
                    padding: 0 1em;
                    color: #656d76;
                }}
                .markdown-body table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                .markdown-body table th,
                .markdown-body table td {{
                    border: 1px solid #d0d7de;
                    padding: 6px 13px;
                }}
                .markdown-body table tr:nth-child(2n) {{
                    background-color: #f6f8fa;
                }}
                @media (prefers-color-scheme: dark) {{
                    .markdown-body {{
                        background: #1e293b;
                        color: #e2e8f0;
                    }}
                    .markdown-body pre {{
                        background-color: #0f172a;
                    }}
                    .markdown-body code {{
                        background-color: rgba(99,110,123,0.4);
                    }}
                    .markdown-body blockquote {{
                        border-left-color: #30363d;
                        color: #8b949e;
                    }}
                    .markdown-body table th,
                    .markdown-body table td {{
                        border-color: #30363d;
                    }}
                    .markdown-body table tr:nth-child(2n) {{
                        background-color: #0f172a;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="chat-title">学术对话存档</h1>
                <div class="chat-body">
                    {chat_content}
                    {references_content}
                </div>
            </div>
            {js_code}
        </body>
        </html>
        """
