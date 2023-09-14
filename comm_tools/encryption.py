#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/1
# @Author : Spike
# @Descr   :
import binascii
import argparse
import os, sys

from pyDes import des, CBC, PAD_PKCS5
jobpath = os.path.dirname(os.path.dirname(__file__))
sys.path.append(jobpath)  # 外部运行，将项目目录添加成临时环境变量
"""
    DES加密、解密
"""

def encrypt_text(info):
    """
    DES 加密
    :param : 原始字符串
    :return: 加密后字符串，16进制
    """
    encrypt_key = os.environ['private_key'][:4]
    key = "ZDNC{}".format(encrypt_key)
    secret_key = key  # 密码
    iv = secret_key  # 偏移
    # secret_key:加密密钥，CBC:加密模式，iv:偏移, padmode:填充
    des_obj = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    # 返回为字节
    secret_bytes = des_obj.encrypt(info.encode("utf-8"), padmode=PAD_PKCS5)
    # 返回为16进制
    return binascii.b2a_hex(secret_bytes).decode("utf-8")


def three_types_of_encryption(info):
    for i in range(3):
        info = encrypt_text(info)
    return info


def triple_decryption(info):
    for i in range(3):
        info = decrypt_text(info)
    return info


def decrypt_text(info):
    """
    DES 解密
    :param : 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    encrypt_key = os.environ['private_key'][:4]
    key = "ZDNC{}".format(encrypt_key)
    secret_key = key
    iv = secret_key
    des_obj = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    decrypt_str = des_obj.decrypt(binascii.a2b_hex(info.encode("utf-8")), padmode=PAD_PKCS5)
    return bytes.decode(decrypt_str) # bytes.decode() 将bit转为str


def main():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt text using DES algorithm.')
    parser.add_argument('--en', metavar='text', help='Encrypt the input text')
    parser.add_argument('--de', metavar='text', help='Decrypt the input text')
    parser.add_argument('--en3', metavar='text', help='Encrypt the input text')
    parser.add_argument('--de3', metavar='text', help='Decrypt the input text')

    args = parser.parse_args()

    if args.en:
        encrypted_text = encrypt_text(args.en)
        print("Encrypted text: {}".format(encrypted_text))
    elif args.de:
        decrypted_text = decrypt_text(args.de)
        print("Decrypted text: {}".format(decrypted_text))
    elif args.en3:
        decrypted_text = three_types_of_encryption(args.en3)
        print("Decrypted text: {}".format(decrypted_text))
    elif args.de3:
        decrypted_text = triple_decryption(args.de3)
        print("Decrypted text: {}".format(decrypted_text))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()