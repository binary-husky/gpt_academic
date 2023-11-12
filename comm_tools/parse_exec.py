#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/30
# @Author : Spike
# @Descr   :
import json
import curlconverter

from comm_tools import func_box
from comm_tools import toolbox


WEB_PORT = toolbox.get_conf('WEB_PORT')
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
    parser.add_argument('--curl2py', metavar='text', help='**清理端口')
    args = parser.parse_args()
    if args.clear:
        check_proxy_free(args.clear)
    if args.curl2py:
        converter_curl_python(args.curl2py)
    else:
        print('必须选一个带**')

if __name__ == '__main__':
    main()
