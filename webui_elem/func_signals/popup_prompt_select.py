# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
import json

from webui_elem.func_signals.__import__ import *

# TODO < -------------------------------- 基础功能函数注册区 -------------------------------->
def prompt_retrieval(prompt_cls, ipaddr, search=False):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        is_all： prompt类型
        ipaddr： 查询的用户ip
    Returns:
        返回一个列表
    """
    all_, personal = get_conf('preset_prompt')['key']
    if not prompt_cls:
        prompt_cls = all_  # 保底
    count_dict = {}
    if all_ == prompt_cls:
        count_dict.update(prompt_repository.get_all_prompt_dict())
    elif personal == prompt_cls:
        count_dict.update(prompt_repository.get_user_prompt_dict(ipaddr))
    else:
        count_dict.update(prompt_repository.get_class_prompt_dict(prompt_cls))
    retrieval = []
    if count_dict != {}:  # 判断是Prompt还是
        for cls in count_dict:
            for key in count_dict[cls]:
                content = count_dict[cls][key]
                if check_list_format(content):
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
    data = prompt_retrieval(prompt_cls=is_all, ipaddr=user_client_mark(ipaddr))
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
    user_info = user_client_mark(ipaddr)
    if file.name.endswith('json'):
        with open(file.name) as f:
            upload_data = json.loads(f.read())
    elif file.name.endswith('yaml'):
        upload_data = yaml.safe_load(file.file)
    else:
        upload_data = []
    if upload_data:
        prompt_repository.batch_import_prompt_list(pro_select, pro_select, user_info)
        ret_data = prompt_retrieval(prompt_cls=pro_select, ipaddr=user_info)
        return gr.update(samples=ret_data, visible=True), prompt, pro_select
    else:
        prompt['samples'] = [
            [f'{html_tag_color("数据解析失败，请检查文件是否符合规范", color="red")}', pro_select]]
        return prompt['samples'], prompt, []


def prompt_delete(pro_name, prompt_dict, pro_class, ipaddr: gr.Request):
    user_addr = user_client_mark(ipaddr)
    if not pro_name:
        raise gr.Error('删除名称不能为空')
    find_prompt = [i for i in prompt_dict['samples'] if i[1] == pro_name]
    if not any(find_prompt):
        raise gr.Error(f'无法找到 {pro_name}')
    prompt = prompt_repository.query_prompt(pro_name, pro_class, user_addr)
    if not prompt:
        raise gr.Error(f'无法找到 {pro_name}，或请不要在所有人分类下删除')
    else:
        status, msg = prompt_repository.deleted_prompt(pro_name, pro_class, user_addr)
        if not status:
            raise gr.Error(msg)
    data = prompt_retrieval(prompt_cls=None, ipaddr=user_addr)
    prompt_dict['samples'] = data
    toast = gr.update(value=spike_toast(f'`{pro_name}` 删除成功'), visible=True)
    yield gr.update(samples=data, visible=True), prompt_dict, toast
    time.sleep(1)
    yield gr.update(samples=data, visible=True), prompt_dict, gr.update(visible=False)


def prompt_save(txt, name, prompt: gr.Dataset, prompt_class, ipaddr: gr.Request):
    """
    编辑和保存Prompt
    Args:
        txt： Prompt正文
        name： Prompt的名字
        prompt： dataset原始对象
        prompt_class: 提示词分类
        ipaddr：请求用户信息
    Returns:
        返回注册函数所需的对象
    """
    if not prompt_class:
        raise gr.Error('保存分类不能为空 ！')
    user_info = user_client_mark(ipaddr)
    if txt and name:
        status, msg = prompt_repository.add_prompt(prompt_class, name, txt, user_info)
        if not status:
            raise gr.Error(msg)
        else:
            result = prompt_retrieval(prompt_cls=prompt_class, ipaddr=user_info)
            prompt['samples'] = result
            toast = gr.update(value=spike_toast(msg), visible=True)
            yield gr.update(samples=result, visible=True), prompt, toast
            time.sleep(1)
            yield gr.update(samples=result, visible=True), prompt, gr.update(visible=False)
    elif not txt or not name:
        raise gr.Error('!!!!编辑区域 or 名称不能为空!!!!')


def prompt_input(edit_check, input_txt: str, cookies, llm_select, index, data, ipaddr: gr.Request):
    """
    点击dataset的值使用Prompt
    Args:
        txt： 输入框正文
        index： 点击的Dataset下标
        data： dataset原始对象
    Returns:
        返回注册函数所需的对象
    """
    from webui_elem.func_signals.chatbot_history import clear_chat_cookie
    from webui_elem.func_signals.popup_mask_reader import mask_to_chatbot
    data_name = str(data['samples'][index][1])
    data_str = str(data['samples'][index][2])
    data_cls = str(data['samples'][index][3])
    mask_ = check_list_format(data_str)
    chatbot_cookie = clear_chat_cookie(llm_model=llm_select, cookie=cookies, ipaddr=ipaddr)
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
    from webui_elem.func_signals.popup_history_seach import search_highlight
    sorted_dict = prompt_retrieval(prompt_cls=tab_cls, ipaddr=user_client_mark(ipaddr))
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
    user_path = os.path.join(init_path.private_history_path, user_client_mark(ipaddr))
    history_handle = HistoryJsonHandle(os.path.join(user_path, file_name + ".json"))
    cookie_combo = history_handle.update_for_history(cookies, file_name)
    return gr.update(value=file_name), * cookie_combo

