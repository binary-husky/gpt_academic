from ..predict import predict_no_ui
from ..utils import catch_exception

FAST_DEBUG = False


@catch_exception
def func_template(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    history = []  # Clear the history to avoid input overflow
    for i in range(5):
        i_say = f"I give you a number, you give me the square of that number. I give you the number:{i}"
        chatbot.append((i_say, "[Local Message] waiting gpt response."))
        yield chatbot, history, "Normal"  # Since requesting gpt takes some time, we promptly display the status

        gpt_say = predict_no_ui(
            inputs=i_say, top_p=top_p, temperature=temperature
        )  # Request gpt, which takes some time

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, "Normal"  # Display
