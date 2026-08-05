

class HtmlFormatter:
    """聊天记录HTML格式生成器"""

    def __init__(self, chatbot, history):
        self.chatbot = chatbot
        self.history = history
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

    def format_chat_content(self) -> str:
        """格式化聊天内容"""
        chat_content = []
        for q, a in self.chatbot:
            question = str(q) if q is not None else ""
            answer = str(a) if a is not None else ""
            chat_content.append(f'''
            <div class="QaBox">
                <div class="Question">{question}</div>
                <div class="Answer">{answer}</div>
            </div>
            ''')
        return "\n".join(chat_content)

    def format_history_content(self) -> str:
        """格式化历史记录内容"""
        if not self.history:
            return ""

        history_content = []
        for entry in self.history:
            history_content.append(f'''
            <div class="historyBox">
                <div class="entry">{entry}</div>
            </div>
            ''')
        return "\n".join(history_content)

    def create_document(self) -> str:
        """生成完整的HTML文档

        Returns:
            str: 完整的HTML文档字符串
        """
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>对话存档</title>
            <style>{self.css_styles}</style>
        </head>
        <body>
            <div class="container">
                <h1 class="chat-title">对话存档</h1>
                <div class="chat-body">
                    {self.format_chat_content()}
                </div>
            </div>
        </body>
        </html>
        """
