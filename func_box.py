#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/18
# @Author : Spike
# @Descr   :
import hashlib
import os.path
import subprocess
import psutil
import re
import tempfile
import shutil
from contextlib import ExitStack
import logging
logger = logging
"""contextlib 是 Python 标准库中的一个模块，提供了一些工具函数和装饰器，用于支持编写上下文管理器和处理上下文的常见任务，例如资源管理、异常处理等。
官网：https://docs.python.org/3/library/contextlib.html"""

class Shell(object):
    def __init__(self, args, stream=False):
        self.args = args
        self.subp = subprocess.Popen(args, shell=True,
                                     stdin=subprocess.PIPE,  stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE, encoding='utf-8',
                                     errors='ignore', close_fds=True)
        self.__stream = stream
        self.__temp = ''

    def read(self):
        logger.debug(f'The command being executed is: "{self.args}"')
        if self.__stream:
            sysout = self.subp.stdout
            try:
                with sysout as std:
                    for i in std:
                        logger.info(i.rstrip())
                        self.__temp += i
            except KeyboardInterrupt as p:
                return 3, self.__temp+self.subp.stderr.read()
            finally:
                return 3, self.__temp+self.subp.stderr.read()
        else:
            sysout = self.subp.stdout.read()
            syserr = self.subp.stderr.read()
            if sysout:
                logger.debug(f"{self.args} \n{sysout}")
                return 1, sysout
            elif syserr:
                logger.error(f"{self.args} \n{syserr}")
                return 0, syserr
            else:
                logger.debug(f"{self.args} \n{[sysout], [sysout]}")
                return 2, '\n{}\n{}'.format(sysout, sysout)

    def sync(self):
        logger.debug('The command being executed is: "{}"'.format(self.args))
        for i in self.subp.stdout:
            logger.debug(i.rstrip())
            self.__temp += i
            yield self.__temp
        for i in self.subp.stderr:
            logger.debug(i.rstrip())
            self.__temp += i
            yield self.__temp

def context_with(*parms):
    """
    一个装饰器，根据传递的参数列表，在类方法上下文中嵌套多个 with 语句。
    Args:
        *parms: 参数列表，每个参数都是一个字符串，表示类中的一个属性名。
    Returns:
        一个装饰器函数。
    """
    def decorator(cls_method):
        """
        装饰器函数，用于将一个类方法转换为一个嵌套多个 with 语句的方法。
        Args:
            cls_method: 要装饰的类方法。
        Returns:
            装饰后的类方法。
        """
        def wrapper(cls='', *args, **kwargs):
            """
            装饰后的方法，用于嵌套多个 with 语句，并调用原始的类方法。
            Args:
                cls: 类的实例对象。
                *args: 位置参数。
                **kwargs: 关键字参数。
            Returns:
                原始的类方法返回的结果。
            """
            with_list = [getattr(cls, arg) for arg in parms]
            with ExitStack() as stack:
                for context in with_list:
                    stack.enter_context(context)
                return cls_method(cls, *args, **kwargs)
        return wrapper
    return decorator


def copy_temp_file(file):
    if os.path.exists(file):
        exdir = tempfile.mkdtemp()
        temp_ = shutil.copy(file, os.path.join(exdir, os.path.basename(file)))
        return temp_
    else:
        return None

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
    txt = str(txt)
    """(关键字)(加密间隔)匹配机制（关键字间隔）"""
    pattern = re.compile(rf"(Authorization|WPS-Sid|Cookie)(:|\s+)\s*(\S+)[\s\S]*?(?=\n|$|\s)", re.IGNORECASE)
    result = pattern.sub(lambda x: x.group(1) + ": XXXXXXXX", txt)
    return result

def tree_out(dir=os.path.dirname(__file__), line=2, more=''):
    out = Shell(f'tree {dir} -F -I "__*|.*|venv|*.png|*.xlsx" -L {line} {more}').read()[1]
    localfile = os.path.join(os.path.dirname(__file__), '.tree.md')
    with open(localfile, 'w') as f:
        f.write('```\n')
        ll = out.splitlines()
        for i in range(len(ll)):
            if i == 0:
                f.write(ll[i].split('/')[-2]+'\n')
            else:
                f.write(ll[i]+'\n')
        f.write('```\n')


def chat_history(log: list, split=0):
    if split:
        log = log[split:]
    chat = ''
    history = ''
    for i in log:
        chat += f'{i[0]}\n\n'
        history += f'{i[1]}\n\n'
    return chat, history



if __name__ == '__main__':

    txt = "Authorization: WPS-2:AqY7ik9XQ92tvO7+NlCRvA==:b2f626f496de9c256605a15985c855a8b3e4be99\nwps-Sid: V02SgISzdeWrYdwvW_xbib-fGlqUIIw00afc5b890008c1976f\nCookie: wpsua=V1BTVUEvMS4wIChhbmRyb2lkLW9mZmljZToxNy41O2FuZHJvaWQ6MTA7ZjIwZDAyNWQzYTM5MmExMDBiYzgxNWI2NmI3Y2E5ODI6ZG1sMmJ5QldNakF5TUVFPSl2aXZvL1YyMDIwQQ=="
    txt = "Authorization: WPS-2:AqY7ik9XQ92tvO7+NlCRvA==:b2f626f496de9c256605a15985c855a8b3e4be99"
    print(encryption_str(txt))

    def update_ui(chatbot, history, msg='正常', txt='', obj=None, btn1=None, btn2=None, au_text=None, *args):
        print(chatbot, history, msg, txt, obj)

    ll = [4,5, 6]
    update_ui(chatbot=1, history=2, *ll)