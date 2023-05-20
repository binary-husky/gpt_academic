"""
    Translate this project to other languages
    Usage:o
    1. modify LANG
        LANG = "English"

    2. modify TransPrompt
        TransPrompt = f"Replace each json value `#` with translated results in English, e.g., \"原始文本\":\"TranslatedText\". Keep Json format. Do not answer #."

    3. Run `python multi_language.py`. 
        Note: You need to run it multiple times to increase translation coverage because GPT makes mistakes sometimes.

    4. Find translated program in `multi-language\English\*`
    
"""

import os
import json
import functools
import re
import pickle
import time

CACHE_FOLDER = "gpt_log"
blacklist = ['multi-language', 'gpt_log', '.git', 'private_upload', 'multi_language.py']

# LANG = "TraditionalChinese"
# TransPrompt = f"Replace each json value `#` with translated results in Traditional Chinese, e.g., \"原始文本\":\"翻譯後文字\". Keep Json format. Do not answer #."

# LANG = "Japanese"
# TransPrompt = f"Replace each json value `#` with translated results in Japanese, e.g., \"原始文本\":\"テキストの翻訳\". Keep Json format. Do not answer #."

LANG = "English"
TransPrompt = f"Replace each json value `#` with translated results in English, e.g., \"原始文本\":\"TranslatedText\". Keep Json format. Do not answer #."


if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)


def lru_file_cache(maxsize=128, ttl=None, filename=None):
    """
    Decorator that caches a function's return value after being called with given arguments. 
    It uses a Least Recently Used (LRU) cache strategy to limit the size of the cache.
    maxsize: Maximum size of the cache. Defaults to 128.
    ttl: Time-to-Live of the cache. If a value hasn't been accessed for `ttl` seconds, it will be evicted from the cache.
    filename: Name of the file to store the cache in. If not supplied, the function name + ".cache" will be used.
    """
    cache_path = os.path.join(CACHE_FOLDER, f"{filename}.cache") if filename is not None else None

    def decorator_function(func):
        cache = {}
        _cache_info = {
            "hits": 0,
            "misses": 0,
            "maxsize": maxsize,
            "currsize": 0,
            "ttl": ttl,
            "filename": cache_path,
        }

        @functools.wraps(func)
        def wrapper_function(*args, **kwargs):
            key = str((args, frozenset(kwargs)))
            if key in cache:
                if _cache_info["ttl"] is None or (cache[key][1] + _cache_info["ttl"]) >= time.time():
                    _cache_info["hits"] += 1
                    print(f'Warning, reading cache, last read {(time.time()-cache[key][1])//60} minutes ago'); time.sleep(2)
                    cache[key][1] = time.time()
                    return cache[key][0]
                else:
                    del cache[key]

            result = func(*args, **kwargs)
            cache[key] = [result, time.time()]
            _cache_info["misses"] += 1
            _cache_info["currsize"] += 1

            if _cache_info["currsize"] > _cache_info["maxsize"]:
                oldest_key = None
                for k in cache:
                    if oldest_key is None:
                        oldest_key = k
                    elif cache[k][1] < cache[oldest_key][1]:
                        oldest_key = k
                del cache[oldest_key]
                _cache_info["currsize"] -= 1

            if cache_path is not None:
                with open(cache_path, "wb") as f:
                    pickle.dump(cache, f)

            return result

        def cache_info():
            return _cache_info

        wrapper_function.cache_info = cache_info

        if cache_path is not None and os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                cache = pickle.load(f)
            _cache_info["currsize"] = len(cache)

        return wrapper_function

    return decorator_function

def contains_chinese(string):
    """
    Returns True if the given string contains Chinese characters, False otherwise.
    """
    chinese_regex = re.compile(u'[\u4e00-\u9fff]+')
    return chinese_regex.search(string) is not None

def split_list(lst, n_each_req):
    """
    Split a list into smaller lists, each with a maximum number of elements.
    :param lst: the list to split
    :param n_each_req: the maximum number of elements in each sub-list
    :return: a list of sub-lists
    """
    result = []
    for i in range(0, len(lst), n_each_req):
        result.append(lst[i:i + n_each_req])
    return result

def map_to_json(map, language):
    dict_ = read_map_from_json(language)
    dict_.update(map)
    with open(f'docs/translate_{language.lower()}.json', 'w', encoding='utf8') as f:
        json.dump(dict_, f, indent=4, ensure_ascii=False)

def read_map_from_json(language):
    if os.path.exists(f'docs/translate_{language.lower()}.json'):
        with open(f'docs/translate_{language.lower()}.json', 'r', encoding='utf8') as f: 
            res = json.load(f)
            res = {k:v for k, v in res.items() if v is not None and contains_chinese(k)}
            return res
    return {}

def advanced_split(splitted_string, spliter, include_spliter=False):
    splitted_string_tmp = []
    for string_ in splitted_string:
        if spliter in string_:
            splitted = string_.split(spliter)
            for i, s in enumerate(splitted):
                if include_spliter:
                    if i != len(splitted)-1:
                        splitted[i] += spliter
                splitted[i] = splitted[i].strip()
            for i in reversed(range(len(splitted))):
                if not contains_chinese(splitted[i]): 
                    splitted.pop(i)
            splitted_string_tmp.extend(splitted)
        else:
            splitted_string_tmp.append(string_)
    splitted_string = splitted_string_tmp
    return splitted_string_tmp

cached_translation = {}
cached_translation = read_map_from_json(language=LANG)

def trans(word_to_translate, language, special=False):
    if len(word_to_translate) == 0: return {}
    from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from toolbox import get_conf, ChatBotWithCookies
    proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY = \
        get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT', 'API_KEY')
    llm_kwargs = {
        'api_key': API_KEY,
        'llm_model': LLM_MODEL,
        'top_p':1.0, 
        'max_length': None,
        'temperature':0.4,
    }
    import random
    N_EACH_REQ = random.randint(16, 32)
    word_to_translate_split = split_list(word_to_translate, N_EACH_REQ)
    inputs_array = [str(s) for s in word_to_translate_split]
    inputs_show_user_array = inputs_array
    history_array = [[] for _ in inputs_array]
    if special: #  to English using CamelCase Naming Convention
        sys_prompt_array = [f"Translate following names to English with CamelCase naming convention. Keep original format" for _ in inputs_array]
    else:
        sys_prompt_array = [f"Translate following sentences to {LANG}. E.g., You should translate sentences to the following format ['translation of sentence 1', 'translation of sentence 2']. Do NOT answer with Chinese!" for _ in inputs_array]
    chatbot = ChatBotWithCookies(llm_kwargs)
    gpt_say_generator = request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array, 
        inputs_show_user_array, 
        llm_kwargs, 
        chatbot, 
        history_array, 
        sys_prompt_array, 
    )
    while True:
        try:
            gpt_say = next(gpt_say_generator)
            print(gpt_say[1][0][1])
        except StopIteration as e:
            result = e.value
            break
    translated_result = {}
    for i, r in enumerate(result):
        if i%2 == 1:
            try:
                res_before_trans = eval(result[i-1])
                res_after_trans = eval(result[i])
                if len(res_before_trans) != len(res_after_trans): 
                    raise RuntimeError
                for a,b in zip(res_before_trans, res_after_trans):
                    translated_result[a] = b
            except:
                # try:
                    # res_before_trans = word_to_translate_split[(i-1)//2]
                    # res_after_trans = [s for s in result[i].split("', '")]
                #     for a,b in zip(res_before_trans, res_after_trans):
                #         translated_result[a] = b
                # except:
                print('GPT输出格式错误，稍后可能需要再试一次')
                res_before_trans = eval(result[i-1])
                for a in res_before_trans:
                    translated_result[a] = None
    return translated_result


def trans_json(word_to_translate, language, special=False):
    if len(word_to_translate) == 0: return {}
    from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from toolbox import get_conf, ChatBotWithCookies
    proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY = \
        get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT', 'API_KEY')
    llm_kwargs = {
        'api_key': API_KEY,
        'llm_model': LLM_MODEL,
        'top_p':1.0, 
        'max_length': None,
        'temperature':0.1,
    }
    import random
    N_EACH_REQ = random.randint(16, 32)
    random.shuffle(word_to_translate)
    word_to_translate_split = split_list(word_to_translate, N_EACH_REQ)
    inputs_array = [{k:"#" for k in s} for s in word_to_translate_split]
    inputs_array = [ json.dumps(i, ensure_ascii=False)  for i in inputs_array]
    
    inputs_show_user_array = inputs_array
    history_array = [[] for _ in inputs_array]
    sys_prompt_array = [TransPrompt for _ in inputs_array]
    chatbot = ChatBotWithCookies(llm_kwargs)
    gpt_say_generator = request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array, 
        inputs_show_user_array, 
        llm_kwargs, 
        chatbot, 
        history_array, 
        sys_prompt_array, 
    )
    while True:
        try:
            gpt_say = next(gpt_say_generator)
            print(gpt_say[1][0][1])
        except StopIteration as e:
            result = e.value
            break
    translated_result = {}
    for i, r in enumerate(result):
        if i%2 == 1:
            try:
                translated_result.update(json.loads(result[i]))
            except:
                print(result[i])
    print(result)
    return translated_result


def step_1_core_key_translate():
    def extract_chinese_characters(file_path):
        syntax = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            import ast
            root = ast.parse(content)
            for node in ast.walk(root):
                if isinstance(node, ast.Name):
                    if contains_chinese(node.id): syntax.append(node.id)
                if isinstance(node, ast.Import):
                    for n in node.names:
                        if contains_chinese(n.name): syntax.append(n.name)
                elif isinstance(node, ast.ImportFrom):
                    for n in node.names:
                        if contains_chinese(n.name): syntax.append(n.name)
                        for k in node.module.split('.'):
                            if contains_chinese(k): syntax.append(k)
            return syntax

    def extract_chinese_characters_from_directory(directory_path):
        chinese_characters = []
        for root, dirs, files in os.walk(directory_path):
            if any([b in root for b in blacklist]):
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    chinese_characters.extend(extract_chinese_characters(file_path))
        return chinese_characters

    directory_path = './'
    chinese_core_names = extract_chinese_characters_from_directory(directory_path)
    chinese_core_keys = [name for name in chinese_core_names]
    chinese_core_keys_norepeat = []
    for d in chinese_core_keys:
        if d not in chinese_core_keys_norepeat: chinese_core_keys_norepeat.append(d)
    need_translate = []
    cached_translation = read_map_from_json(language=LANG)
    cached_translation_keys = list(cached_translation.keys())
    for d in chinese_core_keys_norepeat:
        if d not in cached_translation_keys: 
            need_translate.append(d)

    need_translate_mapping = trans(need_translate, language=LANG, special=True)
    map_to_json(need_translate_mapping, language=LANG)
    cached_translation = read_map_from_json(language=LANG)
    cached_translation = dict(sorted(cached_translation.items(), key=lambda x: -len(x[0])))

    chinese_core_keys_norepeat_mapping = {}
    for k in chinese_core_keys_norepeat:
        chinese_core_keys_norepeat_mapping.update({k:cached_translation[k]})
    chinese_core_keys_norepeat_mapping = dict(sorted(chinese_core_keys_norepeat_mapping.items(), key=lambda x: -len(x[0])))

    # ===============================================
    # copy
    # ===============================================
    def copy_source_code():

        from toolbox import get_conf
        import shutil
        import os
        try: shutil.rmtree(f'./multi-language/{LANG}/')
        except: pass
        os.makedirs(f'./multi-language', exist_ok=True)
        backup_dir = f'./multi-language/{LANG}/'
        shutil.copytree('./', backup_dir, ignore=lambda x, y: blacklist)
    copy_source_code()

    # ===============================================
    # primary key replace
    # ===============================================
    directory_path = f'./multi-language/{LANG}/'
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                syntax = []
                # read again
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for k, v in chinese_core_keys_norepeat_mapping.items():
                    content = content.replace(k, v)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)


def step_2_core_key_translate():

    # =================================================================================================
    # step2 
    # =================================================================================================

    def load_string(strings, string_input):
        string_ = string_input.strip().strip(',').strip().strip('.').strip()
        if string_.startswith('[Local Message]'):
            string_ = string_.replace('[Local Message]', '')
            string_ = string_.strip().strip(',').strip().strip('.').strip()
        splitted_string = [string_]
        # --------------------------------------
        splitted_string = advanced_split(splitted_string, spliter="，", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="。", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="）", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="（", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="(", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter=")", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="<", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter=">", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="[", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="]", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="【", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="】", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="？", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="：", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter=":", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter=",", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="#", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="\n", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter=";", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="`", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="   ", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="- ", include_spliter=False)
        splitted_string = advanced_split(splitted_string, spliter="---", include_spliter=False)
        
        # --------------------------------------
        for j, s in enumerate(splitted_string): # .com
            if '.com' in s: continue
            if '\'' in s: continue
            if '\"' in s: continue
            strings.append([s,0])


    def get_strings(node):
        strings = []
        # recursively traverse the AST
        for child in ast.iter_child_nodes(node):
            node = child
            if isinstance(child, ast.Str):
                if contains_chinese(child.s):
                    load_string(strings=strings, string_input=child.s)
            elif isinstance(child, ast.AST):
                strings.extend(get_strings(child))
        return strings

    string_literals = []
    directory_path = f'./multi-language/{LANG}/'
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                syntax = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # comments
                    comments_arr = []
                    for code_sp in content.splitlines():
                        comments = re.findall(r'#.*$', code_sp)
                        for comment in comments: 
                            load_string(strings=comments_arr, string_input=comment)
                    string_literals.extend(comments_arr)

                    # strings
                    import ast
                    tree = ast.parse(content)
                    res = get_strings(tree, )
                    string_literals.extend(res)

    [print(s) for s in string_literals]
    chinese_literal_names = []
    chinese_literal_names_norepeat = []
    for string, offset in string_literals:
        chinese_literal_names.append(string)
    chinese_literal_names_norepeat = []
    for d in chinese_literal_names:
        if d not in chinese_literal_names_norepeat: chinese_literal_names_norepeat.append(d)
    need_translate = []
    cached_translation = read_map_from_json(language=LANG)
    cached_translation_keys = list(cached_translation.keys())
    for d in chinese_literal_names_norepeat:
        if d not in cached_translation_keys: 
            need_translate.append(d)


    up = trans_json(need_translate, language=LANG, special=False)
    map_to_json(up, language=LANG)
    cached_translation = read_map_from_json(language=LANG)
    cached_translation = dict(sorted(cached_translation.items(), key=lambda x: -len(x[0])))

    # ===============================================
    # literal key replace
    # ===============================================
    directory_path = f'./multi-language/{LANG}/'
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                syntax = []
                # read again
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for k, v in cached_translation.items():
                    if v is None: continue
                    if '"' in v: 
                        v = v.replace('"', "`")
                    if '\'' in v: 
                        v = v.replace('\'', "`")
                    content = content.replace(k, v)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                if file.strip('.py') in cached_translation:
                    file_new = cached_translation[file.strip('.py')] + '.py'
                    file_path_new = os.path.join(root, file_new)
                    with open(file_path_new, 'w', encoding='utf-8') as f:
                        f.write(content)
                    os.remove(file_path)

step_1_core_key_translate()
step_2_core_key_translate()
