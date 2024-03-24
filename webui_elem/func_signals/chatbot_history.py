# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *


# TODO < -------------------------------- 对话函数注册区 ----------------------------------->
def update_models(inputs: list, visions: list, projects: list):
    inputs.extend(visions)
    inputs.extend(projects)
    return inputs


def update_chat(llm_s, cookie):
    chatbot_avatar = get_avatar_img(llm_s, None)
    cookie.update({"bot_avatar": chatbot_avatar[1]})
    return gr.update(avatar_images=chatbot_avatar), cookie


def sm_upload_clear(cookie: dict):
    upload_ho = cookie.get('most_recent_uploaded')
    if upload_ho:
        cookie.pop('most_recent_uploaded')
    return gr.update(value=None), cookie


def generate_random_string(string):
    if len(string) > 20:
        index = random.randint(10, len(string) - 10)
        string = string[index:]
    return string[:25]


def clear_input(inputs, cookies, ipaddr: gr.Request):
    user_addr = user_client_mark(ipaddr)
    user_path = os.path.join(init_path.private_history_path, user_addr)
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    index = 2
    if not cookies.get('first_chat'):
        cookies['first_chat'] = replace_special_chars(generate_random_string(inputs))
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
        user = user_client_mark(ipaddr)
    else:
        user = ipaddr
    chatbot_with_cookie = ChatBotWithCookies(cookies)
    chatbot_with_cookie.write_list(chatbot)
    # user_path = os.path.join(init_path.private_history_path, ipaddr.client.host)
    thread_write_chat_json(chatbot_with_cookie, user)


def clear_chat_cookie(llm_model, ipaddr: gr.Request):
    API_KEY = get_conf('API_KEY')
    cookie = {'api_key': API_KEY, 'llm_model': llm_model}
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    default_params = get_conf('LLM_DEFAULT_PARAMETER')
    llms_combo = [cookie.get(key, default_params[key]) for key in default_params] + [
        gr.update(value=llm_model)]
    output = [[], [], cookie, *llms_combo, '已重置对话记录和对话Cookies',
              gr.update(choices=['新对话'] + only_name, value='新对话'), "新对话"]
    return output


def select_history(select, llm_select, cookies, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    user_history = [f for f in os.listdir(user_path) if f.endswith('.json') and select == os.path.splitext(f)[0]]
    if not user_history:
        default_params, API_KEY = get_conf('LLM_DEFAULT_PARAMETER', 'API_KEY')
        llms_combo = [cookies.get(key, default_params[key]) for key in default_params]
        cookies = {'api_key': API_KEY}
        return [[], [], cookies, *llms_combo, llm_select, select]
    file_path = os.path.join(user_path, user_history[0])
    history_handle = HistoryJsonHandle(file_path)
    history_update_combo = history_handle.update_for_history(cookies, select)
    return [*history_update_combo, select, gr.update(link=html_local_file(file_path))]


def rename_history(old_file, filename: str, ipaddr: gr.Request):
    filename = filename.strip(' \n')
    if filename == "":
        return gr.update()
    if not filename.endswith(".json"):
        filename += ".json"
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    full_path = os.path.join(user_path, filename)
    if not os.path.exists(os.path.join(user_path, f"{old_file}.json")):
        return gr.Error(f'{old_file}历史文件不存在，请刷新页面后尝试')
    repeat_file_index = 2
    while os.path.exists(full_path):  # 命名重复检测
        full_path = os.path.join(user_path, f"{repeat_file_index}_{filename}")
        repeat_file_index += 1
    os.rename(os.path.join(user_path, f"{old_file}.json"), full_path)
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    return gr.update(choices=only_name, value=new_name)


def delete_history(cookies, filename, info, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    full_path = os.path.join(user_path, f"{filename}.json")
    if not os.path.exists(full_path):
        if filename == 'CANCELED':
            return [gr.update() for i in range(16)]
        else:
            raise gr.Error('文件或许已不存在')
    os.remove(full_path)
    file_list, only_name, new_path, new_name = get_files_list(
        os.path.join(init_path.private_history_path, user_client_mark(ipaddr)), filter_format=['.json'])
    history_handle = HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    return [gr.update(choices=only_name, value=new_name), *history_update_combo]


def import_history(file, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    index = 2
    new_file = os.path.basename(file.name)
    while new_file in os.listdir(user_path):
        new_file = f'{index}_{os.path.basename(file.name)}'
        index += 1
    os.rename(file.name, os.path.join(user_path, new_file))
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    return gr.update(choices=only_name, value=new_name)


def refresh_history(cookies, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    history_handle = HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    return [gr.update(choices=only_name, value=new_name), *history_update_combo]


def download_history_json(select, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_path = os.path.join(user_path, f"{select}.json")
    if not os.path.exists(file_path):
        raise gr.Error('当前对话记录空，导出失败')
    link = link_mtime_to_md(file_path)
    return f'下载链接:{link}， 对话记录导出json成功'


def download_history_md(select, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_path = os.path.join(user_path, f"{select}.json")
    if not os.path.exists(file_path):
        raise gr.Error('当前对话记录空，导出失败')
    history_handle = HistoryJsonHandle(file_path)
    history_list = history_handle.base_data_format['chat']
    system = history_handle.base_data_format['chat_llms'].get('system_prompt').replace('\n', '\n> ')
    mark_down = f"> {html_tag_color(tag='System Prompt:', color='#ff6e67')} {system}\n\n"
    for i in history_list:
        chat = i.get('on_chat', ["", ""])
        user, bot = str(chat[0]).replace('\n', '\n> '), str(chat[1]).replace('\n', '\n> ')
        mark_down += f"> {html_tag_color(tag='User:', color='#3e9855')} \n{user}\n\n"
        mark_down += f"> {html_tag_color(tag='Bot:', color='#bc8af4')} \n{bot}\n\n"
    mark_down += f"```json\n# 对话调优参数\n{history_handle.base_data_format['chat_llms']}\n```"
    is_plugin = history_list[-1].get('plugin')
    if is_plugin:
        mark_down += f"```json\n# 插件调优参数\n{is_plugin}\n```"
    file_path = os.path.join(user_path, f'{select}.md')
    with open(file=file_path, mode='w') as f:
        f.write(mark_down)
    link = link_mtime_to_md(file_path)
    return f'下载链接:{link}, 对话记录转换为markdown成功'


def converter_history_masks(chatbot, system_prompt, ipaddr: gr.Request):
    mask_dataset = [['system', system_prompt]]
    for i in chatbot:
        mask_dataset.append(['user', match_chat_information(i[0])])
        mask_dataset.append(['assistant', match_chat_information(i[1])])
    return gr.update(value=mask_dataset)