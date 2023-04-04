
def check_proxy(proxies):
    import requests
    proxies_https = proxies['https'] if proxies is not None else '无'
    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        data = response.json()
        print(f'查询代理的地理位置，返回的结果是{data}')
        if 'country_name' in data:
            country = data['country_name']
            result = f"代理配置 {proxies_https}, 代理所在地：{country}"
        elif 'error' in data:
            result = f"代理配置 {proxies_https}, 代理所在地：未知，IP查询频率受限"
        print(result)
        return result
    except:
        result = f"代理配置 {proxies_https}, 代理所在地查询超时，代理可能无效"
        print(result)
        return result


def auto_update():
    from toolbox import get_conf
    import requests, time, json
    proxies, = get_conf('proxies')
    response = requests.get("https://raw.githubusercontent.com/binary-husky/chatgpt_academic/master/version", 
                            proxies=proxies, timeout=1)
    remote_json_data = json.loads(response.text)
    remote_version = remote_json_data['version']
    if remote_json_data["show_feature"]:
        new_feature = "新功能：" + remote_json_data["new_feature"]
    else:
        new_feature = ""
    with open('./version', 'r', encoding='utf8') as f: 
        current_version = f.read()
        current_version = json.loads(current_version)['version']
    if (remote_version - current_version) >= 0.05:
        print(f'\n新版本可用。新版本:{remote_version}，当前版本:{current_version}。{new_feature}')
        print('Github更新地址:\nhttps://github.com/binary-husky/chatgpt_academic\n')
        time.sleep(3)
        return
    else:
        return


if __name__ == '__main__':
    import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
    from toolbox import get_conf
    proxies, = get_conf('proxies')
    check_proxy(proxies)
    