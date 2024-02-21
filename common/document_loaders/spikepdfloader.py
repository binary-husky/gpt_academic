# encoding: utf-8
# @Time   : 2024/2/21
# @Author : Spike
# @Descr   :
import os
from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from crazy_functions.crazy_utils import read_and_clean_pdf_text
from common.path_handler import init_path


class ReaderPDFEve(UnstructuredFileLoader):

    def _get_elements(self) -> List:
        def pdf2md(file_path):
            save_path = os.path.dirname(file_path)
            _, content = read_and_clean_pdf_text(file_path, save_path)
            return content.replace(init_path.base_path, './')

        markdown = pdf2md(file_path=self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=markdown, **self.unstructured_kwargs)