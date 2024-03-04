# encoding: utf-8
# @Time   : 2023/9/2
# @Author : Spike
# @Descr   :
import json
import os, random
import copy
import re
import tempfile
import time
import uuid
from typing import List

import gradio as gr
import pandas as pd

import yaml
from yarl import URL

from common import toolbox
from common import db_handler
from common import func_box
from common import history_handler
from common.path_handler import init_path
from common.logger_handler import logger

# 处理latex options
latex_delimiters_dict = {
    'default': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ],
    'strict': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ],
    'all': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
        {"left": "\\begin{equation}", "right": "\\end{equation}", "display": True},
        {"left": "\\begin{align}", "right": "\\end{align}", "display": True},
        {"left": "\\begin{alignat}", "right": "\\end{alignat}", "display": True},
        {"left": "\\begin{gather}", "right": "\\end{gather}", "display": True},
        {"left": "\\begin{CD}", "right": "\\end{CD}", "display": True},
    ],
    'disabled': [],
    'else': [
        {"left": "$$", "right": "$$", "display": True},
        {"left": "$", "right": "$", "display": False},
        {"left": "\\(", "right": "\\)", "display": False},
        {"left": "\\[", "right": "\\]", "display": True},
    ]

}


def spinner_chatbot_loading(chatbot):
    loading = [''.join(['.' * random.randint(1, 5)])]
    # 将元组转换为列表并修改元素
    loading_msg = copy.deepcopy(chatbot)
    temp_list = list(loading_msg[-1])

    temp_list[1] = func_box.pattern_html(temp_list[1]) + f'{random.choice(loading)}'
    # 将列表转换回元组并替换原始元组
    loading_msg[-1] = tuple(temp_list)
    return loading_msg


def get_database_cls(t):
    return "_".join(str(t).split('_')[0:-1])


def filter_database_tables():
    tables = db_handler.PromptDb(None).get_tables()
    split_tab = []
    for t in tables:
        if str(t).endswith('_sys'):
            split_tab.append(get_database_cls(t))
    split_tab_new = split_tab
    return split_tab_new


# TODO < -------------------------------- 弹窗数注册区 ----------------------------------->
def on_theme_dropdown_changed(theme, ):
    from webui_elem.theme import load_dynamic_theme
    adjust_theme, adjust_dynamic_theme = load_dynamic_theme(theme)
    if adjust_dynamic_theme:
        try:
            css_part2 = adjust_dynamic_theme._get_theme_css()
        except:
            raise
    else:
        css_part2 = adjust_theme._get_theme_css()
    return css_part2, gr.update()


def switch_latex_output(select):
    if select not in list(latex_delimiters_dict):
        latex = latex_delimiters_dict['else']
    else:
        latex = latex_delimiters_dict[select]
    return gr.update(latex_delimiters=latex)


# TODO < -------------------------------- 对话函数注册区 ----------------------------------->
def update_chat(llm_s):
    return gr.update(avatar_images=func_box.get_avatar_img(llm_s))


def sm_upload_clear(cookie: dict):
    upload_ho = cookie.get('most_recent_uploaded')
    if upload_ho:
        cookie.pop('most_recent_uploaded')
    return gr.update(value=None), cookie


def clear_input(inputs, cookies, ipaddr: gr.Request):
    user_addr = func_box.user_client_mark(ipaddr)
    user_path = os.path.join(init_path.private_history_path, user_addr)
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    index = 2
    if not cookies.get('first_chat'):
        cookies['first_chat'] = func_box.replace_special_chars(str(inputs)[:25])
        select_file = cookies.get('first_chat')
        while select_file in only_name:  # 重名处理
            select_file = f"{index}_{cookies['first_chat']}"
            index += 1
        cookies['first_chat'] = select_file
        only_name = [cookies['first_chat']] + only_name
        # 先写入一个空文件占位
        with open(os.path.join(user_path, cookies['first_chat'] + ".json"), mode='w') as f:
            f.write('{}')
    output = [gr.update(value=''), inputs, gr.update(visible=True), gr.update(), gr.update(visible=False),
              gr.update(choices=only_name, value=cookies['first_chat']), gr.update(value=None)]
    yield output
    logger.info(f"{cookies['llm_model']}_{user_addr}: {inputs[:100]} {'.' * 10}")


def stop_chat_refresh(chatbot, cookies, ipaddr: gr.Request):
    if isinstance(ipaddr, gr.Request):
        user = func_box.user_client_mark(ipaddr)
    else:
        user = ipaddr
    chatbot_with_cookie = toolbox.ChatBotWithCookies(cookies)
    chatbot_with_cookie.write_list(chatbot)
    # user_path = os.path.join(init_path.private_history_path, ipaddr.client.host)
    history_handler.thread_write_chat_json(chatbot_with_cookie, user)


def clear_chat_cookie(llm_model, ipaddr: gr.Request):
    API_KEY = toolbox.get_conf('API_KEY')
    cookie = {'api_key': API_KEY, 'llm_model': llm_model}
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    default_params = toolbox.get_conf('LLM_DEFAULT_PARAMETER')
    llms_combo = [cookie.get(key, default_params[key]) for key in default_params] + [
        gr.update(value=llm_model)]
    output = [[], [], cookie, *llms_combo, '已重置对话记录和对话Cookies',
              gr.update(choices=['新对话'] + only_name, value='新对话'), "新对话"]
    return output


def select_history(select, llm_select, cookies, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    user_history = [f for f in os.listdir(user_path) if f.endswith('.json') and select == os.path.splitext(f)[0]]
    if not user_history:
        default_params, API_KEY = toolbox.get_conf('LLM_DEFAULT_PARAMETER', 'API_KEY')
        llms_combo = [cookies.get(key, default_params[key]) for key in default_params]
        cookies = {'api_key': API_KEY}
        return [[], [], cookies, *llms_combo, llm_select, select]
    file_path = os.path.join(user_path, user_history[0])
    history_handle = history_handler.HistoryJsonHandle(file_path)
    history_update_combo = history_handle.update_for_history(cookies, select)
    return [*history_update_combo, select, gr.update(link=func_box.html_local_file(file_path))]


def rename_history(old_file, filename: str, ipaddr: gr.Request):
    filename = filename.strip(' \n')
    if filename == "":
        return gr.update()
    if not filename.endswith(".json"):
        filename += ".json"
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    full_path = os.path.join(user_path, filename)
    if not os.path.exists(os.path.join(user_path, f"{old_file}.json")):
        return gr.Error(f'{old_file}历史文件不存在，请刷新页面后尝试')
    repeat_file_index = 2
    while os.path.exists(full_path):  # 命名重复检测
        full_path = os.path.join(user_path, f"{repeat_file_index}_{filename}")
        repeat_file_index += 1
    os.rename(os.path.join(user_path, f"{old_file}.json"), full_path)
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    return gr.update(choices=only_name, value=new_name)


def delete_history(cookies, filename, info, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    full_path = os.path.join(user_path, f"{filename}.json")
    if not os.path.exists(full_path):
        if filename == 'CANCELED':
            return [gr.update() for i in range(16)]
        else:
            raise gr.Error('文件或许已不存在')
    os.remove(full_path)
    file_list, only_name, new_path, new_name = func_box.get_files_list(
        os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr)), filter_format=['.json'])
    history_handle = history_handler.HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    return [gr.update(choices=only_name, value=new_name), *history_update_combo]


def import_history(file, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    index = 2
    new_file = os.path.basename(file.name)
    while new_file in os.listdir(user_path):
        new_file = f'{index}_{os.path.basename(file.name)}'
        index += 1
    os.rename(file.name, os.path.join(user_path, new_file))
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    return gr.update(choices=only_name, value=new_name)


def refresh_history(cookies, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    history_handle = history_handler.HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    return [gr.update(choices=only_name, value=new_name), *history_update_combo]


def download_history_json(select, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    file_path = os.path.join(user_path, f"{select}.json")
    if not os.path.exists(file_path):
        raise gr.Error('当前对话记录空，导出失败')
    link = func_box.link_mtime_to_md(file_path)
    return f'下载链接:{link}， 对话记录导出json成功'


def download_history_md(select, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    file_path = os.path.join(user_path, f"{select}.json")
    if not os.path.exists(file_path):
        raise gr.Error('当前对话记录空，导出失败')
    history_handle = history_handler.HistoryJsonHandle(file_path)
    history_list = history_handle.base_data_format['chat']
    system = history_handle.base_data_format['chat_llms'].get('system_prompt').replace('\n', '\n> ')
    mark_down = f"> {func_box.html_tag_color(tag='System Prompt:', color='#ff6e67')} {system}\n\n"
    for i in history_list:
        chat = i.get('on_chat', ["", ""])
        user, bot = str(chat[0]).replace('\n', '\n> '), str(chat[1]).replace('\n', '\n> ')
        mark_down += f"> {func_box.html_tag_color(tag='User:', color='#3e9855')} \n{user}\n\n"
        mark_down += f"> {func_box.html_tag_color(tag='Bot:', color='#bc8af4')} \n{bot}\n\n"
    mark_down += f"```json\n# 对话调优参数\n{history_handle.base_data_format['chat_llms']}\n```"
    is_plugin = history_list[-1].get('plugin')
    if is_plugin:
        mark_down += f"```json\n# 插件调优参数\n{is_plugin}\n```"
    file_path = os.path.join(user_path, f'{select}.md')
    with open(file=file_path, mode='w') as f:
        f.write(mark_down)
    link = func_box.link_mtime_to_md(file_path)
    return f'下载链接:{link}, 对话记录转换为markdown成功'


def converter_history_masks(chatbot, system_prompt, ipaddr: gr.Request):
    mask_dataset = [['system', system_prompt]]
    for i in chatbot:
        mask_dataset.append(['user', func_box.match_chat_information(i[0])])
        mask_dataset.append(['assistant', func_box.match_chat_information(i[1])])
    return gr.update(value=mask_dataset)


# TODO < -------------------------------- 小按钮函数注册区 -------------------------------->
def delete_latest_chat(chatbot, history, cookies: dict, ipaddr: gr.Request):
    select = cookies.get('first_chat', '')
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr), f"{select}.json")
    history_handle = history_handler.HistoryJsonHandle(user_path)
    history_handle.delete_the_latest_chat()
    history_update_combo = history_handle.update_for_history(cookies, select)
    return history_update_combo


def get_user_upload(chatbot, txt, ipaddr: gr.Request):
    """
    获取用户上传过的文件
    """
    private_upload = init_path.private_files_path.replace(init_path.base_path, '.')
    user_history = os.path.join(private_upload, func_box.user_client_mark(ipaddr))
    history = """| 编号 | 目录 | 目录内文件 |\n| --- | --- | --- |\n"""
    count_num = 1
    for root, d, file in os.walk(user_history):
        if txt in str(file) or txt in root:
            file_link = "<br>".join([f'{func_box.html_view_blank(f"{root}/{i}")}' for i in file])
            history += f'| {count_num} | {root} | {file_link} |\n'
            count_num += 1
    chatbot.append([None,  # 'Load Submission History like `{txt}`....',
                    f'{history}\n\n'
                    f'[Local Message] 请自行复制以上目录 or 目录+文件, 填入输入框以供函数区高亮按钮使用\n\n'
                    f'{func_box.html_tag_color("提交前记得请检查头尾空格哦～")}\n\n'])
    return chatbot


# TODO < -------------------------------- 基础功能函数注册区 -------------------------------->
def prompt_retrieval(prompt_cls, hosts, search=False):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        is_all： prompt类型
        hosts： 查询的用户ip
    Returns:
        返回一个列表
    """
    all_, personal = toolbox.get_conf('preset_prompt')['key']
    if not prompt_cls: prompt_cls = all_  # 保底
    count_dict = {}
    hosts_tabs = func_box.prompt_personal_tag(prompt_cls, hosts)
    if all_ == prompt_cls:
        for tab in db_handler.PromptDb(None).get_tables():
            if str(tab).endswith('sys'):
                data, source = db_handler.PromptDb(tab).get_prompt_value(None)
                if data: count_dict.update({get_database_cls(tab): data})
        data, source = db_handler.PromptDb(f'{hosts_tabs}').get_prompt_value(None)
        if data: count_dict.update({personal: data})
    elif personal == prompt_cls:
        data, source = db_handler.PromptDb(f'{hosts_tabs}').get_prompt_value(None)
        if data: count_dict.update({personal: data})
    elif hosts_tabs and prompt_cls:
        data, source = db_handler.PromptDb(f'{hosts_tabs}').get_prompt_value(None)
        if data: count_dict.update({prompt_cls: data})
    retrieval = []
    if count_dict != {}:  # 上面是一段屎山， 不知道自己为什么要这样写，反正能用
        for cls in count_dict:
            for key in count_dict[cls]:
                content = count_dict[cls][key]
                if func_box.check_list_format(content):
                    show_key = f'🎭 ' + key
                else:
                    show_key = key
                retrieval.append([show_key, key, content, cls])
        retrieval.reverse()
        return retrieval
    else:
        return retrieval


def change_check_txt(checkbox, prompt):
    if checkbox:
        return gr.update(label='Prompt - 复用', samples=prompt['samples'], visible=True)
    else:
        return gr.update(label='Prompt - 编辑', samples=prompt['samples'], visible=True)


def prompt_reduce(is_all, prompt: gr.Dataset, ipaddr: gr.Request):  # is_all, ipaddr: gr.Request
    """
    刷新提示词
    Args:
        is_all： prompt类型
        prompt： dataset原始对象
        ipaddr：请求用户信息
    Returns:
        返回注册函数所需的对象
    """
    data = prompt_retrieval(prompt_cls=is_all, hosts=func_box.user_client_mark(ipaddr))
    prompt['samples'] = data
    return gr.update(samples=data, visible=True), prompt, is_all


def prompt_upload_refresh(file, prompt, pro_select, ipaddr: gr.Request):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        file： 上传的文件
        prompt： 原始prompt对象
        ipaddr：ipaddr用户请求信息
    Returns:
        注册函数所需的元祖对象
    """
    user_info = func_box.user_client_mark(ipaddr)
    tab_cls = func_box.prompt_personal_tag(pro_select, func_box.user_client_mark(ipaddr))
    if file.name.endswith('json'):
        upload_data = func_box.check_json_format(file.name)
    elif file.name.endswith('yaml'):
        upload_data = yaml.safe_load(file.file)
    else:
        upload_data = {}
    if upload_data != {}:
        status = db_handler.PromptDb(f'{tab_cls}').inset_prompt(upload_data, user_info)
        ret_data = prompt_retrieval(prompt_cls=tab_cls, hosts=func_box.user_client_mark(ipaddr))
        return gr.update(samples=ret_data, visible=True), prompt, tab_cls
    else:
        prompt['samples'] = [
            [f'{func_box.html_tag_color("数据解析失败，请检查文件是否符合规范", color="red")}', tab_cls]]
        return prompt['samples'], prompt, []


def prompt_delete(pro_name, prompt_dict, select_check, ipaddr: gr.Request):
    user_addr = func_box.user_client_mark(ipaddr)
    if not pro_name:
        raise gr.Error('删除名称不能为空')
    find_prompt = [i for i in prompt_dict['samples'] if i[1] == pro_name]
    if not any(find_prompt):
        raise gr.Error(f'无法找到 {pro_name}')
    tab_cls = func_box.prompt_personal_tag(select_check, user_addr)
    sqlite_handle = db_handler.PromptDb(table=f'{tab_cls}')
    _, source = sqlite_handle.get_prompt_value(find=pro_name)
    if not _:
        raise gr.Error(f'无法找到 {pro_name}，或请不要在所有人分类下删除')
    if str(source) in user_addr or '127.0.0.1' == user_addr or 'spike' == user_addr:
        sqlite_handle.delete_prompt(pro_name)
    else:
        raise gr.Error(f'无法删除不属于你创建的 {pro_name}，如有紧急需求，请联系管理员')
    data = prompt_retrieval(prompt_cls=None, hosts=user_addr)
    prompt_dict['samples'] = data
    toast = gr.update(value=func_box.spike_toast(f'`{pro_name}` 删除成功'), visible=True)
    yield gr.update(samples=data, visible=True), prompt_dict, toast
    time.sleep(1)
    yield gr.update(samples=data, visible=True), prompt_dict, gr.update(visible=False)


def prompt_save(txt, name, prompt: gr.Dataset, pro_select, ipaddr: gr.Request):
    """
    编辑和保存Prompt
    Args:
        txt： Prompt正文
        name： Prompt的名字
        prompt： dataset原始对象
        ipaddr：请求用户信息
    Returns:
        返回注册函数所需的对象
    """
    if not pro_select:
        raise gr.Error('保存分类不能为空 ！')
    user_info = func_box.user_client_mark(ipaddr)
    tab_cls = func_box.prompt_personal_tag(pro_select, func_box.user_client_mark(ipaddr))
    if txt and name:
        sql_obj = db_handler.PromptDb(f'{tab_cls}')
        _, source = sql_obj.get_prompt_value(name)
        status = sql_obj.inset_prompt({name: txt}, user_info)
        if status:
            raise gr.Error('!!!!已有其他人保存同名的配置，请修改名   称后再保存')
        else:
            result = prompt_retrieval(prompt_cls=pro_select, hosts=func_box.user_client_mark(ipaddr))
            prompt['samples'] = result
            toast = gr.update(value=func_box.spike_toast(f'`{name}` 保存成功'), visible=True)
            yield gr.update(samples=result, visible=True), prompt, toast
            time.sleep(1)
            yield gr.update(samples=result, visible=True), prompt, gr.update(visible=False)
    elif not txt or not name:
        raise gr.Error('!!!!编辑区域 or 名称不能为空!!!!')


def prompt_input(edit_check, input_txt: str, llm_select, index, data, ipaddr: gr.Request):
    """
    点击dataset的值使用Prompt
    Args:
        txt： 输入框正文
        index： 点击的Dataset下标
        data： dataset原始对象
    Returns:
        返回注册函数所需的对象
    """
    data_name = str(data['samples'][index][1])
    data_str = str(data['samples'][index][2])
    data_cls = str(data['samples'][index][3])
    mask_ = func_box.check_list_format(data_str)
    chatbot_cookie = clear_chat_cookie(llm_model=llm_select, ipaddr=ipaddr)
    mask_comb = [gr.update() for i in range(3)]
    prompt_comb = [gr.update() for i in range(3)]
    tab_select = gr.update()
    if edit_check:
        if mask_:
            _item, chatbot_cookie[0], chatbot_cookie[1] = mask_to_chatbot(mask_)
            chatbot_cookie[-5] = _item[0][1]  # system
            chatbot_cookie[2].update({'first_chat': data_name})
        else:
            chatbot_cookie = [gr.update() for i in chatbot_cookie]
            if data_str.find('{{{v}}}') != -1:
                input_txt = data_str.replace('{{{v}}}', input_txt)
            else:
                input_txt = input_txt + data_str
    else:
        chatbot_cookie = [gr.update() for i in chatbot_cookie]
        if mask_:
            tab_select = gr.update(selected='masks')
            mask_comb = [data_cls, mask_, data_name]
        else:
            tab_select = gr.update(selected='prompt')
            prompt_comb = [data_cls, data_str, data_name]
    all_comb = [tab_select] + prompt_comb + mask_comb + chatbot_cookie + [input_txt]

    return all_comb


def prompt_search(tab_cls, sear_txt, sp, data_base, ipaddr: gr.Request):
    sorted_dict = prompt_retrieval(prompt_cls=tab_cls, hosts=func_box.user_client_mark(ipaddr))
    search_result = search_highlight(sorted_dict, sear_txt, False, [0, 2, 3], sp)
    data_base['samples'] = search_result
    return gr.update(samples=search_result, visible=True), data_base


def show_prompt_result(index, data: gr.Dataset, cookies, ipaddr: gr.Request):
    """
    查看Prompt的对话记录结果
    Args:
        index： 点击的Dataset下标
        data： dataset原始对象
        chatbot：聊天机器人
    Returns:
        返回注册函数所需的对象
    """
    click = data['samples'][index]
    file_name = click[2]
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    history_handle = history_handler.HistoryJsonHandle(os.path.join(user_path, file_name + ".json"))
    cookie_combo = history_handle.update_for_history(cookies, file_name)
    return gr.update(value=file_name), *cookie_combo


# TODO < -------------------------------- 搜索函数注册区 -------------------------------->
def search_highlight(sorted_dict, txt, source, keyword: list, sp):
    dateset_list = []
    for key in sorted_dict:
        # 开始匹配关键字
        index = str(key[keyword[0]]).lower().find(txt.lower())
        index_ = str(key[keyword[1]]).lower().find(txt.lower())
        if index != -1 or index_ != -1:
            if index == -1: index = index_  # 增加搜索prompt 名称
            # sp=split 用于判断在哪里启动、在哪里断开
            if index - sp > 0:
                start = index - sp
            else:
                start = 0
            if len(key[0]) > sp * 2:
                end = key[0][-sp:]
            else:
                end = ''
            # 判断有没有传需要匹配的字符串，有则筛选、无则全返
            if txt == '' and len(key[0]) >= sp:
                show = key[0][0:sp] + " . . . " + end
                show = show.replace('<', '')
            elif txt == '' and len(key[0]) < sp:
                show = key[0][0:sp]
                show = show.replace('<', '')
            else:
                show = str(key[0][start:index + sp]).replace('<', '').replace(txt, func_box.html_tag_color(txt))
            if source:
                show += f"  {func_box.html_tag_color(' in ' + str(key[1]))}"
            if not show: show = key[keyword[0]]
            dateset_list.append([show, key[keyword[0]], key[keyword[1]], key[keyword[2]]])
    return dateset_list


def reuse_chat(result, chatbot, history, say):
    """复用对话记录"""
    if result is None or result == []:
        return chatbot, history, gr.update(), gr.update()
    else:
        chatbot += result
        history += [func_box.pattern_html(_) for i in result for _ in i]
        return chatbot, history, say


def draw_results(txt, prompt: dict, percent, ipaddr: gr.Request):
    """
    绘制搜索结果
    Args:
        txt (str): 过滤文本
        prompt : 原始的dataset对象
        percent (int): 最大显示文本
        ipaddr : 请求人信息
    Returns:
        注册函数所需的元祖对象
    """
    lst = {}
    file_list, only_name, new_path, new_name = func_box.get_files_list(
        os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr)), filter_format=['.json'])
    for i in file_list:
        chat_list = history_handler.HistoryJsonHandle(i).base_data_format.get('chat')
        file_name = os.path.splitext(os.path.basename(i))[0]
        chat_str = ''.join([u for k in chat_list for u in k['on_chat'] if u is not None])
        lst.update({chat_str: file_name})
    sorted_dict = sorted(lst.items(), key=lambda x: x[1], reverse=True)
    search_result = search_highlight(sorted_dict, txt, True, [0, 1, 0], percent)
    prompt['samples'] = search_result
    return gr.update(samples=search_result, visible=True), prompt


# TODO < -------------------------------- 面具编辑函数注册区 -------------------------------->
def mask_to_chatbot(data):
    population = []
    history = []
    chatbot = []
    for i, item in enumerate(data):
        if i == 0:
            item[0] = 'system'
        elif i % 2 == 0:
            item[0] = 'assistant'
            history.append(item[1])
        else:
            item[0] = 'user'
            history.append(item[1])
        population.append(item)
    for you, bot in zip(history[0::2], history[1::2]):
        if not you: you = None
        if not bot: bot = None
        chatbot.append([you, bot])
    return population, chatbot, history


def mask_setting_role(data):
    """
    Args:
        data: 为每行数据预设一个角色
    Returns:
    """
    setting_set, zip_chat, _ = mask_to_chatbot(data)
    return setting_set, zip_chat


def mask_del_new_row(data):
    if len(data) == 1:
        return [['system', '']]
    if data:
        return data[:-1]
    else:
        return data


def mask_clear_all(data, state, info):
    if state == 'CANCELED':
        return data
    else:
        return [['system', '']]


def reader_analysis_output(file: gr.File, choice, ipaddr: gr.Request):
    from crazy_functions.reader_fns.crazy_box import file_reader_content
    user_mark = func_box.user_client_mark(ipaddr)
    save_path = os.path.join(init_path.private_files_path, user_mark, 'reader')
    content, status = file_reader_content(file_path=file.name, save_path=save_path, plugin_kwargs={})
    if isinstance(content, list):
        content = func_box.to_markdown_tabs(head=content[0], tabs=content[1:], column=True)
    tokens = func_box.num_tokens_from_string([content])

    toast = gr.update(value=func_box.spike_toast(content=f'Submitting a dialog is expected to consume: `{tokens}`',
                                                 title='Completed'), visible=True)
    yield content, gr.Textbox.update(label=f'{tokens} Token', value=content), toast
    time.sleep(2)
    yield content, gr.Textbox.update(label=f'{tokens} Token', value=content), gr.update(visible=False)


# TODO < -------------------------------- 页面刷新函数注册区 -------------------------------->
def mobile_access(request: gr.Request):  # 为适配手机端
    user_agent = request.kwargs['headers']['user-agent'].lower()
    if user_agent.find('android') != -1 or user_agent.find('iphone') != -1:
        return gr.update(visible=False), gr.Dropdown.update(show_label=False)
    else:
        return gr.update(), gr.update()


def refresh_load_data(prompt, request: gr.Request):
    """
    Args:
        prompt: prompt dataset组件
    Returns:
        预期是每次刷新页面，加载最新数据
    """
    user_addr = func_box.user_client_mark(request)
    preset_prompt = toolbox.get_conf('preset_prompt')
    all = preset_prompt['key']
    is_all = preset_prompt['value']
    data = prompt_retrieval(prompt_cls=is_all, hosts=user_addr)
    prompt['samples'] = data

    kb_details_tm = base.kb_details_to_dict()
    kb_list = base.kb_dict_to_list(kb_details_tm)
    know_list = gr.update(choices=kb_list + ['新建知识库'], show_label=True)
    know_load = gr.update(choices=list(kb_details_tm.keys()), label='知识库', show_label=True)

    select_list = filter_database_tables()
    favicon_appname = func_box.favicon_ascii()
    outputs = [gr.update(samples=data, visible=True), prompt, favicon_appname,
               gr.update(choices=all + select_list), gr.update(choices=[all[1]] + select_list),
               gr.update(choices=[all[1]] + select_list),
               know_list, know_load]
    return outputs


def refresh_user_data(cookies, proxy_info, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, func_box.user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = func_box.get_files_list(user_path, filter_format=['.json'])
    history_handle = history_handler.HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    outputs = [gr.update(choices=only_name, value=new_name, visible=True), *history_update_combo,
               new_name, gr.update(value=f"你好，`{func_box.user_client_mark(ipaddr)}` {proxy_info}")]
    return outputs


# TODO < -------------------------------- 页面登陆函数注册区 -------------------------------->
def user_login(user, password):
    sql_handle = db_handler.UserDb()
    user_account = sql_handle.get_user_account(user)
    if user_account.get('user'):
        if user == user_account['user'] and password == user_account['password']:
            return True
        else:
            return False
    else:
        sql_handle.update_user(user, password)
        return True


# TODO < -------------------------------- 知识库函数注册区 -------------------------------------->
from common.knowledge_base.kb_service import base
from common.knowledge_base import kb_doc_api, kb_api
from common.configs import kb_config
from crazy_functions.reader_fns.crazy_box import detach_cloud_links


def kb_select_show(select: gr.Dropdown):
    if select == '新建知识库':
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)


def kb_name_select_then(kb_name):
    kb_dict = base.kb_list_to_dict([kb_name])
    kb_name = list(kb_dict.keys())[0]
    file_details = pd.DataFrame(base.get_kb_file_details(kb_name))
    if 'file_name' in file_details:
        db_file_list = file_details['file_name'].to_list()
        file_name = db_file_list[0]
        last_details = __get_kb_details_df(file_details, file_details["No"] == 1)
        last_fragment = __get_kb_fragment_df(kb_name, file_name)
        kb_file_list = gr.update(choices=db_file_list, value=file_name)
        kb_file_details = gr.DataFrame.update(value=last_details, label=f'{file_name}-文件详情')
        kb_file_fragment = gr.DataFrame.update(value=last_fragment, label=f'{file_name}-文件片段编辑')
    else:
        kb_file_list = gr.update(choices=[], value='')
        kb_file_details = gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_details_template)))
        kb_file_fragment = gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_fragment_template)))

    kb_name_tm = base.kb_details_to_dict()
    kb_info = base.get_kb_details_by_name(kb_name).get('kb_info', '')
    update_output = {
        'kb_name_list': gr.update(choices=base.kb_dict_to_list(kb_name_tm) + ['新建知识库']),
        'kb_info_txt': kb_info,
        'kb_file_list': kb_file_list,
        'kb_file_details': kb_file_details,
        'kb_file_fragment': kb_file_fragment
    }
    return list(update_output.values())


def kb_name_change_btn(name):
    if name:
        return gr.Button.update(variant='primary')
    else:
        return gr.Button.update(variant='secondary')


def kb_upload_btn(upload: gr.Files, cloud: str):
    if upload or URL(cloud).host:
        return gr.Button.update(variant='primary')
    else:
        return gr.Button.update(variant='secondary')


def kb_introduce_change_btn(kb_name, kb_info):
    kb_dict = base.kb_list_to_dict([kb_name])
    kb_name = list(kb_dict.keys())[0]
    resp = kb_doc_api.update_info(kb_name, kb_info)

    if not resp.data != 200:
        raise gr.Error(json.dumps(resp.__dict__, indent=4, ensure_ascii=False))
    else:
        return gr.update()
        # yield gr.update(value=func_box.spike_toast('更新知识库简介成功'), visible=True)
        # time.sleep(1)
        # yield gr.update(visible=False)


def kb_date_add_row(source_data: pd.DataFrame):
    # 添加一行数据
    last_index = source_data.iloc[-1].iloc[1]
    # 检查最后一行的第一个元素是否为整数类型
    if last_index.dtype == 'int64':
        new_index = last_index + 1
    else:
        new_index = 'ErrorType'
    new_row_data = [uuid.uuid4(), new_index, '', '']
    source_data.loc[len(source_data)] = new_row_data

    return gr.update(value=source_data)


def kb_new_confirm(kb_name, kb_type, kb_model, kb_info):
    kb_name_tm = base.kb_details_to_dict()

    if not kb_name or not kb_type or not kb_model:
        keywords = {"知识库名称": kb_name, "向量类型": kb_type, "Embedding 模型": kb_model}
        error_keyword = " - ".join([f"【{i}】" for i in keywords if not keywords[i]])
        raise gr.Error(f'缺失 {error_keyword} 字段,无法创建, ')

    kb_server_list = base.KBServiceFactory.get_service_by_name(kb_name)
    if kb_name in kb_name_tm or kb_server_list is not None:
        raise gr.Error(f'{kb_name} 已存在同名知识库，请重新命名')

    kb = base.KBServiceFactory.get_service(kb_name, kb_type, kb_model)
    kb.kb_info = kb_info
    try:
        kb.create_kb()
    except Exception as e:
        msg = f"创建知识库出错： {e}"
        logger.error(f'{e.__class__.__name__}: {msg}')
        raise gr.Error(msg)
    select_name = base.kb_name_tm_merge(kb_name, kb_type, kb_model)
    new_output = {
        'new_clo': gr.update(visible=False),
        'edit_clo': gr.update(visible=True),
    }

    edit_output = {
        'kb_name_list': gr.update(choices=[select_name] + base.kb_dict_to_list(kb_name_tm) + ['新建知识库'],
                                  value=select_name),
        'kb_info_txt': kb_info,
        'kb_file_list': gr.update(choices=[], value=''),
        'kb_file_details': gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_details_template))),
        'kb_file_fragment': gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_fragment_template)))
    }
    return list(new_output.values()) + list(edit_output.values())


def __get_kb_details_df(file_details: pd.DataFrame, condition: pd.Series):
    select_document = file_details[condition]

    select_kb_details = copy.deepcopy(kb_config.file_details_template)

    select_kb_details.update({
        '文档加载器': select_document['document_loader'].to_list(),
        '分词器': select_document['text_splitter'].to_list(),
        '文档片段数量': select_document['docs_count'].to_list(),
        '向量库': select_document['in_db'].to_list(),
        '源文件': select_document['in_folder'].to_list()
    })
    return pd.DataFrame(data=select_kb_details)


def __get_kb_fragment_df(kb_name, file_name):
    kb_fragment = copy.deepcopy(kb_config.file_fragment_template)

    info_fragment = kb_doc_api.search_docs(query='', knowledge_base_name=kb_name,
                                           top_k=1, score_threshold=1,
                                           file_name=file_name, metadata={})

    for i, v in enumerate(info_fragment):
        kb_fragment['id'].append(info_fragment[i].id)
        kb_fragment['N'].append(i + 1)
        kb_fragment['内容'].append(info_fragment[i].page_content)
        kb_fragment['删除'].append('')
    return pd.DataFrame(data=kb_fragment)


def kb_file_update_confirm(upload_files: List, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader,
                           cloud_link, ipaddr: gr.Request):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    user = func_box.user_client_mark(ipaddr)
    cloud_map, status = detach_cloud_links(cloud_link, {'ipaddr': user}, ['*'])
    if status:
        raise gr.Error(f'文件下载失败，{cloud_map}')

    files = [f.name for f in upload_files] + list(cloud_map.keys())
    response = kb_doc_api.upload_docs(files=files, knowledge_base_name=kb_name, override=True,
                                      to_vector_store=True, chunk_size=kb_max, chunk_overlap=kb_similarity,
                                      loader_enhance=kb_loader, docs={}, not_refresh_vs_cache=False,
                                      text_splitter_name=kb_tokenizer)
    if response.code != 200:
        raise gr.Error(json.dumps(response.__dict__, indent=4, ensure_ascii=False))
    if response.data.get('failed_files'):
        raise gr.Error(json.dumps(response.data, indent=4, ensure_ascii=False))
    return kb_name_select_then(kb_name)


def kb_select_file(kb_name, kb_file: str):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    file_details = pd.DataFrame(base.get_kb_file_details(kb_name))

    last_details = __get_kb_details_df(file_details, file_details["file_name"] == kb_file)
    last_fragment = __get_kb_fragment_df(kb_name, kb_file)

    return gr.update(value=last_details, label=f'{kb_file}-文件详情'), gr.update(value=last_fragment,
                                                                                 label=f'{kb_file}-文档片段编辑')


def kb_base_del(kb_name, del_confirm, _):
    if del_confirm == 'CANCELED':
        return gr.update(visible=False), gr.update(visible=True), gr.update()
    else:
        kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
        response = kb_api.delete_kb(kb_name)
        if response.code != 200:
            raise gr.Error(json.dumps(response.__dict__, indent=4, ensure_ascii=False))
        kb_name_list = base.kb_dict_to_list(base.kb_details_to_dict()) + ['新建知识库']

        return gr.update(visible=True), gr.update(visible=False), gr.update(choices=kb_name_list,
                                                                            value='新建知识库')


def kb_docs_file_source_del(kb_name, kb_file, _):
    if kb_file == 'CANCELED':
        return gr.update(), gr.update(), gr.update(), gr.update()
    kb_name_d = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.delete_docs(knowledge_base_name=kb_name_d, file_names=[kb_file],
                                  delete_content=True, not_refresh_vs_cache=False)
    if resp.code == 200 and not resp.data.get('failed_files'):
        toast = gr.update(
            value=func_box.spike_toast('彻底删除成功 🏴‍☠️'),
            visible=True)
        _, _, file_list, details, fragment = kb_name_select_then(kb_name)
        yield toast, file_list, details, fragment
        time.sleep(1)
        yield gr.update(visible=False), file_list, details, fragment
    else:
        yield gr.Error(f'删除失败, {resp.__dict__}')


def kb_vector_del(kb_name, kb_file):
    kb_name_d = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.delete_docs(knowledge_base_name=kb_name_d, file_names=[kb_file],
                                  delete_content=False, not_refresh_vs_cache=False)
    if resp.code == 200 and not resp.data.get('failed_files'):
        toast = gr.update(
            value=func_box.spike_toast('仅从向量库中删除，后续该文档不会被向量召回，如需重新引用，重载向量数据即可'),
            visible=True)
        yield toast, *kb_select_file(kb_name, kb_file)
        time.sleep(1)
        yield gr.update(visible=False), gr.update(), gr.update()
    else:
        yield gr.Error(f'删除失败, {resp.__dict__}')


def kb_vector_reload(_, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader, kb_file):
    kb_name_k = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.update_docs(
        knowledge_base_name=kb_name_k, file_names=[kb_file], docs={},
        chunk_size=kb_max, chunk_overlap=kb_similarity, override_custom_docs=True,
        loader_enhance=kb_loader, not_refresh_vs_cache=False,
        text_splitter_name=kb_tokenizer
    )
    if resp.code == 200 and not resp.data.get('failed_files'):
        yield gr.update(value=func_box.spike_toast('重载向量数据成功'), visible=True), *kb_select_file(kb_name, kb_file)
        time.sleep(1)
        yield gr.update(visible=False), gr.update(), gr.update()
    else:
        yield gr.Error(f'重载向量数据失败, {resp.__dict__}'), gr.update(), gr.update()


def kb_base_changed_save(_, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader,
                         kb_file, kb_dataFrame: pd.DataFrame):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    info_fragment = kb_doc_api.search_docs(query='', knowledge_base_name=kb_name,
                                           top_k=1, score_threshold=1,
                                           file_name=kb_file, metadata={})

    origin_docs = {}
    for x in info_fragment:
        origin_docs[x.id] = {"page_content": x.page_content,
                             "type": x.type,
                             "metadata": x.metadata}
    changed_docs = []
    for index, row in kb_dataFrame.iterrows():
        origin_doc = origin_docs.get(row['id'])
        if origin_doc:
            if row["删除"] not in ["Y", "y", 1, '1']:
                changed_docs.append({
                    "page_content": row["内容"],
                    "type": origin_doc['type'],
                    "metadata": origin_doc["metadata"],
                })
            else:
                logger.warning(f'删除{row.get("id")}片段：{origin_doc.get("page_content")}')
        else:
            changed_docs.append({
                "page_content": row["内容"],
                "type": 'Document',
                "metadata": {"metadata": kb_file},
            })
    if changed_docs:
        resp = kb_doc_api.update_docs(
            knowledge_base_name=kb_name, file_names=[kb_file], docs={kb_file: changed_docs},
            chunk_size=kb_max, chunk_overlap=kb_similarity, override_custom_docs=False,
            loader_enhance=kb_loader, not_refresh_vs_cache=False,
            text_splitter_name=kb_tokenizer
        )
        if resp.code == 200 and not resp.data.get('failed_files'):
            yield gr.update(value=func_box.spike_toast('更新成功'), visible=True), gr.update()
            time.sleep(1)
            yield gr.update(value=func_box.spike_toast('更新成功'), visible=False), gr.update()
        else:
            yield gr.Error(f'更新失败, {resp.__dict__}')
