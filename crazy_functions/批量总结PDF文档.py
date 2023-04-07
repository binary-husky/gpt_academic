from request_llm.bridge_chatgpt import predict_no_ui
from toolbox import CatchException, report_execption, write_results_to_file, predict_no_ui_but_counting_down
import re
import unicodedata
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

def 解析PDF(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt):
    import time, glob, os, fitz
    print('begin analysis on:', file_manifest)
    for index, fp in enumerate(file_manifest):
        with fitz.open(fp) as doc:
            file_content = ""
            for page in doc:
                file_content += page.get_text()
            file_content = clean_text(file_content)
            print(file_content)

        prefix = "接下来请你逐文件分析下面的论文文件，概括其内容" if index==0 else ""
        i_say = prefix + f'请对下面的文章片段用中文做一个概述，文件名是{os.path.relpath(fp, project_folder)}，文章内容是 ```{file_content}```'
        i_say_show_user = prefix + f'[{index}/{len(file_manifest)}] 请对下面的文章片段做一个概述: {os.path.abspath(fp)}'
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        print('[1] yield chatbot, history')
        yield chatbot, history, '正常'

        if not fast_debug: 
            msg = '正常'
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say_show_user, chatbot, top_p, temperature, history=[])   # 带超时倒计时

            print('[2] end gpt req')
            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user); history.append(gpt_say)
            print('[3] yield chatbot, history')
            yield chatbot, history, msg
            print('[4] next')
            if not fast_debug: time.sleep(2)

    all_file = ', '.join([os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)])
    i_say = f'根据以上你自己的分析，对全文进行概括，用学术性语言写一段中文摘要，然后再写一段英文摘要（包括{all_file}）。'
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
    yield chatbot, history, '正常'

    if not fast_debug: 
        msg = '正常'
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(i_say, i_say, chatbot, top_p, temperature, history=history)   # 带超时倒计时

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say); history.append(gpt_say)
        yield chatbot, history, msg
        res = write_results_to_file(history)
        chatbot.append(("完成了吗？", res))
        yield chatbot, history, msg


@CatchException
def 批量总结PDF文档(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结PDF文档。函数插件贡献者: ValeriaWong，Eralien"])
    yield chatbot, history, '正常'

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_execption(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield chatbot, history, '正常'
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield chatbot, history, '正常'
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.pdf', recursive=True)] # + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.tex', recursive=True)] + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.cpp', recursive=True)] + \
                    # [f for f in glob.glob(f'{project_folder}/**/*.c', recursive=True)]
    
    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.tex或.pdf文件: {txt}")
        yield chatbot, history, '正常'
        return

    # 开始正式执行任务
    yield from 解析PDF(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)
