import re
mapping_dic = {
    # "qianfan": "qianfan（文心一言大模型）",
    # "zhipuai": "zhipuai（智谱GLM4超级模型🔥）",
    # "gpt-4-1106-preview": "gpt-4-1106-preview（新调优版本GPT-4🔥）",
    # "gpt-4-vision-preview": "gpt-4-vision-preview（识图模型GPT-4V）",
}

rev_mapping_dic = {}
for k, v in mapping_dic.items():
    rev_mapping_dic[v] = k

def map_model_to_friendly_names(m):
    if m in mapping_dic:
        return mapping_dic[m]
    return m

def map_friendly_names_to_model(m):
    if m in rev_mapping_dic:
        return rev_mapping_dic[m]
    return m

def read_one_api_model_name(model: str):
    """return real model name and max_token.
    """
    max_token_pattern = r"\(max_token=(\d+)\)"
    match = re.search(max_token_pattern, model)
    if match:
        max_token_tmp = match.group(1)  # 获取 max_token 的值
        max_token_tmp = int(max_token_tmp)
        model = re.sub(max_token_pattern, "", model)  # 从原字符串中删除 "(max_token=...)"
    else:
        max_token_tmp = 4096
    return model, max_token_tmp