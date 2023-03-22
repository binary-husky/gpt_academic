
"""
我：用python的requests库查询本机ip地址所在地
ChatGPT:
"""
def check_proxy(proxies):
    import requests
    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        data = response.json()
        country = data['country_name']
        # city = data['city']
        proxies_https = proxies['https'] if proxies is not None else '无'
        result = f"代理配置 {proxies_https}, 代理所在地：{country}"
        print(result)
        return result
    except:
        result = f"代理配置 {proxies_https}, 代理所在地查询超时，代理可能无效"
        print(result)
        return result


if __name__ == '__main__':
    from config import proxies
    check_proxy(proxies)