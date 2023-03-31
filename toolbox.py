import markdown, mdtex2html, threading, importlib, traceback, importlib, inspect, re
from show_math import convert as convert_math
from functools import wraps

def get_reduce_token_percent(text):
    try:
        # text = "maximum context length is 4097 tokens. However, your messages resulted in 4870 tokens"
        pattern = r"(\d+)\s+tokens\b"
        match = re.findall(pattern, text)
        EXCEED_ALLO = 500 # 稍微留一点余地，否则在回复时会因余量太少出问题
        max_limit = float(match[0]) - EXCEED_ALLO
        current_tokens = float(match[1])
        ratio = max_limit/current_tokens
        assert ratio > 0 and ratio < 1
        return ratio, str(int(current_tokens-max_limit))
    except:
        return 0.5, '不详'

def predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature, history=[], sys_prompt='', long_connection=True):
    """
        调用简单的predict_no_ui接口，但是依然保留了些许界面心跳功能，当对话太长时，会自动采用二分法截断
        i_say: 当前输入
        i_say_show_user: 显示到对话界面上的当前输入，例如，输入整个文件时，你绝对不想把文件的内容都糊到对话界面上
        chatbot: 对话界面句柄
        top_p, temperature: gpt参数
        history: gpt参数 对话历史
        sys_prompt: gpt参数 sys_prompt
        long_connection: 是否采用更稳定的连接方式（推荐）
    """
    import time
    from predict import predict_no_ui, predict_no_ui_long_connection
    from toolbox import get_conf
    TIMEOUT_SECONDS, MAX_RETRY = get_conf('TIMEOUT_SECONDS', 'MAX_RETRY')
    # 多线程的时候，需要一个mutable结构在不同线程之间传递信息
    # list就是最简单的mutable结构，我们第一个位置放gpt输出，第二个位置传递报错信息
    mutable = [None, '']
    # multi-threading worker
    def mt(i_say, history):
        while True:
            try:
                if long_connection:
                    mutable[0] = predict_no_ui_long_connection(inputs=i_say, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt)
                else:
                    mutable[0] = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt)
                break
            except ConnectionAbortedError as token_exceeded_error:
                # 尝试计算比例，尽可能多地保留文本
                p_ratio, n_exceed = get_reduce_token_percent(str(token_exceeded_error))
                if len(history) > 0:
                    history = [his[     int(len(his)    *p_ratio):      ] for his in history if his is not None]
                else:
                    i_say = i_say[:     int(len(i_say)  *p_ratio)     ]
                mutable[1] = f'警告，文本过长将进行截断，Token溢出数：{n_exceed}，截断比例：{(1-p_ratio):.0%}。'
            except TimeoutError as e:
                mutable[0] = '[Local Message] 请求超时。'
                raise TimeoutError
            except Exception as e:
                mutable[0] = f'[Local Message] 异常：{str(e)}.'
                raise RuntimeError(f'[Local Message] 异常：{str(e)}.')
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
            try:    # 这个bug没找到触发条件，暂时先这样顶一下
                if type(content) != str: content = str(content)
            except:
                continue
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

def HotReload(f):
    """
        装饰器函数，实现函数插件热更新
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        fn_name = f.__name__
        f_hot_reload = getattr(importlib.reload(inspect.getmodule(f)), fn_name)
        yield from f_hot_reload(*args, **kwargs)
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

    # 第三方库，需要预先pip install rarfile
    # 此外，Windows上还需要安装winrar软件，配置其Path环境变量，如"C:\Program Files\WinRAR"才可以
    elif file_extension == '.rar':
        try:
            import rarfile
            with rarfile.RarFile(file_path) as rf:
                rf.extractall(path=dest_dir)
                print("Successfully extracted rar archive to {}".format(dest_dir))
        except:
            print("Rar format requires additional dependencies to install")
            return '\n\n需要安装pip install rarfile来解压rar文件'

    # 第三方库，需要预先pip install py7zr
    elif file_extension == '.7z':
        try:
            import py7zr
            with py7zr.SevenZipFile(file_path, mode='r') as f:
                f.extractall(path=dest_dir)
                print("Successfully extracted 7z archive to {}".format(dest_dir))
        except:
            print("7z format requires additional dependencies to install")
            return '\n\n需要安装pip install py7zr来解压7z文件'
    else:
        return ''
    return ''

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
    err_msg = ''
    for file in files:
        file_origin_name = os.path.basename(file.orig_name)
        shutil.copy(file.name, f'private_upload/{time_tag}/{file_origin_name}')
        err_msg += extract_archive(f'private_upload/{time_tag}/{file_origin_name}',
                        dest_dir=f'private_upload/{time_tag}/{file_origin_name}.extract')
    moved_files = [fp for fp in glob.glob('private_upload/**/*', recursive=True)]
    txt = f'private_upload/{time_tag}'
    moved_files_str = '\t\n\n'.join(moved_files)
    chatbot.append(['我上传了文件，请查收',
                    f'[Local Message] 收到以下文件: \n\n{moved_files_str}'+
                    f'\n\n调用路径参数已自动修正到: \n\n{txt}'+
                    f'\n\n现在您点击任意实验功能时，以上文件将被作为输入参数'+err_msg])
    return chatbot, txt


def on_report_generated(files, chatbot):
    from toolbox import find_recent_files
    report_files = find_recent_files('gpt_log')
    if len(report_files) == 0: return report_files, chatbot
    # files.extend(report_files)
    chatbot.append(['汇总报告如何远程获取？', '汇总报告已经添加到右侧“文件上传区”（可能处于折叠状态），请查收。'])
    return report_files, chatbot

def get_conf(*args):
    # 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
    res = []
    for arg in args:
        try: r = getattr(importlib.import_module('config_private'), arg)
        except: r = getattr(importlib.import_module('config'), arg)
        res.append(r)
        # 在读取API_KEY时，检查一下是不是忘了改config
        if arg=='API_KEY':
            # 正确的 API_KEY 是 "sk-" + 48 位大小写字母数字的组合
            API_MATCH = re.match(r"sk-[a-zA-Z0-9]{48}$", r)
            if API_MATCH:
                print(f"您的 API_KEY 是: {r[:15]}*** \nAPI_KEY 导入成功")
            else:
                assert False, "正确的 API_KEY 是 'sk-' + '48 位大小写字母数字' 的组合，请在config文件中修改API密钥, 添加海外代理之后再运行。" + \
                            "（如果您刚更新过代码，请确保旧版config_private文件中没有遗留任何新增键值）"
    return res

def clear_line_break(txt):
    txt = txt.replace('\n', ' ')
    txt = txt.replace('  ', ' ')
    txt = txt.replace('  ', ' ')
    return txt
