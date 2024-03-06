# encoding: utf-8
# @Time   : 2024/2/21
# @Author : Spike
# @Descr   :
import os
from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from crazy_functions.reader_fns.local_image import ImgHandler
from common.path_handler import init_path


class ReaderVisionEve(UnstructuredFileLoader):

    def _get_elements(self) -> List:
        def md2md(file_path):
            save_path = os.path.dirname(file_path)
            llm_kwargs = {'llm_model': "gemini-pro-vision"}
            result, _, error = ImgHandler(file_path, save_path).get_llm_vision(llm_kwargs)
            if error:
                raise f"识别图片出错, 使用模型: {llm_kwargs}, 返回错误: {error}"
            return result.replace(init_path.base_path, '.')

        markdown = md2md(file_path=self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=markdown, **self.unstructured_kwargs)