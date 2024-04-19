# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from typing import Dict, List, AnyStr

import requests
from common import gr_converter_html


def get_gpts():
    response = requests.get('https://gpts.ddaiai.com/open/gpts', verify=False)

    return response.json()


def search_gpts(query):
    params = {
        'q': query,
    }
    response = requests.get('https://gpts.ddaiai.com/open/gptsapi/search', params=params)
    return response.json()


def gpts_groups_samples(gpts: List[Dict]) -> List:
    group_htmls = []
    for i in gpts:
        info = i['info'][:25] + '...' if len(i['info']) > 25 else i['info']
        html = gr_converter_html.get_html('gpts_group.html').format(
            logo=i['logo'], title=i['name'], desc=i['info'], hide_desc=info,
            like=i['use_cnt'], bed=i['bad']
        )
        group_htmls.append([html, i])

    return group_htmls


if __name__ == '__main__':
    get_gpts()
