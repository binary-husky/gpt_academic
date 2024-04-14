# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *


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
    from webui_elem.func_signals.popup_prompt_select import prompt_retrieval
    from common.db.repository.prompt_repository import get_all_class

    user_addr = user_client_mark(request)
    preset_prompt = get_conf('preset_prompt')
    all = preset_prompt['key']
    is_all = preset_prompt['value']
    data = prompt_retrieval(prompt_cls=is_all, ipaddr=user_addr)
    prompt['samples'] = data

    kb_details_tm = base.kb_details_to_dict()
    kb_list = base.kb_dict_to_list(kb_details_tm)
    know_list = gr.update(choices=kb_list + ['新建知识库'], show_label=True)
    know_load = gr.update(choices=list(kb_details_tm.keys()), label='知识库', show_label=True)

    select_list = get_all_class()
    favicon_appname = favicon_ascii()
    outputs = [gr.update(samples=data, visible=True), prompt, favicon_appname,
               gr.update(choices=all + select_list), gr.update(choices=[all[1]] + select_list),
               gr.update(choices=[all[1]] + select_list),
               know_list, know_load]
    return outputs


def refresh_user_data(cookies, proxy_info, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    history_handle = HistoryJsonHandle(new_path)
    history_update_combo = history_handle.update_for_history(cookies, new_name)
    outputs = [gr.update(choices=only_name, value=new_name, visible=True), *history_update_combo,
               new_name, gr.update(value=f"你好，`{user_client_mark(ipaddr)}` {proxy_info}")]
    return outputs


# TODO < -------------------------------- 页面登陆函数注册区 -------------------------------->
def user_login(user, password):
    from common.db.repository import user_info_repository
    user_account = user_info_repository.get_user_info(user)
    if user_account:
        if user == user_account.user_name and password == user_account.pass_word:
            return True
        else:
            return False
    else:
        user_info_repository.add_user_info(user, password)
        return True
