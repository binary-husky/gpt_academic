# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals import clear_chat_cookie
from webui_elem.func_signals.__import__ import *

from common.api_server.gpts_store import get_gpts, search_gpts, gpts_groups_samples


def gpts_tag_select(select_tab, samples):
    if select_tab == '🔥 热门应用':
        samples = gpts_groups_samples(get_gpts()['gpts'])
    elif select_tab == '🔍 关键词搜索':
        pass
    else:
        samples = gpts_groups_samples(search_gpts(select_tab)['data']['list'])
    return gr.update(samples=samples), samples


def gpts_select_model(index, samples, cookies, ipaddr: gr.Request):
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    file_list, only_name, new_path, new_name = get_files_list(user_path, filter_format=['.json'])
    gid = samples[index][1]['gid']
    bot_avatar = samples[index][1]['logo']
    gpts_name = samples[index][1]['name']
    chatbot_avatar = get_avatar_img('', bot_avatar)

    chatbot = gr.update(avatar_images=chatbot_avatar, value=[[None, samples[index][1]['info']]])
    cookie_comb = clear_chat_cookie(gid, cookies, ipaddr)[2:-3]
    cookie = cookie_comb[0]
    cookie.update({
        "bot_avatar": bot_avatar,
        "pre_gpts": gpts_name + '_'
    })
    chat_comm = [gr.update(choices=[gpts_name]+only_name, value=gpts_name, visible=True),
                 gr.update(value=gid), chatbot, [], cookie, *cookie_comb[1:]]
    yield chat_comm


def gpts_select_model_toast(gpts_name):
    toast = spike_toast(title='切换GPTs模型', content=gpts_name)
    yield gr.update(visible=True, value=toast)
    time.sleep(1)
    yield gr.update(visible=False)
