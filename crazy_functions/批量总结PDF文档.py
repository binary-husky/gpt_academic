from loguru import logger

from toolbox import update_ui, promote_file_to_downloadzone, gen_time_str
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.crazy_utils import read_and_clean_pdf_text
from crazy_functions.crazy_utils import input_clipping



def 解析PDF(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    file_write_buffer = []
    for file_name in file_manifest:
        logger.info('begin analysis on:', file_name)
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
        if n_fragment >= 20: logger.warning('文章极长，不能达到预期效果')
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
def 批量总结PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结PDF文档。函数插件贡献者: ValeriaWong，Eralien"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_exception(chatbot, history,
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
        if txt == "": txt = '空空如也的输入栏'
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
