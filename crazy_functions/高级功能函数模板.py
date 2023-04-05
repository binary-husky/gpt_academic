from request_llm.bridge_chatgpt import predict_no_ui_long_connection
from toolbox import CatchException, report_execption, write_results_to_file
import datetime

@CatchException
def 高阶功能模板函数(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 请注意，您正在调用一个[函数插件]的模板，该函数面向希望实现更多有趣功能的开发者，它可以作为创建新功能函数的模板。为了做到简单易读，该函数只有25行代码，所以不会实时反馈文字流或心跳，请耐心等待程序输出完成。此外我们也提供可同步处理大量文件的多线程Demo供您参考。您若希望分享新的功能模组，请不吝PR！"))
    yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

    for i in range(5):
        currentMonth = (datetime.date.today() + datetime.timedelta(days=i)).month
        currentDay = (datetime.date.today() + datetime.timedelta(days=i)).day
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？列举两条并发送相关图片。发送图片时，请使用Markdown，将Unsplash API中的PUT_YOUR_QUERY_HERE替换成描述该事件的一个最重要的单词。'
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

        # history = [] 每次询问不携带之前的询问历史
        gpt_say = predict_no_ui_long_connection(
            inputs=i_say, top_p=top_p, temperature=temperature, history=[], 
            sys_prompt="当你想发送一张照片时，请使用Markdown, 并且不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT_YOUR_QUERY_HERE >)。") # 请求gpt，需要一段时间

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield chatbot, history, '正常'  # 显示