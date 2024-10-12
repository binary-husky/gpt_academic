import os
from llama_index.core import SimpleDirectoryReader

supports_format = ['.csv', '.docx', '.epub', '.ipynb',  '.mbox', '.md', '.pdf',  '.txt', '.ppt',
                   '.pptm', '.pptx']


# 修改后的 extract_text 函数，结合 SimpleDirectoryReader 和自定义解析逻辑
def extract_text(file_path):
    _, ext = os.path.splitext(file_path.lower())

    # 使用 SimpleDirectoryReader 处理它支持的文件格式
    if ext in supports_format:
        try:
            reader = SimpleDirectoryReader(input_files=[file_path])
            documents = reader.load_data()
            if len(documents) > 0:
                return documents[0].text
        except Exception as e:
            pass

    return None
