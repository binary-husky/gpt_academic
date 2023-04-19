#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import hashlib

def md5_str(st):
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 更新 MD5 对象的内容
    md5.update(str(st).encode())
    # 获取加密后的结果
    result = md5.hexdigest()
    return result