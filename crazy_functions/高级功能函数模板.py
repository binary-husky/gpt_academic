from predict import predict_no_ui
from toolbox import CatchException, report_execption, write_results_to_file, predict_no_ui_but_counting_down
fast_debug = False

@CatchException
def 高阶功能模板函数(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    for i in range(5):
        i_say = f'我给出一个数字，你给出该数字的平方。我给出数字：{i}'
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, '正常'  # 由于请求gpt需要一段时间，我们先及时地做一次状态显示

        gpt_say = predict_no_ui(inputs=i_say, top_p=top_p, temperature=temperature) # 请求gpt，需要一段时间

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield chatbot, history, '正常'  # 显示