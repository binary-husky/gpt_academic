from pathlib import Path

from loguru import logger
from ..utils import (
    catch_exception,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)

import time

FAST_DEBUG = False


def parse_source_code(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemprompttxt
):
    """
    Function: parse_source_code

    This function takes in a file manifest, project folder, top_p, temperature, chatbot, history, and systemPromptTxt as input parameters. It analyzes each file in the file manifest and generates an overview of the program file. It then summarizes the overall function and structure of the program and organizes the function of each file using a markdown table.

    Parameters:
    - file_manifest: A list of file paths to be analyzed.
    - project_folder: The path to the project folder.
    - top_p: The nucleus sampling top_p value.
    - temperature: The nucleus sampling temperature value.
    - chatbot: A list of chatbot messages.
    - history: A list of chatbot message history.
    - systemPromptTxt: The system prompt text.

    Returns:
    - chatbot: A list of chatbot messages.
    - history: A list of chatbot message history.
    - msg: A message indicating the status of the function.
    """
    logger.info("begin analysis on:", file_manifest)
    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        prefix = (
            "next, please analyze the following project file by file."
            if index == 0
            else ""
        )
        i_say = (
            prefix
            + f"please give an overview of the following program file. the file name is {Path(fp).relative_to(project_folder)}, and the file code is ```{file_content}```"
        )
        i_say_show_user = (
            prefix
            + f"[{index}/{len(file_manifest)}] please give an overview of the following program file: {Path(fp).absolute()}"
        )
        chatbot.append((i_say_show_user, "[local message] waiting gpt response."))
        yield chatbot, history, "normal"

        if not FAST_DEBUG:
            msg = "normal"

            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(
                i_say, i_say_show_user, chatbot, top_p, temperature, history=[]
            )  # with timeout countdown

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            yield chatbot, history, msg
            if not FAST_DEBUG:
                time.sleep(2)

    all_file = ", ".join(
        [Path(fp).relative_to(project_folder) for index, fp in enumerate(file_manifest)]
    )
    i_say = f"based on your analysis above, summarize the overall function and structure of the program. then use a markdown table to organize the function of each file (including {all_file})."
    chatbot.append((i_say, "[local message] waiting gpt response."))
    yield chatbot, history, "normal"

    if not FAST_DEBUG:
        msg = "normal"
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(
            i_say, i_say, chatbot, top_p, temperature, history=history
        )  # with timeout countdown

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, msg
        res = write_results_to_file(history)
        chatbot.append(("are you done?", res))
        yield chatbot, history, msg


@catch_exception
def parse_project(txt, top_p, temperature, chatbot, history, systemprompttxt, web_port):
    """
        parse_project(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)

    This function takes in several parameters and performs the following actions:
    1. Clears the history to avoid input overflow
    2. Imports necessary modules
    3. Lists all python files in the current directory
    4. For each file, prompts the user to give an overview of the file's content
    5. Uses GPT to generate a response to the user's input
    6. Asks the user to summarize the overall function and structure of the program and organize the function of each file in a markdown table
    7. Uses GPT to generate a response to the user's input
    8. Writes the results to a file
    9. Asks the user if they are done

    Parameters:
    - txt: Not used in the function
    - top_p: Float value between 0 and 1 representing the nucleus sampling top probability
    - temperature: Float value representing the softmax temperature for sampling
    - chatbot: A list of tuples representing the conversation between the user and the chatbot
    - history: A list of strings representing the conversation history
    - systemPromptTxt: Not used in the function
    - WEB_PORT: Not used in the function

    Returns:
    - chatbot: A list of tuples representing the updated conversation between the user and the chatbot
    - history: A list of strings representing the updated conversation history
    - "normal": A string representing the status of the conversation
    """
    history = []  # clear history to avoid input overflow

    file_manifest = list(Path(".").glob("*.py"))

    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        prefix = (
            "next, please analyze your program composition. don't be nervous,"
            if index == 0
            else ""
        )
        i_say = (
            prefix
            + f"please give an overview of the following program file. the file name is {Path(fp).name}, and the file code is ```{file_content}```"
        )
        i_say_show_user = (
            prefix
            + f"[{index}/{len(file_manifest)}] please give an overview of the following program file: {Path(fp).absolute()}"
        )
        chatbot.append((i_say_show_user, "[local message] waiting gpt response."))
        yield chatbot, history, "normal"

        if not FAST_DEBUG:
            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(
                i_say, i_say_show_user, chatbot, top_p, temperature, history=[]
            )  # with timeout countdown

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            yield chatbot, history, "normal"
            time.sleep(2)

    i_say = f"based on your analysis above, summarize the overall function and structure of the program. then use a markdown table to organize the function of each file (including {file_manifest})."
    chatbot.append((i_say, "[local message] waiting gpt response."))
    yield chatbot, history, "normal"

    if not FAST_DEBUG:
        # ** gpt request **
        gpt_say = yield from predict_no_ui_but_counting_down(
            i_say, i_say, chatbot, top_p, temperature, history=history
        )  # with timeout countdown

        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say)
        history.append(gpt_say)
        yield chatbot, history, "normal"
        res = write_results_to_file(history)
        chatbot.append(("are you done?", res))
        yield chatbot, history, "normal"


@catch_exception
def parse_c_header(
    txt, top_p, temperature, chatbot, history, systemprompttxt, web_port
):
    """
    Function: parse_c_header

    Parameters:
    - txt: str, path to local project folder or empty string
    - top_p: float, top_p value for GPT-3 API
    - temperature: float, temperature value for GPT-3 API
    - chatbot: OpenAI API object, initialized with GPT-3 credentials
    - history: list, conversation history
    - systemPromptTxt: str, system prompt text for GPT-3 API
    - WEB_PORT: int, port number for web server

    Returns:
    - chatbot: OpenAI API object, initialized with GPT-3 credentials
    - history: list, conversation history
    - "normal": str, indicates normal conversation flow

    Description:
    This function takes in the path to a local project folder or an empty string, and uses glob to find all .h header files in the folder and its subfolders. If no .h header files are found, an exception is reported and the function returns. Otherwise, the function calls parse_source_code with the list of .h header files, project folder path, top_p, temperature, chatbot, history, and systemPromptTxt as parameters. The function yields the output of parse_source_code.

    """
    history = []  # clear history to avoid input overflow
    import glob
    import os

    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = "empty input field"
        report_execption(
            chatbot,
            history,
            a=f"parse project: {txt}",
            b=f"cannot find local project or access denied: {txt}",
        )
        yield chatbot, history, "normal"
        return
    file_manifest = list(glob.glob(f"{project_folder}/**/*.h", recursive=True))  # + \
    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"parse project: {txt}",
            b=f"cannot find any .h header files: {txt}",
        )
        yield chatbot, history, "normal"
        return
    yield from parse_source_code(
        file_manifest,
        project_folder,
        top_p,
        temperature,
        chatbot,
        history,
        systemprompttxt,
    )


@catch_exception
def parse_python_project(
    txt, top_p, temperature, chatbot, history, systemprompttxt, web_port
):
    """
    Parses all Python files in a given project folder and its subdirectories.

    :param txt: The path to the project folder.
    :type txt: str
    :param top_p: The top-p value to use when generating completions with the OpenAI API.
    :type top_p: float
    :param temperature: The temperature value to use when generating completions with the OpenAI API.
    :type temperature: float
    :param chatbot: The chatbot instance to use.
    :type chatbot: Chatbot
    :param history: The history of previous user inputs and chatbot responses.
    :type history: List[Tuple[str, str]]
    :param systemprompttxt: The prompt text to use when generating completions with the OpenAI API.
    :type systemprompttxt: str
    :param web_port: The port number of the local web server, used to display generated code in a web browser.
    :type web_port: int

    :return: A sequence of responses generated by the OpenAI API.
    :rtype: Generator[Tuple[Chatbot, List[Tuple[str, str]], str], None, None]
    """

    history = []  # clear history to avoid input overflow
    import glob
    import os

    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = "empty input field"
        report_execption(
            chatbot,
            history,
            a=f"parse project: {txt}",
            b=f"cannot find local project or access denied: {txt}",
        )
        yield chatbot, history, "normal"
        return

    file_manifest = list(glob.glob(f"{project_folder}/**/*.py", recursive=True))
    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"parse project: {txt}",
            b=f"cannot find any python files: {txt}",
        )
        yield chatbot, history, "normal"

    yield from parse_source_code(
        file_manifest,
        project_folder,
        top_p,
        temperature,
        chatbot,
        history,
        systemprompttxt,
    )
