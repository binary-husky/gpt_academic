from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime, re

@CatchException
def 高阶功能模板函数(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 请注意，您正在调用一个[函数插件]的模板，该函数面向希望实现更多有趣功能的开发者，它可以作为创建新功能函数的模板（该函数只有20多行代码）。此外我们也提供可同步处理大量文件的多线程Demo供您参考。您若希望分享新的功能模组，请不吝PR！"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    for i in range(5):
        currentMonth = (datetime.date.today() + datetime.timedelta(days=i)).month
        currentDay = (datetime.date.today() + datetime.timedelta(days=i)).day
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？用中文列举两条，然后分别给出描述事件的两个英文单词。' + '当你给出关键词时，使用以下json格式：{"KeyWords":[EnglishKeyWord1,EnglishKeyWord2]}。'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt='输出格式示例：1908年，美国消防救援事业发展的“美国消防协会”成立。关键词：{"KeyWords":["Fire","American"]}。'
        )
        gpt_say = get_images(gpt_say)
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新


def get_images(gpt_say):
    def get_image_by_keyword(keyword):
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(f'https://wallhaven.cc/search?q={keyword}', timeout=2)
        for image_element in BeautifulSoup(response.content, 'html.parser').findAll("img"):
            if "data-src" in image_element: break
        return image_element["data-src"]

    for keywords in re.findall('{"KeyWords":\[(.*?)\]}', gpt_say):
        keywords = [n.strip('"') for n in keywords.split(',')]
        try:
            description = keywords[0]
            url = get_image_by_keyword(keywords[0])
            img_tag = f"\n\n![{description}]({url})"
            gpt_say += img_tag
        except:
            continue
    return gpt_say