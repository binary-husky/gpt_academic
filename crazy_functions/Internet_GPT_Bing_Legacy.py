from toolbox import CatchException, update_ui
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, input_clipping
import requests
from bs4 import BeautifulSoup
from request_llms.bridge_all import model_info


def bing_search(query, proxies=None):
    query = query
    url = f"https://cn.bing.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
    response = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = []
    for g in soup.find_all('li', class_='b_algo'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            if not link.startswith('http'):
                continue
            title = g.find('h2').text
            item = {'title': title, 'link': link}
            results.append(item)

    # for r in results:
    #     print(r['link'])
    return results


def scrape_text(url, proxies) -> str:
    """Scrape text from a webpage

    Args:
        url (str): The URL to scrape text from

    Returns:
        str: The scraped text
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
        'Content-Type': 'text/plain',
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=8)
        if response.encoding == "ISO-8859-1": response.encoding = response.apparent_encoding
    except:
        return "无法连接到该网页"
    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text

@CatchException
def 连接bing搜索回答问题(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append((f"请结合互联网信息回答以下问题：{txt}",
                    "[Local Message] 请注意，您正在调用一个[函数插件]的模板，该模板可以实现ChatGPT联网信息综合。该函数面向希望实现更多有趣功能的开发者，它可以作为创建新功能函数的模板。您若希望分享新的功能模组，请不吝PR！"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

    # ------------- < 第1步：爬取搜索引擎的结果 > -------------
    from toolbox import get_conf
    proxies = get_conf('proxies')
    urls = bing_search(txt, proxies)
    history = []
    if len(urls) == 0:
        chatbot.append((f"结论：{txt}",
                        "[Local Message] 受到bing限制，无法从bing获取信息！"))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
        return
    # ------------- < 第2步：依次访问网页 > -------------
    max_search_result = 8   # 最多收纳多少个网页的结果
    for index, url in enumerate(urls[:max_search_result]):
        res = scrape_text(url['link'], proxies)
        history.extend([f"第{index}份搜索结果：", res])
        chatbot.append([f"第{index}份搜索结果：", res[:500]+"......"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

    # ------------- < 第3步：ChatGPT综合 > -------------
    i_say = f"从以上搜索结果中抽取信息，然后回答问题：{txt}"
    i_say, history = input_clipping(    # 裁剪输入，从最长的条目开始裁剪，防止爆token
        inputs=i_say,
        history=history,
        max_token_limit=model_info[llm_kwargs['llm_model']]['max_token']*3//4
    )
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=i_say,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
        sys_prompt="请从给定的若干条搜索结果中抽取信息，对最相关的两个搜索结果进行总结，然后回答问题。"
    )
    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say);history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

