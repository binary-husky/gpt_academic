#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import hashlib
import psutil
import re

def md5_str(st):
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 更新 MD5 对象的内容
    md5.update(str(st).encode())
    # 获取加密后的结果
    result = md5.hexdigest()
    return result


def ipaddr():  # 获取本地ipx
    ip = psutil.net_if_addrs()
    for i in ip:
        if ip[i][0][3]:
            return ip[i][0][1]

def encryption_str(txt: str):
    """(关键字)(加密间隔)匹配机制（关键字间隔）"""
    pattern = re.compile(rf"(Authorization|WPS-Sid|Cookie)(:|\s+)\s*(\S+)[\s\S]*?(?=\n|$|\s)", re.IGNORECASE)
    result = pattern.sub(lambda x: x.group(1) + ": XXXXXXXX", txt)
    return result


if __name__ == '__main__':

    txt = "Authorization: WPS-2:AqY7ik9XQ92tvO7+NlCRvA==:b2f626f496de9c256605a15985c855a8b3e4be99\nwps-Sid: V02SgISzdeWrYdwvW_xbib-fGlqUIIw00afc5b890008c1976f\nCookie: wpsua=V1BTVUEvMS4wIChhbmRyb2lkLW9mZmljZToxNy41O2FuZHJvaWQ6MTA7ZjIwZDAyNWQzYTM5MmExMDBiYzgxNWI2NmI3Y2E5ODI6ZG1sMmJ5QldNakF5TUVFPSl2aXZvL1YyMDIwQQ=="
    txt = "Authorization: WPS-2:AqY7ik9XQ92tvO7+NlCRvA==:b2f626f496de9c256605a15985c855a8b3e4be99"
    print(encryption_str(txt))



