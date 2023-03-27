from ..predict import predict_no_ui
from ..utils import catch_exception

FAST_DEBUG = False


@catch_exception
def func_template(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
    """
        Function: func_template

    Parameters:
    - txt: str, input text to be passed to GPT-3
    - top_p: float, top_p value for GPT-3
    - temperature: float, temperature value for GPT-3
    - chatbot: list, list of tuples containing chat history
    - history: list, list of previous inputs and outputs
    - systemPromptTxt: str, system prompt text for GPT-3
    - WEB_PORT: int, port number for web server

    Returns:
    - chatbot: list, updated list of tuples containing chat history
    - history: list, updated list of previous inputs and outputs
    - "Normal": str, status of the function

    Description:
    This function takes in input text, top_p value, temperature value, chatbot history, previous history, system prompt text, and web port number. It clears the history to avoid input overflow and then loops through 5 iterations. In each iteration, it prompts the user to give the square of a number and then sends the input to GPT-3 for a response. It updates the chatbot history with the input and GPT-3 response and appends them to the history list. It then yields the updated chatbot history, history list, and "Normal" status
    """

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
