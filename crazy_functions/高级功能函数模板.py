<<<<<<< HEAD
from predict import predict_no_ui_long_connection
from toolbox import CatchException, report_execption, write_results_to_file
import datetime

@CatchException
def 高阶功能模板函数(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 请注意，您正在调用一个[函数插件]的模板，该函数面向希望实现更多有趣功能的开发者，它可以作为创建新功能函数的模板。为了做到简单易读，该函数只有25行代码，所以不会实时反馈文字流或心跳，请耐心等待程序输出完成。此外我们也提供可同步处理大量文件的多线程Demo供您参考。您若希望分享新的功能模组，请不吝PR！"))
    yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

=======
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
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
    for i in range(5):
        currentMonth = (datetime.date.today() + datetime.timedelta(days=i)).month
        currentDay = (datetime.date.today() + datetime.timedelta(days=i)).day
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？列举两条并发送相关图片。发送图片时，请使用Markdown，将Unsplash API中的PUT_YOUR_QUERY_HERE替换成描述该事件的一个最重要的单词。'
<<<<<<< HEAD
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

        # history = [] 每次询问不携带之前的询问历史
        gpt_say = predict_no_ui_long_connection(
            inputs=i_say, top_p=top_p, temperature=temperature, history=[], 
            sys_prompt="当你想发送一张照片时，请使用Markdown, 并且不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT_YOUR_QUERY_HERE >)。") # 请求gpt，需要一段时间

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield chatbot, history, '正常'  # 显示
=======
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="当你想发送一张照片时，请使用Markdown, 并且不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT_YOUR_QUERY_HERE >)。"
        )
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
>>>>>>> d883c7f34bcbb60b45767fd7eedeba2a703b7f13
