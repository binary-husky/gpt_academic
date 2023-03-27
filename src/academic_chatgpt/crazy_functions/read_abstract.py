from loguru import logger
from toolbox import (
    CatchException,
    predict_no_ui_but_counting_down,
    report_execption,
    write_results_to_file,
)

fast_debug = False


def parse_paper(
    file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt
):
    import os
    import time

    logger.info("begin analysis on: %s", file_manifest)
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

    all_file = ", ".join(
        [os.path.relpath(fp, project_folder) for index, fp in enumerate(file_manifest)]
    )
    i_say = f"Based on your analysis above, summarize the entire text, write a paragraph of Chinese abstract in academic language, and then write a paragraph of English abstract (including {all_file})."
    chatbot.append((i_say, "[Local Message] waiting gpt response."))
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
        chatbot.append(("Are you done?", res))
        yield chatbot, history, msg


@CatchException
def read_artical_write_abstract(
    txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT
):
    history = []  # clear history to avoid input overflow
    import glob
    import os

    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = "Empty input field"
        report_execption(
            chatbot,
            history,
            a=f"Parse project: {txt}",
            b=f"Cannot find local project or have no access: {txt}",
        )
        yield chatbot, history, "normal"
        return
    file_manifest = list(glob.glob(f"{project_folder}/**/*.tex", recursive=True))  # + \
    if len(file_manifest) == 0:
        report_execption(
            chatbot,
            history,
            a=f"Parse project: {txt}",
            b=f"Cannot find any .tex files: {txt}",
        )
        yield chatbot, history, "normal"
        return
    yield from parse_paper(
        file_manifest,
        project_folder,
        top_p,
        temperature,
        chatbot,
        history,
        systemPromptTxt,
    )
