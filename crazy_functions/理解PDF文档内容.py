from toolbox import update_ui
from toolbox import CatchException, report_execption
from .crazy_utils import read_and_clean_pdf_text
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
fast_debug = False


def 解析PDF(file_name, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import tiktoken
    print('begin analysis on:', file_name)

    ############################## <第 0 步，切割PDF> ##################################
    # 递归地切割PDF文件，每一块（尽量是完整的一个section，比如introduction，experiment等，必要时再进行切割）
    # 的长度必须小于 2500 个 Token
    file_content, page_one = read_and_clean_pdf_text(file_name) # （尝试）按照章节切割PDF

    TOKEN_LIMIT_PER_FRAGMENT = 2500

    from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf
    from toolbox import get_conf
    enc = tiktoken.encoding_for_model(*get_conf('LLM_MODEL'))
    def get_token_num(txt): return len(enc.encode(txt))
    paper_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
        txt=file_content,  get_token_fn=get_token_num, limit=TOKEN_LIMIT_PER_FRAGMENT)
    page_one_fragments = breakdown_txt_to_satisfy_token_limit_for_pdf(
        txt=str(page_one), get_token_fn=get_token_num, limit=TOKEN_LIMIT_PER_FRAGMENT//4)
    # 为了更好的效果，我们剥离Introduction之后的部分（如果有）
    paper_meta = page_one_fragments[0].split('introduction')[0].split('Introduction')[0].split('INTRODUCTION')[0]
    
    ############################## <第 1 步，从摘要中提取高价值信息，放到history中> ##################################
    final_results = []
    final_results.append(paper_meta)

    ############################## <第 2 步，迭代地历遍整个文章，提取精炼信息> ##################################
    i_say_show_user = f'首先你在英文语境下通读整篇论文。'; gpt_say = "[Local Message] 收到。"           # 用户提示
    chatbot.append([i_say_show_user, gpt_say]); yield from update_ui(chatbot=chatbot, history=[])    # 更新UI

    iteration_results = []
    last_iteration_result = paper_meta  # 初始值是摘要
    MAX_WORD_TOTAL = 4096
    n_fragment = len(paper_fragments)
    if n_fragment >= 20: print('文章极长，不能达到预期效果')
    for i in range(n_fragment):
        NUM_OF_WORD = MAX_WORD_TOTAL // n_fragment
        i_say = f"Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words: {paper_fragments[i]}"
        i_say_show_user = f"[{i+1}/{n_fragment}] Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words: {paper_fragments[i][:200]}"
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user,  # i_say=真正给chatgpt的提问， i_say_show_user=给用户看的提问
                                                                           llm_kwargs, chatbot, 
                                                                           history=["The main idea of the previous section is?", last_iteration_result], # 迭代上一次的结果
                                                                           sys_prompt="Extract the main idea of this section."  # 提示
                                                                        ) 
        iteration_results.append(gpt_say)
        last_iteration_result = gpt_say

    ############################## <第 3 步，整理history> ##################################
    final_results.extend(iteration_results)
    final_results.append(f'接下来，你是一名专业的学术教授，利用以上信息，使用中文回答我的问题。')
    # 接下来两句话只显示在界面上，不起实际作用
    i_say_show_user = f'接下来，你是一名专业的学术教授，利用以上信息，使用中文回答我的问题。'; gpt_say = "[Local Message] 收到。"
    chatbot.append([i_say_show_user, gpt_say])

    ############################## <第 4 步，设置一个token上限，防止回答时Token溢出> ##################################
    from .crazy_utils import input_clipping
    _, final_results = input_clipping("", final_results, max_token_limit=3200)
    yield from update_ui(chatbot=chatbot, history=final_results) # 注意这里的历史记录被替代了


@CatchException
def 理解PDF文档内容标准文件输入(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "理解PDF论文内容，并且将结合上下文内容，进行学术解答。函数插件贡献者: Hanzoe, binary-husky"])
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
