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
import requests
import tiktoken
import copy
import random
import gradio as gr
import csv
import datetime
import qrcode

from PIL import Image, ImageOps
from bs4 import BeautifulSoup
from common import toolbox
from common.logger_handler import logger
from common.path_handler import init_path
from webui_elem.overwrites import escape_markdown


class Shell:
    def __init__(self, args):
        self.__args = args
        self.subp = subprocess.Popen(self.__args, shell=True,
                                     stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE, encoding='utf-8',
                                     errors='ignore', close_fds=True)
        self._thread = None
        self.__result = ''
        self.__error_msg = ''

    def start(self):
        sys_out = self.subp.stdout
        logger.debug(f'Start running commands: {self.__args}')
        try:
            for i in sys_out:
                logger.info(i.rstrip())
                self.__result += i
        except KeyboardInterrupt as p:
            return self.__result
        except Exception as p:
            return self.__result
        finally:
            self.__error_msg = self.subp.stderr.read()
            return self.__result


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


def html_folded_code(txt):
    # 使用markdown的代码块折叠多余的信息，最多显示三行，详情可以全局搜索language-folded
    mark_txt = f'```folded\n{txt}\n```'
    return mark_txt


def html_a_blank(__href, name=''):
    if not name:
        name = __href
    a = f'<a href="{__href}" target="_blank" class="svelte-xrr240">{name}</a>'
    a = f"[{__href}]({name})"
    return a


# 绝对路径转相对路径
def local_relative_path(file):
    return file.replace(init_path.base_path, ".")


def html_local_file(file):
    if os.path.exists(str(file)):
        file = f'file={local_relative_path(file)}'
    return file


def link_mtime_to_md(file, time_stamp=True):
    link_local = html_local_file(file)
    link_name = os.path.basename(file)
    a = f"[{link_name}]({link_local})"
    if time_stamp:
        a = a[:-1] + f"?{os.path.getmtime(file)})"
    return a


def html_view_blank(__href: str, to_tabs=False):
    __file = __href.replace(init_path.base_path, ".")
    __href = html_local_file(__href)
    a = link_mtime_to_md(__file)
    if to_tabs:
        a = f' {__file}'
        a = "\n\n" + to_markdown_tabs(head=['下载地址', '插件复用地址'], tabs=[[__file], [a]]) + "\n\n"
    return a


def html_iframe_code(html_file):
    html_file = html_local_file(html_file)
    ifr = f'<iframe width="100%" height="500px" frameborder="0" src="{html_file}"></iframe>'
    return ifr


def html_download_blank(__href, dir_name=''):
    if os.path.exists(__href):
        __href = f'/spike/file={__href}'
    if not dir_name:
        dir_name = str(__href).split('/')[-1]
    a = f'<a href="{__href}" target="_blank" download="{dir_name}" class="svelte-xrr240">{dir_name}</a>'
    return a


def html_local_img(__file, layout='left', max_width=None, max_height=None, md=True):
    style = ''
    if max_width is not None:
        style += f"max-width: {max_width};"
    if max_height is not None:
        style += f"max-height: {max_height};"
    file_name = os.path.basename(__file)
    __file = html_local_file(__file)
    a = f'<div align="{layout}"><img src="{__file}" style="{style}"></div>'
    if md:
        a = f'![{file_name}]({__file})'
    return a


# 提取markdown链接
def extract_link_pf(text, valid_types: list):
    file_mapping_links = {}
    pattern_link = r"(!?\[[^\]]+\]\([^\)]+\))"
    matches_path = re.findall(pattern_link, text)
    for md_link in matches_path:
        pattern_file = r"\(file=(.*?)\)"
        matches_path = re.findall(pattern_file, md_link)
        pattern_local = r"\((/[^)]+)\)"
        matches_local = re.findall(pattern_local, md_link)
        if matches_path:
            if matches_path[0].split('.')[-1] in valid_types:
                file_mapping_links.update({local_relative_path(matches_path[0]): md_link})
        elif matches_local:
            if os.path.exists(matches_local[0]):
                if matches_local[0].split('.')[-1] in valid_types:
                    file_mapping_links.update({local_relative_path(matches_local[0]): md_link})
    return file_mapping_links


# 批量转换图片为base64
def batch_encode_image(files: dict):
    encode_map = {}
    for fp in files:
        file_type = os.path.basename(fp).split('.')[-1]
        encode_map[fp] = {
            "data": toolbox.encode_image(fp),
            "type": file_type.replace('jpg', 'jpeg')  # google 识别不了jpg图片格式，狗日的
        }
    return encode_map


def file_manifest_filter_type(file_list, filter_: list = None, md_type=False):
    new_list = []
    if not filter_:
        filter_ = valid_img_extensions
    for file in file_list:
        if str(os.path.basename(file)).split('.')[-1] in filter_:
            new_list.append(html_local_img(file, md=md_type))
        elif os.path.exists(file):
            new_list.append(link_mtime_to_md(file, time_stamp=False))
        else:
            new_list.append(file)
    return new_list


def ipaddr():
    # 获取本地ipx
    ip = psutil.net_if_addrs()
    for i in ip:
        if i == '以太网':
            return ip[i][1].address
        if ip[i][0][3]:
            return ip[i][0][1]


def user_client_mark(request: gr.Request):
    if request.username:
        return request.username
    else:
        return request.client.host


def encryption_str(txt: str) -> object:
    """(关键字)(加密间隔)匹配机制（关键字间隔）"""
    txt = str(txt)
    pattern = re.compile(r"(Authorization|WPS-Sid|Cookie)(:|\s+)\s*([\w-]+?)(,|$|\s)", re.IGNORECASE)
    result = pattern.sub(lambda x: x.group(1) + "XXXX加密封条XXXX" + x.group(4), txt)
    return result


def tree_out(dir=os.path.dirname(__file__), line=2, filter='', more=''):
    """
    获取本地文件的树形结构转化为Markdown代码文本
    Args:
        dir: 指定目录，不指定则当前目录
        line: 深入检索文档深度
        more: 添加更多命令
        filter: 过滤文件
    Returns: None
    """
    filter_list = '__*|.*|venv|*.png|*.xlsx'
    if filter: filter_list += f'|{filter}'
    out = Shell(f'tree {dir} -F -I "{filter_list}" -L {line} {more}').start()
    localfile = os.path.join(dir, '.tree.md')
    with open(localfile, 'w', encoding='utf-8') as f:
        f.write('```\n')
        ll = out.splitlines()
        file = []
        dir_f = []
        for i in ll:
            # 过滤出常规的文件夹内文件
            if '│\xa0\xa0     ├' in i or '│\xa0\xa0 ├──' in i or '│\xa0\xa0 └──' in i or '│\xa0\xa0 │' in i:
                dir_f.append(i)
            elif '    ├──' in i or '    └──' in i:  # 过滤字符串末尾的文件夹内文件
                i = i.replace('    ', '│\xa0\xa0')
                dir_f.append(i)
            elif i.endswith('/'):  # 文件夹处理
                i = i.replace('└──', '├──')
                dir_f.append(i)
            else:
                file.append(i)
        file[-3] = file[-3].replace('├──', '└──')
        f.write('\n'.join(dir_f) + '\n'.join(file))
        f.write('\n```\n')


def check_json_format(file):
    """
    检查上传的Json文件是否符合规范
    """
    new_dict = {}
    data = json.load(file)
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


def prompt_personal_tag(select, ipaddr):
    all_, personal = toolbox.get_conf('preset_prompt')['key']
    if select and personal != select and all_ != select:
        tab_cls = select + '_sys'
    else:
        tab_cls = str(ipaddr)
    return tab_cls


def check_expected_time():
    """检查是否工作时间"""
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


def get_files_list(folder_path, filter_format: list):
    # 获取符合条件的文件列表
    os.makedirs(folder_path, exist_ok=True)
    file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f))
                 and os.path.splitext(f)[1] in filter_format]
    # 使用文件修改时间排序文件列表
    sorted_files = sorted(file_list, key=lambda x: os.path.getmtime(x), reverse=True)
    only_name = [os.path.splitext(os.path.basename(f))[0] for f in sorted_files]
    # 获取最新的文件名
    newest_file = only_name[0] if only_name else None
    newest_file_path = sorted_files[0] if only_name else None
    return sorted_files, only_name, newest_file_path, newest_file


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
        count_tokens += len(encoding.encode(str(i)))
    return count_tokens


def check_list_format(input_string):
    try:
        list_object = ast.literal_eval(input_string)
        if isinstance(list_object, list):
            return list_object
        else:
            return False
    except:
        return False


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


def get_html(filename):
    path = os.path.join(init_path.base_path, "docs/assets/html", filename)
    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            return file.read()
    return ""


def spike_toast(content='保存成功', title='Success'):
    return get_html('gradio_toast.html').format(title=title, content=content)


def md_division_line():
    gr.Markdown("---", elem_classes="hr-line")


def git_log_list():
    ll = Shell("git log --pretty=format:'%s | %h' -n 10").start().splitlines()
    return [i.split('|') for i in ll if 'branch' not in i][:5]


def replace_special_chars(file_name):
    # 该正则表达式匹配除了数字、字母、下划线、点、空格、中文字符、【和】以外的所有字符
    new_name = re.sub(r'[^\d\w\s\.\_\u4e00-\u9fff【】]', '', file_name).rstrip().replace(' ', '_')
    if not new_name:
        new_name = created_atime()
    return new_name


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
        row_data = file_manifest_filter_type(row_data, filter_=None)
        tabs_list += "".join([tab_format % i for i in row_data]) + '|\n'
    return tabs_list


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
        icon_path = toolbox.get_conf('qc_icon_path')
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
    qr_path = os.path.join(init_path.logs_path, file_name)
    img.save(qr_path)
    return qr_path


def created_atime():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def 通知机器人(error):
    robot_hook = toolbox.get_conf('robot_hook')
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


def match_chat_information(text):
    pattern = r'<div class="raw-message hideM"><pre>(.*?)</pre></div>'
    match = re.search(pattern, text, flags=re.DOTALL)
    if match:
        return escape_markdown(match.group(1), reverse=True)
    else:
        return text


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


def get_avatar_img(llm_s):
    chat_bot_path = os.path.join(init_path.assets_path, 'imgs')
    file_list, only_name, new_path, new_name = get_files_list(chat_bot_path, filter_format=['.png'])
    chat_img = ''
    for i in range(len(only_name)):
        if only_name[i] in llm_s:
            chat_img = file_list[i]
    if chat_img:
        return ['./docs/assets/imgs/tester.png', chat_img.replace(init_path.base_path, '.')]
    else:
        return ['./docs/assets/imgs/tester.png', './docs/assets/imgs/user.png']


valid_img_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'svg', 'webp', 'ico', 'tif', 'tiff', 'raw', 'eps', 'gif']


def split_parse_url(url, tag: list | None, index=1) -> str:
    if url:  # 有url 才往下走
        url_parts = re.split('[/?=&#]+', url)
        if not tag and url:
            return url_parts[index]
        for i in range(len(url_parts)):
            if url_parts[i] in tag:
                return url_parts[i + index]


def split_domain_url(link_limit, start='http', domain_name: list = ['']) -> list:
    link = str(link_limit).split()
    links = []
    for i in link:
        if i.startswith(start) and any(name in i for name in domain_name):
            links.append(i)
    return links


if __name__ == '__main__':
    # print(get_files_list('', ['.json']))
    print(extract_link_pf('', valid_img_extensions))
