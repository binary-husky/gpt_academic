import platform
from sys import stdout

if platform.system()=="Linux":
    pass
else:
    from colorama import init
    init()

# Do you like the elegance of Chinese characters?
def print红(*kw,**kargs):
    print("\033[0;31m",*kw,"\033[0m",**kargs)
def print绿(*kw,**kargs):
    print("\033[0;32m",*kw,"\033[0m",**kargs)
def print黄(*kw,**kargs):
    print("\033[0;33m",*kw,"\033[0m",**kargs)
def print蓝(*kw,**kargs):
    print("\033[0;34m",*kw,"\033[0m",**kargs)
def print紫(*kw,**kargs):
    print("\033[0;35m",*kw,"\033[0m",**kargs)
def print靛(*kw,**kargs):
    print("\033[0;36m",*kw,"\033[0m",**kargs)

def print亮红(*kw,**kargs):
    print("\033[1;31m",*kw,"\033[0m",**kargs)
def print亮绿(*kw,**kargs):
    print("\033[1;32m",*kw,"\033[0m",**kargs)
def print亮黄(*kw,**kargs):
    print("\033[1;33m",*kw,"\033[0m",**kargs)
def print亮蓝(*kw,**kargs):
    print("\033[1;34m",*kw,"\033[0m",**kargs)
def print亮紫(*kw,**kargs):
    print("\033[1;35m",*kw,"\033[0m",**kargs)
def print亮靛(*kw,**kargs):
    print("\033[1;36m",*kw,"\033[0m",**kargs)

# Do you like the elegance of Chinese characters?
def sprint红(*kw):
    return "\033[0;31m"+' '.join(kw)+"\033[0m"
def sprint绿(*kw):
    return "\033[0;32m"+' '.join(kw)+"\033[0m"
def sprint黄(*kw):
    return "\033[0;33m"+' '.join(kw)+"\033[0m"
def sprint蓝(*kw):
    return "\033[0;34m"+' '.join(kw)+"\033[0m"
def sprint紫(*kw):
    return "\033[0;35m"+' '.join(kw)+"\033[0m"
def sprint靛(*kw):
    return "\033[0;36m"+' '.join(kw)+"\033[0m"
def sprint亮红(*kw):
    return "\033[1;31m"+' '.join(kw)+"\033[0m"
def sprint亮绿(*kw):
    return "\033[1;32m"+' '.join(kw)+"\033[0m"
def sprint亮黄(*kw):
    return "\033[1;33m"+' '.join(kw)+"\033[0m"
def sprint亮蓝(*kw):
    return "\033[1;34m"+' '.join(kw)+"\033[0m"
def sprint亮紫(*kw):
    return "\033[1;35m"+' '.join(kw)+"\033[0m"
def sprint亮靛(*kw):
    return "\033[1;36m"+' '.join(kw)+"\033[0m"
