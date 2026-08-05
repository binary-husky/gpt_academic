from datetime import datetime
import os
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def convert_markdown_to_pdf(markdown_text):
    """将Markdown文本转换为PDF格式的纯文本"""
    if not markdown_text:
        return ""

    # 标准化换行符
    markdown_text = markdown_text.replace('\r\n', '\n').replace('\r', '\n')

    # 处理标题、粗体、斜体
    markdown_text = re.sub(r'^#\s+(.+)$', r'\1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'\*\*(.+?)\*\*', r'\1', markdown_text)
    markdown_text = re.sub(r'\*(.+?)\*', r'\1', markdown_text)

    # 处理列表
    markdown_text = re.sub(r'^\s*[-*+]\s+(.+?)(?=\n|$)', r'• \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^\s*\d+\.\s+(.+?)(?=\n|$)', r'\1', markdown_text, flags=re.MULTILINE)

    # 处理链接
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', markdown_text)

    # 处理段落
    markdown_text = re.sub(r'\n{2,}', '\n', markdown_text)
    markdown_text = re.sub(r'(?<!\n)(?<!^)(?<!•\s)(?<!\d\.\s)\n(?![\s•\d])', '\n\n', markdown_text, flags=re.MULTILINE)

    # 清理空白
    markdown_text = re.sub(r' +', ' ', markdown_text)
    markdown_text = re.sub(r'(?m)^\s+|\s+$', '', markdown_text)

    return markdown_text.strip()

class PDFFormatter:
    """聊天记录PDF文档生成器 - 使用 Noto Sans CJK 字体"""

    def __init__(self):
        self._init_reportlab()
        self._register_fonts()
        self.styles = self._get_reportlab_lib()['getSampleStyleSheet']()
        self._create_styles()

    def _init_reportlab(self):
        """初始化 ReportLab 相关组件"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        self._lib = {
            'A4': A4,
            'getSampleStyleSheet': getSampleStyleSheet,
            'ParagraphStyle': ParagraphStyle,
            'cm': cm
        }

        self._platypus = {
            'SimpleDocTemplate': SimpleDocTemplate,
            'Paragraph': Paragraph,
            'Spacer': Spacer
        }

    def _get_reportlab_lib(self):
        return self._lib

    def _get_reportlab_platypus(self):
        return self._platypus

    def _register_fonts(self):
        """注册 Noto Sans CJK 字体"""
        possible_font_paths = [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto/NotoSansCJK-Regular.ttc'
        ]

        font_registered = False
        for path in possible_font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont('NotoSansCJK', path))
                    font_registered = True
                    break
                except:
                    continue

        if not font_registered:
            print("Warning: Could not find Noto Sans CJK font. Using fallback font.")
            self.font_name = 'Helvetica'
        else:
            self.font_name = 'NotoSansCJK'

    def _create_styles(self):
        """创建文档样式"""
        ParagraphStyle = self._lib['ParagraphStyle']

        # 标题样式
        self.styles.add(ParagraphStyle(
            name='Title_Custom',
            fontName=self.font_name,
            fontSize=24,
            leading=38,
            alignment=1,
            spaceAfter=32
        ))

        # 日期样式
        self.styles.add(ParagraphStyle(
            name='Date_Style',
            fontName=self.font_name,
            fontSize=16,
            leading=20,
            alignment=1,
            spaceAfter=20
        ))

        # 问题样式
        self.styles.add(ParagraphStyle(
            name='Question_Style',
            fontName=self.font_name,
            fontSize=12,
            leading=18,
            leftIndent=28,
            spaceAfter=6
        ))

        # 回答样式
        self.styles.add(ParagraphStyle(
            name='Answer_Style',
            fontName=self.font_name,
            fontSize=12,
            leading=18,
            leftIndent=28,
            spaceAfter=12
        ))

    def create_document(self, history, output_path):
        """生成PDF文档"""
        # 创建PDF文档
        doc = self._platypus['SimpleDocTemplate'](
            output_path,
            pagesize=self._lib['A4'],
            rightMargin=2.6 * self._lib['cm'],
            leftMargin=2.8 * self._lib['cm'],
            topMargin=3.7 * self._lib['cm'],
            bottomMargin=3.5 * self._lib['cm']
        )

        # 构建内容
        story = []
        Paragraph = self._platypus['Paragraph']

        # 添加对话内容
        for i in range(0, len(history), 2):
            question = history[i]
            answer = convert_markdown_to_pdf(history[i + 1]) if i + 1 < len(history) else ""

            if question:
                q_text = f'问题 {i // 2 + 1}：{str(question)}'
                story.append(Paragraph(q_text, self.styles['Question_Style']))

            if answer:
                a_text = f'回答 {i // 2 + 1}：{str(answer)}'
                story.append(Paragraph(a_text, self.styles['Answer_Style']))

        # 构建PDF
        doc.build(story)

        return doc
