#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import ast
import hashlib
import json
import os.path
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import Levenshtein
import psutil
import re
import tempfile
import shutil
import logging
import requests
import yaml
import tiktoken
import pandas as pd
logger = logging
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm
import pyperclip
import random
import gradio as gr
from comm_tools import toolbox
from comm_tools import prompt_generator
from bs4 import BeautifulSoup
import copy
SqliteHandle = prompt_generator.SqliteHandle

"""contextlib 是 Python 标准库中的一个模块，提供了一些工具函数和装饰器，用于支持编写上下文管理器和处理上下文的常见任务，例如资源管理、异常处理等。
官网：https://docs.python.org/3/library/contextlib.html"""


class Shell(object):
    def __init__(self, args, stream=False):
        self.args = args
        self.subp = subprocess.Popen(args, shell=True,
                                     stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE, encoding='utf-8',
                                     errors='ignore', close_fds=True)
        self.__stream = stream
        self.__temp = ''

    def read(self):
        logger.debug(f'The command being executed is: "{self.args}"')
        if self.__stream:
            sysout = self.subp.stdout
            try:
                with sysout as std:
                    for i in std:
                        logger.info(i.rstrip())
                        self.__temp += i
            except KeyboardInterrupt as p:
                return 3, self.__temp + self.subp.stderr.read()
            finally:
                return 3, self.__temp + self.subp.stderr.read()
        else:
            sysout = self.subp.stdout.read()
            syserr = self.subp.stderr.read()
            self.subp.stdin
            if sysout:
                logger.debug(f"{self.args} \n{sysout}")
                return 1, sysout
            elif syserr:
                logger.error(f"{self.args} \n{syserr}")
                return 0, syserr
            else:
                logger.debug(f"{self.args} \n{[sysout], [sysout]}")
                return 2, '\n{}\n{}'.format(sysout, sysout)

    def sync(self):
        logger.debug('The command being executed is: "{}"'.format(self.args))
        for i in self.subp.stdout:
            logger.debug(i.rstrip())
            self.__temp += i
            yield self.__temp
        for i in self.subp.stderr:
            logger.debug(i.rstrip())
            self.__temp += i
            yield self.__temp


def timeStatistics(func):
    """
    统计函数执行时常的装饰器
    """

    def statistics(*args, **kwargs):
        startTiem = time.time()
        obj = func(*args, **kwargs)
        endTiem = time.time()
        ums = startTiem - endTiem
        print('func:{} > Time-consuming: {}'.format(func, ums))
        return obj

    return statistics


def copy_temp_file(file):
    if os.path.exists(file):
        exdir = tempfile.mkdtemp()
        temp_ = shutil.copy(file, os.path.join(exdir, os.path.basename(file)))
        return temp_
    else:
        return None


def md5_str(st):
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 更新 MD5 对象的内容
    md5.update(str(st).encode())
    # 获取加密后的结果
    result = md5.hexdigest()
    return result


def html_tag_color(tag, color=None, font='black'):
    """
    将文本转换为带有高亮提示的html代码
    """
    if not color:
        rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        color = f"rgb{rgb}"
    tag = f'<span style="background-color: {color}; font-weight: bold; color: {font}">&nbsp;{tag}&ensp;</span>'
    return tag


def html_a_blank(__href, name=''):
    if not name:
        name = __href
    a = f'<a href="{__href}" target="_blank" class="svelte-xrr240">{name}</a>'
    return a


def html_local_file(file):
    if os.path.exists(file):
        file = f'/gradio/file={file.replace(base_path, ".")}'
    return file


def html_view_blank(__href: str, file_name='', to_tabs=False):
    __file = __href.replace(base_path, ".")
    __href = html_local_file(__href)
    if not file_name:
        file_name = __href.split('/')[-1]
    a = f'<a href="{__href}" target="_blank" class="svelte-xrr240">{file_name}</a>'
    if to_tabs:
        a = "\n\n"+to_markdown_tabs(head=['下载地址', '插件复用地址'], tabs=[[a], [__file]])+"\n\n"
    return a


def html_iframe_code(html_file):
    html_file = html_local_file(html_file)
    ifr = f'<iframe width="100%" height="500px" frameborder="0" src="{html_file}"></iframe>'
    return ifr


def html_download_blank(__href, dir_name=''):
    if os.path.exists(__href):
        __href = f'/gradio/file={__href}'
    if not dir_name:
        dir_name = str(__href).split('/')[-1]
    a = f'<a href="{__href}" target="_blank" download="{dir_name}" class="svelte-xrr240">{dir_name}</a>'
    return a


def html_local_img(__file, layout='left', max_width=None, max_height=None):
    style = ''
    if max_width is not None:
        style += f"max-width: {max_width};"
    if max_height is not None:
        style += f"max-height: {max_height};"
    a = f'<div align="{layout}"><img src="file={__file}" style="{style}"></div>'
    return a

def ipaddr():
    # 获取本地ipx
    ip = psutil.net_if_addrs()
    for i in ip:
        if ip[i][0][3]:
            return ip[i][0][1]


def encryption_str(txt: str):
    """(关键字)(加密间隔)匹配机制（关键字间隔）"""
    txt = str(txt)
    pattern = re.compile(r"(Authorization|WPS-Sid|Cookie)(:|\s+)\s*([\w-]+?)(,|$|\s)", re.IGNORECASE)
    result = pattern.sub(lambda x: x.group(1) + "XXXX加密封条XXXX" + x.group(4), txt)
    return result


def tree_out(dir=os.path.dirname(__file__), line=2, more=''):
    """
    获取本地文件的树形结构转化为Markdown代码文本
    """
    out = Shell(f'tree {dir} -F -I "__*|.*|venv|*.png|*.xlsx" -L {line} {more}').read()[1]
    localfile = os.path.join(os.path.dirname(__file__), '.tree.md')
    with open(localfile, 'w') as f:
        f.write('```\n')
        ll = out.splitlines()
        for i in range(len(ll)):
            if i == 0:
                f.write(ll[i].split('/')[-2] + '\n')
            else:
                f.write(ll[i] + '\n')
        f.write('```\n')


def chat_history(log: list, split=0):
    """
    auto_gpt 使用的代码，后续会迁移
    """
    if split:
        log = log[split:]
    chat = ''
    history = ''
    for i in log:
        chat += f'{i[0]}\n\n'
        history += f'{i[1]}\n\n'
    return chat, history


def df_similarity(s1, s2):
    """弃用，会警告，这个库不会用"""
    def add_space(s):
        return ' '.join(list(s))

    # 将字中间加入空格
    s1, s2 = add_space(s1), add_space(s2)
    # 转化为TF矩阵
    cv = CountVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))


def check_json_format(file):
    """
    检查上传的Json文件是否符合规范
    """
    new_dict = {}
    data = JsonHandle(file).load()
    if type(data) is list and len(data) > 0:
        if type(data[0]) is dict:
            for i in data:
                new_dict.update({i['act']: i['prompt']})
    return new_dict


def json_convert_dict(file):
    """
    批量将json转换为字典
    """
    new_dict = {}
    for root, dirs, files in os.walk(file):
        for f in files:
            if f.startswith('prompt') and f.endswith('json'):
                new_dict.update(check_json_format(f))
    return new_dict




def draw_results(txt, prompt: dict, percent, switch, ipaddr: gr.Request):
    """
    绘制搜索结果
    Args:
        txt (str): 过滤文本
        prompt : 原始的dataset对象
        percent (int): TF系数，用于计算文本相似度
        switch (list): 过滤个人或所有人的Prompt
        ipaddr : 请求人信息
    Returns:
        注册函数所需的元祖对象
    """
    data = diff_list(txt, percent=percent, switch=switch, hosts=ipaddr.client.host)
    prompt['samples'] = data
    return gr.Dataset.update(samples=data, visible=True), prompt


def diff_list(txt='', percent=0.70, switch: list = None, lst: dict = None, sp=15, hosts=''):
    """
    按照搜索结果统计相似度的文本，两组文本相似度>70%的将统计在一起，取最长的作为key
    Args:
        txt (str): 过滤文本
        percent (int): TF系数，用于计算文本相似度
        switch (list): 过滤个人或所有人的Prompt
        lst：指定一个列表或字典
        sp: 截取展示的文本长度
        hosts : 请求人的ip
    Returns:
        返回一个列表
    """
    is_all = toolbox.get_conf('preset_prompt')[0]['value']
    count_dict = {}
    if not lst:
        lst = {}
        tabs = SqliteHandle().get_tables()
        if is_all in switch:
            data, source = SqliteHandle(f"ai_common_{hosts}").get_prompt_value(txt)
            lst.update(data)
        else:
            for tab in tabs:
                if tab.startswith('ai_common'):
                    data, source = SqliteHandle(f"{tab}").get_prompt_value(txt)
                    lst.update(data)
        data, source = SqliteHandle(f"ai_private_{hosts}").get_prompt_value(txt)
        lst.update(data)
    # diff 数据，根据precent系数归类数据
    str_ = time.time()
    def tf_factor_calcul(i):
        found = False
        dict_copy = count_dict.copy()
        for key in dict_copy.keys():
            str_tf = Levenshtein.jaro_winkler(i, key)
            if str_tf >= percent:
                if len(i) > len(key):
                    count_dict[i] = count_dict.copy()[key] + 1
                    count_dict.pop(key)
                else:
                    count_dict[key] += 1
                found = True
                break
        if not found: count_dict[i] = 1
    with ThreadPoolExecutor(100) as executor:
        executor.map(tf_factor_calcul, lst)
    print('计算耗时', time.time()-str_)
    sorted_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    if switch:
        sorted_dict += prompt_retrieval(is_all=switch, hosts=hosts, search=True)
    dateset_list = []
    for key in sorted_dict:
        # 开始匹配关键字
        index = str(key[0]).lower().find(txt.lower())
        index_ = str(key[1]).lower().find(txt.lower())
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
            show += f"  {html_tag_color(' X ' + str(key[1]))}"
            if lst.get(key[0]):
                be_value = lst[key[0]]
            else:
                be_value = None
            value = be_value
            dateset_list.append([show, key[0], value, key[1]])
    return dateset_list


def prompt_upload_refresh(file, prompt, pro_select, cls_name, ipaddr: gr.Request):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        file： 上传的文件
        prompt： 原始prompt对象
        ipaddr：ipaddr用户请求信息
    Returns:
        注册函数所需的元祖对象
    """
    user_info = ipaddr.client.host
    if pro_select == '新建分类':
        if not cls_name:
            result = [[f'{html_tag_color("若选择新建分类，分类名不能为空", color="red")}', '']]
            prompt['samples'] = [[f'{html_tag_color("选择新建分类，分类名不能为空", color="red")}', '']]
            return gr.update(), gr.Dataset.update(samples=result, visible=True), prompt, pro_select
        tab_cls = non_personal_tag(cls_name, ipaddr.client.host)
    else:
        tab_cls = non_personal_tag(pro_select, ipaddr.client.host)
    if file.name.endswith('json'):
        upload_data = check_json_format(file.name)
    elif file.name.endswith('yaml'):
        upload_data = YamlHandle(file.name).load()
    else:
        upload_data = {}
    if upload_data != {}:
        status = SqliteHandle(f'prompt_{tab_cls}').inset_prompt(upload_data, user_info)
        ret_data = prompt_retrieval(is_all=tab_cls, hosts=tab_cls)
        return gr.Dataset.update(samples=ret_data, visible=True), prompt, tab_cls
    else:
        prompt['samples'] = [[f'{html_tag_color("数据解析失败，请检查文件是否符合规范", color="red")}', tab_cls]]
        return prompt['samples'], prompt, []


def prompt_retrieval(is_all, hosts='', search=False):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        is_all： prompt类型
        hosts： 查询的用户ip
        search：支持搜索，搜索时将key作为key
    Returns:
        返回一个列表
    """
    all_, personal = toolbox.get_conf('preset_prompt')[0]['key']
    count_dict = {}
    if all_ == is_all:
        for tab in SqliteHandle('ai_common').get_tables():
            if tab.startswith('prompt'):
                data, source = SqliteHandle(tab).get_prompt_value(None)
                if data: count_dict.update(data)
    elif personal == is_all:
        data, source = SqliteHandle(f'prompt_{hosts}').get_prompt_value(None)
        if data: count_dict.update(data)
    elif hosts and is_all != '新建分类':
        data, source = SqliteHandle(f'prompt_{hosts}').get_prompt_value(None)
        if data: count_dict.update(data)
    retrieval = []
    if count_dict != {}:
        for key in count_dict:
            if not search:
                retrieval.append([key, count_dict[key]])
            else:
                retrieval.append([count_dict[key], key])
        return retrieval
    else:
        return retrieval


def prompt_reduce(is_all, prompt: gr.Dataset, pro_cls, ipaddr: gr.Request):  # is_all, ipaddr: gr.Request
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        is_all： prompt类型
        prompt： dataset原始对象
        ipaddr：请求用户信息
    Returns:
        返回注册函数所需的对象
    """
    tab_cls = non_personal_tag(pro_cls, ipaddr.client.host)
    data = prompt_retrieval(is_all=is_all, hosts=tab_cls)
    prompt['samples'] = data
    return gr.Dataset.update(samples=data, visible=True), prompt, is_all


def non_personal_tag(select, ipaddr):
    all_, personal = toolbox.get_conf('preset_prompt')[0]['key']
    if select and personal != select and all_ != select:
        tab_cls = select+'_sys'
    else:
        tab_cls = ipaddr
    return tab_cls

def prompt_save(txt, name, prompt: gr.Dataset, pro_select, cls_name, ipaddr: gr.Request):
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
    user_info = ipaddr.client.host
    if pro_select == '新建分类':
        if not cls_name:
            result = [[f'{html_tag_color("选择新建分类，分类名不能为空", color="red")}', '']]
            prompt['samples'] = [[name, txt]]
            return txt, name, gr.update(), gr.Dataset.update(samples=result, visible=True), prompt, gr.Tabs.update()
        tab_cls = non_personal_tag(cls_name, ipaddr.client.host)
    else:
        tab_cls = non_personal_tag(pro_select, ipaddr.client.host)
    if txt and name:
        all_, personal = toolbox.get_conf('preset_prompt')[0]['key']
        if pro_select == all_:
            cls_name = personal
        elif pro_select != '新建分类':
            cls_name = pro_select
        sql_obj = SqliteHandle(f'prompt_{tab_cls}')
        cls_update = gr.Dropdown.update(value=cls_name, choices=filter_database_tables())
        _, source = sql_obj.get_prompt_value(name)
        status = sql_obj.inset_prompt({name: txt}, user_info)
        if status:
            result = [[f'{html_tag_color("!!!!已有其他人保存同名的prompt，请修改prompt名称后再保存", color="red")}', '']]
            prompt['samples'] = [[name, txt]]
            return txt, name, cls_update, gr.Dataset.update(samples=result, visible=True), prompt, gr.Tabs.update(selected='chatbot')
        else:
            result = prompt_retrieval(is_all=cls_name, hosts=tab_cls)
            prompt['samples'] = result
            return "", "", cls_update, gr.Dataset.update(samples=result, visible=True), prompt, gr.Tabs.update(
                selected='chatbot')
    elif not txt or not name:
        result = [[f'{html_tag_color("编辑框 or 名称不能为空!!!!!", color="red")}', '']]
        prompt['samples'] = [[name, txt]]
        return txt, name, cls_name, gr.Dataset.update(samples=result, visible=True), prompt, gr.Tabs.update(selected='chatbot')


def prompt_input(txt: str, prompt_str, name_str,  index, data: gr.Dataset, tabs_index):
    """
    点击dataset的值使用Prompt
    Args:
        txt： 输入框正文
        index： 点击的Dataset下标
        data： dataset原始对象
    Returns:
        返回注册函数所需的对象
    """
    data_str = str(data['samples'][index][1])
    data_name = str(data['samples'][index][0])
    rp_str = '{{{v}}}'
    def str_v_handle(__str):
        if data_str.find(rp_str) != -1 and __str:
            txt_temp = data_str.replace(rp_str, __str)
        else:
            txt_temp = data_str + txt
        return txt_temp
    if tabs_index == 1 or txt == '':
        new_txt = str_v_handle(txt)
        return new_txt, data_str, data_name
    else:
        new_txt = str_v_handle(txt)
        return new_txt, data_str, name_str


def copy_result(history):
    """复制history"""
    if history != []:
        pyperclip.copy(history[-1])
        return '已将结果复制到剪切板'
    else:
        return "无对话记录，复制错误！！"


def str_is_list(s):
    try:
        list_ast = ast.literal_eval(s)
        return isinstance(list_ast, list)
    except (SyntaxError, ValueError):
        return False


def show_prompt_result(index, data: gr.Dataset, chatbot, pro_edit, pro_name):
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
    if str_is_list(click[2]):
        list_copy = eval(click[2])
        for i in range(0, len(list_copy), 2):
            if i + 1 >= len(list_copy):  # 如果下标越界了，单独处理最后一个元素
                chatbot.append([list_copy[i]])
            else:
                chatbot.append([list_copy[i], list_copy[i + 1]])
            yield chatbot, pro_edit, pro_name, gr.Tabs.update(), gr.Accordion.update()
    elif click[2] is None:
        pro_edit = click[1]
        pro_name = click[3]
        chatbot.append([click[3], click[1]])
    yield chatbot, pro_edit, pro_name, gr.Tabs.update(selected='func_tab'), gr.Accordion.update(open=True)



def pattern_html(html):
    bs = BeautifulSoup(str(html), 'html.parser')
    md_message = bs.find('div', {'class': 'md-message'})
    if md_message:
        return md_message.get_text(separator='')
    else:
        return ""

import datetime
def check_expected_time():
    current_time = datetime.datetime.now().time()
    morning_start = datetime.time(9, 0)
    morning_end = datetime.time(12, 0)
    afternoon_start = datetime.time(14, 0)
    afternoon_end = datetime.time(18, 0)
    if (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end):
        return False
    else:
        return True

def get_directory_list(folder_path, user_info='temp'):
    directory_list = []
    users_list = []
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            directory_list.append(dir_name)
        if user_info in files and 'index.faiss' in files:
            users_list.append(os.path.basename(root))
    return directory_list, users_list


def thread_write_chat(chatbot, ipaddr, models):
    """
    对话记录写入数据库
    """
    chatbot = copy.copy(chatbot)
    # i_say = pattern_html(chatbot[-1][0])
    i_say = chatbot[-1][0]
    encrypt, private = toolbox.get_conf('switch_model')[0]['key']
    gpt_result = []
    for i in chatbot:
        for v in i:
            gpt_result.append(v)
    if private in models:
        SqliteHandle(f'ai_private_{ipaddr}').inset_prompt({i_say: gpt_result}, '')
    else:
        SqliteHandle(f'ai_common_{ipaddr}').inset_prompt({i_say: gpt_result}, '')


base_path = os.path.dirname(os.path.dirname(__file__))
prompt_path = os.path.join(base_path, 'users_data')
knowledge_path = os.path.join(prompt_path, 'knowledge')
knowledge_path_sys_path = os.path.join(prompt_path, 'knowledge', 'system')
users_path = os.path.join(base_path, 'private_upload')
logs_path = os.path.join(base_path, 'gpt_log')

import os
import csv
import datetime


def split_csv_by_quarter(file_path, date_format='%Y-%m-%d %H:%M:%S'):
    # 获取文件名和扩展名
    file_name, file_ext = os.path.splitext(file_path)
    result_files = {}

    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)  # 读取表头
        first_row = next(reader)  # 读取第一行数据
        first_cell = first_row[0]  # 第一列的值
        try:
            datetime.datetime.strptime(first_cell, date_format)  # 判断第一列是否为时间格式
            is_datetime = True
        except ValueError:
            is_datetime = False

        if is_datetime:
            # 拆分文件并写入新的CSV文件
            quarter_start = datetime.datetime.strptime(first_cell, date_format).date()
            for row in reader:
                cell_value = row[0]
                if not cell_value:
                    continue
                cell_date = datetime.datetime.strptime(cell_value, date_format).date()
                quarter_data = [row]
                quarter_start = quarter_start.replace(year=cell_date.year).replace(month=cell_date.month)
                quarter = quarter_start.month // 3 + 1
                if quarter > 4: quarter = 4
                quarter_file_path = f"{file_name}_{quarter_start.year}_Q{quarter}{file_ext}"
                writer = csv.writer(open(quarter_file_path, 'a', newline=''))
                writer.writerows(quarter_data)  # 写入季度数据
                result_files[quarter_file_path] = ''

            # 在写入完所有数据后再写入表头
            for quarter_file_path in result_files:
                with open(quarter_file_path, 'r+') as quarter_file:
                    content = quarter_file.read()
                    quarter_file.seek(0, 0)  # 将文件指针移回文件开头
                    quarter_file.write(','.join(headers) + '\n')  # 写入表头
                    quarter_file.write(content)  # 写入之前的内容
        else:
            result_files[file_path] = ''
    result_files = [i for i in result_files]
    return result_files


def handling_defect_files(file_manifest: list):
    bugs_list = [mani for mani in file_manifest if '缺陷' in mani]  # 筛选出带有缺陷字样的文件list
    file_manifest = [x for x in file_manifest if x not in bugs_list]  # 过滤掉筛选出来的文件
    temp_file = []
    for i in bugs_list:
        temp_file.extend(split_csv_by_quarter(i))
    file_manifest.extend(temp_file)
    return file_manifest


def new_button_display(select):
    if '新建分类' == select:
        return gr.Textbox.update(visible=True)
    else:
        return gr.Textbox.update(visible=False)


def reuse_chat(result, chatbot, history, say):
    """复用对话记录"""
    if result is None or result == []:
        return chatbot, history, gr.update(), gr.update(), gr.Column.update()
    else:
        chatbot += result
        history += [pattern_html(_) for i in result for _ in i]
        return chatbot, history, say, gr.Tabs.update(selected='chatbot'), gr.Column.update(visible=False)


def num_tokens_from_string(listing: list, encoding_name: str = 'cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    count_tokens = 0
    for i in listing:
        encoding = tiktoken.get_encoding(encoding_name)
        count_tokens += len(encoding.encode(i))
    return count_tokens


def spinner_chatbot_loading(chatbot):
    loading = [''.join(['.' * random.randint(1, 5)])]
    # 将元组转换为列表并修改元素
    loading_msg = copy.deepcopy(chatbot)
    temp_list = list(loading_msg[-1])

    temp_list[1] = pattern_html(temp_list[1]) + f'{random.choice(loading)}'
    # 将列表转换回元组并替换原始元组
    loading_msg[-1] = tuple(temp_list)
    return loading_msg


def filter_database_tables():
    tables = SqliteHandle().get_tables()
    preset = toolbox.get_conf('preset_prompt')[0]['key']
    split_tab = []
    for t in tables:
        if str(t).startswith('prompt_') and str(t).endswith('_sys'):
            split_tab.append("_".join(str(t).split('_')[1:-1]))
    split_tab_new = ['新建分类'] + preset + split_tab
    return split_tab_new


def refresh_load_data(prompt, crazy_list, request: gr.Request):
    """
    Args:
        prompt: prompt dataset组件
    Returns:
        预期是每次刷新页面，加载最新数据
    """
    is_all = toolbox.get_conf('preset_prompt')[0]['value']
    data = prompt_retrieval(is_all=is_all)
    prompt['samples'] = data
    selected = random.sample(crazy_list, 4)
    know_list = ['新建分类'] + os.listdir(knowledge_path)
    load_list, user_list = get_directory_list(os.path.join(knowledge_path, '公共知识库'), request.client.host)
    know_cls = gr.Dropdown.update(choices=know_list, value='公共知识库')
    know_load = gr.Dropdown.update(choices=load_list, label='公共知识库')
    know_user = gr.Dropdown.update(choices=user_list)
    select_list = filter_database_tables()
    outputs = [gr.Dataset.update(samples=data, visible=True), prompt, gr.Dropdown.update(choices=select_list),
               gr.Dataset.update(samples=[[i] for i in selected]), selected,
               know_cls, know_user, know_load]
    return outputs


def txt_converter_json(input_string):
    try:
        if input_string.startswith("{") and input_string.endswith("}"):
            # 尝试将字符串形式的字典转换为字典对象
            dict_object = ast.literal_eval(input_string)
        else:
            # 尝试将字符串解析为JSON对象
            dict_object = json.loads(input_string)
        formatted_json_string = json.dumps(dict_object, indent=4, ensure_ascii=False)
        return formatted_json_string
    except (ValueError, SyntaxError):
        return input_string


def clean_br_string(s):
    s = re.sub('<\s*br\s*/?>', '\n', s)  # 使用正则表达式同时匹配<br>、<br/>、<br />、< br>和< br/>
    return s

def update_btn(self: gr.Button = None,
    value:  str = '',
    variant:  str = '',
    visible:  bool = True,
    interactive: bool = True,
    elem_id: str = '',
    label: str = None
):
    if self:
        if not variant: variant = self.variant
        if visible is None: visible = self.visible
        if not value: value = self.value
        if interactive is None: interactive = self.interactive
        if not elem_id: elem_id = self.elem_id
        if label is None: label = self.label
    return {
        "variant": variant,
        "visible": visible,
        "value": value,
        "interactive": interactive,
        'elem_id': elem_id,
        'label': label,
        "__type__": "update",
    }

def get_html(filename):
    path = os.path.join(base_path, "docs/assets", "html", filename)
    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            return file.read()
    return ""


def git_log_list():
    ll = Shell("git log --pretty=format:'%s | %h' -n 10").read()[1].splitlines()

    return [i.split('|') for i in ll if 'branch' not in i][:5]


def to_markdown_tabs(head: list, tabs: list, alignment=':---:', column=False):
    """
    Args:
        head: 表头：[]
        tabs: 表值：[[列1], [列2], [列3], [列4]]
        alignment: :--- 左对齐， :---: 居中对齐， ---: 右对齐
        column: True to keep data in columns, False to keep data in rows (default).
    Returns:
        A string representation of the markdown table.
    """
    if column:
        transposed_tabs = list(map(list, zip(*tabs)))
    else:
        transposed_tabs = tabs
    # Find the maximum length among the columns
    max_len = max(len(column) for column in transposed_tabs)

    tab_format = "| %s "
    tabs_list = "".join([tab_format % i for i in head]) + '|\n'
    tabs_list += "".join([tab_format % alignment for i in head]) + '|\n'

    for i in range(max_len):
        row_data = [tab[i] if i < len(tab) else '' for tab in transposed_tabs]
        tabs_list += "".join([tab_format % i for i in row_data]) + '|\n'
    return tabs_list

from PIL import Image, ImageOps
import qrcode
def qr_code_generation(data, icon_path=None, file_name='qc_icon.png'):
    # 创建qrcode对象
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=10, border=2,)
    qr.add_data(data)
    # 创建二维码图片
    img = qr.make_image()
    # 图片转换为RGBA格式
    img = img.convert('RGBA')
    # 返回二维码图片的大小
    img_w, img_h = img.size
    # 打开logo
    if not icon_path:
        icon_path = os.path.join(base_path, 'docs/wps_logo.png')
    logo = Image.open(icon_path)
    # logo大小为二维码的四分之一
    logo_w = img_w // 4
    logo_h = img_w // 4
    # 修改logo图片大小
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)  # or Image.Resampling.LANCZOS
    # 填充logo背景色透明
    ImageOps.pad(logo, (logo_w, logo_h), method=Image.LANCZOS)
    # 把logo放置在二维码中间
    w = (img_w - logo_w) // 2
    h = (img_h - logo_h) // 2
    img.paste(logo, (w, h))
    qr_path = os.path.join(logs_path, file_name)
    img.save(qr_path)
    return qr_path


def created_atime():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def 通知机器人(error):
    robot_hook, = toolbox.get_conf('robot_hook')
    title = '## 警告警告\n'
    results = "> <font color='red'>{}</font>".format('哈喽小主，chatbot 遇到意料之外的状况了呢，详情请查看以下报错信息')
    notice = '<at user_id="-1">所有人</at>'
    # 发送内容
    markdown = {
        "msgtype": "markdown",
        "markdown": {
            "text": f"{title}\n\n{results}\n\n{notice}\n\n{error}"
        }
    }
    # 发送通知
    quet = requests.post(url=robot_hook, json=markdown, verify=False)


def get_files_and_dirs(path, filter_allow):
    result = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            result.append('./{}'.format(item))
            result.append(item)
        elif os.path.isdir(item_path):
            if item not in filter_allow:
                result.append(item)
    return result


def replace_expected_text(prompt: str, content: str, expect='{{{v}}}'):
    """ 查找prompt中expect相关占位符，并将content替换到prompt中
    Args:
        prompt: 提示词
        content:  正文
        expect: 预期替换的文本
    Returns:
    """
    if content:
        if prompt.find(expect) != -1:
            content = prompt.replace(expect, content)
        else:
            content = content + prompt
    return content


class YamlHandle:

    def __init__(self, file=os.path.join(prompt_path, 'ai_common.yaml')):
        if not os.path.exists(file):
            Shell(f'touch {file}').read()
        self.file = file
        self._load = self.load()

    def load(self) -> dict:
        with open(file=self.file, mode='r') as f:
            data = yaml.safe_load(f)
            return data

    def update(self, key, value):
        date = self._load
        if not date:
            date = {}
        date[key] = value
        with open(file=self.file, mode='w') as f:
            yaml.dump(date, f, allow_unicode=True)
        return date

    def dump_dict(self, new_dict):
        date = self._load
        if not date:
            date = {}
        date.update(new_dict)
        with open(file=self.file, mode='w') as f:
            yaml.dump(date, f, allow_unicode=True)
        return date


class JsonHandle:

    def __init__(self, file):
        self.file = file

    def load(self) -> object:
        with open(self.file, 'r') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    # print(split_csv_by_quarter('/Users/kilig/Desktop/testbug/国际客户端项目-缺陷池-Win端-全部缺陷.csv'))
    print(html_view_blank('/Users/kilig/Job/Python-project/kso_gpt/config.py', to_tabs=True))
