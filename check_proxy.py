
def check_proxy(proxies):
    import requests
    proxies_https = proxies['https'] if proxies is not None else '无'
    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        data = response.json()
        print(f'查询代理的地理位置，返回的结果是{data}')
        country = data['country_name']
        result = f"代理配置 {proxies_https}, 代理所在地：{country}"
        print(result)
        return result
    except:
        result = f"代理配置 {proxies_https}, 代理所在地查询超时，代理可能无效"
        print(result)
        return result


if __name__ == '__main__':
    try: from config_private import proxies # 放自己的秘密如API和代理网址 os.path.exists('config_private.py')
    except: from config import proxies
    check_proxy(proxies)