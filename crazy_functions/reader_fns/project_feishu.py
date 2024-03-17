# encoding: utf-8
# @Time   : 2024/3/14
# @Author : Spike
# @Descr   :
import json
import os

import requests
from common.func_box import split_parse_url, to_markdown_tabs, handle_timestamp, is_within_days
from common.toolbox import get_conf
from pydantic import BaseModel
from typing import AnyStr, Literal

(ISSUE_REVERSE_MAPPING, STORY_REVERSE_MAPPING, CASE_REVERSE_MAPPING, STORY_LIST_REVERSE_MAPPING, PROJECT_USER_KEY,
 PROJECT_BASE_HOST, PROJECT_FEISHU_HEADER, WorkItems, STORY_LIST_FILTER_TIME) = get_conf(
    'ISSUE_REVERSE_MAPPING', 'STORY_REVERSE_MAPPING', 'CASE_REVERSE_MAPPING', 'STORY_LIST_REVERSE_MAPPING',
    'PROJECT_USER_KEY', 'PROJECT_BASE_HOST', 'PROJECT_FEISHU_HEADER', 'WorkItems', 'STORY_LIST_FILTER_TIME')

work_items = WorkItems()


class ProjectFeishu:

    def __init__(self, url, header=None):
        self.url = url
        self.base_url = f'https://{PROJECT_BASE_HOST}'
        self.headers = PROJECT_FEISHU_HEADER
        self.user_key = PROJECT_USER_KEY
        if header:
            self.headers = header
        self.project_id_map = self._get_project_dict()
        self.project_api_name = split_parse_url(url, None, 2)
        self.project_id = self.project_id_map.get(self.project_api_name, '')
        self.__name_key_type_init(self.project_id)

    def __name_key_type_init(self, project_id):
        if project_id:
            self.items_mapping = self._get_project_reverse_mapping(project_id)
            for story_name in work_items.story_name:
                if self.items_mapping.get(story_name):
                    self.story_api_name = self.items_mapping[story_name]['api_name']
                    self.story_type_key = self.items_mapping[story_name]['type_key']
                    self.story_id = split_parse_url(self.url, [self.story_api_name], 2)

            for issue_name in work_items.issue_name:
                if self.items_mapping.get(issue_name):
                    self.issue_api_name = self.items_mapping[issue_name]['api_name']
                    self.issue_type_key = self.items_mapping[issue_name]['type_key']
                    self.issue_id = split_parse_url(self.url, [self.issue_api_name], 2)

            for case_name in work_items.case_name:
                if self.items_mapping.get(case_name):
                    self.case_api_name = self.items_mapping[case_name]['api_name']
                    self.case_type_key = self.items_mapping[case_name]['type_key']
                    self.case_id = split_parse_url(self.url, [self.case_api_name], 2)

    def _get_project_dict(self):
        """获取所有项目"""
        json_data = {
            'page_size': 100, 'page_num': 1,
            'fuzzy_name': '', 'need_master': False, 'asset_group': False,
        }

        response = requests.post(
            f'{self.base_url}/goapi/v1/cross_project/project/list',
            headers=self.headers, json=json_data, verify=False
        )
        info_data = response.json()
        project_dict = {i['simple_name']: i['id'] for i in info_data['data']['value']}
        return project_dict

    def _get_item_group(self, item_name):
        json_data = {
            "type": "page_conf",
            "projectId": self.project_id,
            "realTypeKey": self.story_type_key,
            "LOCALE": "zh"
        }
        response = requests.post(self.base_url + '/new-bff/render_config', headers=self.headers,
                                 json=json_data, verify=False)
        config_dict = response.json()
        item_config = []
        if config_dict.get('page_conf_data'):
            config_data = config_dict['page_conf_data']['data']
            for data in config_data:
                for i in data['schema']:
                    if i.get('reform_data_scopes'):
                        for scopes in i['reform_data_scopes']:
                            for conditions in scopes['condition_group']['conditions']:
                                if conditions['fieldItem']['label'] in item_name:
                                    conditions.update({'value_list': [self.story_id]})  # "originalValue": []
                                    item_config.extend(scopes['condition_group']['conditions'])
                                    return item_config

    def _get_project_reverse_mapping(self, project_id=None):
        project_id = project_id if project_id else self.project_id
        url = f'{self.base_url}/goapi/v1/projects/{project_id}/work_item_types'
        response = requests.get(url, headers=self.headers, verify=False)
        work_item_types = response.json()
        reveres_mapping = []
        feature_reveres_mapping = [reveres_mapping.extend(i) for i in list(work_items.dict().values())]
        if work_item_types.get('data') and work_item_types.get('statusCode', 0) != 403:
            mapping = {i['name']: {"type_key": i['type_key'], "api_name": i['api_name']}
                       for i in work_item_types['data'] if i['name'] in reveres_mapping}
            return mapping
        else:
            return {}

    def post_homepage_render_data(self, project_id=None, tab_key: Literal['all', 'participated'] = 'participated'):
        """获取首页数据"""
        url = f'{self.base_url}/new-bff/homepage_render_data'
        body = {
            "localData": {},
            "userName": self.user_key,
            "projectInfo": {
                "_id": project_id if project_id else self.project_id,
                "roles": []
            },
            "realTypeKey": self.story_type_key,
            "LOCALE": "zh",
            "activeTabKey": tab_key,
            "isInGreyRecentlyUsed": True
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(body), verify=False)
        return response.json()

    def get_home_story_list(self, filter_time: int | bool = False, unscheduled=''):
        """获取所有项目首页需求列表"""
        story_list = []
        for api_name in self.project_id_map:
            self.__name_key_type_init(self.project_id_map[api_name])
            if self.__dict__.get('issue_type_key'):
                story_mapping = self._get_key_reverse_mapping(self.story_type_key,
                                                              STORY_LIST_REVERSE_MAPPING, self.project_id_map[api_name])
                home_data = self.post_homepage_render_data(self.project_id_map[api_name])
                time_ids = [i for i in story_mapping if story_mapping[i]['name'] in STORY_LIST_FILTER_TIME]
                if home_data and story_mapping:
                    for item in home_data['homepage_work_items']['data']['work_items']:
                        node_info = self._owner_times_extraction(item, time_ids, unscheduled)
                        node_in_times = any(
                            [is_within_days(i['times'][t], filter_time) for i in node_info for t in i['times']])
                        if not filter_time or node_in_times:
                            work_item = {'项目链接': f"{self.base_url}/{api_name}/"
                                                     f"{self.story_api_name}/detail/{item['story_id']}"}
                            work_item.update(self._data_mapping_extraction(item, story_mapping))
                            work_item.update({'我负责的需求节点': "-".join(i['state_name'] for i in node_info)})
                            story_list.append(work_item)
        return story_list

    def _get_key_reverse_mapping(self, key, mapping, project_id=None):
        """获取字段映射key-value"""
        project_id = project_id if project_id else self.project_id
        url = f'{self.base_url}/goapi/v3/settings/{project_id}/{key}/fields'
        response = requests.get(url, headers=self.headers, verify=False)
        issue_fields = response.json()
        fields_map_dict = {}
        for i in issue_fields['data']:
            if i['name'] in mapping:
                fields_map_dict[i['key']] = {'name': i['name']}
                if i.get('select_options'):  # 处理枚举字段
                    fields_map_dict[i['key']].update(
                        {"enum_map": {j['value']: j['label'] for j in i['select_options']}})
                elif i.get('compound_fields'):  # 处理复合字段
                    fields_map_dict[i['key']].update(
                        {"compound_map": {j['key']: j['name'] for j in i['compound_fields']}})
        # 排个序
        fields_map_sort = {k: fields_map_dict[k] for i in mapping
                           for k in fields_map_dict if fields_map_dict[k]['name'] == i}
        return fields_map_sort

    def query_prams(self, key, item_name):
        item_group_list = self._get_item_group(item_name)
        query = {
            "condition_group": {"conjunction": "AND", "groups": [
                {"conjunction": "AND", "conditions": [],
                 "groups": [{"conjunction": "OR", "conditions": [], "groups": [
                     {"conjunction": "AND", "conditions": item_group_list, "groups": []}]}]}]},
            "data_source": [{"project_key": self.project_id, "work_item_type_key": key}],
            "pagination": {}, "is_instant_query": False, "find_aborted": False,
            "need_check_dirty_fields": True,
            "allow_truncate": True, "user_key": self.user_key}
        data = {"QueryString": json.dumps(query)}

        return data

    def _get_work_list(self, key, item_name):
        """获取项目下的所有"""
        data = self.query_prams(key, item_name)
        response = requests.post(f'{self.base_url}/goapi/v4/search/group_info', verify=False,
                                 headers=self.headers, json=data)
        items_id_list = []
        issue_result = response.json()
        if issue_result['data']['list']:
            if issue_result['data']['list']:
                for i in issue_result['data']['list']:
                    items_id_list.extend([i['work_item_id'] for i in i['work_items']])
        return items_id_list

    def post_story_items(self):
        """获取项目下的需求详情"""
        url = f'{self.base_url}/goapi/v2/projects/{self.project_id}/work_item/story/{self.story_id}'
        response = requests.get(url, headers=self.headers, verify=False)
        return response.json()

    @staticmethod
    def _data_mapping_extraction(type_items, fields_map_dict):
        data_dict = {}
        for key in fields_map_dict:  # 自定义详情
            if type_items.get(key):
                map_key = fields_map_dict[key]['name']
                data_dict[map_key] = ''
                if isinstance(type_items.get(key), dict):
                    if type_items[key].get('doc_img', []):
                        data_dict[map_key] = "\n".join(
                            [f"![{i.split('?')[-1]}]({i})" for i in type_items[key].get('doc_img', [])]) + '\n'
                    data_dict[map_key] += type_items[key].get('doc_text', '')
                elif isinstance(type_items[key], list) and fields_map_dict[key].get('enum_map'):
                    data_dict[map_key] = "".join([fields_map_dict[key]['enum_map'][i] for i in type_items[key]])
                elif isinstance(type_items[key], list):
                    data_dict[map_key] = "".join([str(i) for i in type_items[key]])  # 确保是字符串
                elif fields_map_dict[key].get('compound_map'):  # 复合字段处理
                    for i, v in enumerate(type_items[key]):
                        content = ''
                        for t in v:
                            content += fields_map_dict[key]['compound_map'][t['field_key']] + f': ' + \
                                       t["value"]["doc_text"] + '\n'
                        index = "-" + str(i) if i > 0 else ''
                        data_dict[fields_map_dict[key]['name'] + index] = content
                else:
                    data_dict[map_key] = type_items[key]
                if isinstance(data_dict.get(map_key, ''), str):  # 如果是字符串，那么去掉前后空格
                    data_dict[map_key] = data_dict[map_key].strip()
                elif isinstance(data_dict[map_key], int):  # 如果是数字，那么那么尝试转换为时间字符串
                    data_dict[map_key] = handle_timestamp(data_dict[map_key])
        return data_dict

    def _owner_times_extraction(self, story_items, filter_time_ids: list, unscheduled=''):
        node_owner_info = []
        for i in story_items['node_schedules']:  # 节点详情
            user_names = [user['username'] for user in i['owner_in_charge']]
            if self.user_key in user_names:
                times = {
                    'start_time': i['estimate_start_time'],
                    'end_time': i['estimate_end_time'] if i['estimate_end_time'] else unscheduled,
                }
                for ids in filter_time_ids:
                    times.update({ids: i.get(ids, None)})
                node_owner_info.append({
                    'state_name': i['state_name'], 'owner': i['owner_in_charge'], 'times': times
                })
        return node_owner_info

    @staticmethod
    def _node_schedules_extraction(story_items):
        node_dict = {'当前需求节点': "-".join([i['name'] for i in story_items['state_times'] if not i['end']])}
        all_state_status = ''
        sum_actual_times = 0
        sum_points_times = 0
        for i in story_items['node_schedules']:  # 节点详情
            state_name = i['state_name'] + ':'
            #  state_name += '' if i['state_id'] == 'started' else '' 拿不准这个状态，暂时不做
            subtasks = " -> ".join(
                [f"【{t['name']}】-{t['schedules'][0]['points']}/人天" for t in i['subtasks'] if t['schedules']])
            if i['points']:
                node_points_time = i['points'] if i['points'] else 0
                sum_points_times += node_points_time
                node_actual_time = i['actual_work_time'] if i['actual_work_time'] else 0
                sum_actual_times += node_actual_time
                schedules_times = '\n节点预估工时: ' + str(node_points_time) + '/人天' if node_points_time else ''
                schedules_times += '\t节点实消工时: ' + str(node_actual_time) + "/人天" if node_actual_time else ''
            else:
                schedules_times = f"\n节点截止时间: {handle_timestamp(i['estimate_end_time'])}" if i[
                    'estimate_end_time'] else ''
            subtasks = "\n节点任务详情: " + subtasks if subtasks else ''
            all_state_status += f"{state_name} {subtasks}{schedules_times}\n"
        node_dict.update({'所有需求节点任务及耗时': all_state_status})
        node_dict.update({'需求预计总工时': str(sum_points_times) + '/人天'})
        node_dict.update({'当前所耗总工时': str(sum_actual_times) + '/人天'})
        return node_dict

    def get_story_items_dict(self):
        """获取需求详情"""
        fields_map_dict = self._get_key_reverse_mapping(self.story_type_key, STORY_REVERSE_MAPPING)
        story_items = self.post_story_items().get('data', {})
        story_dict = self._data_mapping_extraction(story_items, fields_map_dict)
        node_dict = self._node_schedules_extraction(story_items)
        story_dict.update(node_dict)
        return story_dict

    def post_work_items(self, key, item_name, ids: list = None):
        """获取项目下的缺陷详情"""
        url = f'{self.base_url}/goapi/v4/search/work_items_by_id'
        body = {
            "data_source": [
                {
                    "project_key": self.project_id,
                    "work_item_type_key": key
                }
            ],
            "ids": ids if ids else [self.issue_id]
        }
        if not ids or not self.issue_id:
            body['ids'] = self._get_work_list(key, item_name)
        response = requests.post(url, headers=self.headers, data=json.dumps(body), verify=False)
        return response.json()

    def _mapping_extraction(self, type_items, fields_map_dict):
        items_list = []
        if type_items['data']['work_items']:
            for items in type_items['data']['work_items']:
                items_dict = self._data_mapping_extraction(items, fields_map_dict)
                if items_dict and items_dict not in items_list:
                    items_list.append(items_dict)
        return items_list

    def get_issue_items_list(self, ids: list = None):
        """获取缺陷列表"""
        issue_items = self.post_work_items(key=self.issue_type_key, item_name=work_items.issue_item_name, ids=ids)
        fields_map_dict = self._get_key_reverse_mapping(self.issue_type_key, ISSUE_REVERSE_MAPPING)
        issue_list = self._mapping_extraction(issue_items, fields_map_dict)
        return issue_list

    def get_case_items_list(self, ids: list = None):
        """获取用例列表"""
        issue_items = self.post_work_items(key=self.issue_type_key, item_name=work_items.case_item_name, ids=ids)
        fields_map_dict = self._get_key_reverse_mapping(self.case_type_key, CASE_REVERSE_MAPPING)
        case_list = self._mapping_extraction(issue_items, fields_map_dict)
        return case_list


def __get_story(story_result):
    markdown_project = '## 需求详情\n'
    for i in story_result:
        markdown_project += f'{i}: {story_result[i]}\n\n'
    return markdown_project


def __get_item_list(issue_result):
    head = []
    tab_list = []
    for i in issue_result:
        head = list(i.keys()) if len(head) < len(i.keys()) else head
        tab_list.append(list(i.values()))
    markdown_project = to_markdown_tabs(head=head, tabs=tab_list, column=True)
    return markdown_project


def converter_project_md(link, project_folder, header=None):
    feishu_project = ProjectFeishu(link, header)
    markdown_project = ''
    if feishu_project.story_id:
        markdown_project += __get_story(feishu_project.get_story_items_dict()) + '\n'

        issue_content = __get_item_list(feishu_project.get_issue_items_list())
        markdown_project += '### 缺陷详情\n' + issue_content if issue_content else '' + '\n'

        issue_content = __get_item_list(feishu_project.get_case_items_list())
        markdown_project += '### 用例详情\n' + issue_content if issue_content else '' + '\n'

    elif feishu_project.issue_id:
        issue_content = __get_item_list(feishu_project.get_issue_items_list([feishu_project.issue_id]))
        markdown_project += '### 缺陷详情\n' + issue_content if issue_content else '' + '\n'

    elif feishu_project.case_id:
        issue_content = __get_item_list(feishu_project.get_issue_items_list([feishu_project.case_id]))
        markdown_project += '### 用例详情\n' + issue_content if issue_content else '' + '\n'

    file_name = feishu_project.story_id if feishu_project.story_id else feishu_project.issue_id
    with open(os.path.join(project_folder, f'{file_name}.md'), 'w', encoding='utf-8') as f:
        f.write(markdown_project)
    return {os.path.join(project_folder, f'{file_name}.md'): link}


def get_project_from_limit(link_limit, project_folder, header=None):
    success = ''
    file_mapping = {}
    project_folder = os.path.join(project_folder, 'project_feishu')
    os.makedirs(project_folder, exist_ok=True)
    for limit in link_limit:
        file_mapping.update(converter_project_md(limit, project_folder, header))
    return success, file_mapping


if __name__ == '__main__':
    # converter_project_md('https://project.feishu.cn/middleoffice/story/detail/3014376768#issue_management_new', './')
    feishu = ProjectFeishu('')
    # print(feishu._get_work_list(feishu.items_mapping[work_items.case_name]['type_key']))
    # print(feishu.get_story_items_dict())
    feishu.get_home_story_list(7)
