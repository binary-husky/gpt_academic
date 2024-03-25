# encoding: utf-8
# @Time   : 2023/7/29
# @Author : Spike
# @Descr   : 金山云文档
import os
import re
import time
import json
import requests
import urllib.parse

from bs4 import BeautifulSoup
from common import toolbox, func_box
from crazy_functions.reader_fns.crazy_box import Utils
from crazy_functions import crazy_utils


class Kdocs:

    def __init__(self, url, cookies=None):
        if cookies:
            self.cookies = cookies
            if isinstance(cookies, str):
                self.cookies = json.loads(cookies)
        else:
            self.cookies = toolbox.get_conf('WPS_COOKIES')
        self.url = url
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
        self.file_comments_ulr = 'https://www.kdocs.cn/api/v3/office/outline/file/%f/comment'
        self.url_share_tag = func_box.split_parse_url(url, ['l'])
        self.url_dirs_tag = func_box.split_parse_url(url, ['ent'])
        if self.url_share_tag:
            self.file_info_parm = self.get_file_info_parm()
        self.docs_old_type = ['.docs', '.doc', '.pptx', '.ppt', '.xls', '.xlsx', '.pdf', '.csv', '.txt', '.pom', '.pof',
                              '.xmind']
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
        params_continue = {"task_id": "", "download_as": [
            {"suffix": ".otl", "as": ".pdf"},
            {"suffix": ".ksheet", "as": ".xlsx"},
            {"suffix": ".pof", "as": ".png"},
            {"suffix": ".pom", "as": ".png"}]}
        parm_bulk_download = {'file_ids': [], 'csrfmiddlewaretoken': self.cookies['csrf']}
        parm_bulk_download.update({'file_ids': [self.url_dirs_tag]})
        dw_response = requests.post(self.bulk_download_url, cookies=self.cookies, headers=self.ex_headers,
                                    json=parm_bulk_download, verify=False).json()
        if dw_response.get('data', False):
            task_id = dw_response['data']['task_id']
            task_info = dw_response['data'].get('online_file'), dw_response['data'].get('online_fnum')
        else:
            print(dw_response['result'])
            task_id = None
            task_info = None
        if task_id:
            params_continue.update({'task_id': task_id})
            requests.post(self.bulk_continue_url, cookies=self.cookies, headers=self.ex_headers,
                          json=params_continue, verify=False).json()
        return task_id, task_info

    def polling_batch_download_tasks(self, task_id):
        # 轮询任务状态，提取下载链接
        params_task = {'task_id': task_id}
        link = ''
        faillist = ''
        if task_id:
            for i in range(600):
                response = requests.get(url=self.task_result_url,
                                        params=params_task,
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

        link_name = self.file_info_parm['fname']
        for t in self.to_img_type:
            if t in link_name:
                link_name = link_name + self.to_img_type[t]
        link = ''
        for t in self.docs_old_type:
            if t in link_name and file_type in link_name:
                link = self.get_docs_old_link()
        for t in self.media_type:
            if t in link_name and file_type in link_name:
                link = self.get_media_link()
        for t in self.smart_type:
            if file_type == self.smart_type[t]:
                file_type = t
            if t in link_name and file_type in link_name:
                link = self.get_kdocs_intelligence_link(type=self.smart_type[t])
                link_name = link_name + f".{self.smart_type[t]}"
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

    def get_comments_desc(self, tag: list):
        comm_url = self.file_comments_ulr.replace('%f', self.url_share_tag)
        if tag:
            comm_url += f'?pageno=0&size=100&sids={",".join(tag)}'
        response = requests.get(comm_url, headers=self.headers,
                                cookies=self.cookies, verify=False)
        selections = response.json()['selections']
        comments_desc = {}
        for desc in selections:
            comments_desc[desc['selection_text']] = ''
            for i in desc['comments']:
                user_ = ''
                if i.get('user_info'):
                    user_ = i['user_info']['name'] + ':'
                reverse_order = f"\n> {user_} {i['comment']['content']['text']}" + comments_desc[desc['selection_text']]
                comments_desc[desc['selection_text']] = reverse_order
        return comments_desc

    def get_kdocs_intelligence_link(self, type='xlsx'):
        # 智能文档下载
        self.parm_export_preload = {"ver": "56"}
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
        parm_shapes_data = {"objects": [], "expire": 86400000, "support_webp": True, "with_thumbnail": True,
                            "support_lossless": True}
        otl_url_str = self.url_share_tag
        if otl_url_str is None: return
        for pic in pic_dict:
            pic_parm = {'attachment_id': pic, "imgId": pic_dict[pic], "max_edge": 1180, "source": ""}
            parm_shapes_data['objects'].append(pic_parm)
        json_data = json.dumps(parm_shapes_data)
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
                                       'file_id': file_id, 'group_id': group_id})
            return True
        else:
            return None


def if_kdocs_url_isap(url):
    kdocs = Kdocs(url)
    if 'otl' in kdocs.file_info_parm['fname']:
        return True
    return False


def get_docs_content(url, image_processing=False):
    """
    Args: 爬虫程序，通过拿到分享链接提取文档内信息
        url: 文档url
        image_processing: 是否开始OCR
    Returns:
    """
    kdocs = Kdocs(url)
    utils = Utils()
    json_data, json_dict = kdocs.get_file_content()
    text_values = utils.find_all_text_keys(json_data, filter_type='')

    _all, content, pic_dict, file_dict = utils.statistical_results(text_values, img_proce=image_processing)
    pic_dict_convert = kdocs.get_file_pic_url(pic_dict)
    empty_picture_count = sum(1 for item in _all if 'picture' in item and not item['picture']['caption'])
    # 提取补充说明
    desc_tag = utils.comments
    comments_desc = kdocs.get_comments_desc(tag=desc_tag)
    for key in comments_desc:
        index = content.find(key) + len(key)
        content = content[:index] + f"\n 补充说明: {comments_desc[key]}" + content[index:]
    return _all, content, empty_picture_count, pic_dict_convert, file_dict


def get_kdocs_dir(limit, project_folder, cookies=None):
    """
    Args:
        limit: 文档目录路径
        cookies:
        project_folder: 写入的文件
    Returns: [文件列表], 目录内文件信息, 失败信息
    """
    kdocs = Kdocs(limit, cookies)
    task_id, task_info = kdocs.submit_batch_download_tasks()
    link, task_faillist = kdocs.polling_batch_download_tasks(task_id)
    resp = kdocs.wps_file_download(link)
    content = resp.content
    temp_file = os.path.join(project_folder, kdocs.url_dirs_tag + '.zip')
    with open(temp_file, 'wb') as f:
        f.write(content)
    decompress_directory = os.path.join(project_folder, 'extract', kdocs.url_dirs_tag)
    toolbox.extract_archive(temp_file, decompress_directory)
    file_list = []
    file_mapping = {}
    success, file_manifest = crazy_utils.get_files_from_everything(decompress_directory, '', project_folder)
    file_list.extend(file_manifest)
    for fp in file_list:
        file_mapping[func_box.local_relative_path(fp)] = limit
    return file_mapping, task_info, task_faillist


def get_kdocs_files(limit, project_folder, cookies=None):
    """
    Args:
        limit: 金山文档分享文件地址
        cookies:
        project_folder: 存储地址
    Returns: [提取的文件list]
    """
    kdocs = Kdocs(limit, cookies)
    link, name = kdocs.document_aggregation_download(file_type='')
    tag = kdocs.url_share_tag
    if link:
        resp = requests.get(url=link, verify=False)
        content = resp.content
    else:
        return None
    if content:
        tag_path = os.path.join(project_folder, tag)
        temp_file = os.path.join(os.path.join(project_folder, tag, name))
        os.makedirs(tag_path, exist_ok=True)
        with open(temp_file, 'wb') as f:
            f.write(content)
        return {func_box.local_relative_path(temp_file): limit}


def get_kdocs_from_limit(link_limit, project_folder, cookies=None):
    """
    Args:
        cookies:
        link_limit: kudos 文件分享链接
        project_folder: 存放地址
    Returns:
    """
    file_mapping = {}
    success = ''
    project_folder = os.path.join(project_folder, 'k_docs')
    for limit in link_limit:
        if '/ent/' in limit:
            files, info, fail = get_kdocs_dir(limit, project_folder, cookies)
            file_mapping.update(files)
            success += f"{limit}文件信息如下：{info}\n\n 下载任务状况：{fail}\n\n"
        else:
            file_mapping.update(get_kdocs_files(limit, project_folder, cookies))
    return success, file_mapping


if __name__ == '__main__':
    pass
