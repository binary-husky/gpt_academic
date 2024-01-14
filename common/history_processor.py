# encoding: utf-8
# @Time   : 2023/9/20
# @Author : Spike
# @Descr   :
import json
import os
import copy
import gradio as gr
from common import toolbox
from common import func_box
from bs4 import BeautifulSoup
from common.path_handle import init_path


class HistoryJsonHandle:

    def __init__(self, file_name):
        from webui_elem.overwrites import escape_markdown
        self.escape_markdown = escape_markdown
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

    def analysis_chat_history(self, chat_list: list[list], cookies: dict):
        copy_cookies = copy.copy(cookies)
        copy_cookies.pop('api_key')
        copy_cookies.pop('know_dict')
        if cookies.get('plugin_state'):
            copy_cookies.pop('plugin_state')
        self.base_data_format['chat_llms'].update(copy_cookies)
        index_old = len(self.base_data_format['chat'])
        for chat in chat_list[index_old:]:
            handle_chat = []
            for i in chat:
                if str(i).find(self.chat_tag) != -1:
                    soup = BeautifulSoup(i, 'html.parser')
                    raw_message = soup.select_one('.raw-message.hideM').text
                    handle_chat.append(raw_message)
                else:
                    handle_chat.append(i)
            chat_format = {'on_chat': handle_chat}
            self.base_data_format['chat'].append(chat_format)
        if cookies.get('is_plugin'):
            self.base_data_format['chat'][-1].update({'plugin': cookies.get('is_plugin')})
            del self.base_data_format['chat_llms']['is_plugin']
        # 在写入前，记得删除key
        if self.base_data_format['chat_llms'].get('api-key'):
            del self.base_data_format['chat_llms']['api-key']
        with open(self.file_name, 'w', encoding='utf-8') as fp:
            json.dump(self.base_data_format, fp, indent=2, ensure_ascii=False)
        return self

    def delete_the_latest_chat(self):
        try:
            self.base_data_format['chat'] = self.base_data_format['chat'][:-1]
            self.base_data_format['chat_llms']['history'] = self.base_data_format['chat_llms']['history'][:-2]
        except:
            pass
        if self.base_data_format['chat_llms'].get('api-key'):
            del self.base_data_format['chat_llms']['api-key']
        with open(self.file_name, 'w', encoding='utf-8') as fp:
            json.dump(self.base_data_format, fp, indent=2, ensure_ascii=False)
        return self

    def update_for_history(self, cookies: dict, select):
        cookies.update(self.base_data_format['chat_llms'])
        llms = self.base_data_format['chat_llms']
        default_params, LLM_MODEL, = toolbox.get_conf('LLMS_DEFAULT_PARAMETER', 'LLM_MODEL')
        llms_combo = [llms.get(key, default_params[key]) for key in default_params]
        llms_combo[-1] = self.base_data_format['chat_llms'].get('system_prompt', '')
        llm_select = str(self.base_data_format['chat_llms'].get('llm_model', LLM_MODEL)).split('&')[0]
        llms_combo.append(gr.update(value=llm_select))
        chatbot = gr.update(value=[i['on_chat'] for i in self.base_data_format['chat']],
                                    avatar_images=func_box.get_avatar_img(llm_select))
        history = self.base_data_format['chat_llms'].get('history', [])
        try:
            cookies['first_chat'] = select
            cookies['last_chat'] = self.base_data_format['chat'][-1]['on_chat'][0]
            return [chatbot, history, cookies, *llms_combo]
        except Exception:
            return [chatbot, history, cookies, *llms_combo]


def _get_user_object(chatbot, ipaddr):
    chatbot = copy.copy(chatbot)
    cookies = chatbot.get_cookies()
    file_path = os.path.join(init_path.history_path, ipaddr)
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f"{cookies['first_chat']}.json")
    return file_name, cookies


def thread_write_chat_json(chatbot, ipaddr):
    file_name, cookies = _get_user_object(chatbot, ipaddr)
    history_json_handle = HistoryJsonHandle(file_name)
    history_json_handle.analysis_chat_history(chatbot, cookies)


def get_user_basedata(chatbot, ipaddr):
    file_name, cookies = _get_user_object(chatbot, ipaddr)
    history_json_handle = HistoryJsonHandle(file_name)
    base_data = history_json_handle.base_data_format
    return base_data

# class PromptJsonHandle:
# 不能用文件去保存提示词，如果多个用户操作同一份文件，会出错呢
