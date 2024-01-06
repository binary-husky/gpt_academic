<<<<<<< HEAD
from predict import predict_no_ui
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
=======
from toolbox import update_ui, promote_file_to_downloadzone, gen_time_str
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import read_and_clean_pdf_text
from .crazy_utils import input_clipping



def 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    file_write_buffer = []
    for file_name in file_manifest:
        print('begin analysis on:', file_name)
        ############################## <第 0 步，切割PDF> ##################################
        # 递归地切割PDF文件，每一块（尽量是完整的一个section，比如introduction，experiment等，必要时再进行切割）
        # 的长度必须小于 2500 个 Token
        file_content, page_one = read_and_clean_pdf_text(file_name) # （尝试）按照章节切割PDF
        file_content = file_content.encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
        page_one = str(page_one).encode('utf-8', 'ignore').decode()  # avoid reading non-utf8 chars
        
        TOKEN_LIMIT_PER_FRAGMENT = 2500

        from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
        paper_fragments = breakdown_text_to_satisfy_token_limit(txt=file_content,  limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs['llm_model'])
        page_one_fragments = breakdown_text_to_satisfy_token_limit(txt=str(page_one), limit=TOKEN_LIMIT_PER_FRAGMENT//4, llm_model=llm_kwargs['llm_model'])
        # 为了更好的效果，我们剥离Introduction之后的部分（如果有）
        paper_meta = page_one_fragments[0].split('introduction')[0].split('Introduction')[0].split('INTRODUCTION')[0]
        
        ############################## <第 1 步，从摘要中提取高价值信息，放到history中> ##################################
        final_results = []
        final_results.append(paper_meta)

        ############################## <第 2 步，迭代地历遍整个文章，提取精炼信息> ##################################
        i_say_show_user = f'首先你在中文语境下通读整篇论文。'; gpt_say = "[Local Message] 收到。"           # 用户提示
        chatbot.append([i_say_show_user, gpt_say]); yield from update_ui(chatbot=chatbot, history=[])    # 更新UI

        iteration_results = []
        last_iteration_result = paper_meta  # 初始值是摘要
        MAX_WORD_TOTAL = 4096 * 0.7
        n_fragment = len(paper_fragments)
        if n_fragment >= 20: print('文章极长，不能达到预期效果')
        for i in range(n_fragment):
            NUM_OF_WORD = MAX_WORD_TOTAL // n_fragment
            i_say = f"Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} Chinese characters: {paper_fragments[i]}"
            i_say_show_user = f"[{i+1}/{n_fragment}] Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} Chinese characters: {paper_fragments[i][:200]}"
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user,  # i_say=真正给chatgpt的提问， i_say_show_user=给用户看的提问
                                                                                llm_kwargs, chatbot, 
                                                                                history=["The main idea of the previous section is?", last_iteration_result], # 迭代上一次的结果
                                                                                sys_prompt="Extract the main idea of this section with Chinese."  # 提示
                                                                                ) 
            iteration_results.append(gpt_say)
            last_iteration_result = gpt_say

        ############################## <第 3 步，整理history，提取总结> ##################################
        final_results.extend(iteration_results)
        final_results.append(f'Please conclude this paper discussed above。')
        # This prompt is from https://github.com/kaixindelele/ChatPaper/blob/main/chat_paper.py
        NUM_OF_WORD = 1000
        i_say = """
1. Mark the title of the paper (with Chinese translation)
2. list all the authors' names (use English)
3. mark the first author's affiliation (output Chinese translation only)
4. mark the keywords of this article (use English)
5. link to the paper, Github code link (if available, fill in Github:None if not)
6. summarize according to the following four points.Be sure to use Chinese answers (proper nouns need to be marked in English)
    - (1):What is the research background of this article?
    - (2):What are the past methods? What are the problems with them? Is the approach well motivated?
    - (3):What is the research methodology proposed in this paper?
    - (4):On what task and what performance is achieved by the methods in this paper? Can the performance support their goals?
Follow the format of the output that follows:                  
1. Title: xxx\n\n
2. Authors: xxx\n\n
3. Affiliation: xxx\n\n
4. Keywords: xxx\n\n
5. Urls: xxx or xxx , xxx \n\n
6. Summary: \n\n
    - (1):xxx;\n 
    - (2):xxx;\n 
    - (3):xxx;\n
    - (4):xxx.\n\n
Be sure to use Chinese answers (proper nouns need to be marked in English), statements as concise and academic as possible,
do not have too much repetitive information, numerical values using the original numbers.
        """
        # This prompt is from https://github.com/kaixindelele/ChatPaper/blob/main/chat_paper.py
        file_write_buffer.extend(final_results)
        i_say, final_results = input_clipping(i_say, final_results, max_token_limit=2000)
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user='开始最终总结', 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=final_results, 
            sys_prompt= f"Extract the main idea of this paper with less than {NUM_OF_WORD} Chinese characters"
        )
        final_results.append(gpt_say)
        file_write_buffer.extend([i_say, gpt_say])
        ############################## <第 4 步，设置一个token上限> ##################################
        _, final_results = input_clipping("", final_results, max_token_limit=3200)
        yield from update_ui(chatbot=chatbot, history=final_results) # 注意这里的历史记录被替代了

    res = write_history_to_file(file_write_buffer)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    yield from update_ui(chatbot=chatbot, history=final_results) # 刷新界面


@CatchException
def 批量总结PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结PDF文档。函数插件贡献者: ValeriaWong，Eralien"])
<<<<<<< HEAD
    yield chatbot, history, '正常'
=======
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
<<<<<<< HEAD
        report_execption(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield chatbot, history, '正常'
=======
        report_exception(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
<<<<<<< HEAD
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
=======
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.pdf', recursive=True)]
    
    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.tex或.pdf文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
