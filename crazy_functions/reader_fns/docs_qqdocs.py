# encoding: utf-8
# @Time   : 2023/9/2
# @Author : Spike
# @Descr   : 腾讯云文档
import re
import json
import time
import os
import requests

from common import func_box
from common import toolbox
from crazy_functions.reader_fns import crazy_box
from common.path_handle import init_path


class QQDocs:

    def __init__(self, link):
        self._hosts = 'docs.qq.com'
        self.link = link
        self.link_id = func_box.split_parse_url(link, None, index=3)
        self.file_info_dict = {'tag': '',}
        self.cookies = toolbox.get_conf('QQ_COOKIES')
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


def get_qqdocs_files(limit, project_folder, file_types, ipaddr):
    """
    Args:
        limit: 腾讯文档分享文件地址
        project_folder: 存储地址
        file_types: 指定的文件类型
        ipaddr: 用户信息
    Returns: [提取的文件list]
    """
    qqdocs = QQDocs(limit)
    d_link, f_name = qqdocs.obtain_file_download_link()
    for _type in file_types:
        if _type in f_name:
            resp = requests.get(url=d_link, verify=False)
            file_path = os.path.join(project_folder, f_name)
            with open(file_path, mode='wb') as f:
                f.write(resp.content)
            return [file_path]
    return []


def get_qqdocs_from_everything(txt, type: list=[''], ipaddr='temp'):
    """
    Args:
        txt: kudos 文件分享码
        type: type=='' 时，将支持所有文件类型
        ipaddr: 用户信息
    Returns:
    """
    link_limit = func_box.split_domain_url(link_limit=txt, domain_name=['docs.qq'])
    file_manifest = []
    success = ''
    project_folder = os.path.join(init_path.users_path, ipaddr, 'qqdocs')
    os.makedirs(project_folder, exist_ok=True)
    for limit in link_limit:
        file_manifest += get_qqdocs_files(limit, project_folder, type, ipaddr)
    return success, file_manifest, project_folder



if __name__ == '__main__':
    pass






