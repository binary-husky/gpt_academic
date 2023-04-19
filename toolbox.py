import markdown
import importlib
import traceback
import inspect
import re
from latex2mathml.converter import convert as tex2mathml
from functools import wraps, lru_cache
############################### 插件输入输出接驳区 #######################################
class ChatBotWithCookies(list):
    def __init__(self, cookie):
        self._cookies = cookie

    def write_list(self, list):
        for t in list:
            self.append(t)

    def get_list(self):
        return [t for t in self]

    def get_cookies(self):
        return self._cookies

def ArgsGeneralWrapper(f):
    """
    装饰器函数，用于重组输入参数，改变输入参数的顺序与结构。
    """
    def decorated(cookies, max_length, llm_model, txt, txt2, top_p, temperature, chatbot, history, system_prompt, *args):
        txt_passon = txt
        if txt == "" and txt2 != "": txt_passon = txt2
        # 引入一个有cookie的chatbot
        cookies.update({
            'top_p':top_p, 
            'temperature':temperature,
        })
        llm_kwargs = {
            'api_key': cookies['api_key'],
            'llm_model': llm_model,
            'top_p':top_p, 
            'max_length': max_length,
            'temperature':temperature,
        }
        plugin_kwargs = {
            # 目前还没有
        }
        chatbot_with_cookie = ChatBotWithCookies(cookies)
        chatbot_with_cookie.write_list(chatbot)
        yield from f(txt_passon, llm_kwargs, plugin_kwargs, chatbot_with_cookie, history, system_prompt, *args)
    return decorated

def update_ui(chatbot, history, msg='正常', **kwargs):  # 刷新界面
    """
    刷新用户界面
    """
    assert isinstance(chatbot, ChatBotWithCookies), "在传递chatbot的过程中不要将其丢弃。必要时，可用clear将其清空，然后用for+append循环重新赋值。"
    yield chatbot.get_cookies(), chatbot, history, msg

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
            tb_str = '```\n' + traceback.format_exc() + '```'
            if chatbot is None or len(chatbot) == 0:
                chatbot = [["插件调度异常", "异常原因"]]
            chatbot[-1] = (chatbot[-1][0],
                           f"[Local Message] 实验性函数调用出错: \n\n{tb_str} \n\n当前代理可用性: \n\n{check_proxy(proxies)}")
            yield from update_ui(chatbot=chatbot, history=history, msg=f'异常 {e}') # 刷新界面
    return decorated


def HotReload(f):
    """
    HotReload的装饰器函数，用于实现Python函数插件的热更新。
    函数热更新是指在不停止程序运行的情况下，更新函数代码，从而达到实时更新功能。
    在装饰器内部，使用wraps(f)来保留函数的元信息，并定义了一个名为decorated的内部函数。
    内部函数通过使用importlib模块的reload函数和inspect模块的getmodule函数来重新加载并获取函数模块，
    然后通过getattr函数获取函数名，并在新模块中重新加载函数。
    最后，使用yield from语句返回重新加载过的函数，并在被装饰的函数上执行。
    最终，装饰器函数返回内部函数。这个内部函数可以将函数的原始定义更新为最新版本，并执行函数的新版本。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        fn_name = f.__name__
        f_hot_reload = getattr(importlib.reload(inspect.getmodule(f)), fn_name)
        yield from f_hot_reload(*args, **kwargs)
    return decorated


####################################### 其他小工具 #####################################

def get_reduce_token_percent(text):
    """
        * 此函数未来将被弃用
    """
    try:
        # text = "maximum context length is 4097 tokens. However, your messages resulted in 4870 tokens"
        pattern = r"(\d+)\s+tokens\b"
        match = re.findall(pattern, text)
        EXCEED_ALLO = 500  # 稍微留一点余地，否则在回复时会因余量太少出问题
        max_limit = float(match[0]) - EXCEED_ALLO
        current_tokens = float(match[1])
        ratio = max_limit/current_tokens
        assert ratio > 0 and ratio < 1
        return ratio, str(int(current_tokens-max_limit))
    except:
        return 0.5, '不详'



def write_results_to_file(history, file_name=None):
    """
    将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os
    import time
    if file_name is None:
        # file_name = time.strftime("chatGPT分析报告%Y-%m-%d-%H-%M-%S", time.localtime()) + '.md'
        file_name = 'chatGPT分析报告' + \
            time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.md'
    os.makedirs('./gpt_log/', exist_ok=True)
    with open(f'./gpt_log/{file_name}', 'w', encoding='utf8') as f:
        f.write('# chatGPT 分析报告\n')
        for i, content in enumerate(history):
            try:    # 这个bug没找到触发条件，暂时先这样顶一下
                if type(content) != str:
                    content = str(content)
            except:
                continue
            if i % 2 == 0:
                f.write('## ')
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




def report_execption(chatbot, history, a, b):
    """
    向chatbot中添加错误信息
    """
    chatbot.append((a, b))
    history.append(a)
    history.append(b)


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
    pre = '<div class="markdown-body">'
    suf = '</div>'
    markdown_extension_configs = {
        'mdx_math': {
            'enable_dollar_delimiter': True,
            'use_gitlab_delimiters': False,
        },
    }
    find_equation_pattern = r'<script type="math/tex(?:.*?)>(.*?)</script>'

    def tex2mathml_catch_exception(content, *args, **kwargs):
        try:
            content = tex2mathml(content, *args, **kwargs)
        except:
            content = content
        return content

    def replace_math_no_render(match):
        content = match.group(1)
        if 'mode=display' in match.group(0):
            content = content.replace('\n', '</br>')
            return f"<font color=\"#00FF00\">$$</font><font color=\"#FF00FF\">{content}</font><font color=\"#00FF00\">$$</font>"
        else:
            return f"<font color=\"#00FF00\">$</font><font color=\"#FF00FF\">{content}</font><font color=\"#00FF00\">$</font>"

    def replace_math_render(match):
        content = match.group(1)
        if 'mode=display' in match.group(0):
            if '\\begin{aligned}' in content:
                content = content.replace('\\begin{aligned}', '\\begin{array}')
                content = content.replace('\\end{aligned}', '\\end{array}')
                content = content.replace('&', ' ')
            content = tex2mathml_catch_exception(content, display="block")
            return content
        else:
            return tex2mathml_catch_exception(content)
        
    def markdown_bug_hunt(content):
        """
        解决一个mdx_math的bug（单$包裹begin命令时多余<script>）
        """
        content = content.replace('<script type="math/tex">\n<script type="math/tex; mode=display">', '<script type="math/tex; mode=display">')
        content = content.replace('</script>\n</script>', '</script>')
        return content
    

    if ('$' in txt) and ('```' not in txt):  # 有$标识的公式符号，且没有代码段```的标识
        # convert everything to html format
        split = markdown.markdown(text='---')
        convert_stage_1 = markdown.markdown(text=txt, extensions=['mdx_math', 'fenced_code', 'tables', 'sane_lists'], extension_configs=markdown_extension_configs)
        convert_stage_1 = markdown_bug_hunt(convert_stage_1)
        # re.DOTALL: Make the '.' special character match any character at all, including a newline; without this flag, '.' will match anything except a newline. Corresponds to the inline flag (?s).
        # 1. convert to easy-to-copy tex (do not render math)
        convert_stage_2_1, n = re.subn(find_equation_pattern, replace_math_no_render, convert_stage_1, flags=re.DOTALL)
        # 2. convert to rendered equation
        convert_stage_2_2, n = re.subn(find_equation_pattern, replace_math_render, convert_stage_1, flags=re.DOTALL)
        # cat them together
        return pre + convert_stage_2_1 + f'{split}' + convert_stage_2_2 + suf
    else:
        return pre + markdown.markdown(txt, extensions=['fenced_code', 'codehilite', 'tables', 'sane_lists']) + suf


def close_up_code_segment_during_stream(gpt_reply):
    """
    在gpt输出代码的中途（输出了前面的```，但还没输出完后面的```），补上后面的```
    
    Args:
        gpt_reply (str): GPT模型返回的回复字符串。

    Returns:
        str: 返回一个新的字符串，将输出代码片段的“后面的```”补上。

    """
    if '```' not in gpt_reply:
        return gpt_reply
    if gpt_reply.endswith('```'):
        return gpt_reply

    # 排除了以上两个情况，我们
    segments = gpt_reply.split('```')
    n_mark = len(segments) - 1
    if n_mark % 2 == 1:
        # print('输出代码片段中！')
        return gpt_reply+'\n```'
    else:
        return gpt_reply


def format_io(self, y):
    """
    将输入和输出解析为HTML格式。将y中最后一项的输入部分段落化，并将输出部分的Markdown和数学公式转换为HTML格式。
    """
    if y is None or y == []:
        return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask)  # 输入部分太自由，预处理一波
    gpt_reply = close_up_code_segment_during_stream(gpt_reply)  # 当代码输出半截的时候，试着补上后个```
    y[-1] = (
        None if i_ask is None else markdown.markdown(i_ask, extensions=['fenced_code', 'tables']),
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
        if file_path.endswith('.log'):
            continue
        created_time = os.path.getmtime(file_path)
        if created_time >= one_minute_ago:
            if os.path.isdir(file_path):
                continue
            recent_files.append(file_path)

    return recent_files


def on_file_uploaded(files, chatbot, txt, txt2, checkboxes):
    if len(files) == 0:
        return chatbot, txt
    import shutil
    import os
    import time
    import glob
    from toolbox import extract_archive
    try:
        shutil.rmtree('./private_upload/')
    except:
        pass
    time_tag = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    os.makedirs(f'private_upload/{time_tag}', exist_ok=True)
    err_msg = ''
    for file in files:
        file_origin_name = os.path.basename(file.orig_name)
        shutil.copy(file.name, f'private_upload/{time_tag}/{file_origin_name}')
        err_msg += extract_archive(f'private_upload/{time_tag}/{file_origin_name}',
                                   dest_dir=f'private_upload/{time_tag}/{file_origin_name}.extract')
    moved_files = [fp for fp in glob.glob(
        'private_upload/**/*', recursive=True)]
    if "底部输入区" in checkboxes:
        txt = ""
        txt2 = f'private_upload/{time_tag}'
    else:
        txt = f'private_upload/{time_tag}'
        txt2 = ""
    moved_files_str = '\t\n\n'.join(moved_files)
    chatbot.append(['我上传了文件，请查收',
                    f'[Local Message] 收到以下文件: \n\n{moved_files_str}' +
                    f'\n\n调用路径参数已自动修正到: \n\n{txt}' +
                    f'\n\n现在您点击任意“红颜色”标识的函数插件时，以上文件将被作为输入参数'+err_msg])
    return chatbot, txt, txt2


def on_report_generated(files, chatbot):
    from toolbox import find_recent_files
    report_files = find_recent_files('gpt_log')
    if len(report_files) == 0:
        return None, chatbot
    # files.extend(report_files)
    chatbot.append(['汇总报告如何远程获取？', '汇总报告已经添加到右侧“文件上传区”（可能处于折叠状态），请查收。'])
    return report_files, chatbot

def is_openai_api_key(key):
    API_MATCH = re.match(r"sk-[a-zA-Z0-9]{48}$", key)
    return bool(API_MATCH)

def is_api2d_key(key):
    if key.startswith('fk') and len(key) == 41:
        return True
    else:
        return False

def is_any_api_key(key):
    if ',' in key:
        keys = key.split(',')
        for k in keys:
            if is_any_api_key(k): return True
        return False
    else:
        return is_openai_api_key(key) or is_api2d_key(key)


def select_api_key(keys, llm_model):
    import random
    avail_key_list = []
    key_list = keys.split(',')

    if llm_model.startswith('gpt-'):
        for k in key_list:
            if is_openai_api_key(k): avail_key_list.append(k)

    if llm_model.startswith('api2d-'):
        for k in key_list:
            if is_api2d_key(k): avail_key_list.append(k)

    if len(avail_key_list) == 0:
        raise RuntimeError(f"您提供的api-key不满足要求，不包含任何可用于{llm_model}的api-key。")

    api_key = random.choice(avail_key_list) # 随机负载均衡
    return api_key

@lru_cache(maxsize=128)
def read_single_conf_with_lru_cache(arg):
    from colorful import print亮红, print亮绿, print亮蓝
    try:
        r = getattr(importlib.import_module('config_private'), arg)
    except:
        r = getattr(importlib.import_module('config'), arg)
    # 在读取API_KEY时，检查一下是不是忘了改config
    if arg == 'API_KEY':
        print亮蓝(f"[API_KEY] 本项目现已支持OpenAI和API2D的api-key。也支持同时填写多个api-key，如API_KEY=\"openai-key1,openai-key2,api2d-key3\"")
        print亮蓝(f"[API_KEY] 您既可以在config.py中修改api-key(s)，也可以在问题输入区输入临时的api-key(s)，然后回车键提交后即可生效。")
        if is_any_api_key(r):
            print亮绿(f"[API_KEY] 您的 API_KEY 是: {r[:15]}*** API_KEY 导入成功")
        else:
            print亮红( "[API_KEY] 正确的 API_KEY 是'sk'开头的51位密钥（OpenAI），或者 'fk'开头的41位密钥，请在config文件中修改API密钥之后再运行。")
    if arg == 'proxies':
        if r is None:
            print亮红('[PROXY] 网络代理状态：未配置。无代理状态下很可能无法访问OpenAI家族的模型。建议：检查USE_PROXY选项是否修改。')
        else:
            print亮绿('[PROXY] 网络代理状态：已配置。配置信息如下：', r)
            assert isinstance(r, dict), 'proxies格式错误，请注意proxies选项的格式，不要遗漏括号。'
    return r


def get_conf(*args):
    # 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
    res = []
    for arg in args:
        r = read_single_conf_with_lru_cache(arg)
        res.append(r)
    return res


def clear_line_break(txt):
    txt = txt.replace('\n', ' ')
    txt = txt.replace('  ', ' ')
    txt = txt.replace('  ', ' ')
    return txt


class DummyWith():
    """
    这段代码定义了一个名为DummyWith的空上下文管理器，
    它的作用是……额……没用，即在代码结构不变得情况下取代其他的上下文管理器。
    上下文管理器是一种Python对象，用于与with语句一起使用，
    以确保一些资源在代码块执行期间得到正确的初始化和清理。
    上下文管理器必须实现两个方法，分别为 __enter__()和 __exit__()。 
    在上下文执行开始的情况下，__enter__()方法会在代码块被执行前被调用，
    而在上下文执行结束时，__exit__()方法则会被调用。
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return
