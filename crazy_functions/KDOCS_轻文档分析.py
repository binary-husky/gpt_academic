#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
from crazy_functions import crazy_box
from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder

@CatchException
def Kdocs_轻文档分析(link, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history=[]
