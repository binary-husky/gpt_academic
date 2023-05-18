import os
import functools
import os
import pickle
import time

CACHE_FOLDER = "gpt_log"

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



def extract_chinese_characters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        chinese_characters = [] 
        sentence = {'file':file_path, 'begin':-1, 'end':-1, 'word': ""} 
        for index, char in enumerate(content):
            if 0x4e00 <= ord(char) <= 0x9fff:
                sentence['word'] += char
                if sentence['begin'] == -1: sentence['begin'] = index
                sentence['end'] = index
            else:
                if len(sentence['word'])>0:
                    chinese_characters.append(sentence)
                    sentence = {'file':file_path, 'begin':-1, 'end':-1, 'word': ""} 
        return chinese_characters

def extract_chinese_characters_from_directory(directory_path):
    chinese_characters = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                chinese_characters.extend(extract_chinese_characters(file_path))
    return chinese_characters

directory_path = './'
chinese_characters = extract_chinese_characters_from_directory(directory_path)
word_to_translate = {}
for d in chinese_characters:
    word_to_translate[d['word']] = "TRANS"

def break_dictionary(d, n):
    items = list(d.items())
    num_dicts = (len(items) + n - 1) // n
    return [{k: v for k, v in items[i*n:(i+1)*n]} for i in range(num_dicts)]

N_EACH_REQ = 50
word_to_translate_split = break_dictionary(word_to_translate, N_EACH_REQ)
LANG = "English"

@lru_file_cache(maxsize=10, ttl=1e40, filename="translation_cache")
def trans(words):
    # from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
    # from toolbox import get_conf, ChatBotWithCookies
    # proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY = \
    #     get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT', 'API_KEY')
    # llm_kwargs = {
    #     'api_key': API_KEY,
    #     'llm_model': LLM_MODEL,
    #     'top_p':1.0, 
    #     'max_length': None,
    #     'temperature':0.0,
    # }
    # plugin_kwargs = {}
    # chatbot = ChatBotWithCookies(llm_kwargs)
    # history = []
    # for gpt_say in request_gpt_model_in_new_thread_with_ui_alive(
    #     inputs=words, inputs_show_user=words, 
    #     llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
    #     sys_prompt=f"Translate following words to {LANG}, replace `TRANS` with translated result."
    # ):
    #     gpt_say = gpt_say[1][0][1]
    # return gpt_say
    return '{}'

translated_result = {}
for d in word_to_translate_split:
    res = trans(str(d))
    try:
        # convert translated result back to python dictionary
        res_dict = eval(res)
    except:
        print('Unexpected output.')
    translated_result.update(res_dict)

print('All Chinese characters:', chinese_characters)


# =================== create copy =====================
def copy_source_code():
    """
    一键更新协议：备份和下载
    """
    from toolbox import get_conf
    import shutil
    import os
    import requests
    import zipfile
    try: shutil.rmtree(f'./multi-language/{LANG}/')
    except: pass
    os.makedirs(f'./multi-language', exist_ok=True)
    backup_dir = f'./multi-language/{LANG}/'
    shutil.copytree('./', backup_dir, ignore=lambda x, y: ['multi-language', 'gpt_log', '.git', 'private_upload'])
copy_source_code()


for d in chinese_characters:
    d['file'] = f'./multi-language/{LANG}/' + d['file']
    if d['word'] in translated_result:
        d['trans'] = translated_result[d['word']]
    else:
        d['trans'] = None

chinese_characters = sorted(chinese_characters, key=lambda x: len(x['word']), reverse=True)
for d in chinese_characters:
    if d['trans'] is None:
        continue
    


    with open(d['file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    content.replace(d['word'], d['trans'])
    substring = d['trans']
    substring_start_index = content.find(substring)
    substring_end_index = substring_start_index + len(substring) - 1
    if content[substring_start_index].isalpha() or content[substring_start_index].isdigit():
        content = content[:substring_start_index+1]


