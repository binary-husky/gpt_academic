from predict import predict_no_ui_long_connection
from toolbox import CatchException, report_execption, write_results_to_file
import datetime

@CatchException
def 高阶功能模板函数(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    for i in range(5):
        currentMonth = (datetime.date.today() + datetime.timedelta(days=i)).month
        currentDay = (datetime.date.today() + datetime.timedelta(days=i)).day
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？列举两条并发送相关图片。'
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

        # history = [] 每次询问不携带之前的询问历史
        gpt_say = predict_no_ui_long_connection(inputs=i_say, top_p=top_p, temperature=temperature, history=[], sys_prompt="当你想发送一张照片时，请使用 Markdown ,并且 不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT YOUR QUERY HERE >)。") # 请求gpt，需要一段时间

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield chatbot, history, '正常'  # 显示