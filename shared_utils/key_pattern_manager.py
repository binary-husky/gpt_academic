import re
import os
from functools import wraps, lru_cache
from shared_utils.advanced_markdown_format import format_io
from shared_utils.config_loader import get_conf as get_conf


pj = os.path.join
default_user_name = 'default_user'


def is_openai_api_key(key):
    CUSTOM_API_KEY_PATTERN = get_conf('CUSTOM_API_KEY_PATTERN')
    if len(CUSTOM_API_KEY_PATTERN) != 0:
        API_MATCH_ORIGINAL = re.match(CUSTOM_API_KEY_PATTERN, key)
    else:
        API_MATCH_ORIGINAL = re.match(r"sk-[a-zA-Z0-9]{48}$", key)
    return bool(API_MATCH_ORIGINAL)


def is_azure_api_key(key):
    API_MATCH_AZURE = re.match(r"[a-zA-Z0-9]{32}$", key)
    return bool(API_MATCH_AZURE)


def is_api2d_key(key):
    API_MATCH_API2D = re.match(r"fk[a-zA-Z0-9]{6}-[a-zA-Z0-9]{32}$", key)
    return bool(API_MATCH_API2D)


def is_any_api_key(key):
    if ',' in key:
        keys = key.split(',')
        for k in keys:
            if is_any_api_key(k): return True
        return False
    else:
        return is_openai_api_key(key) or is_api2d_key(key) or is_azure_api_key(key)


def what_keys(keys):
    avail_key_list = {'OpenAI Key': 0, "Azure Key": 0, "API2D Key": 0}
    key_list = keys.split(',')

    for k in key_list:
        if is_openai_api_key(k):
            avail_key_list['OpenAI Key'] += 1

    for k in key_list:
        if is_api2d_key(k):
            avail_key_list['API2D Key'] += 1

    for k in key_list:
        if is_azure_api_key(k):
            avail_key_list['Azure Key'] += 1

    return f"检测到： OpenAI Key {avail_key_list['OpenAI Key']} 个, Azure Key {avail_key_list['Azure Key']} 个, API2D Key {avail_key_list['API2D Key']} 个"


def select_api_key(keys, llm_model):
    import random
    avail_key_list = []
    key_list = keys.split(',')

    if llm_model.startswith('gpt-'):
        for k in key_list:
            if is_openai_api_key(k): avail_key_list.append(k)

    if llm_model.startswith('api2d-'):
        for k in key_list:
            if is_api2d_key(k): avail_key_list.append(k)

    if llm_model.startswith('azure-'):
        for k in key_list:
            if is_azure_api_key(k): avail_key_list.append(k)

    if len(avail_key_list) == 0:
        raise RuntimeError(f"您提供的api-key不满足要求，不包含任何可用于{llm_model}的api-key。您可能选择了错误的模型或请求源（右下角更换模型菜单中可切换openai,azure,claude,api2d等请求源）。")

    api_key = random.choice(avail_key_list) # 随机负载均衡
    return api_key
