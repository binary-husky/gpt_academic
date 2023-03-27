import os
import time

from loguru import logger
from ..utils import (
    catch_exception,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)
from pathlib import Path

FAST_DEBUG = False


def generate_comment_for_function(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt
):
    """
    Generates comments for all functions in the given file manifest using GPT-3.

    Args:
        file_manifest (list): A list of file paths to generate comments for.
        project_folder (str): The path to the project folder.
        top_p (float): The top_p value to use for GPT-3.
        temperature (float): The temperature value to use for GPT-3.
        chatbot (list): A list of chatbot messages.
        history (list): A list of chatbot message history.
        systemPromptTxt (str): The system prompt text to use for GPT-3.

    Yields:
        tuple: A tuple containing the updated chatbot messages, message history, and message type.

    """

    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        i_say = f"Please give an overview of the following program file and generate comments for all functions in the file, output the results using markdown tables. The file name is {os.path.relpath(fp, project_folder)}, and the file content is ```{file_content}```"
        i_say_show_user = f"[{index}/{len(file_manifest)}] Please give an overview of the following program file and generate comments for all functions in the file: {os.path.abspath(fp)}"
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield chatbot, history, "normal"

        if not FAST_DEBUG:
            msg = "normal"
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(
                i_say, i_say_show_user, chatbot, top_p, temperature, history=[]
            )  # with timeout countdown

            logger.info("[2] end gpt req")
            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            logger.info("[3] yield chatbot, history")
            yield chatbot, history, msg
            logger.info("[4] next")
            if not FAST_DEBUG:
                time.sleep(2)

    if not FAST_DEBUG:
        res = write_results_to_file(history)
        chatbot.append(("Are you done?", res))
        yield chatbot, history, msg


@catch_exception
def generate_comment_for_function_for_batch(
    txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT
):
    """
        Function: generate_comment_for_function_for_batch

    Parameters:
    - txt: str, path to the project folder or an empty string
    - top_p: float, top_p value for GPT-3 model
    - temperature: float, temperature value for GPT-3 model
    - chatbot: object, instance of the chatbot
    - history: list, chat history
    - systemPromptTxt: str, system prompt text
    - WEB_PORT: int, port number for web server

    Returns:
    - yields chatbot, history, and "normal" status

    Description:
    This function generates comments for functions in a batch of files. It takes in the path to the project folder, top_p and temperature values for the GPT-3 model, an instance of the chatbot, chat history, system prompt text, and the port number for the web server. It clears the chat history to avoid input overflow and imports the necessary modules. If the path to the project folder is empty or cannot be found, it reports an exception and returns "normal" status. If the project folder exists, it generates a list of all .py and .cpp files in the project folder and its subfolders. If no files are found, it reports an exception and returns "normal" status. Otherwise, it yields from the generate_comment_for_function function.

    """
    history = []  # clear history to avoid input overflow

    project_folder = Path(txt)
    if not project_folder.exists or not project_folder.is_dir():
        msg = "empty input field or path is not valid"
        report_execption(
            chatbot,
            history,
            a=f"parse project: {msg}",
            b=f"cannot find local project or access denied: {msg}",
        )
        yield chatbot, history, "normal"

    file_manifest = list(project_folder.rglob("*.py")) + list(
        project_folder.rglob("*cpp")
    )

    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"Parse project: {txt}",
            b=f"Cannot find any .tex files: {txt}",
        )
        yield chatbot, history, "normal"

    yield from generate_comment_for_function(
        file_manifest,
        project_folder,
        top_p,
        temperature,
        chatbot,
        history,
        systemPromptTxt,
    )
