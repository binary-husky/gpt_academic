# encoding: utf-8
# @Time   : 2024/2/21
# @Author : Spike
# @Descr   :
import os
from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from crazy_functions.reader_fns.local_excel import XlsxHandler
from common.path_handler import init_path


class ReaderExcelEve(UnstructuredFileLoader):

    def _get_elements(self) -> List:
        def xl2md(file_path):
            ex_handle = XlsxHandler(file_path)
            ex_dict = ex_handle.read_as_dict(only_sheet=False)
            ex_content = "\n\n---\n\n".join(f"# {i}\n\n```\n{ex_dict[i]}\n```" for i in ex_dict)
            return ex_content.replace(init_path.base_path, './')

        markdown = xl2md(file_path=self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=markdown, **self.unstructured_kwargs)