#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import ast
import copy
import hashlib
import io
import json
import os.path
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import Levenshtein
import psutil
import re
import tempfile
import shutil
from contextlib import ExitStack
import logging
import yaml
import requests
import tiktoken
logger = logging
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm
import pyperclip
import random
import gradio as gr
import toolbox
from prompt_generator import SqliteHandle
from bs4 import BeautifulSoup

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

def html_download_blank(__href, file_name='temp', dir_name=''):
    if os.path.exists(__href):
        __href = f'/file={__href}'
    if not dir_name:
        dir_name = file_name
    a = f'<a href="{__href}" target="_blank" download="{dir_name}" class="svelte-xrr240">{file_name}</a>'
    return a

def html_local_img(__file):
    a = f'<div align="center"><img src="file={__file}"></div>'
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
    pattern = re.compile(rf"(Authorization|WPS-Sid|Cookie)(:|\s+)\s*(\S+)[\s\S]*?(?=\n|$|\s)", re.IGNORECASE)
    result = pattern.sub(lambda x: x.group(1) + ": XXXXXXXX", txt)
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


def draw_results(txt, prompt: gr.Dataset, percent, switch, ipaddr: gr.Request):
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
    prompt.samples = data
    return prompt.update(samples=data, visible=True), prompt


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
    count_dict = {}
    is_all = toolbox.get_conf('prompt_list')[0]['key'][1]
    if not lst:
        lst = {}
        tabs = SqliteHandle().get_tables()
        if is_all in switch:
            lst.update(SqliteHandle(f"ai_common_{hosts}").get_prompt_value(txt))
        else:
            for tab in tabs:
                if tab.startswith('ai_common'):
                    lst.update(SqliteHandle(f"{tab}").get_prompt_value(txt))
        lst.update(SqliteHandle(f"ai_private_{hosts}").get_prompt_value(txt))
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


def prompt_upload_refresh(file, prompt, ipaddr: gr.Request):
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        file： 上传的文件
        prompt： 原始prompt对象
        ipaddr：ipaddr用户请求信息
    Returns:
        注册函数所需的元祖对象
    """
    hosts = ipaddr.client.host
    if file.name.endswith('json'):
        upload_data = check_json_format(file.name)
    elif file.name.endswith('yaml'):
        upload_data = YamlHandle(file.name).load()
    else:
        upload_data = {}
    if upload_data != {}:
        SqliteHandle(f'prompt_{hosts}').inset_prompt(upload_data)
        ret_data = prompt_retrieval(is_all=['个人'], hosts=hosts)
        return prompt.update(samples=ret_data, visible=True), prompt, ['个人']
    else:
        prompt.samples = [[f'{html_tag_color("数据解析失败，请检查文件是否符合规范", color="red")}', '']]
        return prompt.samples, prompt, []


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
    count_dict = {}
    if '所有人' in is_all:
        for tab in SqliteHandle('ai_common').get_tables():
            if tab.startswith('prompt'):
                data = SqliteHandle(tab).get_prompt_value(None)
                if data: count_dict.update(data)
    elif '个人' in is_all:
        data = SqliteHandle(f'prompt_{hosts}').get_prompt_value(None)
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


def prompt_reduce(is_all, prompt: gr.Dataset, ipaddr: gr.Request):  # is_all, ipaddr: gr.Request
    """
    上传文件，将文件转换为字典，然后存储到数据库，并刷新Prompt区域
    Args:
        is_all： prompt类型
        prompt： dataset原始对象
        ipaddr：请求用户信息
    Returns:
        返回注册函数所需的对象
    """
    data = prompt_retrieval(is_all=is_all, hosts=ipaddr.client.host)
    prompt.samples = data
    return prompt.update(samples=data, visible=True), prompt, is_all


def prompt_save(txt, name, prompt: gr.Dataset, ipaddr: gr.Request):
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
    if txt and name:
        yaml_obj = SqliteHandle(f'prompt_{ipaddr.client.host}')
        yaml_obj.inset_prompt({name: txt})
        result = prompt_retrieval(is_all=['个人'], hosts=ipaddr.client.host)
        prompt.samples = result
        return "", "", ['个人'], prompt.update(samples=result, visible=True), prompt
    elif not txt or not name:
        result = [[f'{html_tag_color("编辑框 or 名称不能为空!!!!!", color="red")}', '']]
        prompt.samples = [[f'{html_tag_color("编辑框 or 名称不能为空!!!!!", color="red")}', '']]
        return txt, name, [], prompt.update(samples=result, visible=True), prompt, gr.Tabs.update(selected='chatbot')


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
    data_str = str(data.samples[index][1])
    data_name = str(data.samples[index][0])
    rp_str = '{{{v}}}'

    def str_v_handle(__str):
        if data_str.find(rp_str) != -1 and __str:
            txt_temp = data_str.replace(rp_str, __str)
        elif __str:
            txt_temp = data_str + '\n' + __str
        else:
            txt_temp = data_str
        return txt_temp
    if tabs_index == 1:
        new_txt = str_v_handle(prompt_str)
        return txt, new_txt, data_name
    else:
        new_txt = str_v_handle(txt)
        return new_txt, prompt_str, name_str


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
    click = data.samples[index]
    if str_is_list(click[2]):
        list_copy = eval(click[2])
        for i in range(0, len(list_copy), 2):
            if i + 1 >= len(list_copy):  # 如果下标越界了，单独处理最后一个元素
                chatbot.append([list_copy[i]])
            else:
                chatbot.append([list_copy[i], list_copy[i + 1]])
    elif click[2] is None and pro_edit == '':
        pro_edit = click[1]
        pro_name = click[3]
    else:
        chatbot.append((click[1], click[2]))
    return chatbot, pro_edit, pro_name



def pattern_html(html):
    bs = BeautifulSoup(html, 'html.parser')
    md_message = bs.find('div', {'class': 'md-message'})
    if md_message:
        return md_message.get_text(separator='')
    else:
        return ""


def thread_write_chat(chatbot, history):
    """
    对话记录写入数据库
    """
    private_key = toolbox.get_conf('private_key')[0]
    chat_title = chatbot[0][1].split()
    i_say = pattern_html(chatbot[-1][0])
    if history:
        gpt_result = history
    else:  # 如果历史对话不存在，那么读取对话框
        gpt_result = [pattern_html(v) for i in chatbot for v in i]
    if private_key in chat_title:
        SqliteHandle(f'ai_private_{chat_title[-2]}').inset_prompt({i_say: gpt_result})
    else:
        SqliteHandle(f'ai_common_{chat_title[-2]}').inset_prompt({i_say: gpt_result})


base_path = os.path.dirname(__file__)
prompt_path = os.path.join(base_path, 'users_data')

def reuse_chat(result, chatbot, history, pro_numb, say):
    """复用对话记录"""
    if result is None or result == []:
        return chatbot, history, gr.update(), gr.update(), '', gr.Column.update()
    else:
        if pro_numb:
            chatbot += result
            history += [pattern_html(_) for i in result for _ in i]
        else:
            chatbot.append(result[-1])
            history += [pattern_html(_) for i in result[-2:] for _ in i]
        print(chatbot[-1][0])
        return chatbot, history, say, gr.Tabs.update(selected='chatbot'), '', gr.Column.update(visible=False)


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


def refresh_load_data(chat, history, prompt, crazy_list):
    """
    Args:
        chat: 聊天组件
        history: 对话记录
        prompt: prompt dataset组件

    Returns:
        预期是每次刷新页面，加载最新
    """
    is_all = toolbox.get_conf('prompt_list')[0]['key'][0]
    data = prompt_retrieval(is_all=[is_all])
    prompt.samples = data
    selected = random.sample(crazy_list, 4)
    return prompt.update(samples=data, visible=True), prompt, chat, history, gr.Dataset.update(samples=[[i] for i in selected]), selected



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


def update_btn(self,
    value:  str = None,
    variant:  str = None,
    visible:  bool = None,
    interactive: bool = None,
    elem_id: str = None,
    label: str = None
):
    if not variant: variant = self.variant
    if not visible: visible = self.visible
    if not value: value = self.value
    if not interactive: interactive = self.interactive
    if not elem_id: elem_id = self.elem_id
    if not elem_id: label = self.label
    return {
        "variant": variant,
        "visible": visible,
        "value": value,
        "interactive": interactive,
        'elem_id': elem_id,
        'label': label,
        "__type__": "update",
    }

def update_txt(self,
        value: str = None,
        lines: int  = None,
        max_lines: int  = None,
        placeholder: str  = None,
        label: str  = None,
        show_label: bool  = None,
        visible: bool  = None,
        interactive: bool  = None,
        type: str  = None,
        elem_id: str = None
    ):

        return {
            "lines": self.lines,
            "max_lines": self.max_lines,
            "placeholder": self.placeholder,
            "label": self.label,
            "show_label": self.show_label,
            "visible": self.visible,
            "value": self.value,
            "type": self.type,
            "interactive": self.interactive,
            "elem_id": elem_id,
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
    print(pattern_html('<div class="raw-message hideM">很抱歉，作为一个文</div><div class="md-message"><p>很抱歉，作为一个文</p></div>'))