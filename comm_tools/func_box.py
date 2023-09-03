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
import psutil
import re
import tempfile
import shutil
import logging
import requests
import yaml
import tiktoken
import copy
import pyperclip
import random
import gradio as gr
import numpy as np

logger = logging
from sklearn.feature_extraction.text import CountVectorizer

from scipy.linalg import norm
from bs4 import BeautifulSoup
from comm_tools import toolbox
from comm_tools.database_processor import SqliteHandle

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
        a = "\n\n" + to_markdown_tabs(head=['下载地址', '插件复用地址'], tabs=[[a], [__file]]) + "\n\n"
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


def non_personal_tag(select, ipaddr):
    all_, personal = toolbox.get_conf('preset_prompt')[0]['key']
    if select and personal != select and all_ != select:
        tab_cls = select + '_sys'
    else:
        tab_cls = ipaddr
    return tab_cls


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
    allow_list = []
    build_list = []
    know_user_build, know_user_allow = toolbox.get_conf('know_user_build', 'know_user_allow')
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            if know_user_allow:
                allow_list.append(dir_name)
        if know_user_build and 'index.faiss' in files:
            build_list.append(os.path.basename(root))
        elif user_info in files and 'index.faiss' in files:
            build_list.append(os.path.basename(root))
    return allow_list, build_list


base_path = os.path.dirname(os.path.dirname(__file__))
prompt_path = os.path.join(base_path, 'users_data')
knowledge_path = os.path.join(prompt_path, 'knowledge')
users_path = os.path.join(base_path, 'private_upload')
logs_path = os.path.join(base_path, 'gpt_log')
os.makedirs(knowledge_path, exist_ok=True)
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


def pattern_html(html):
    bs = BeautifulSoup(str(html), 'html.parser')
    md_message = bs.find('div', {'class': 'md-message'})
    if md_message:
        return md_message.get_text(separator='')
    else:
        return ""


def num_tokens_from_string(listing: list, encoding_name: str = 'cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    count_tokens = 0
    for i in listing:
        encoding = tiktoken.get_encoding(encoding_name)
        count_tokens += len(encoding.encode(i))
    return count_tokens


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
               value: str = '',
               variant: str = '',
               visible: bool = True,
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

def thread_write_chat(chatbot, ipaddr, models):
    """
    对话记录写入数据库
    """
    chatbot = copy.copy(chatbot)
    # i_say = pattern_html(chatbot[-1][0])
    i_say = chatbot[-1][0]
    encrypt, private, _ = toolbox.get_conf('switch_model')[0]['key']
    gpt_result = []
    for i in chatbot:
        for v in i:
            gpt_result.append(v)
    if private in models:
        SqliteHandle(f'ai_private_{ipaddr}').inset_prompt({i_say: gpt_result}, '')
    else:
        SqliteHandle(f'ai_common_{ipaddr}').inset_prompt({i_say: gpt_result}, '')


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
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=10, border=2, )
    qr.add_data(data)
    # 创建二维码图片
    img = qr.make_image()
    # 图片转换为RGBA格式
    img = img.convert('RGBA')
    # 返回二维码图片的大小
    img_w, img_h = img.size
    # 打开logo
    if not icon_path:
        icon_path, = toolbox.get_conf('qc_icon_path')
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
    if not robot_hook: return
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
