# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *


# TODO < -------------------------------- 小按钮函数注册区 -------------------------------->
def delete_latest_chat(chatbot, history, cookies: dict, ipaddr: gr.Request):
    select = cookies.get('first_chat', '')
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr), f"{select}.json")
    history_handle = HistoryJsonHandle(user_path)
    history_handle.delete_the_latest_chat()
    history_update_combo = history_handle.update_for_history(cookies, select)
    return history_update_combo


def get_user_upload(chatbot, txt, ipaddr: gr.Request):
    """
    获取用户上传过的文件
    """
    private_upload = init_path.private_files_path.replace(init_path.base_path, '.')
    user_history = os.path.join(private_upload, user_client_mark(ipaddr))
    history = """| 编号 | 目录 | 目录内文件 |\n| --- | --- | --- |\n"""
    count_num = 1
    for root, d, file in os.walk(user_history):
        if txt in str(file) or txt in root:
            file_link = "<br>".join([f'{html_view_blank(f"{root}/{i}")}' for i in file])
            history += f'| {count_num} | {root} | {file_link} |\n'
            count_num += 1
    chatbot.append([None,  # 'Load Submission History like `{txt}`....',
                    f'{history}\n\n'
                    f'[Local Message] 请自行复制以上目录 or 目录+文件, 填入输入框以供函数区高亮按钮使用\n\n'
                    f'{html_tag_color("提交前记得请检查头尾空格哦～")}\n\n'])
    return chatbot
