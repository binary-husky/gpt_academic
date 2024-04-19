# encoding: utf-8
# @Time   : 2024/1/3
# @Author : Spike
# @Descr   : 飞书云文档
import requests
from common.func_box import split_parse_url, local_relative_path
from common.toolbox import get_conf
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
            self.header_cookies = get_conf('FEISHU_HEADER_COOKIE')
        self.base_host = f'https://{get_conf("FEISHU_BASE_HOST")}'
        self.share_tag = split_parse_url(url, None, 3)
        self.share_file_type = split_parse_url(url, None, 2)
        self.is_folder = True if 'folder' == self.share_tag else False
        if self.is_folder:
            self.share_tag = split_parse_url(url, None, 4)
        self.header_cookies.update({'referer': f'{self.base_host}/{self.share_file_type}/{self.share_tag}'})
        self.file_download_url = 'https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/%t/'
        self.file_mapping = {
            'docx': 'docx',
            'sheet': 'xlsx',
            'file': False,
            'wiki': 'docx',
            # 'bitable': 'xlsx' 这较难支持，。。。
        }
        self.type_need_mapping = {
            'wiki': 'docx',
        }
        self.folder_obj_mapping = {}

    def __submit_download_task(self):
        """提交下载任务"""
        share_tag = self.share_tag if self.share_file_type != 'wiki' else self.query_wiki_docs_id()
        share_file_type = self.type_need_mapping.get(self.share_file_type) if self.type_need_mapping.get(
            self.share_file_type) else self.share_file_type
        json_data = {
            'token': share_tag,
            'type': share_file_type,
            'file_extension': self.file_mapping[self.share_file_type],
            'event_source': '1' if self.share_file_type == 'wiki' else '6',
            'need_comment': True,
        }
        response = requests.post(
            f'{self.base_host}/space/api/export/create/',
            headers=self.header_cookies,
            json=json_data, verify=False
        ).json()
        if not response.get('data'):
            raise ValueError(json.dumps(response))
        return response['data']['ticket'], response['data']['job_timeout']

    def query_wiki_docs_id(self):
        """查询wiki文档"""
        params = {
            'wiki_token': self.share_tag,
        }
        response = requests.get(
            f'{self.base_host}/space/api/wiki/v2/tree/get_info',
            params=params, verify=False,
            headers=self.header_cookies)

        return response.json()['data']['tree']['nodes'][self.share_tag]['obj_token']

    def query_folder_list(self, token, deep_link=False):
        """
        Args:
            token: 文件夹token
            deep_link: 是否递归查询
        Returns:
        """
        params = {"token": token}
        response = requests.get(
            f'{self.base_host}/space/api/explorer/v3/children/list/',
            params=params, verify=False,
            headers=self.header_cookies).json()
        nodes = response['data']['entities']['nodes']
        for i in nodes:
            if Feishu(nodes[i]['url']).is_folder:
                if deep_link:
                    self.query_folder_list(nodes[i]['obj_token'], deep_link)
            else:
                self.folder_obj_mapping[nodes[i]['obj_token']] = nodes[i]['url']
        return self.folder_obj_mapping

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
    file_mapping = {}
    file_download_mapping = {}
    if feishu_docs.is_folder:
        folder_obj_mapping = feishu_docs.query_folder_list(feishu_docs.share_tag)
        for obj, link in folder_obj_mapping.items():
            file_download_url, file_name = Feishu(link, header).query_download_task()
            file_download_mapping[file_download_url] = file_name
    else:
        file_download_url, file_name = feishu_docs.query_download_task()
        file_download_mapping[file_download_url] = file_name
    for url, name in file_download_mapping.items():
        if url:
            file_path = os.path.join(project_folder, name)
            resp = requests.get(url=url, headers=feishu_docs.header_cookies, verify=False)
            with open(file_path, mode='wb') as f:
                f.write(resp.content)
            file_mapping.update({local_relative_path(file_path): link})
    return file_mapping


def get_feishu_from_limit(link_limit, project_folder, header=None):
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