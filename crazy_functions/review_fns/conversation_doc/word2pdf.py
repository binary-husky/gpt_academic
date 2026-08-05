from docx2pdf import convert
import os
import platform
from typing import Union
from pathlib import Path
from datetime import datetime

class WordToPdfConverter:
    """Word文档转PDF转换器"""

    @staticmethod
    def _replace_docx_in_filename(filename: Union[str, Path]) -> Path:
        """
        将文件名中的'docx'替换为'pdf'
        例如: 'docx_test.pdf' -> 'pdf_test.pdf'
        """
        path = Path(filename)
        new_name = path.stem.replace('docx', 'pdf')
        return path.parent / f"{new_name}{path.suffix}"

    @staticmethod
    def convert_to_pdf(word_path: Union[str, Path], pdf_path: Union[str, Path] = None) -> str:
        """
        将Word文档转换为PDF

        参数:
            word_path: Word文档的路径
            pdf_path: 可选，PDF文件的输出路径。如果未指定，将使用与Word文档相同的名称和位置

        返回:
            生成的PDF文件路径

        异常:
            如果转换失败，将抛出相应异常
        """
        try:
            word_path = Path(word_path)

            if pdf_path is None:
                # 创建新的pdf路径，同时替换文件名中的docx
                pdf_path = WordToPdfConverter._replace_docx_in_filename(word_path).with_suffix('.pdf')
            else:
                pdf_path = WordToPdfConverter._replace_docx_in_filename(Path(pdf_path))

            # 检查操作系统
            if platform.system() == 'Linux':
                # Linux系统需要安装libreoffice
                if not os.system('which libreoffice') == 0:
                    raise RuntimeError("请先安装LibreOffice: sudo apt-get install libreoffice")

                # 使用libreoffice进行转换
                os.system(f'libreoffice --headless --convert-to pdf "{word_path}" --outdir "{pdf_path.parent}"')

                # 如果输出路径与默认生成的不同，则重命名
                default_pdf = word_path.with_suffix('.pdf')
                if default_pdf != pdf_path:
                    os.rename(default_pdf, pdf_path)
            else:
                # Windows和MacOS使用 docx2pdf
                convert(word_path, pdf_path)

            return str(pdf_path)

        except Exception as e:
            raise Exception(f"转换PDF失败: {str(e)}")

    @staticmethod
    def batch_convert(word_dir: Union[str, Path], pdf_dir: Union[str, Path] = None) -> list:
        """
        批量转换目录下的所有Word文档

        参数:
            word_dir: 包含Word文档的目录路径
            pdf_dir: 可选，PDF文件的输出目录。如果未指定，将使用与Word文档相同的目录

        返回:
            生成的PDF文件路径列表
        """
        word_dir = Path(word_dir)
        if pdf_dir:
            pdf_dir = Path(pdf_dir)
            pdf_dir.mkdir(parents=True, exist_ok=True)

        converted_files = []

        for word_file in word_dir.glob("*.docx"):
            try:
                if pdf_dir:
                    pdf_path = pdf_dir / WordToPdfConverter._replace_docx_in_filename(
                        word_file.with_suffix('.pdf')
                    ).name
                else:
                    pdf_path = WordToPdfConverter._replace_docx_in_filename(
                        word_file.with_suffix('.pdf')
                    )

                pdf_file = WordToPdfConverter.convert_to_pdf(word_file, pdf_path)
                converted_files.append(pdf_file)

            except Exception as e:
                print(f"转换 {word_file} 失败: {str(e)}")

        return converted_files

    @staticmethod
    def convert_doc_to_pdf(doc, output_dir: Union[str, Path] = None) -> str:
        """
        将docx对象直接转换为PDF

        参数:
            doc: python-docx的Document对象
            output_dir: 可选，输出目录。如果未指定，将使用当前目录

        返回:
            生成的PDF文件路径
        """
        try:
            # 设置临时文件路径和输出路径
            output_dir = Path(output_dir) if output_dir else Path.cwd()
            output_dir.mkdir(parents=True, exist_ok=True)

            # 生成临时word文件
            temp_docx = output_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            doc.save(temp_docx)

            # 转换为PDF
            pdf_path = temp_docx.with_suffix('.pdf')
            WordToPdfConverter.convert_to_pdf(temp_docx, pdf_path)

            # 删除临时word文件
            temp_docx.unlink()

            return str(pdf_path)

        except Exception as e:
            if temp_docx.exists():
                temp_docx.unlink()
            raise Exception(f"转换PDF失败: {str(e)}")
