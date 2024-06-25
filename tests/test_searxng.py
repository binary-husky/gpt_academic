def validate_path():
    import os, sys
    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)
validate_path()  # validate path so you can run from base directory

from toolbox import get_conf
import requests

def searxng_request(query, proxies, categories='general', searxng_url=None, engines=None):
    url = 'http://localhost:50001/'

    if engines is None:
        engine = 'bing,'
    if categories == 'general':
        params = {
            'q': query,         # 搜索查询
            'format': 'json',   # 输出格式为JSON
            'language': 'zh',   # 搜索语言
            'engines': engine,
        }
    elif categories == 'science':
        params = {
            'q': query,         # 搜索查询
            'format': 'json',   # 输出格式为JSON
            'language': 'zh',   # 搜索语言
            'categories': 'science'
        }
    else:
        raise ValueError('不支持的检索类型')
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'X-Forwarded-For': '112.112.112.112',
        'X-Real-IP': '112.112.112.112'
    }
    results = []
    response = requests.post(url, params=params, headers=headers, proxies=proxies, timeout=30)
    if response.status_code == 200:
        json_result = response.json()
        for result in json_result['results']:
            item = {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "link": result["url"],
            }
            print(result['engines'])
            results.append(item)
        return results
    else:
        if response.status_code == 429:
            raise ValueError("Searxng（在线搜索服务）当前使用人数太多，请稍后。")
        else:
            raise ValueError("在线搜索失败，状态码: " + str(response.status_code) + '\t' + response.content.decode('utf-8'))
res = searxng_request("vr environment", None, categories='science', searxng_url=None, engines=None)
print(res)