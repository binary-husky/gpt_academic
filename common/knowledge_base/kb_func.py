# encoding: utf-8
# @Time   : 2024/3/4
# @Author : Spike
# @Descr   :
import copy
import json
import re
from typing import Tuple, Any

from common.func_box import replace_expected_text
from common import gr_converter_html
from common.toolbox import update_ui, get_conf
from common.knowledge_base import kb_doc_api
from common.knowledge_base.kb_service import base
from common.db.repository import prompt_repository
from request_llms.bridge_all import model_info


def llm_accelerate_init(llm_kwargs):
    select_llm = llm_kwargs['llm_model']
    response = 'text'
    if select_llm.startswith('gpt-'):
        llm_35_1106 = 'gpt-3.5-turbo-1106'
        avail_llm_models = get_conf('AVAIL_LLM_MODELS')
        if llm_35_1106 not in avail_llm_models:
            select_llm = llm_kwargs['llm_model']
        else:
            select_llm = llm_35_1106
            response = 'json_object'
    return select_llm, response


def get_kb_key_value(kb_names: list):
    kb_kv = []
    for kb_name in kb_names:
        kb_kv.append({'kb_name': kb_name, 'kb_info': base.get_kb_details_by_name(kb_name)['kb_info']})
    return kb_kv


def user_intent_recognition(user_input, history, llm_kwargs) -> tuple[bool, Any] | bool | Any:
    kb_names = llm_kwargs['kb_config']['names']
    llm, response_format = llm_accelerate_init(llm_kwargs)
    ipaddr = llm_kwargs['ipaddr']
    prompt = prompt_repository.query_prompt('意图识别', '知识库提示词', ipaddr, quote_num=True)
    if prompt:
        prompt = prompt.value
    else:
        raise ValueError('没有找到提示词')
    spilt_text = user_input
    if len(user_input) > 200:
        spilt_text = user_input[:100] + user_input[-100:]
    intent_user = replace_expected_text(prompt, spilt_text, '{{{v}}}')
    kb_files = str(get_kb_key_value(kb_names))
    intent_user = replace_expected_text(intent_user, kb_files, '{{{kb}}}')
    cp_llm = copy.deepcopy(llm_kwargs)
    cp_llm.update({'llm_model': llm, 'response_format': response_format})
    response = model_info[llm]['fn_without_ui'](intent_user, cp_llm, history, '', [])
    json_search = re.search(r'\{.*}', response, flags=re.DOTALL)
    if json_search:
        response_dict = json.loads(json_search.group())
        if response_dict.get('func') == 'Chat':
            return response_dict, intent_user
        return response_dict, intent_user
    else:
        return {}, intent_user


def get_vector_to_dict(vector_list):
    data = {}
    for i in vector_list:
        key_work = str(i.score)[:4]+i.metadata['source']
        if not data.get(key_work, False):
            data[key_work] = ''
        try:
            data[key_work] += f"{i.page_content}\n"
        except TypeError:
            pass
    return data


def vector_recall_by_input(user_input, chatbot, history, llm_kwargs, kb_prompt_cls, kb_prompt_name):
    vector_fold_format = gr_converter_html.get_fold_panel()
    vector_content = ''
    chatbot.append([user_input, vector_fold_format(title='意图识别中', content='...', status='')])
    yield from update_ui(chatbot, history)
    user_intent, prompt = user_intent_recognition(user_input, history, llm_kwargs)
    if user_intent.get('kb', {}):
        vector_content += f"意图识别：{user_intent}"
        chatbot[-1][1] = vector_fold_format(title='意图识别成功，准备进行对向量数据库进行召回', content=vector_content,
                                            status='')
        yield from update_ui(chatbot, history)
        source_data = {}
        for intent_kb in user_intent.get('kb', {}):
            chatbot[-1][1] = vector_fold_format(title='向量召回中', content=vector_content, status='')
            yield from update_ui(chatbot, history)
            vector_list = kb_doc_api.search_docs(user_input, knowledge_base_name=intent_kb,
                                                 top_k=llm_kwargs['kb_config']['top-k'],
                                                 score_threshold=llm_kwargs['kb_config']['score'])
            data = get_vector_to_dict(vector_list)
            source_data.update(data)
            vector_content += f"\n向量召回：{json.dumps(data, indent=4, ensure_ascii=False)}"
        if not source_data:
            vector_content += '无数据，转发到普通对话'
            return user_input, history
        chatbot[-1][1] = vector_fold_format(title='向量召回完成', content=vector_content, status='Done')
        yield from update_ui(chatbot, history)
        repeat_recall = ''
        source_text = ''
        for data in source_data:
            if any([i for i in history if data in i]):
                repeat_recall += f'过滤重复召回片段: {data}\n'
            else:
                source_text += f"## {data}\n{source_data[data]}"
        if '专注力转移' in llm_kwargs['input_models'] and source_text:
            title = '向量召回完成, 当前模式为专注力转移，不采用提示词'
            user_show = user_input[:20] + "..." + user_input[-20:] + '\n找到以上文本相关文档片段'
            history = history + [f'{user_show}', source_text]
        elif source_text:
            title = f'向量召回完成, 当前模式专注模式，使用`{kb_prompt_name}`提示词进行对话'
            prompt = prompt_repository.query_prompt(kb_prompt_name, kb_prompt_cls, llm_kwargs['ipaddr'], quote_num=True)
            if prompt:
                prompt = prompt.value
            kb_prompt = replace_expected_text(prompt, source_text, '{{{v}}}')
            user_input = replace_expected_text(kb_prompt, user_input, '{{{q}}}')
        else:
            chatbot[-1][1] = vector_fold_format(title='检测召回完全相同文档，转发到普通对话',
                                                content=repeat_recall,
                                                status='Done')
            return user_input, history
        chatbot[-1][1] = vector_fold_format(title=title,
                                            content=f"# 可用文档片段\n{source_text}\n"
                                                    f"# 重复文档片段\n{repeat_recall}",
                                            status='Done')
        return user_input, history
    chatbot[-1][1] = vector_fold_format(title='无法找到可用知识库, 转发到普通对话',
                                        content=str(user_intent) + f"\nprompt: \n{prompt}",
                                        status='Done')
    yield from update_ui(chatbot, history)
    return user_input, history


if __name__ == '__main__':
    user_intent_recognition('test', {'kb_config': {'names': ['124124'], 'top_k': 5, 'score': 0.5},
                                     'llm_model': 'gpt-3.5-turbo-1106',
                                     'api_key': ''})
