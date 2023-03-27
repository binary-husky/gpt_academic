from pathlib import Path

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
        [
            Path(fp).relative_to(project_folder).as_posix()
            for index, fp in enumerate(file_manifest)
        ]
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

    c_file_manifest = list(project_folder.rglob("*.h"))
    cpp_file_manifest = list(project_folder.rglob("*.hpp"))
    file_manifest = c_file_manifest + cpp_file_manifest

    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"parse project: {txt}",
            b=f"cannot find any .h header files: {txt}",
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

    file_manifest = list(project_folder.rglob("*.py"))

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
