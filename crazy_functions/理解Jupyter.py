#! .\venv\
# encoding: utf-8
# @Time   : 2023/5/23
# @Author : Spike
# @Descr   :
import json
from comm_tools.toolbox import CatchException


class ParseNoteBook:

    def __init__(self, file):
        self.file = file

    def load_dict(self):
        with open(self.file, 'r', encoding='utf-8', errors='replace') as f:
            return json.load(f)


@CatchException
def 翻译理解jupyter(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    pass


if __name__ == '__main__':
    obj = ParseNoteBook('/Users/kilig/Desktop/jupy/NotarizedUpload.ipynb').load_dict()
    print(obj['cells'])

