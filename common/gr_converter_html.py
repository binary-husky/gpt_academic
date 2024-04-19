# encoding: utf-8
# @Time   : 2024/4/19
# @Author : Spike
# @Descr   :
import json
import os
import random
import uuid

from common.path_handler import init_path
from shared_utils.config_loader import get_conf
from common.func_box import valid_img_extensions, local_relative_path
from crazy_functions.reader_fns.local_markdown import to_markdown_tabs


def get_html(filename):
    path = os.path.join(init_path.base_path, "docs/assets/html", filename)
    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            return file.read()
    return ""


def spike_toast(content='保存成功', title='Success'):
    return get_html('gradio_toast.html').format(title=title, content=content)


def html_download_blank(__href, dir_name=''):
    CUSTOM_PATH = get_conf('CUSTOM_PATH')
    if os.path.exists(__href):
        __href = f'{CUSTOM_PATH}file={__href}'
    if not dir_name:
        dir_name = str(__href).split('/')[-1]
    a = f'<a href="{__href}" target="_blank" download="{dir_name}" class="svelte-xrr240">{dir_name}</a>'
    return a


def html_iframe_code(html_file):
    html_file = html_local_file(html_file)
    ifr = f'<iframe width="100%" height="500px" frameborder="0" src="{html_file}"></iframe>'
    return ifr


def get_fold_panel(btn_id=None):
    if not btn_id:
        btn_id = uuid.uuid4().hex

    def _format(title, content: str = '', status=''):
        if isinstance(status, bool) and status:
            status = 'Done'
        fold_html = get_html('fold-panel.html').replace('{id}', btn_id)
        if isinstance(content, dict):
            content = json.dumps(content, indent=4, ensure_ascii=False)
        content = f'\n```\n{content.replace("```", "").strip()}\n```\n'
        title = title.replace('\n', '').strip()
        return fold_html.format(title=f"<p>{title}</p>", content=content, status=status)

    return _format


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
