# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *

from common.api_server.gpts_store import get_gpts, search_gpts, gpts_groups_samples


def gpts_tag_select(select_tab, samples):
    if select_tab == '热门应用':
        samples = gpts_groups_samples(get_gpts()['gpts'])
    elif select_tab == '关键词搜索':
        pass
    else:
        samples = gpts_groups_samples(search_gpts(select_tab)['data']['list'])
    return gr.update(samples=samples), samples


def gpts_select_model(index, samples, cookie):
    gid = samples[index][1]['gid']
    bot_avatar = samples[index][1]['logo']
    chatbot_avatar = get_avatar_img('', bot_avatar)
    cookie.update({"bot_avatar": bot_avatar})
    chat_comm = [gr.update(value=gid), gr.update(avatar_images=chatbot_avatar), cookie]
    toast = spike_toast('切换GPTs模型', samples[index][1]['name'])
    yield chat_comm + [gr.update(visible=True, value=toast)]
    time.sleep(1)
    yield chat_comm + [gr.update(visible=False)]
