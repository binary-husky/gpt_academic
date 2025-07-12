import os

supports_format = ['.csv', '.docx', '.epub', '.ipynb',  '.mbox', '.md', '.pdf',  '.txt', '.ppt', '.pptm', '.pptx', '.bat']


# 修改后的 extract_text 函数，结合 SimpleDirectoryReader 和自定义解析逻辑
def extract_text(file_path):
    from llama_index.core import SimpleDirectoryReader
    _, ext = os.path.splitext(file_path.lower())

    # 使用 SimpleDirectoryReader 处理它支持的文件格式
    if ext in supports_format:
        try:
            reader = SimpleDirectoryReader(input_files=[file_path])
            print(f"Extracting text from {file_path} using SimpleDirectoryReader")
            documents = reader.load_data()
            print(f"Complete: Extracting text from {file_path} using SimpleDirectoryReader")
            buffer = [ doc.text for doc in documents ]
            return '\n'.join(buffer)
        except Exception as e:
            pass
    else:
        return '格式不支持'
