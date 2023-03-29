from loguru import logger
from ..utils import (
    catch_exception,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)

from pathlib import Path
import time
import os


FAST_DEBUG = False


def parse_PDF(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt
):
    logger.info(f"begin analysis on: {file_manifest}")
    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        prefix = (
            "Next, please analyze the following paper files one by one and summarize their contents"
            if index == 0
            else ""
        )

        i_say = (
            prefix
            + f"Please summarize the following article fragment in Chinese, the file name is {os.path.relpath(fp, project_folder)}, and the article content is ```{file_content}```"
        )
        i_say_show_user = (
            prefix
            + f"[{index}/{len(file_manifest)}] Please summarize the following article fragment in Chinese: {os.path.abspath(fp)}"
        )
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        logger.info("[1] yield chatbot, history")
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

    all_file = ", ".join(
        [os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)]
    )
    i_say = f"Based on your analysis above, summarize the entire text, write a paragraph of Chinese abstract in academic language, and then write a paragraph of English abstract (including {all_file})."
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
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
        chatbot.append(("Are you done?", res))
        yield chatbot, history, msg


def parse_paper(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt
):
    logger.info(f"begin analysis on: {file_manifest}")

    for index, fp in enumerate(file_manifest):
        with open(fp, encoding="utf-8") as f:
            file_content = f.read()

        prefix = (
            "Next, please analyze the following paper files one by one and summarize their contents"
            if index == 0
            else ""
        )
        i_say = (
            prefix
            + f"Please summarize the following article fragment in Chinese, the file name is {os.path.relpath(fp, project_folder)}, and the article content is ```{file_content}```"
        )
        i_say_show_user = (
            prefix
            + f"[{index}/{len(file_manifest)}] Please summarize the following article fragment in Chinese: {os.path.abspath(fp)}"
        )
        chatbot.append((i_say_show_user, "[Local Message] waiting gpt response."))
        logger.info("[1] yield chatbot, history")
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

    all_file = ", ".join(
        [os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)]
    )
    i_say = f"Based on your analysis above, summarize the entire text, write a paragraph of Chinese abstract in academic language, and then write a paragraph of English abstract (including {all_file})."
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
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
        chatbot.append(("Are you done?", res))
        yield chatbot, history, msg


@catch_exception
def read_artical_write_abstract(
    txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT
):
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

    file_manifest = list(project_folder.rglob("*.tex"))

    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"Parse project: {txt}",
            b=f"Cannot find any .tex files: {txt}",
        )
        yield chatbot, history, "normal"

    yield from parse_paper(
        file_manifest,
        project_folder,
        top_p,
        temperature,
        chatbot,
        history,
        systemPromptTxt,
    )
