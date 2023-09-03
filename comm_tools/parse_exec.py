#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/30
# @Author : Spike
# @Descr   :
import json
import curlconverter

from comm_tools import func_box
from comm_tools import toolbox


WEB_PORT, = toolbox.get_conf('WEB_PORT')
PORT = toolbox.find_free_port() if WEB_PORT <= 0 else WEB_PORT


def check_proxy_free(port):
    if not port: port = PORT
    proxy_state = func_box.Shell(f'lsof -i :{port}').read()[1].splitlines()
    if proxy_state != ["", ""]:
        print('Kill Old Server')
        for i in proxy_state[1:]:
            func_box.Shell(f'kill -9 {i.split()[1]}').read()
        import time
        time.sleep(5)


def converter_curl_python(comm):
    resp = curlconverter.CurlConverter(comm).convert()
    cookie_str = ''
    for i in resp['headers']:
        if i.lower().startswith('cookie'):
            cookie_str += i
    cookie_dict = {}
    # 去除字符串中的"Cookie: "前缀
    cookie_string = cookie_str.replace("Cookie: ", "")
    # 按照分号进行分割
    cookie_list = cookie_string.split("; ")
    # 遍历每个键值对的字符串，将键和值组成字典形式
    for item in cookie_list:
        try:
            key = item.split("=")
            cookie_dict[key[0]] = "=".join(key[1:])
        except:
            print(f'过滤{item}')
    cookie_dict = {'Cookies': cookie_dict}
    cookie_dict.update(resp)
    print(json.dumps(cookie_dict, indent=1))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='命令行工具')
    parser.add_argument('--clear', metavar='text', help='**清理端口')
    args = parser.parse_args()
    if args.clear:
        check_proxy_free(args.clear)
    else:
        print('必须选一个带**')

if __name__ == '__main__':
    # main()
    print(converter_curl_python(
        'curl -H "Host: docs.qq.com" -H "Cookie: RK=uGvhhCQ0zj; ptcz=99c50f94a55160ab18fc6eb8f096b3f8ba5ff39929bd1050b651976e22690272; pac_uid=0_53b2f679b8958; iip=0; pgv_pvid=3226633567; eas_sid=S1Y6E7m5q5G980D7p3Y0V6r1i9; _hjSessionUser_2765497=eyJpZCI6ImE2ZmVkYzQ3LWUxYTItNTNkZC05MjQyLTdjMGE0NTFkNGVjMyIsImNyZWF0ZWQiOjE2NzY5NzM5MjIxNDksImV4aXN0aW5nIjpmYWxzZX0=; _ga=GA1.2.672540206.1676973925; fingerprint=25068f269dc748cfa1f72b18c9bb567485; traceid=5c93285746; TOK=5c932857469d443e; hashkey=5c932857; pgv_info=ssid=s1566934721485879; low_login_enable=1; uin=o2411123479; skey=@RLRg3Do1o; luin=o2411123479; lskey=00010000028f61e566ebc077aaf94f4d0d3710de98d0c5aa880aef892ca4b6f9fb91e1d00a68532db2764d7c; p_uin=o2411123479; pt4_token=lz-mBvVtcG*phwWovBO2jlUnS*sDLRURsHwxK9pjL8A_; p_skey=AvdKkMELItneZVvg5zevEmFZYlTK9f1x08ha*sR69-w_; p_luin=o2411123479; p_lskey=000400009940d03062ae753a92f6c2a73f81f94bca33f37c6706df4546a5aa32d7d81e61dd0fcdaa2207fca4; uid=144115211492590730; utype=qq; vfwebqq=addce68ddab2c5a4e3220b3eaef97ef878695bfe5bf61074af22048b997fd3f31f7885037d12d55e; DOC_QQ_APPID=101458937; DOC_QQ_OPENID=7F1531B5C41FFEB3ED1AC333D7FC65DC; env_id=gray-pct50; gray_user=true; DOC_SID=6709e087993a4c13a8f4fb4959847db0e6ec453fe1924b549847b98a9e814ce5; SID=6709e087993a4c13a8f4fb4959847db0e6ec453fe1924b549847b98a9e814ce5; uid_key=EOP1mMQHGixKNE9lMWNNYmtpejZHZEVZNUNrSzE4WHpXcWVCdjYyYTFHTG9rK2l5ZFVzPSJISVFQZGMRpDexb8grhGKnpwXwY4nhwrKrS%2FjKVVKPaBjNBpA%2Fst%2BPOBtPPPCvpU7xEdHxZNhXKvAGgvuahRO05oQi4C8Mzl0%2BKPTH36gG; optimal_cdn_domain=docs2.gtimg.com; loginTime=1693665288205; backup_cdn_domain=docs.gtimg.com; tgw_l7_route=9639dd27992b806a49369cbdd9e714a4; clean_env=0" -H "sec-ch-ua: \"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Microsoft Edge\";v=\"116\"" -H "sec-ch-ua-mobile: ?0" -H "sec-ch-ua-platform: \"macOS\"" -H "upgrade-insecure-requests: 1" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" -H "sec-fetch-site: none" -H "sec-fetch-mode: navigate" -H "sec-fetch-user: ?1" -H "sec-fetch-dest: document" -H "accept-language: en-US,en;q=0.9,ja;q=0.8" --compressed "https://docs.qq.com/sheet/DT3JRQW9nYnVkRVh1?tab=BB08J2"'))