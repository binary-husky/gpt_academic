# encoding: utf-8
# @Time   : 2024/1/3
# @Author : Spike
# @Descr   : 飞书云文档
import requests
from common import func_box
from common import toolbox
from common.path_handler import init_path
import os
import json


class Feishu:

    def __init__(self, url, headers=None):
        self.url = url
        if headers:
            self.header_cookies = headers
            if isinstance(headers, str):
                self.header_cookies = json.loads(headers)
        else:
            self.header_cookies = toolbox.get_conf('FEISHU_HEADER_COOKIE')
        self.base_host = 'https://lg0v2tirko.feishu.cn'
        self.share_tag = func_box.split_parse_url(url, None, 3)
        self.share_file_type = func_box.split_parse_url(url, None, 2)
        self.header_cookies.update({'referer': f'{self.base_host}/{self.share_file_type}/{self.share_tag}'})
        self.file_download_url = 'https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/%t/'
        self.file_mapping = {
            'docx': 'docx',
            'sheet': 'xlsx',
            'file': False
            # 'bitable': 'xlsx' 这较难支持，。。。
        }

    def __submit_download_task(self):
        """提交下载任务"""
        json_data = {
            'token': self.share_tag,
            'type': self.share_file_type,
            'file_extension': self.file_mapping[self.share_file_type],
            'event_source': '1',
            'need_comment': True,
        }
        response = requests.post(
            f'{self.base_host}/space/api/export/create/',
            headers=self.header_cookies,
            json=json_data, verify=False
        ).json()
        return response['data']['ticket'], response['data']['job_timeout']

    def query_download_task(self):
        """查询下载任务状态"""
        params = {
            'token': self.share_tag,
            'type': self.share_file_type,
            'synced_block_host_token': self.share_tag,
            'synced_block_host_type': '22',
        }
        if self.file_mapping[self.share_file_type]:  # 支持转换提交转换任务
            ticket_id, time_out = self.__submit_download_task()
            for i in range(time_out):
                response = requests.get(
                    f'{self.base_host}/space/api/export/result/{ticket_id}',
                    params=params, verify=False,
                    headers=self.header_cookies,
                ).json()
                if response['data']['result']['file_token']:
                    file_name = response['data']['result']['file_name']
                    file_type = response['data']['result']['file_extension']
                    file_download_url = response['data']['result']['file_token']
                    return self.file_download_url.replace('%t', file_download_url), file_name + "." + file_type
        else:  # 不支持转换的默认直接下载
            return self.file_download_url.replace('%t', self.share_tag), self.get_docs_file_name()

    def get_docs_file_name(self):
        """获取文件名"""
        params = {
            'obj_token': self.share_file_type,
            'obj_type': '12',
        }
        response = requests.get(
            f'{self.base_host}/space/api/explorer/v2/obj/path/',
            params=params, verify=False,
            headers=self.header_cookies,
        ).json()
        return response['data']['entities']['nodes']['name']


def get_feishu_file(link, project_folder, header=None):
    feishu_docs = Feishu(link, header)
    file_download_url, file_name = feishu_docs.query_download_task()
    if file_download_url:
        file_path = os.path.join(project_folder, file_name)
        resp = requests.get(url=file_download_url, headers=feishu_docs.header_cookies, verify=False)
        with open(file_path, mode='wb') as f:
            f.write(resp.content)
        return {func_box.local_relative_path(file_path): link}
    else:
        return {}


def get_feishu_from_limit(link_limit,  project_folder, header=None):
    """
    Args:
        link_limit: kudos 文件分享码
        project_folder: 存放地址
        header: 飞书cookie
    Returns:
    """
    success = ''
    file_mapping = {}
    project_folder = os.path.join(project_folder, 'feishu')
    os.makedirs(project_folder, exist_ok=True)
    for limit in link_limit:
        file_mapping.update(get_feishu_file(limit, project_folder, header))
    return success, file_mapping


if __name__ == '__main__':
    pass