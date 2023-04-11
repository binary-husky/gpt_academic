from toolbox import update_ui
from toolbox import CatchException, report_execption
import re
import unicodedata
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
fast_debug = False

def is_paragraph_break(match):
    """
    根据给定的匹配结果来判断换行符是否表示段落分隔。
    如果换行符前为句子结束标志（句号，感叹号，问号），且下一个字符为大写字母，则换行符更有可能表示段落分隔。
    也可以根据之前的内容长度来判断段落是否已经足够长。
    """
    prev_char, next_char = match.groups()

    # 句子结束标志
    sentence_endings = ".!?"

    # 设定一个最小段落长度阈值
    min_paragraph_length = 140

    if prev_char in sentence_endings and next_char.isupper() and len(match.string[:match.start(1)]) > min_paragraph_length:
        return "\n\n" 
    else:
        return " "

def normalize_text(text):
    """
    通过把连字（ligatures）等文本特殊符号转换为其基本形式来对文本进行归一化处理。
    例如，将连字 "fi" 转换为 "f" 和 "i"。
    """
    # 对文本进行归一化处理，分解连字
    normalized_text = unicodedata.normalize("NFKD", text)

    # 替换其他特殊字符
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', normalized_text)

    return cleaned_text

def clean_text(raw_text):
    """
    对从 PDF 提取出的原始文本进行清洗和格式化处理。
    1. 对原始文本进行归一化处理。
    2. 替换跨行的连词，例如 “Espe-\ncially” 转换为 “Especially”。
    3. 根据 heuristic 规则判断换行符是否是段落分隔，并相应地进行替换。
    """
    # 对文本进行归一化处理
    normalized_text = normalize_text(raw_text)

    # 替换跨行的连词
    text = re.sub(r'(\w+-\n\w+)', lambda m: m.group(1).replace('-\n', ''), normalized_text)

    # 根据前后相邻字符的特点，找到原文本中的换行符
    newlines = re.compile(r'(\S)\n(\S)')

    # 根据 heuristic 规则，用空格或段落分隔符替换原换行符
    final_text = re.sub(newlines, lambda m: m.group(1) + is_paragraph_break(m) + m.group(2), text)

    return final_text.strip()

def 解析PDF(file_name, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, glob, os, fitz
    print('begin analysis on:', file_name)

    with fitz.open(file_name) as doc:
        file_content = ""
        for page in doc:
            file_content += page.get_text()
        file_content = clean_text(file_content)
        # print(file_content)
    split_number = 10000
    split_group = (len(file_content)//split_number)+1
    for i in range(0,split_group):
        if i==0:
            prefix = "接下来请你仔细分析下面的论文，学习里面的内容（专业术语、公式、数学概念）.并且注意：由于论文内容较多，将分批次发送，每次发送完之后，你只需要回答“接受完成”"
            i_say = prefix + f'文件名是{file_name}，文章内容第{i+1}部分是 ```{file_content[i*split_number:(i+1)*split_number]}```'
            i_say_show_user = f'文件名是：\n{file_name},\n由于论文内容过长，将分批请求（共{len(file_content)}字符，将分为{split_group}批，每批{split_number}字符）。\n当前发送{i+1}/{split_group}部分'
        elif i==split_group-1:
            i_say = f'你只需要回答“所有论文接受完成，请进行下一步”。文章内容第{i+1}/{split_group}部分是 ```{file_content[i*split_number:]}```'
            i_say_show_user = f'当前发送{i+1}/{split_group}部分'
        else:
            i_say = f'你只需要回答“接受完成”。文章内容第{i+1}/{split_group}部分是 ```{file_content[i*split_number:(i+1)*split_number]}```'
            i_say_show_user = f'当前发送{i+1}/{split_group}部分'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user, llm_kwargs, chatbot, history=[], sys_prompt="")   # 带超时倒计时
        while "完成" not in gpt_say:
            i_say = f'你只需要回答“接受完成”。文章内容第{i+1}/{split_group}部分是 ```{file_content[i*split_number:(i+1)*split_number]}```'
            i_say_show_user = f'出现error，重新发送{i+1}/{split_group}部分'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user, llm_kwargs, chatbot, history=[], sys_prompt="")   # 带超时倒计时
            time.sleep(1)
        chatbot[-1] = (i_say_show_user, gpt_say)
        history.append(i_say_show_user); history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        time.sleep(2)

    i_say = f'接下来，请你扮演一名专业的学术教授，利用你的所有知识并且结合这篇文章，回答我的问题。（请牢记：1.直到我说“退出”，你才能结束任务；2.所有问题需要紧密围绕文章内容;3.如果有公式，请使用tex渲染)'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # ** gpt request **
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say, llm_kwargs, chatbot, history=history, sys_prompt="")   # 带超时倒计时
    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say); history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


@CatchException
def 理解PDF文档内容(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "理解PDF论文内容，并且将结合上下文内容，进行学术解答。函数插件贡献者: Hanzoe。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    txt = filedialog.askopenfilename()

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_execption(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 开始正式执行任务
    yield from 解析PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)



@CatchException
def 理解PDF文档内容标准文件输入(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "理解PDF论文内容，并且将结合上下文内容，进行学术解答。函数插件贡献者: Hanzoe。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_execption(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.pdf', recursive=True)]
    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.tex或.pdf文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    txt = file_manifest[0]
    # 开始正式执行任务
    yield from 解析PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
