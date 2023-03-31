
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


if __name__ == '__main__':
    import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
    from toolbox import get_conf
    proxies, = get_conf('proxies')
    check_proxy(proxies)
    