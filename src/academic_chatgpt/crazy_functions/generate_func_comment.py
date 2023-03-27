import os
import time

from loguru import logger
from ..utils import (
    catch_exception,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)

fast_debug = False


def generate_comment_for_function(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt
):
    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        i_say = f"Please give an overview of the following program file and generate comments for all functions in the file, output the results using markdown tables. The file name is {os.path.relpath(fp, project_folder)}, and the file content is ```{file_content}```"
        i_say_show_user = f"[{index}/{len(file_manifest)}] Please give an overview of the following program file and generate comments for all functions in the file: {os.path.abspath(fp)}"
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        yield chatbot, history, "normal"

        if not fast_debug:
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
            if not fast_debug:
                time.sleep(2)

    if not fast_debug:
        res = write_results_to_file(history)
        chatbot.append(("Are you done?", res))
        yield chatbot, history, msg


@catch_exception
def generate_comment_for_function_for_batch(
    txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT
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
            a=f"Parse project: {txt}",
            b=f"Cannot find local project or have no access: {txt}",
        )
        yield chatbot, history, "normal"
    file_manifest = list(glob.glob(f"{project_folder}/**/*.py", recursive=True)) + list(
        glob.glob(f"{project_folder}/**/*.cpp", recursive=True)
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
