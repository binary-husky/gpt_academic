"""
这是什么？
    这个文件用于函数插件的单元测试
    运行方法 python crazy_functions/crazy_functions_test.py
"""

def validate_path():
    import os, sys
    dir_name = os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) +  '/..')
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)
    
validate_path() # validate path so you can run from base directory
from colorful import *
from toolbox import get_conf, ChatBotWithCookies
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY = \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT', 'API_KEY')

llm_kwargs = {
    'api_key': API_KEY,
    'llm_model': LLM_MODEL,
    'top_p':1.0, 
    'max_length': None,
    'temperature':1.0,
}
plugin_kwargs = { }
chatbot = ChatBotWithCookies(llm_kwargs)
history = []
system_prompt = "Serve me as a writing and programming assistant."
web_port = 1024


def test_解析一个Python项目():
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    txt = "crazy_functions/test_project/python/dqn"
    for cookies, cb, hist, msg in 解析一个Python项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_解析一个Cpp项目():
    from crazy_functions.解析项目源代码 import 解析一个C项目
    txt = "crazy_functions/test_project/cpp/cppipc"
    for cookies, cb, hist, msg in 解析一个C项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_Latex英文润色():
    from crazy_functions.Latex全文润色 import Latex英文润色
    txt = "crazy_functions/test_project/latex/attention"
    for cookies, cb, hist, msg in Latex英文润色(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_Markdown中译英():
    from crazy_functions.批量Markdown翻译 import Markdown中译英
    txt = "README.md"
    for cookies, cb, hist, msg in Markdown中译英(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_批量翻译PDF文档():
    from crazy_functions.批量翻译PDF文档_多线程 import 批量翻译PDF文档
    txt = "crazy_functions/test_project/pdf_and_word"
    for cookies, cb, hist, msg in 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_谷歌检索小助手():
    from crazy_functions.谷歌检索小助手 import 谷歌检索小助手
    txt = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=auto+reinforcement+learning&btnG="
    for cookies, cb, hist, msg in 谷歌检索小助手(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_总结word文档():
    from crazy_functions.总结word文档 import 总结word文档
    txt = "crazy_functions/test_project/pdf_and_word"
    for cookies, cb, hist, msg in 总结word文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_下载arxiv论文并翻译摘要():
    from crazy_functions.下载arxiv论文翻译摘要 import 下载arxiv论文并翻译摘要
    txt = "1812.10695"
    for cookies, cb, hist, msg in 下载arxiv论文并翻译摘要(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        print(cb)

def test_联网回答问题():
    from crazy_functions.联网的ChatGPT import 连接网络回答问题
    # txt = "“我们称之为高效”是什么梗？"               #   
    # txt = "为什么说枪毙P社玩家没有一个冤枉的？"       #  
    # txt = "谁是应急食品？"                          #  '根据以上搜索结果可以得知，应急食品是“原神”游戏中的角色派蒙的外号。'
    # txt = "道路千万条，安全第一条。后面两句是？"      #  '行车不规范，亲人两行泪。'
    # txt = "特朗普为什么被捕了？"                    #  特朗普涉嫌向一名色情片女星付“封口费”，因此被刑事起诉，随后前往纽约市出庭受审。在不同的搜索结果中，可能会有不同的具体描述和表述方式。
    # txt = "丁仪砸了水滴之后发生了什么？"             # 丁仪用地质锤砸烂了水滴，这个行为让三体智子和其他观众们感到震惊和不解。在第1份搜索结果中，作者吐槽了一个脑洞——丁仪的破解方法是通过修炼、悟道和掌握一种新的“道”，称为“丁仪化身宇宙之道，可以轻易出现在宇宙的任何一个地方，.............
    txt = "What is in the canister?"                # 根据搜索结果并没有找到与 Rainbow Six Siege 游戏中 Smoke 的 Canister 中装有何种物质相关的官方信息。
    for cookies, cb, hist, msg in 连接网络回答问题(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port): print(cb)
    for i, it in enumerate(cb): print亮蓝(it[0]); print亮黄(it[1])

# test_解析一个Python项目()
# test_Latex英文润色()
# test_Markdown中译英()
# test_批量翻译PDF文档()
# test_谷歌检索小助手()
# test_总结word文档()
# test_下载arxiv论文并翻译摘要()
# test_解析一个Cpp项目()

test_联网回答问题()


input("程序完成，回车退出。")
print("退出。")