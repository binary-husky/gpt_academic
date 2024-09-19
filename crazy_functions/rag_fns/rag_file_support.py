import os

import markdown
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from docx import Document as DocxDocument


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = DocxDocument(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text_from_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    return markdown.markdown(md_content)

def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return soup.get_text()

def extract_text(file_path):
    _, ext = os.path.splitext(file_path.lower())
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.md':
        return extract_text_from_md(file_path)
    elif ext == '.html':
        return extract_text_from_html(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")