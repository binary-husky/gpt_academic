from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime
@CatchException
def 高阶功能模板函数(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
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
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？列举两条并发送相关图片。发送图片时，请使用Markdown，将Unsplash API中的PUT_YOUR_QUERY_HERE替换成描述该事件的一个最重要的单词。'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="当你想发送一张照片时，请使用Markdown, 并且不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT_YOUR_QUERY_HERE >)。"
        )
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新




PROMPT = """
请你给出围绕“{subject}”的逻辑关系图，使用mermaid语法，mermaid语法举例：
```mermaid
graph TD
    P(编程) --> L1(Python)
    P(编程) --> L2(C)
    P(编程) --> L3(C++)
    P(编程) --> L4(Javascipt)
    P(编程) --> L5(PHP)
```
"""
@CatchException
def 测试图表渲染(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "一个测试mermaid绘制图表的功能，您可以在输入框中输入一些关键词，然后使用mermaid+llm绘制图表。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    
    if txt == "": txt = "空白的输入栏" # 调皮一下
    
    i_say_show_user = f'请绘制有关“{txt}”的逻辑关系图。'
    i_say = PROMPT.format(subject=txt)
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say,
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=""
    )
    history.append(i_say); history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新