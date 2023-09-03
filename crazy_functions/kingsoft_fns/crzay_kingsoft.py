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
from comm_tools import toolbox, func_box
from crazy_functions.kingsoft_fns import crazy_box
from crazy_functions import crazy_utils
from comm_tools import ocr_tools

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
        self.parm_bulk_download = {'file_ids': [], 'csrfmiddlewaretoken': self.cookies['csrf']}
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
        self.docs_old_type = ['.docs', '.doc', '.pptx', '.ppt', '.xls', '.xlsx', '.pdf', '.csv', '.txt', '.pom', '.pof', '.xmind']
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
            task_info = dw_response['data'].get('online_file'), dw_response['data'].get('online_fnum')
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
            if file_type == self.smart_type[t]:
                file_type = t
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
    utils = crazy_box.Utils()
    json_data, json_dict = kdocs.get_file_content()
    text_values = utils.find_all_text_keys(json_data, filter_type='')
    _all, content, pic_dict, file_dict = utils.statistical_results(text_values, img_proce=image_processing)
    pic_dict_convert = kdocs.get_file_pic_url(pic_dict)
    empty_picture_count = sum(1 for item in _all if 'picture' in item and not item['picture']['caption'])
    return _all, content, empty_picture_count, pic_dict_convert, file_dict


def get_kdocs_dir(limit, project_folder, type, ipaddr):
    """
    Args:
        limit: 文档目录路径
        project_folder: 写入的文件
        type: 文件类型, 不过这里没用到
        ipaddr:  文件所属标识
    Returns: [文件列表], 目录内文件信息, 失败信息
    """
    kdocs = Kdocs(limit)
    task_id, task_info = kdocs.submit_batch_download_tasks()
    link, task_faillist = kdocs.polling_batch_download_tasks(task_id)
    resp = kdocs.wps_file_download(link)
    content = resp.content
    temp_file = os.path.join(project_folder, kdocs.url_dirs_tag + '.zip')
    with open(temp_file, 'wb') as f: f.write(content)
    decompress_directory = os.path.join(project_folder, 'extract', kdocs.url_dirs_tag)
    toolbox.extract_archive(temp_file, decompress_directory)
    file_list = []
    img_list = []
    for f_t in kdocs.docs_old_type:
        _, file_, _ = crazy_utils.get_files_from_everything(decompress_directory, type=f_t, ipaddr=ipaddr)
        file_list += file_
    for i_t in crazy_box.Utils().picture_format:
        _, file_, _ = crazy_utils.get_files_from_everything(decompress_directory, type=i_t, ipaddr=ipaddr)
        file_list += file_
    file_list += crazy_box.batch_recognition_images_to_md(img_list, ipaddr)
    return file_list, task_info, task_faillist


def get_kdocs_files(limit, project_folder, type, ipaddr):
    """
    Args:
        limit: 金山文档分享文件地址
        project_folder: 存储地址
        type: 指定的文件类型
        ipaddr: 用户信息
    Returns: [提取的文件list]
    """
    if type == 'otl':
        _, content, _, pic_dict, _ = get_docs_content(limit)
        name = 'temp.md'
        tag = content.splitlines()[0][:20]
        for i in pic_dict:  # 增加OCR选项
            img_content, img_result, _ = ocr_tools.Paddle_ocr_select(ipaddr=ipaddr, trust_value=True
                                                                  ).img_def_content(img_path=pic_dict[i], img_tag=i)
            content = str(content).replace(f"{i}", f"{func_box.html_local_img(img_result)}\n```{img_content}```")
            name = tag + '.md'
            content = content.encode('utf-8')
    elif type or type == '':
        kdocs = Kdocs(limit)
        link, name = kdocs.document_aggregation_download(file_type=type)
        tag = kdocs.url_share_tag
        if link:
            resp = requests.get(url=link, verify=False)
            content = resp.content
        else:
            return []
    else:
        return []
    if content:
        tag_path = os.path.join(project_folder, tag)
        temp_file = os.path.join(os.path.join(project_folder, tag, name))
        os.makedirs(tag_path, exist_ok=True)
        with open(temp_file, 'wb') as f: f.write(content)
        return [temp_file]


def get_kdocs_from_everything(txt, type='', ipaddr='temp'):
    """
    Args:
        txt: kudos 文件分享码
        type: type=='' 时，将支持所有文件类型
        ipaddr: 用户信息
    Returns:
    """
    link_limit = crazy_box.Utils().split_startswith_txt(link_limit=txt)
    file_manifest = []
    success = ''
    project_folder = os.path.join(func_box.users_path, ipaddr, 'kdocs')
    os.makedirs(project_folder, exist_ok=True)
    if link_limit:
        for limit in link_limit:
            if '/ent/' in limit:
                file_list, info, fail = get_kdocs_dir(limit, project_folder, type, ipaddr)
                file_manifest += file_list
                success += f"{limit}文件信息如下：{info}\n\n 下载任务状况：{fail}\n\n"
            else:
                file_manifest += get_kdocs_files(limit, project_folder, type, ipaddr)
    return success, file_manifest, project_folder


def smart_document_extraction(url, llm_kwargs, plugin_kwargs, chatbot, history, files):
    img_ocr, = crazy_box.json_args_return(plugin_kwargs, ['开启OCR'])
    ovs_data, content, empty_picture_count, pic_dict, kdocs_dict = get_docs_content(url, image_processing=img_ocr)
    if img_ocr:
        you_say = '请检查数据，并进行处理'
        if pic_dict:  # 当有图片文件时，再去提醒
            title = crazy_box.long_name_processing(content)
            ocr_process = f'检测到`{title}`文档中存在{func_box.html_tag_color(empty_picture_count)}张图片，为了产出结果不存在遗漏，正在逐一进行识别\n\n' \
                          f'> 红框为采用的文案,可信指数低于 {func_box.html_tag_color(llm_kwargs["ocr"])} 将不采用, 可在Setting 中进行配置\n\n'
            chatbot.append([you_say, ocr_process])
        else:
            ocr_process = ''
        if pic_dict:
            yield from toolbox.update_ui(chatbot, history, '正在调用OCR组件，已启用多线程解析，请稍等')
            ocr_func = ocr_tools.Paddle_ocr_select(ipaddr=llm_kwargs['ipaddr'],
                                                   trust_value=llm_kwargs['ocr']).identify_cache
            thread_submission = ocr_tools.submit_threads_ocr(pic_dict, func=ocr_func,
                                                             max_threads=llm_kwargs.get('worker_num', 5))
            for t in thread_submission:
                try:
                    img_content, img_result, error = thread_submission[t].result()
                    content = str(content).replace(f"{t}",
                                                   f"{func_box.html_local_img(img_result)}\n```{img_content}```")
                    if error:
                        ocr_process += f'`tips: {error}`'
                    ocr_process += f'{t} 识别完成，识别效果如下{func_box.html_local_img(img_result)}\n\n'
                    chatbot[-1] = [you_say, ocr_process]
                    yield from toolbox.update_ui(chatbot, history)
                except Exception:
                    ocr_process += f'{t} 识别失败，过滤这个图片\n\n'
                    chatbot[-1] = [you_say, ocr_process]
                    yield from toolbox.update_ui(chatbot, history)

    else:
        if empty_picture_count >= 5:
            chatbot.append(['请检查文档内容', f'\n\n 需求文档中没有{func_box.html_tag_color("描述")}的图片数量' \
                                              f'有{func_box.html_tag_color(empty_picture_count)}张，生成的测试用例可能存在遗漏点，'
                                              f'可以参考以下方法对图片进行描述补充，或在自定义插件参数中开始OCR功能\n\n' \
                                              f'{func_box.html_local_img("docs/imgs/pic_desc.png")}'])
        yield from toolbox.update_ui(chatbot, history)
    title = crazy_box.long_name_processing(content)
    temp_list = [title, content]
    temp_file = yield from crazy_box.result_written_to_markdwon(temp_list, llm_kwargs, plugin_kwargs, chatbot, history)
    files.extend(temp_file)
