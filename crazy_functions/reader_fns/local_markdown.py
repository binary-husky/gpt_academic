# encoding: utf-8
# @Time   : 2024/1/15
# @Author : Spike
# @Descr   : Markdown 文件处理工具
import os
import re
import json

from common.func_box import Shell


class MdProcessor:

    def __init__(self, content):
        self.content_text = content

    @staticmethod
    def _clean_br_string(s):
        s = re.sub('<\s*br\s*/?>', '\n', s)  # 使用正则表达式同时匹配<br>、<br/>、<br />、< br>和< br/>
        s = s.replace(' ', '')  # 去除所有空格
        s = s.replace('<b>', '\n')
        return s

    def tabs_to_list(self):
        test_case = []
        if type(self.content_text) is str:
            self.content_text = [self.content_text]
        for value in self.content_text:
            test_case_content = value.splitlines()
            for i in test_case_content:
                if re.findall(r'\|\s*[:|-]+\s*\|', i):  # 过滤表头
                    test_case = test_case[:-1]
                    continue
                if i.find('|') != -1:
                    test_case.append([self._clean_br_string(i) for i in i.split('|')[1:]])
                elif i.find('｜') != -1:
                    test_case.append([self._clean_br_string(i) for i in i.split('｜')[1:]])
                else:
                    print('脏数据过滤，这个不符合写入测试用例的条件')
        return test_case

    def json_to_list(self):
        supplementary_data = []
        if 'raise' in self.content_text:
            # 尝试GPT返回错误超出Token限制导致的Json数据结构错误
            content_data = "\n".join([item for item in str(self.content_text).splitlines() if item != ''][:-1])
            if re.search(r'[^\w\s\]]', content_data[-1]):  # 判断是不是有,号之类的特殊字符
                content_data = content_data[:-1]  # 有则排除
            content_data += ']'
        # 尝试兼容一些错误的JSON数据
        fix_data = self.content_text.replace('][', '],[').replace(']\n[', '],[')
        fix_data = fix_data.replace('\n...\n', '').replace('\n\n...\n\n', '')
        pattern = r'\[[^\[\]]*\]'
        result = re.findall(pattern, fix_data)
        for sp in result:
            __list = []
            try:
                __list = json.loads(sp)
                supplementary_data.append(__list)
            except:
                print(f'{sp} 测试用例转dict失败了来看看')
        return supplementary_data


class MdHandler:

    def __init__(self, md_path, output_dir=None):
        """
        Args:
            md_path: 文件路径
            output_dir: 保存路径，如果没有另存为操作，可以为空
        """
        if output_dir:
            self.output_dir = os.path.join(output_dir, 'markdown')
            os.makedirs(self.output_dir, exist_ok=True)
        self.md_path = md_path
        self.file_name = os.path.basename(md_path).split('.')[0]
        self.content_text = ''

    def set_content(self, content):
        self.content_text = content

    def get_content(self):
        with open(self.md_path, 'r', encoding='utf-8') as f:
            self.content_text = f.read()
            return self.content_text

    def save_markdown(self, content):
        self.content_text = content
        with open(self.md_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_mark_map(self):
        from common import func_box
        user_path = os.path.join(self.output_dir, 'mark_map')
        os.makedirs(user_path, exist_ok=True)
        html_file = os.path.join(user_path, f"{self.file_name}.html")
        Shell(f'npx markmap-cli --no-open "{self.md_path}" -o "{html_file}"').start()
        return html_file

    def save_excel(self):
        ...

    def save_pdf(self):
        ...

    def save_word(self):
        ...

    def save_xmind(self):
        ...

    def save_powerpoint(self):
        ...


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
    from common.gr_converter_html import file_manifest_filter_type
    if column:
        transposed_tabs = list(map(list, zip(*tabs)))
    else:
        transposed_tabs = tabs
    if not head or not tabs:
        return None
    # Find the maximum length among the columns
    max_len = max(len(column) for column in transposed_tabs)

    tab_format = "| %s "
    tabs_list = "".join([tab_format % i for i in head]) + '|\n'
    tabs_list += "".join([tab_format % alignment for i in head]) + '|\n'

    for i in range(max_len):
        row_data = [str(tab[i]).replace('\n', '<b>') if i < len(tab) else '' for tab in transposed_tabs]
        row_data = file_manifest_filter_type(row_data, filter_=None)
        tabs_list += "".join([tab_format % i for i in row_data]) + '|\n'
    return tabs_list