#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/20
# @Author : Spike
# @Descr   :
import json
import os
import copy
import re
from comm_tools import toolbox


class HistoryJsonHandle:

    def __init__(self, file_name):
        from comm_tools.overwrites import escape_markdown
        self.escape_markdown = escape_markdown
        self.chat_format = {'on_chat': []}
        self.plugin_format = {}
        self.base_data_format = {
            'chat': [],
            'chat_llms': {}
        }
        self.chat_tag = 'raw-message hideM'
        self.file_name = file_name
        if os.path.exists(str(self.file_name)):
            with open(self.file_name, 'r') as fp:
                self.base_data_format.update(json.load(fp))

    def analysis_chat_history(self, chat_list: list[list], history: list, cookies: dict, kwargs: dict):
        copy_cookies = copy.copy(cookies)
        # copy_cookies.pop('is_plugin')
        copy_cookies.pop('api_key')
        self.base_data_format['chat_llms'].update(copy_cookies)
        new_chat = chat_list[-1]
        handle_chat = []
        for i in new_chat:
            if str(i).find(self.chat_tag) != -1:
                pattern = re.compile(r'<div class="raw-message hideM">(.*?)</div>')
                match = pattern.search(str(i))
                i = self.escape_markdown(match.group()[1], reverse=True)
                handle_chat.append(i)
            else:
                handle_chat.append(i)
        self.chat_format['on_chat'] = handle_chat
        if kwargs:
            self.chat_format['plugin'] = kwargs
        self.base_data_format['chat'].append(self.chat_format)
        # 在写入前，记得删除key
        if self.base_data_format['chat_llms'].get('api-key'):
            del self.base_data_format['chat_llms']['api-key']
        with open(self.file_name, 'w') as fp:
            json.dump(self.base_data_format, fp, indent=2, ensure_ascii=False)
        return self

    def delete_the_latest_chat(self):
        self.base_data_format['chat'] = self.base_data_format['chat'][:-1]
        self.base_data_format['chat_llms']['history'] = self.base_data_format['chat_llms']['history'][:-2]
        if self.base_data_format['chat_llms'].get('api-key'):
            del self.base_data_format['chat_llms']['api-key']
        with open(self.file_name, 'w') as fp:
            json.dump(self.base_data_format, fp, indent=2, ensure_ascii=False)
        return self

    def update_for_history(self, cookies: dict, select):
        # cookies.update(self.base_data_format['chat_llms'])
        llms = self.base_data_format['chat_llms']
        default_params, = toolbox.get_conf('LLMS_DEFAULT_PARAMETER')
        llms_combo = [llms.get(key, default_params[key]) for key in default_params]
        llms_combo.append(self.base_data_format['chat_llms'].get('system_prompt', ''))
        try:
            chatbot = [i['on_chat'] for i in self.base_data_format['chat']]
            history = self.base_data_format['chat_llms'].get('history', [])
            cookies['is_plugin'] = self.base_data_format['chat'][-1].get('plugin', '')
            cookies['first_chat'] = select
            if not cookies.get('last_chat'):
                cookies['last_chat'] = self.base_data_format['chat'][-1]['on_chat'][0]
            return [chatbot, history, cookies, *llms_combo]
        except Exception:
            return [[], [], cookies, *llms_combo]


# class PromptJsonHandle:
# 不能用文件去保存提示词，如果多个用户操作同一份文件，会出错呢
