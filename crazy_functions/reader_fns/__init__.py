# encoding: utf-8
# @Time   : 2023/8/30
# @Author : Spike
# @Descr   :
# 云文件下载方法
from .docs_feishu import Feishu
from .docs_kingsoft import Kdocs
from .docs_qqdocs import QQDocs

# 本地文件处理方法
from .local_word import DocxHandler
from .local_excel import XlsxHandler
from .local_xmind import XmindHandle
