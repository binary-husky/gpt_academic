import subprocess
import os

supports_format = ['.csv', '.docx', '.epub', '.ipynb',  '.mbox', '.md', '.pdf',  '.txt', '.ppt', '.pptm', '.pptx', '.bat']

def convert_to_markdown(file_path: str) -> str:
    """
    将支持的文件格式转换为Markdown格式
    Args:
        file_path: 输入文件路径
    Returns:
        str: 转换后的Markdown文件路径，如果转换失败则返回原始文件路径
    """
    _, ext = os.path.splitext(file_path.lower())

    if ext in ['.docx', '.doc', '.pptx', '.ppt', '.pptm', '.xls', '.xlsx', '.csv', 'pdf']:
        try:
            # 创建输出Markdown文件路径
            md_path = os.path.splitext(file_path)[0] + '.md'
            # 使用markitdown工具将文件转换为Markdown
            command = f"markitdown {file_path} > {md_path}"
            subprocess.run(command, shell=True, check=True)
            print(f"已将{ext}文件转换为Markdown: {md_path}")
            return md_path
        except Exception as e:
            print(f"{ext}转Markdown失败: {str(e)}，将继续处理原文件")
            return file_path

    return file_path

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
