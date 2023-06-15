#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/14
# @Author : Spike
# @Descr   :
import re
import json
from bs4 import BeautifulSoup
import requests
from toolbox import get_conf


class Utils:

    def __init__(self):
        self.find_keys_type = 'type'
        self.find_keys_value = ['text', 'caption']
        self.find_keys_tags = 'picture'

    def find_all_text_keys(self, dictionary, parent_type=None, text_values=None, filter_type=''):
        """
        嵌套查找self.find_keys_value相关的key和value
        Args:
            dictionary: 字典或列表
            parent_type: 匹配的type，作为新列表的key，用于分类
            text_values: 存储列表
            filter_type: 当前层级find_keys_type==filter_type时，不继续往下嵌套
        Returns:
            text_values和排序后的context_
        """
        # 初始化 text_values 为空列表，用于存储找到的所有text值
        if text_values is None:
            text_values = []
        # 如果输入的dictionary不是字典类型，返回已收集到的text值
        if not isinstance(dictionary, dict):
            return text_values
        # 获取当前层级的 type 值
        current_type = dictionary.get(self.find_keys_type, parent_type)
        # 如果字典中包含 'text' 或 'caption' 键，将对应的值添加到 text_values 列表中
        for key in self.find_keys_value:
            if key in dictionary:
                content_value = dictionary.get(key, None)
                text_values.append({current_type: content_value})
        # 如果当前类型不等于 filter_type，则继续遍历子级属性
        if current_type != filter_type:
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    self.find_all_text_keys(value, current_type, text_values, filter_type)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self.find_all_text_keys(item, current_type, text_values, filter_type)
        context_ = [i[_] for i in text_values for _ in i if _ == self.find_keys_tags and i[_] != '' f'{self.find_keys_tags}:'+i[_]]
        context_ = '\n'.join(context_)
        return text_values, context_


WPS_COOKIES, WPS_HEADERS, WPS_PARM, WPS_URL_OTL = get_conf('WPS_COOKIES', 'WPS_HEADERS', 'WPS_PARM', 'WPS_URL_OTL')
class Kdocs:

    def __init__(self, url):

        self.url = url
        self.cookies = WPS_COOKIES
        self.headers = WPS_HEADERS
        self.parm_data = WPS_PARM
        self.tol_url = WPS_URL_OTL

    def get_file_info(self):
        """
        获取传递过来的文档HTML信息
        Returns:
            HTML信息
        """
        response = requests.get(self.url, cookies=self.cookies, headers=self.headers)
        return response.text

    def get_file_content(self):
        """
        爬虫解析文档内容
        Returns:
            文档内容
        """
        url_parts = self.url.split('/')
        try:
            l_index = url_parts.index('l')
            otl_url_str = url_parts[l_index + 1]
        except ValueError:
            return None
        html_content = self.get_file_info()
        file_info = self.bs4_file_info(html_content)  # 调用 bs4_file_info() 方法解析 html_content，获取文件信息
        self.parm_data.update(file_info)  # 更新类的一个参数 parm_data
        json_data = json.dumps(self.parm_data)
        response = requests.post(
            str(self.tol_url).replace('%v', otl_url_str),
            cookies=self.cookies,
            headers=self.headers,
            data=json_data,)
        return response.text

    def bs4_file_info(self, html_str):
        """
        bs4爬虫文档信息，没有这个可不行🤨
        Args:
            html_str: HTML信息
        Returns:
            {'connid': 文档id, 'group': 文档的群组, 'front_ver': 文档版本}
        """
        html = BeautifulSoup(html_str, "html.parser")
        # Find all script tags in the HTML
        script_tags = html.find_all("script")
        json_string = None
        # Iterate through script tags to find the one containing required data
        for tag in script_tags:
            if tag.string and "window.__WPSENV__" in tag.string:
                json_string = re.search(r"window\.__WPSENV__=(.*);", tag.string).group(1)
                break
        if json_string:
            # Load the JSON data from the found string
            json_data = json.loads(json_string)
            file_connid = json_data['conn_id']
            file_group = json_data['user_group']
            file_front_ver = json_data['file_version']
            return {'connid': file_connid, 'group': file_group, 'front_ver': file_front_ver}
        else:
            return None




if __name__ == '__main__':
    json_data = Kdocs('https://kdocs.cn/l/cfNEKXKfEZNn').get_file_content()
    dict_data = json.loads(json_data)
    context = Utils().find_all_text_keys(dict_data, filter_type='')
    print(context)
