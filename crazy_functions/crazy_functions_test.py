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
    # txt = "“我们称之为高效”是什么梗？"
    # >>        从第0份、第1份、第2份搜索结果可以看出，“我们称之为高效”是指在游戏社区中，用户们用来形容一些游戏策略或行为非常高效且能够带来好的效果的用语。这个用语最初可能是在群星（Stellaris）这个游戏里面流行起来的，后来也传播到了其他游戏中，比如巨像（Titan）等游戏。其中第1份搜索结果中的一篇文章也指出，“我们称之为高效”这 一用语来源于群星（Stellaris）游戏中的一个情节。
    # txt = "为什么说枪毙P社玩家没有一个冤枉的？"
    # >>        它们都是关于一个知乎用户所发的帖子，引用了一群游戏玩家对于需要对P社玩家进行枪毙的讨论，这个话题的本质是玩家们对于P 社游戏中的政治与历史元素的不同看法，以及其中不少玩家以极端立场宣扬的想法和言论，因此有人就以枪毙这些玩家来回应此类言论。但是这个话题本身并没有实质内容，只是一个玩笑或者恶搞，并不应该被当做真实的态度或者观点，因此这种说法没有实际意义。
    # txt = "谁是应急食品？"
    # >>        '根据以上搜索结果可以得知，应急食品是“原神”游戏中的角色派蒙的外号。'
    # txt = "道路千万条，安全第一条。后面两句是？"
    # >>        '行车不规范，亲人两行泪。'
    # txt = "What is in the canister?"
    # >>        Rainbow Six Siege 游戏中 Smoke 的 Canister 中装有何种物质相关的官方信息。
    # txt = "失败的man是什么?"
    # >>        根据第1份搜索结果，可以得知失败的man是指一位在B站购买了蜘蛛侠COS服后穿上后被网友嘲笑的UP主，而“失败的man”是蜘蛛侠英文名“spiderman”的谐音梗，并且网友们还 给这位UP主起了“苍蝇侠”的外号。因此，失败的man是指这位UP主在穿上蜘蛛侠COS服后被网友嘲笑的情况。
    # txt = "老六是什么，起源于哪里？"
    # >>        老六是网络流行语，最初起源于游戏《CSGO》，指游戏中玩家中独来独往、游离于队伍之外的“自由人”或玩得比较菜或者玩得比较阴险的人 ，后来逐渐演变成指玩得比较阴险的玩家。
    # txt = "罗小黑战记因为什么经常被吐槽？"
    # >>        3. 更新速度。罗小黑战记的更新时间不定，时而快时而慢，给观众留下了等待的时间过长的印象。
    # txt = "沙特、伊朗最近的关系如何？"
    # >>        最近在中国的斡旋下，沙特和伊朗于3月10日达成了恢复两国外交关系的协议，这表明两国关系已经重新回到正常化状态。
    # txt = "You should have gone for the head. What does that mean?"
    # >>        The phrase "You should have gone for the head" is a quote from the Marvel movies, Avengers: Infinity War and Avengers: Endgame. It was spoken by the character Thanos in Infinity War and by Thor in Endgame.
    txt = "AutoGPT是什么？"
    # >>        AutoGPT是一个基于GPT-4语言模型的开源应用程序。它可以根据用户需求自主执行任务，包括事件分析、营销方案撰写、代码编程、数学运算等等，并完全不需要用户插手。它可以自己思考，给出实现的步骤和实现细节，甚至可以自问自答执 行任务。最近它在GitHub上爆火，成为了业内最热门的项目之一。
    # txt = "钟离带什么圣遗物？"
    for cookies, cb, hist, msg in 连接网络回答问题(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port): 
        print("当前问答：", cb[-1][-1].replace("\n"," "))
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