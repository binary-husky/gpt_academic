from toolbox import CatchException, update_ui, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, input_clipping
import requests
from bs4 import BeautifulSoup
from request_llms.bridge_all import model_info
import urllib.request
import random
from functools import lru_cache
from check_proxy import check_proxy
from .prompts.Search import Search_optimizer, Search_academic_optimizer

def optimizer(query, proxies, categories='general', searxng_url=None, engines=None):
    # ------------- < 第1步：尝试进行搜索优化 > -------------
    pass

@lru_cache
def get_auth_ip():
    ip = check_proxy(None, return_ip=True)
    if ip is None:
        return '114.114.114.' + str(random.randint(1, 10))
    return ip

def searxng_request(query, proxies, categories='general', searxng_url=None, engines=None):
    if searxng_url is None:
        url = get_conf("SEARXNG_URL")
    else:
        url = searxng_url

    if engines == "Mixed":
        engines = None

    if categories == 'general':
        params = {
            'q': query,         # 搜索查询
            'format': 'json',   # 输出格式为JSON
            'language': 'zh',   # 搜索语言
            'engines': engines,
        }
    elif categories == 'science':
        params = {
            'q': query,         # 搜索查询
            'format': 'json',   # 输出格式为JSON
            'language': 'zh',   # 搜索语言
            'categories': 'science'
        }
    else:
        raise ValueError('不支持的检索类型')

    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'X-Forwarded-For': get_auth_ip(),
        'X-Real-IP': get_auth_ip()
    }
    results = []
    response = requests.post(url, params=params, headers=headers, proxies=proxies, timeout=30)
    if response.status_code == 200:
        json_result = response.json()
        for result in json_result['results']:
            item = {
                "title": result.get("title", ""),
                "source": result.get("engines", "unknown"),
                "content": result.get("content", ""),
                "link": result["url"],
            }
            results.append(item)
        return results
    else:
        if response.status_code == 429:
            raise ValueError("Searxng（在线搜索服务）当前使用人数太多，请稍后。")
        else:
            raise ValueError("在线搜索失败，状态码: " + str(response.status_code) + '\t' + response.content.decode('utf-8'))

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
def 连接网络回答问题(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    optimizer_history = history[:-8]
    history = []    # 清空历史，以免输入溢出
    chatbot.append((f"请结合互联网信息回答以下问题：{txt}", "检索中..."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # ------------- < 第1步：爬取搜索引擎的结果 > -------------
    from toolbox import get_conf
    proxies = get_conf('proxies')
    categories = plugin_kwargs.get('categories', 'general')
    searxng_url = plugin_kwargs.get('searxng_url', None)
    engines = plugin_kwargs.get('engine', None)
    optimizer = plugin_kwargs.get('optimizer', 0)
    urls = searxng_request(txt, proxies, categories, searxng_url, engines=engines)
    history = []
    if len(urls) == 0:
        chatbot.append((f"结论：{txt}",
                        "[Local Message] 受到限制，无法从searxng获取信息！请尝试更换搜索引擎。"))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    # ------------- < 第2步：依次访问网页 > -------------
    max_search_result = 5   # 最多收纳多少个网页的结果
    chatbot.append(["联网检索中 ...", None])
    for index, url in enumerate(urls[:max_search_result]):
        res = scrape_text(url['link'], proxies)
        prefix = f"第{index}份搜索结果 [源自{url['source'][0]}搜索] （{url['title'][:25]}）："
        history.extend([prefix, res])
        res_squeeze = res.replace('\n', '...')
        chatbot[-1] = [prefix + "\n\n" + res_squeeze[:500] + "......", None]
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # ------------- < 第3步：ChatGPT综合 > -------------
    if optimizer == 0:
        i_say = f"从以上搜索结果中抽取信息，然后回答问题：{txt}"
        i_say, history = input_clipping(    # 裁剪输入，从最长的条目开始裁剪，防止爆token
            inputs=i_say,
            history=history,
            max_token_limit=min(model_info[llm_kwargs['llm_model']]['max_token']*3//4, 8192)
        )
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
            sys_prompt="请从给定的若干条搜索结果中抽取信息，对最相关的两个搜索结果进行总结，然后回答问题。"
        )
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
    #* 或者使用搜索优化器，这样可以保证后续问答能读取到有效的历史记录
    else:
        i_say = f"从以上搜索结果中抽取与问题：{txt} 相关的信息，"
        i_say, history = input_clipping(    # 裁剪输入，从最长的条目开始裁剪，防止爆token
            inputs=i_say,
            history=history,
            max_token_limit=min(model_info[llm_kwargs['llm_model']]['max_token']*3//4, 8192)
        )
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
            sys_prompt="请从给定的若干条搜索结果中抽取信息，对最相关的三个搜索结果进行总结"
        )
        chatbot[-1] = (i_say, gpt_say)
        history = []
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

        # ------------- < 第4步：根据综合回答问题 > -------------
        i_say = f"请根据以上搜索结果回答问题：{txt}"
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
            sys_prompt="请根据给定的若干条搜索结果回答问题"
        )
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history)