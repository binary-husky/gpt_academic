# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *


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
                show = str(key[0][start:index + sp]).replace('<', '').replace(txt, html_tag_color(txt))
            if source:
                show += f"  {html_tag_color(' in ' + str(key[1]))}"
            if not show: show = key[keyword[0]]
            dateset_list.append([show, key[keyword[0]], key[keyword[1]], key[keyword[2]]])
    return dateset_list


def reuse_chat(result, chatbot, history, say):
    """复用对话记录"""
    if result is None or result == []:
        return chatbot, history, gr.update(), gr.update()
    else:
        chatbot += result
        history += [pattern_html(_) for i in result for _ in i]
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
    file_list, only_name, new_path, new_name = get_files_list(
        os.path.join(init_path.private_history_path, user_client_mark(ipaddr)), filter_format=['.json'])
    for i in file_list:
        chat_list = HistoryJsonHandle(i).base_data_format.get('chat')
        file_name = os.path.splitext(os.path.basename(i))[0]
        chat_str = ''.join([u for k in chat_list for u in k['on_chat'] if u is not None])
        lst.update({chat_str: file_name})
    sorted_dict = sorted(lst.items(), key=lambda x: x[1], reverse=True)
    search_result = search_highlight(sorted_dict, txt, True, [0, 1, 0], percent)
    prompt['samples'] = search_result
    return gr.update(samples=search_result, visible=True), prompt
