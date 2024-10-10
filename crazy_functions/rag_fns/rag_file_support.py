import os
from llama_index.core import SimpleDirectoryReader

# 保留你原有的自定义解析函数
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# 修改后的 extract_text 函数，结合 SimpleDirectoryReader 和自定义解析逻辑
def extract_text(file_path):
    _, ext = os.path.splitext(file_path.lower())

    # 使用 SimpleDirectoryReader 处理它支持的文件格式
    if ext in ['.txt', '.md', '.pdf', '.docx', '.html']:
        try:
            reader = SimpleDirectoryReader(input_files=[file_path])
            documents = reader.load_data()
            if len(documents) > 0:
                return documents[0].text
        except Exception as e:
            pass

    # 如果 SimpleDirectoryReader 失败，或文件格式不支持，使用自定义解析逻辑
    if ext == '.pdf':
        try:
            return extract_text_from_pdf(file_path)
        except Exception as e:
            pass
    return None
