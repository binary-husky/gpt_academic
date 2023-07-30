#! .\venv\
# encoding: utf-8
# @Time   : 2023/7/29
# @Author : Spike
# @Descr   :
import os
import re
import time
import json
import requests
import urllib.parse

from bs4 import BeautifulSoup
from comm_tools import toolbox

class Kdocs:

    def __init__(self, url):
        WPS_COOKIES, = toolbox.get_conf('WPS_COOKIES',)
        self.url = url
        self.cookies = WPS_COOKIES
        self.headers = {
            'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
            'content-type': 'text/plain;charset=UTF-8',
            'x-csrf-rand': '',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}
        self.ex_headers = {
            'Host': 'www.kdocs.cn',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'sec-ch-ua-platform': '"macOS"',
            'origin': 'https://www.kdocs.cn',
        }
        self.dzip_header = {
            'Host': 'kdzip-download.kdocs.cn',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',

            }
        self.parm_otl_data = {"connid": "",
                              "args": {"password": "", "readonly": False, "modifyPassword": "", "sync": True,
                                       "startVersion": 0, "endVersion": 0},
                              "ex_args": {"queryInitArgs": {"enableCopyComments": False, "checkAuditRule": False}},
                              "group": "", "front_ver": ""}
        self.parm_shapes_data = {"objects": [], "expire": 86400000, "support_webp": True, "with_thumbnail": True,
                                 "support_lossless": True}
        self.parm_export_preload = {"ver": "56"}
        self.parm_bulk_download = {'file_ids': []}
        self.params_task = {'task_id': ''}
        self.params_continue = {"task_id": "", "download_as": [
                            {"suffix": ".otl", "as": ".pdf"},
                            {"suffix": ".ksheet", "as": ".xlsx"},
                            {"suffix": ".pof", "as": ".png"},
                            {"suffix": ".pom", "as": ".png"}]}
        self.tol_url = 'https://www.kdocs.cn/api/v3/office/file/%v/open/otl'
        self.shapes_url = 'https://www.kdocs.cn/api/v3/office/file/%v/attachment/shapes'
        self.kdocs_download_url = 'https://drive.kdocs.cn/api/v5/groups/%g/files/%f/download?isblocks=false&support_checksums=md5,sha1,sha224,sha256,sha384,sha512'
        self.drive_download_url = 'https://drive.wps.cn/api/v3/groups/%g/files/%f/download?isblocks=false'
        self.group_url = 'https://drive.wps.cn/api/v5/links/%v?review=true'
        self.export_url = 'https://www.kdocs.cn/api/v3/office/file/%f/export/%t/result'
        self.preload_url = 'https://www.kdocs.cn/api/v3/office/file/%f/export/%t/preload'
        self.bulk_download_url = 'https://www.kdocs.cn/kfc/batch/v2/files/download'
        self.bulk_continue_url = 'https://www.kdocs.cn/kfc/batch/v2/files/download/continue'
        self.task_result_url = 'https://www.kdocs.cn/kfc/batch/v2/files/download/progress'
        self.url_share_tag = ''
        self.url_dirs_tag = ''
        self.split_link_tags()
        if self.url_share_tag:
            self.file_info_parm = self.get_file_info_parm()
        self.docs_old_type = ['.docs', '.doc', '.pptx', '.ppt', '.xls', '.xlsx', '.pdf', '.csv', '.txt', '.pom', '.pof']
        self.to_img_type = {'.pom': '.png', '.pof': '.png'}
        self.media_type = ['.mp4', '.m4a', '.wav', '.mpga', '.mpeg', '.mp3', '.avi', '.mkv', '.flac', '.aac']
        self.smart_type = {'.otl': 'pdf', '.ksheet': 'xlsx'}

    def get_file_info_html(self):
        """
        获取传递过来的文档HTML信息
        Returns:
            HTML信息
        """
        response = requests.get(self.url, cookies=self.cookies, headers=self.headers, verify=False)
        return response.text

    def get_file_info_parm(self):
        # 获取分享文件info信息
        response = requests.get(self.group_url.replace("%v", self.url_share_tag),
                                cookies=self.cookies,
                                headers=self.headers, verify=False).json()
        try:
            file_info = response['fileinfo']
        except KeyError:
            file_info = {}
        return file_info

    def submit_batch_download_tasks(self):
        # 提交目录转换任务
        self.parm_bulk_download.update({'file_ids': [self.url_dirs_tag]})
        dw_response = requests.post(self.bulk_download_url, cookies=self.cookies, headers=self.ex_headers,
                                 json=self.parm_bulk_download, verify=False).json()
        if dw_response.get('data', False):
            task_id = dw_response['data']['task_id']
            task_info = dw_response['data']['online_file'], dw_response['data']['online_fnum']
        else:
            print(dw_response['result'])
            task_id = None
            task_info = None
        if task_id:
            self.params_continue.update({'task_id': task_id})
            requests.post(self.bulk_continue_url, cookies=self.cookies, headers=self.ex_headers,
                          json=self.params_continue, verify=False).json()
        return task_id, task_info

    def polling_batch_download_tasks(self, task_id):
        # 轮询任务状态，提取下载链接
        self.params_task.update({'task_id': task_id})
        link = ''
        faillist = ''
        if task_id:
            for i in range(600):
                response = requests.get(url=self.task_result_url,
                                        params=self.params_task,
                                        cookies=self.cookies,
                                        headers=self.ex_headers, verify=False).json()
                if response['data'].get('url', False):
                    link = response['data'].get('url', '')
                    faillist = str(response['data'].get('faillist', ''))
                    break
                time.sleep(3)
        return link, faillist

    def wps_file_download(self, url):
        # 需要wpscookie文件下载
        response = requests.get(url=url, cookies=self.cookies, headers=self.dzip_header, verify=False)
        return response

    def document_aggregation_download(self, file_type=''):
        #
        link_name = self.file_info_parm['fname']
        for t in self.to_img_type:
            if t in link_name:
                link_name = link_name+self.to_img_type[t]
        link = ''
        for t in self.docs_old_type:
            if t in link_name and file_type in link_name:
                link = self.get_docs_old_link()
        for t in self.media_type:
            if t in link_name and file_type in link_name:
                link = self.get_media_link()
        for t in self.smart_type:
            if t in link_name and file_type in link_name:
                link = self.get_kdocs_intelligence_link(type=self.smart_type[t])
                link_name = link_name+f".{self.smart_type[t]}"
        return link, link_name

    def get_media_link(self):
        # 媒体文件下载
        response = requests.get(self.drive_download_url.replace("%g", str(self.file_info_parm['groupid'])
                                                                ).replace('%f', str(self.file_info_parm['id'])),
                                cookies=self.cookies,
                                headers=self.headers, verify=False)
        link = response.json()['fileinfo']['url']
        return self.url_decode(link)

    def get_docs_old_link(self):
        # ppt、doc、pdf、xls下载
        response = requests.get(self.kdocs_download_url.replace("%g", str(self.file_info_parm['groupid'])
                                                                ).replace('%f', str(self.file_info_parm['id'])),
                                cookies=self.cookies,
                                headers=self.headers, verify=False)
        try:
            link = response.json()['fileinfo']['url']
        except:
            link = response.json()['url']
        return self.url_decode(link)

    def get_kdocs_intelligence_link(self, type='xlsx'):
        # 智能文档下载
        response_task = requests.post(
            self.preload_url.replace('%f', str(self.file_info_parm['id'])).replace('%t', type),
            cookies=self.cookies,
            headers=self.ex_headers,
            json=self.parm_export_preload, verify=False
        )
        self.parm_export_preload.update(response_task.json())
        for i in range(20):
            response_link = requests.post(
                self.export_url.replace('%f', str(self.file_info_parm['id'])).replace('%t', type),
                cookies=self.cookies,
                headers=self.ex_headers,
                json=self.parm_export_preload, verify=False
            )
            if response_link.json()['status'] == 'finished':
                return response_link.json()['data']['url']
        return None

    def split_link_tags(self):
        # 提取tag，给后续请求试用
        url_parts = re.split('[/\?&#]+', self.url)
        try:
            try:
                l_index = url_parts.index('l')
                otl_url_str = url_parts[l_index + 1]
                self.url_share_tag = otl_url_str
            except ValueError:
                l_index = url_parts.index('ent')
                otl_url_str = url_parts[-1]
                self.url_dirs_tag = otl_url_str
        except ValueError:
            print('既不是在线文档，也不是文档目录')
            return ''

    def get_file_content(self):
        """
        爬虫解析文档内容
        Returns:
            文档内容
        """
        otl_url_str = self.url_share_tag
        if otl_url_str is None: return
        html_content = self.get_file_info_html()
        self.bs4_file_info(html_content)  # 调用 bs4_file_info() 方法解析 html_content，获取文件信息# 更新类的parm_data 和 headers
        json_data = json.dumps(self.parm_otl_data)
        response = requests.post(
            str(self.tol_url).replace('%v', otl_url_str),
            cookies=self.cookies,
            headers=self.headers,
            data=json_data, verify=False)
        return response.json(), response.text

    def get_file_pic_url(self, pic_dict: dict):
        otl_url_str = self.url_share_tag
        if otl_url_str is None: return
        for pic in pic_dict:
            pic_parm = {'attachment_id': pic, "imgId": pic_dict[pic], "max_edge": 1180, "source": ""}
            self.parm_shapes_data['objects'].append(pic_parm)
        json_data = json.dumps(self.parm_shapes_data)
        response = requests.post(
            str(self.shapes_url).replace('%v', otl_url_str),
            cookies=self.cookies,
            headers=self.headers,
            data=json_data, verify=False)
        url_data = response.json()['data']
        for pic in url_data:
            try:
                pic_dict[pic] = self.url_decode(url_data[pic]['url'])
            except Exception as f:
                pass
        return pic_dict

    @staticmethod
    def url_decode(url):
        decoded_url = urllib.parse.unquote(url)
        return decoded_url


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
            file_id = json_data['root_file_id']
            group_id = json_data['file_info']['file']['group_id']
            self.headers['x-csrf-rand'] = json_data['csrf_token']
            self.parm_otl_data.update({'connid': file_connid, 'group': file_group, 'front_ver': file_front_ver,
                                       'file_id': file_id, 'group_id':group_id})
            return True
        else:
            return None