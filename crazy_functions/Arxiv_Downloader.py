import re, requests, unicodedata, os
from toolbox import update_ui, get_log_folder
from toolbox import write_history_to_file, promote_file_to_downloadzone
from toolbox import CatchException, report_exception, get_conf
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from loguru import logger

def download_arxiv_(url_pdf):
    if 'arxiv.org' not in url_pdf:
        if ('.' in url_pdf) and ('/' not in url_pdf):
            new_url = 'https://arxiv.org/abs/'+url_pdf
            logger.info('下载编号：', url_pdf, '自动定位：', new_url)
            # download_arxiv_(new_url)
            return download_arxiv_(new_url)
        else:
            logger.info('不能识别的URL！')
            return None
    if 'abs' in url_pdf:
        url_pdf = url_pdf.replace('abs', 'pdf')
        url_pdf = url_pdf + '.pdf'

    url_abs = url_pdf.replace('.pdf', '').replace('pdf', 'abs')
    title, other_info = get_name(_url_=url_abs)

    paper_id = title.split()[0]  # '[1712.00559]'
    if '2' in other_info['year']:
        title = other_info['year'] + ' ' + title

    known_conf = ['NeurIPS', 'NIPS', 'Nature', 'Science', 'ICLR', 'AAAI']
    for k in known_conf:
        if k in other_info['comment']:
            title = k + ' ' + title

    download_dir = get_log_folder(plugin_name='arxiv')
    os.makedirs(download_dir, exist_ok=True)

    title_str = title.replace('?', '？')\
        .replace(':', '：')\
        .replace('\"', '“')\
        .replace('\n', '')\
        .replace('  ', ' ')\
        .replace('  ', ' ')

    requests_pdf_url = url_pdf
    file_path = download_dir+title_str

    logger.info('下载中')
    proxies = get_conf('proxies')
    r = requests.get(requests_pdf_url, proxies=proxies)
    with open(file_path, 'wb+') as f:
        f.write(r.content)
    logger.info('下载完成')

    x = "%s  %s %s.bib" % (paper_id, other_info['year'], other_info['authors'])
    x = x.replace('?', '？')\
        .replace(':', '：')\
        .replace('\"', '“')\
        .replace('\n', '')\
        .replace('  ', ' ')\
        .replace('  ', ' ')
    return file_path, other_info


def get_name(_url_):
    from bs4 import BeautifulSoup
    logger.info('正在获取文献名！')
    logger.info(_url_)

    proxies = get_conf('proxies')
    res = requests.get(_url_, proxies=proxies)

    bs = BeautifulSoup(res.text, 'html.parser')
    other_details = {}

    # get year
    try:
        year = bs.find_all(class_='dateline')[0].text
        year = re.search(r'(\d{4})', year, re.M | re.I).group(1)
        other_details['year'] = year
        abstract = bs.find_all(class_='abstract mathjax')[0].text
        other_details['abstract'] = abstract
    except:
        other_details['year'] = ''
        logger.info('年份获取失败')

    # get author
    try:
        authors = bs.find_all(class_='authors')[0].text
        authors = authors.split('Authors:')[1]
        other_details['authors'] = authors
    except:
        other_details['authors'] = ''
        logger.info('authors获取失败')

    # get comment
    try:
        comment = bs.find_all(class_='metatable')[0].text
        real_comment = None
        for item in comment.replace('\n', ' ').split('   '):
            if 'Comments' in item:
                real_comment = item
        if real_comment is not None:
            other_details['comment'] = real_comment
        else:
            other_details['comment'] = ''
    except:
        other_details['comment'] = ''
        logger.info('年份获取失败')

    title_str = BeautifulSoup(
        res.text, 'html.parser').find('title').contents[0]
    logger.info('获取成功：', title_str)
    # arxiv_recall[_url_] = (title_str+'.pdf', other_details)
    # with open('./arxiv_recall.pkl', 'wb') as f:
    #     pickle.dump(arxiv_recall, f)

    return title_str+'.pdf', other_details



@CatchException
def 下载arxiv论文并翻译摘要(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    CRAZY_FUNCTION_INFO = "下载arxiv论文并翻译摘要，函数插件作者[binary-husky]。正在提取摘要并下载PDF文档……"
    import glob
    import os

    # 基本信息：功能、贡献者
    chatbot.append(["函数插件功能？", CRAZY_FUNCTION_INFO])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import bs4
    except:
        report_exception(chatbot, history,
            a = f"解析项目: {txt}",
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade beautifulsoup4```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 提取摘要，下载PDF文档
    try:
        pdf_path, info = download_arxiv_(txt)
    except:
        report_exception(chatbot, history,
            a = f"解析项目: {txt}",
            b = f"下载pdf文件未成功")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 翻译摘要等
    i_say =            f"请你阅读以下学术论文相关的材料，提取摘要，翻译为中文。材料如下：{str(info)}"
    i_say_show_user =  f'请你阅读以下学术论文相关的材料，提取摘要，翻译为中文。论文：{pdf_path}'
    chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    msg = '正常'
    # ** gpt request **
    # 单线，获取文章meta信息
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say,
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot, history=[],
        sys_prompt="Your job is to collect information from materials and translate to Chinese。",
    )

    chatbot[-1] = (i_say_show_user, gpt_say)
    history.append(i_say_show_user); history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history, msg=msg) # 刷新界面
    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    promote_file_to_downloadzone(pdf_path, chatbot=chatbot)

    chatbot.append(("完成了吗？", res + "\n\nPDF文件也已经下载"))
    yield from update_ui(chatbot=chatbot, history=history, msg=msg) # 刷新界面

