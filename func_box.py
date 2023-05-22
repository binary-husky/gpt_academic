#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import hashlib
import json
import os.path
import subprocess
import threading
import time
import psutil
import re
import tempfile
import shutil
from contextlib import ExitStack
import logging
import yaml
import requests
logger = logging
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm
import pyperclip
import random
import gradio as gr
import toolbox
from prompt_generator import SqliteHandle
"""contextlib 是 Python 标准库中的一个模块，提供了一些工具函数和装饰器，用于支持编写上下文管理器和处理上下文的常见任务，例如资源管理、异常处理等。
官网：https://docs.python.org/3/library/contextlib.html"""

class Shell(object):
    def __init__(self, args, stream=False):
        self.args = args
        self.subp = subprocess.Popen(args, shell=True,
                                     stdin=subprocess.PIPE,  stderr=subprocess.PIPE,
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
                return 3, self.__temp+self.subp.stderr.read()
            finally:
                return 3, self.__temp+self.subp.stderr.read()
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
    def statistics(*args, **kwargs):
        startTiem = time.time()
        obj = func(*args, **kwargs)
        endTiem = time.time()
        ums = startTiem - endTiem
        print('func:{} > Time-consuming: {}'.format(func, ums))
        return obj
    return statistics

def context_with(*parms):
    """
    一个装饰器，根据传递的参数列表，在类方法上下文中嵌套多个 with 语句。
    Args:
        *parms: 参数列表，每个参数都是一个字符串，表示类中的一个属性名。
    Returns:
        一个装饰器函数。
    """
    def decorator(cls_method):
        """
        装饰器函数，用于将一个类方法转换为一个嵌套多个 with 语句的方法。
        Args:
            cls_method: 要装饰的类方法。
        Returns:
            装饰后的类方法。
        """
        def wrapper(cls='', *args, **kwargs):
            """
            装饰后的方法，用于嵌套多个 with 语句，并调用原始的类方法。
            Args:
                cls: 类的实例对象。
                *args: 位置参数。
                **kwargs: 关键字参数。
            Returns:
                原始的类方法返回的结果。
            """
            with_list = [getattr(cls, arg) for arg in parms]
            with ExitStack() as stack:
                for context in with_list:
                    stack.enter_context(context)
                return cls_method(cls, *args, **kwargs)
        return wrapper
    return decorator


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


def html_tag_color(tag, color=None):
    if not color:
        rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        color = f"rgb{rgb}"
    tag = f'<span style="background-color: {color}; font-weight: bold; color: black">&nbsp;{tag}&ensp;</span>'
    return tag

def ipaddr():  # 获取本地ipx
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
    out = Shell(f'tree {dir} -F -I "__*|.*|venv|*.png|*.xlsx" -L {line} {more}').read()[1]
    localfile = os.path.join(os.path.dirname(__file__), '.tree.md')
    with open(localfile, 'w') as f:
        f.write('```\n')
        ll = out.splitlines()
        for i in range(len(ll)):
            if i == 0:
                f.write(ll[i].split('/')[-2]+'\n')
            else:
                f.write(ll[i]+'\n')
        f.write('```\n')


def chat_history(log: list, split=0):
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
    new_dict = {}
    data = JsonHandle(file).load()
    if type(data) is list and len(data) > 0:
        if type(data[0]) is dict:
            for i in data:
                new_dict.update({i['act']: i['prompt']})
    return new_dict

def json_convert_dict():
    new_dict = {}
    for root, dirs, files in os.walk(prompt_path):
        for f in files:
            if f.startswith('prompt') and f.endswith('json'):
                new_dict.update(check_json_format(f))
    return new_dict

def draw_results(txt, prompt: gr.Dataset, percent, switch, ipaddr: gr.Request):
    data = diff_list(txt, percent=percent, switch=switch, hosts=ipaddr.client.host)
    prompt.samples = data
    return prompt.update(samples=data, visible=True), prompt


def diff_list(txt='', percent=0.70, switch: list = None, lst: list = None, sp=15, hosts=''):
    import difflib
    count_dict = {}
    if not lst:
        lst = SqliteHandle('ai_common').get_prompt_value()
        lst.update(SqliteHandle(f"ai_private_{hosts}").get_prompt_value())
    # diff 数据，根据precent系数归类数据
    for i in lst:
        found = False
        for key in count_dict.keys():
            str_tf = difflib.SequenceMatcher(None, i, key).ratio()
            if str_tf >= percent:
                if len(i) > len(key):
                    count_dict[i] = count_dict[key] + 1
                    count_dict.pop(key)
                else:
                    count_dict[key] += 1
                found = True
                break
        if not found: count_dict[i] = 1
    sorted_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    if switch:
        sorted_dict += prompt_retrieval(is_all=switch, hosts=hosts, search=True)
    dateset_list = []
    for key in sorted_dict:
        # 开始匹配关键字
        index = key[0].find(txt)
        if index != -1:
            # sp=split 用于判断在哪里启动、在哪里断开
            if index-sp > 0: start = index-sp
            else: start = 0
            if len(key[0]) > sp * 2:  end = key[0][-sp:]
            else: end = ''
            # 判断有没有传需要匹配的字符串，有则筛选、无则全返
            if txt == '' and len(key[0]) >= sp: show = key[0][0:sp] + " . . . " + end
            elif txt == '' and len(key[0]) < sp: show = key[0][0:sp]
            else: show = str(key[0][start:index + sp]).replace(txt, html_tag_color(txt))
            show += f"  {html_tag_color(' X ' + str(key[1]))}"
            if lst.get(key[0]): be_value = lst[key[0]]
            else: be_value = "这个prompt还没有对话过呢，快去试试吧～"
            value = be_value
            dateset_list.append([show, key[0], value])
    return dateset_list


def search_list(txt, sp=15):
    lst = SqliteHandle('ai_common').get_prompt_value()
    dateset_list = []
    for key in lst:
        index = key.find(txt)
        if index != -1:
            if index-sp > 0: start = index-sp
            else: start = 0
            show = str(key[start:index+sp]).replace(txt, html_tag_color(txt))
            value = lst[key]
            dateset_list.append([show, key, value])
    return dateset_list


def prompt_upload_refresh(file, prompt, ipaddr: gr.Request):
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
    count_dict = {}
    user_path = os.path.join(prompt_path, f'prompt_{hosts}.yaml')
    if '所有人' in is_all:
        for tab in SqliteHandle('ai_common').get_tables():
            if tab.startswith('prompt'):
                data = SqliteHandle(tab).get_prompt_value()
                if data: count_dict.update(data)
    elif '个人' in is_all:
         data = SqliteHandle(f'prompt_{hosts}').get_prompt_value()
         if data: count_dict.update(data)
    retrieval = []
    if count_dict != {}:
        for key in count_dict:
            if not  search:
                retrieval.append([key, count_dict[key]])
            else:
                retrieval.append([count_dict[key], key])
        return retrieval
    else:
        return retrieval


def prompt_reduce(is_all, prompt: gr.Dataset, ipaddr: gr.Request): # is_all, ipaddr: gr.Request
    data = prompt_retrieval(is_all=is_all, hosts=ipaddr.client.host)
    prompt.samples = data
    return prompt.update(samples=data, visible=True), prompt, is_all


def prompt_save(txt, name, checkbox, prompt: gr.Dataset, ipaddr: gr.Request):
    if txt and name:
        yaml_obj = SqliteHandle(f'prompt_{ipaddr.client.host}')
        yaml_obj.inset_prompt({name: txt})
        result = prompt_retrieval(is_all=checkbox+['个人'], hosts=ipaddr.client.host)
        prompt.samples = result
        return "", "", ['个人'], prompt.update(samples=result, visible=True), prompt
    elif not txt or not name:
        result = [[f'{html_tag_color("编辑框 or 名称不能为空!!!!!", color="red")}', '']]
        prompt.samples = [[f'{html_tag_color("编辑框 or 名称不能为空!!!!!", color="red")}', '']]
        return txt, name, [], prompt.update(samples=result, visible=True), prompt

def prompt_input(txt, index, data: gr.Dataset):
    data_str = str(data.samples[index][1])
    if txt:
        txt = data_str+'\n'+txt
    else: 
        txt = data_str
    return txt

def copy_result(history):
    if history != []:
        pyperclip.copy(history[-1])
        return '已将结果复制到剪切板'
    else:
        return "无对话记录，复制错误！！"


def show_prompt_result(index, data: gr.Dataset, chatbot):
    click = data.samples[index]
    chatbot.append((click[1], click[2]))
    return chatbot


def thread_write_chat(chatbot):
    private_key = toolbox.get_conf('private_key')[0]
    chat_title = chatbot[0][0].split()
    i_say = chatbot[-1][0].strip("<p>/p")
    gpt_result = chatbot[-1][1].strip('<div class="markdown-body">/div')
    if private_key in chat_title:
        SqliteHandle(f'ai_private_{chat_title[-2]}').inset_prompt({i_say: gpt_result})
    else:
        SqliteHandle(f'ai_common').inset_prompt({i_say: gpt_result})


base_path = os.path.dirname(__file__)
prompt_path = os.path.join(base_path, 'prompt_users')

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

    def __init__(self, file=os.path.join(prompt_path, 'prompts-PlexPt.json')):
        if not os.path.exists(file):
            Shell(f'touch {file}').read()
        self.file = file

    def load(self):
        with open(file=self.file, mode='r') as f:
            data = json.load(f)
            return data

class FileHandle:

    def __init__(self, file=None):
        self.file = file

    def read(self):
        with open(file=self.file, mode='r') as f:
            print(f.read())


    def read_link(self):
        link = 'https://github.com/PlexPt/awesome-chatgpt-prompts-zh/blob/main/prompts-zh.json'
        name = link.split('/')[3]+link.split('/')[-1]
        new_file = os.path.join(base_path, 'gpt_log', name)
        response = requests.get(url=link, verify=False)
        with open(new_file, "wb") as f:
            f.write(response.content)


if __name__ == '__main__':
   for i in YamlHandle().load():
       print(i)


