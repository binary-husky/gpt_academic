import os
from llama_index.core import SimpleDirectoryReader

supports_format = ['.csv', '.docx','.doc', '.epub', '.ipynb',  '.mbox', '.md', '.pdf',  '.txt', '.ppt',
                   '.pptm', '.pptx','.py', '.xls', '.xlsx', '.html', '.json', '.xml', '.yaml', '.yml' ,'.m']

def read_docx_doc(file_path):
    if file_path.split(".")[-1] == "docx":
        from docx import Document
        doc = Document(file_path)
        file_content = "\n".join([para.text for para in doc.paragraphs])
    else:
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.visible = False
            # 打开文件
            doc = word.Documents.Open(os.getcwd() + '/' + file_path)
            # file_content = doc.Content.Text
            doc = word.ActiveDocument
            file_content = doc.Range().Text
            doc.Close()
            word.Quit()
        except:
            raise RuntimeError('请先将.doc文档转换为.docx文档。')
    return file_content

# 修改后的 extract_text 函数，结合 SimpleDirectoryReader 和自定义解析逻辑
import os

def extract_text(file_path):
    _, ext = os.path.splitext(file_path.lower())

    # 使用 SimpleDirectoryReader 处理它支持的文件格式
    if ext in ['.docx', '.doc']:
        return read_docx_doc(file_path)
    try:
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        if len(documents) > 0:
            return documents[0].text
    except Exception as e:
        pass

    return None
