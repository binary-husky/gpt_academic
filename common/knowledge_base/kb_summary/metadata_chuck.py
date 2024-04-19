# encoding: utf-8
# @Time   : 2024/3/25
# @Author : Spike
# @Descr   :
import json
import os
import time

from common.knowledge_base import kb_doc_api, kb_func
from request_llms.bridge_all import predict_no_ui_long_connection as no_ui_long_connection, model_info
from concurrent.futures import ThreadPoolExecutor, Future
from common.db.repository import prompt_repository
from common.func_box import replace_expected_text
from crazy_functions.reader_fns.crazy_box import split_list_token_limit, breakdown_text_to_satisfy_token_limit
from crazy_functions.reader_fns.crazy_box import file_reader_content
from typing import Dict, AnyStr
from common.logger_handler import logger


class SummaryMetadata:

    def __init__(self, llm_kwargs: dict, max_token: int = None, max_thread=10):
        self.llm_model = llm_kwargs.get('llm_model', 'gpt-3.5')
        self.llm_kwargs = llm_kwargs
        if max_token:
            self.max_token = max_token
        else:
            self._tokens = model_info[self.llm_model]['max_token']
            self.max_token = self._tokens / 2 - self._tokens / 4
        self.get_token_num = model_info[self.llm_model]['token_cnt']
        self.doc_ids = ''
        self.max_thread = max_thread
        self.docs_windows = {}
        self.file_windows = {}
        self.thread_: Dict[AnyStr, Future] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_thread)

    def __thread_input(self, input_, observe_window):
        result = no_ui_long_connection(input_, self.llm_kwargs, [],
                                       '', observe_window=observe_window)
        return result, observe_window

    def _thread_summary_input(self):
        observe_window = ["", time.time(), ""]  # [流式输出, 计算超时时间，异常输出]
        for file_name, input_ in self.file_windows.items():
            t = self.executor.submit(self.__thread_input, input_, observe_window)
            self.docs_windows[file_name] = observe_window + [input_]
            self.thread_[file_name] = t

    def _calculate_max_token(self, inputs, file_name):
        segments = []
        if isinstance(inputs, list):
            segments.extend(split_list_token_limit(data=inputs, get_num=self.get_token_num, max_num=self.max_token))
        else:
            segments.extend(breakdown_text_to_satisfy_token_limit(inputs, self.max_token, self.llm_model))
        for i, v in enumerate(segments):
            prompt = prompt_repository.query_prompt('提取文本摘要', '知识库提示词', source=None, quote_num=True)
            if prompt:
                prompt = prompt.value
            else:
                raise ValueError('无法找到提示词')
            v = replace_expected_text(prompt, v)
            self.file_windows[file_name + "_" + str(i)] = v
        return self.file_windows

    def __join_thread_result(self):
        while True:
            worker_done = [self.thread_[h].done() for h in self.thread_]
            run_status = {i: self.docs_windows[i][0] for i in self.docs_windows}
            yield run_status
            if all(worker_done):
                self.executor.shutdown()
                break

    def from_file_summary_(self, files: list):
        for f in files:
            file_name = os.path.basename(f).split('.')[0]
            content, _status = file_reader_content(f, os.path.dirname(f), {})
            if _status:
                logger.warning(_status)
            self._calculate_max_token(content, file_name)
        self._thread_summary_input()
        return self.__join_thread_result()

    def from_kb_summary_(self, kb_name, kb_file):
        info_fragment = kb_doc_api.search_docs(query='', knowledge_base_name=kb_name,
                                               top_k=1, score_threshold=1,
                                               file_name=kb_file, metadata={})
        self.doc_ids = ",".join([i.id for i in info_fragment])
        temp_windows = kb_func.get_vector_to_dict(info_fragment)
        for file_name, content in temp_windows.items():
            file_name = os.path.basename(file_name)
            self._calculate_max_token(content, file_name)
        self._thread_summary_input()
        return self.__join_thread_result()


if __name__ == '__main__':
    from common.toolbox import get_conf

    llm_kwargs = {
        "llm_model": 'gpt-3.5-turbo',
        "api_key": get_conf('API_KEY')
    }
    # summary = SummaryMetadata(llm_kwargs)
    # t = summary.from_file_summary_([''])