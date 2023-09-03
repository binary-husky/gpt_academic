#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/2
# @Author : Spike
# @Descr   :
import re
import json
import time
import os
import requests

from comm_tools import func_box
from comm_tools import toolbox
from crazy_functions.kingsoft_fns import crazy_box


class QQDocs:

    def __init__(self, link):
        self._hosts = 'docs.qq.com'
        self.link = link
        self.link_id = self.split_link_id()
        self.file_info_dict = {'tag': '',}
        self.cookies, = toolbox.get_conf('QQ_COOKIES')
        self.file_info_header = {
            'Host': self._hosts,
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62',
            'referer': 'https://docs.qq.com/',
            'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
        }
        self.file_info_url = 'https://docs.qq.com/dop-api/opendoc'
        self.blind_task_url = 'https://docs.qq.com/v1/export/export_office'
        self.obtain_d_link_url = 'https://docs.qq.com/v1/export/query_progress'
        self.get_file_info()

    def split_link_id(self):
        # 提取tag，给后续请求使用
        url_parts = re.split('[/\?&#]+', self.link)
        try:
            l_index = url_parts.index(self._hosts)
            url_id = url_parts[l_index + 2]
            self.link_id = url_id
            return url_id
        except ValueError:
            print('既不是在线文档，也不是文档目录')
            return ''

    def get_file_info(self):
        file_info_params = {
            'noEscape': '1',
            'id': self.link_id,
            'normal': '1',
            'outformat': '1',
            'startrow': '0',
            'endrow': '60',
            'wb': '1',
            'nowb': '0',
            'callback': 'clientVarsCallback',
        }
        re_pattern = re.compile(rf'{re.escape(file_info_params["callback"])}\((.*?)\)')
        response = requests.get(self.file_info_url, params=file_info_params,
                                headers=self.file_info_header,
                                verify=False)
        json_resp = re_pattern.findall(response.text)
        if json_resp:
            dict_info = json.loads(json_resp[0])
            info_vars = dict_info['clientVars']
            self.file_info_dict['tag'] = info_vars.get('padId', '')

    def submit_the_blind_task(self):
        blind_task_params = {
            'exportType': '0',
            'switches': '{"embedFonts":false}',
            'exportSource': 'client',
            'docId': self.file_info_dict['tag'],
        }
        response = requests.post(self.blind_task_url, headers=self.file_info_header,
                                 cookies=self.cookies, data=blind_task_params, verify=False)
        json_resp = response.json()
        return json_resp['operationId']

    def obtain_file_download_link(self):
        d_link_params = {
            'operationId': self.submit_the_blind_task()
        }
        for i in range(600):
            response = requests.get(self.obtain_d_link_url, params=d_link_params, cookies=self.cookies,
                                    headers=self.file_info_header, verify=False)
            json_resp = response.json()
            if int(json_resp.get('ret', '1')) > 100:
                raise TypeError(f'该类型文档不支持导出\n {json_resp}')
            file_url = json_resp.get('file_url', '')
            if file_url:
                file_name = json_resp.get('file_name')
                return file_url, file_name
            else:
                print(f'下载任务进度： {json_resp.get("progress")}')


def get_qqdocs_files():
    pass


if __name__ == '__main__':
    qqdocs = QQDocs('https://docs.qq.com/slide/DS2FGRVdxdE1LTURI')
    print(qqdocs.obtain_file_download_link())





