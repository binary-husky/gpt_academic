from pathlib import Path

from loguru import logger
from ..utils import (
    catch_exception,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)

fast_debug = False


def parse_source_code(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemprompttxt
):
    import time

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

        if not fast_debug:
            msg = "normal"

            # ** gpt request **
            gpt_say = yield from predict_no_ui_but_counting_down(
                i_say, i_say_show_user, chatbot, top_p, temperature, history=[]
            )  # with timeout countdown

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.append(i_say_show_user)
            history.append(gpt_say)
            yield chatbot, history, msg
            if not fast_debug:
                time.sleep(2)

    all_file = ", ".join(
        [Path(fp).relative_to(project_folder) for index, fp in enumerate(file_manifest)]
    )
    i_say = f"based on your analysis above, summarize the overall function and structure of the program. then use a markdown table to organize the function of each file (including {all_file})."
    chatbot.append((i_say, "[local message] waiting gpt response."))
    yield chatbot, history, "normal"

    if not fast_debug:
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
    history = []  # clear history to avoid input overflow
    import time

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

        if not fast_debug:
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

    if not fast_debug:
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
