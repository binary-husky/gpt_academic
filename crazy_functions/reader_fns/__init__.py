# encoding: utf-8
# @Time   : 2023/8/30
# @Author : Spike
# @Descr   :
# 云文件下载方法
from .docs_feishu import *
from .docs_kingsoft import *
from .docs_qqdocs import *
from .project_feishu import *

# 本地文件处理方法
from .local_word import DocxHandler
from .local_excel import XlsxHandler
from .local_xmind import XmindHandle
from .local_markdown import MdHandler, MdProcessor
from .local_pdf import PDFHandler
from .local_image import *
