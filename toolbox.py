import markdown, mdtex2html, threading, importlib, traceback
from show_math import convert as convert_math
from functools import wraps
import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

def predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature, history=[], sys_prompt=''):
    """
        调用简单的predict_no_ui接口，但是依然保留了些许界面心跳功能，当对话太长时，会自动采用二分法截断
    """
    import time
    from predict import predict_no_ui
    from toolbox import get_conf
    TIMEOUT_SECONDS, MAX_RETRY = get_conf('TIMEOUT_SECONDS', 'MAX_RETRY')
    # 多线程的时候，需要一个mutable结构在不同线程之间传递信息
    # list就是最简单的mutable结构，我们第一个位置放gpt输出，第二个位置传递报错信息
    mutable = [None, '']
    # multi-threading worker
    def mt(i_say, history):
        while True:
            try:
                mutable[0] = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt)
                break
            except ConnectionAbortedError as e:
                if len(history) > 0:
                    history = [his[len(his)//2:] for his in history if his is not None]
                    mutable[1] = 'Warning! History conversation is too long, cut into half. '
                else:
                    i_say = i_say[:len(i_say)//2]
                    mutable[1] = 'Warning! Input file is too long, cut into half. '
            except TimeoutError as e:
                mutable[0] = '[Local Message] Failed with timeout.'
                raise TimeoutError
    # 创建新线程发出http请求
    thread_name = threading.Thread(target=mt, args=(i_say, history)); thread_name.start()
    # 原来的线程则负责持续更新UI，实现一个超时倒计时，并等待新线程的任务完成
    cnt = 0
    while thread_name.is_alive():
        cnt += 1
        chatbot[-1] = (i_say_show_user, f"[Local Message] {mutable[1]}waiting gpt response {cnt}/{TIMEOUT_SECONDS*2*(MAX_RETRY+1)}"+''.join(['.']*(cnt%4)))
        yield chatbot, history, '正常'
        time.sleep(1)
    # 把gpt的输出从mutable中取出来
    gpt_say = mutable[0]
    if gpt_say=='[Local Message] Failed with timeout.': raise TimeoutError
    return gpt_say

def write_results_to_file(history, file_name=None):
    """
        将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os, time
    if file_name is None:
        # file_name = time.strftime("chatGPT分析报告%Y-%m-%d-%H-%M-%S", time.localtime()) + '.md'
        file_name = 'chatGPT分析报告' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.md'
    os.makedirs('./gpt_log/', exist_ok=True)
    with open(f'./gpt_log/{file_name}', 'w', encoding = 'utf8') as f:
        f.write('# chatGPT 分析报告\n')
        for i, content in enumerate(history):
            if i%2==0: f.write('## ')
            f.write(content)
            f.write('\n\n')
    res = '以上材料已经被写入' + os.path.abspath(f'./gpt_log/{file_name}')
    print(res)
    return res

def regular_txt_to_markdown(text):
    """
        将普通文本转换为Markdown格式的文本。
    """
    text = text.replace('\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    text = text.replace('\n\n\n', '\n\n')
    return text

def CatchException(f):
    """
        装饰器函数，捕捉函数f中的异常并封装到一个生成器中返回，并显示到聊天当中。
    """
    @wraps(f)
    def decorated(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
        try:
            yield from f(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)
        except Exception as e:
            from check_proxy import check_proxy
            from toolbox import get_conf
            proxies, = get_conf('proxies')
            tb_str = regular_txt_to_markdown(traceback.format_exc())
            chatbot[-1] = (chatbot[-1][0], f"[Local Message] 实验性函数调用出错: \n\n {tb_str} \n\n 当前代理可用性: \n\n {check_proxy(proxies)}")
            yield chatbot, history, f'异常 {e}'
    return decorated

def report_execption(chatbot, history, a, b):
    """
        向chatbot中添加错误信息
    """
    chatbot.append((a, b))
    history.append(a); history.append(b)

def text_divide_paragraph(text):
    """
        将文本按照段落分隔符分割开，生成带有段落标签的HTML代码。
    """
    if '```' in text:
        # careful input
        return text
    else:
        # wtf input
        lines = text.split("\n")
        for i, line in enumerate(lines):
            lines[i] = lines[i].replace(" ", "&nbsp;")
        text = "</br>".join(lines)
        return text

def markdown_convertion(txt):
    """
        将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    if ('$' in txt) and ('```' not in txt):
        return markdown.markdown(txt,extensions=['fenced_code','tables']) + '<br><br>' + \
            markdown.markdown(convert_math(txt, splitParagraphs=False),extensions=['fenced_code','tables'])
    else:
        return markdown.markdown(txt,extensions=['fenced_code','tables'])


def format_io(self, y):
    """
        将输入和输出解析为HTML格式。将y中最后一项的输入部分段落化，并将输出部分的Markdown和数学公式转换为HTML格式。
    """
    if y is None or y == []: return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask) # 输入部分太自由，预处理一波
    y[-1] = (
        None if i_ask is None else markdown.markdown(i_ask, extensions=['fenced_code','tables']),
        None if gpt_reply is None else markdown_convertion(gpt_reply)
    )
    return y


def find_free_port():
    """
        返回当前系统中可用的未使用端口。
    """
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def extract_archive(file_path, dest_dir):
    import zipfile
    import tarfile
    import os
    # Get the file extension of the input file
    file_extension = os.path.splitext(file_path)[1]

    # Extract the archive based on its extension
    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zipobj:
            zipobj.extractall(path=dest_dir)
            print("Successfully extracted zip archive to {}".format(dest_dir))

    elif file_extension in ['.tar', '.gz', '.bz2']:
        with tarfile.open(file_path, 'r:*') as tarobj:
            tarobj.extractall(path=dest_dir)
            print("Successfully extracted tar archive to {}".format(dest_dir))
    else:
        return

def find_recent_files(directory):
    """
        me: find files that is created with in one minutes under a directory with python, write a function
        gpt: here it is!
    """
    import os
    import time
    current_time = time.time()
    one_minute_ago = current_time - 60
    recent_files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if file_path.endswith('.log'): continue
        created_time = os.path.getctime(file_path)
        if created_time >= one_minute_ago:
            if os.path.isdir(file_path): continue
            recent_files.append(file_path)

    return recent_files


def on_file_uploaded(files, chatbot, txt):
    if len(files) == 0: return chatbot, txt
    import shutil, os, time, glob
    from toolbox import extract_archive
    try: shutil.rmtree('./private_upload/')
    except: pass
    time_tag = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    os.makedirs(f'private_upload/{time_tag}', exist_ok=True)
    for file in files:
        file_origin_name = os.path.basename(file.orig_name)
        shutil.copy(file.name, f'private_upload/{time_tag}/{file_origin_name}')
        extract_archive(f'private_upload/{time_tag}/{file_origin_name}', 
                        dest_dir=f'private_upload/{time_tag}/{file_origin_name}.extract')
    moved_files = [fp for fp in glob.glob('private_upload/**/*', recursive=True)]
    txt = f'private_upload/{time_tag}'
    moved_files_str = '\t\n\n'.join(moved_files)
    chatbot.append(['我上传了文件，请查收', 
                    f'[Local Message] 收到以下文件: \n\n{moved_files_str}\n\n调用路径参数已自动修正到: \n\n{txt}\n\n现在您点击任意实验功能时，以上文件将被作为输入参数'])
    return chatbot, txt


def on_report_generated(files, chatbot):
    from toolbox import find_recent_files
    report_files = find_recent_files('gpt_log')
    if len(report_files) == 0: return report_files, chatbot
    # files.extend(report_files)
    chatbot.append(['汇总报告如何远程获取？', '汇总报告已经添加到右侧文件上传区，请查收。'])
    return report_files, chatbot

def get_conf(*args):
    # 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
    res = []
    for arg in args:
        try: r = getattr(importlib.import_module('config_private'), arg)
        except: r = getattr(importlib.import_module('config'), arg)
        res.append(r)
        # 在读取API_KEY时，检查一下是不是忘了改config
        if arg=='API_KEY' and len(r) != 51:
            assert False, "正确的API_KEY密钥是51位，请在config文件中修改API密钥, 添加海外代理之后再运行。" + \
                        "（如果您刚更新过代码，请确保旧版config_private文件中没有遗留任何新增键值）"
    return res

def clear_line_break(txt):
    txt = txt.replace('\n', ' ')
    txt = txt.replace('  ', ' ')
    txt = txt.replace('  ', ' ')
    return txt

def readPdf(pdfPath):
    """
    读取pdf文件，返回文本内容
    """
    fp = open(pdfPath, 'rb')

    # Create a PDF parser object associated with the file object
    parser = PDFParser(fp)

    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    # device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS.
    # Set parameters for analysis.
    laparams = LAParams(
        char_margin=10.0,
        line_margin=0.2,
        boxes_flow=0.2,
        all_texts=False,
    )
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # loop over all pages in the document
    outTextList = []
    for page in PDFPage.create_pages(document):
        # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()
        for obj in layout._objs:
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                # print(obj.get_text())
                outTextList.append(obj.get_text())

    return outTextList