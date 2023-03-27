import os
import threading
import time
from functools import wraps

import markdown
from loguru import logger
from .show_math import convert as convert_math


def predict_no_ui_but_counting_down(
    i_say, i_say_show_user, chatbot, top_p, temperature, history=[]
):
    """Call the simple predict_no_ui interface, but still retain some interface heartbeat functionality. When the conversation is too long, binary truncation will be automatically used."""
    import time

    try:
        from config_private import MAX_RETRY, TIMEOUT_SECONDS
    except ModuleNotFoundError:
        from config import MAX_RETRY, TIMEOUT_SECONDS
    from predict import predict_no_ui

    # When using multi-threading, a mutable structure is needed to pass information between different threads
    # list is the simplest mutable structure, we put the gpt output in the first position, and pass the error message in the second position
    mutable = [None, ""]

    # multi-threading worker
    def mt(i_say, history):
        while True:
            try:
                mutable[0] = predict_no_ui(
                    inputs=i_say, top_p=top_p, temperature=temperature, history=history
                )
                break
            except ConnectionAbortedError:
                if len(history) > 0:
                    history = [
                        his[len(his) // 2 :] for his in history if his is not None
                    ]
                    mutable[
                        1
                    ] = "Warning! History conversation is too long, cut into half. "
                else:
                    i_say = i_say[: len(i_say) // 2]
                    mutable[1] = "Warning! Input file is too long, cut into half. "
            except TimeoutError:
                mutable[0] = "[Local Message] Failed with timeout"

    # create a new thread to send http request
    thread_name = threading.Thread(target=mt, args=(i_say, history))
    thread_name.start()
    # The original thread is responsible for continuously updating the UI, implementing a timeout countdown, and waiting for the new thread to complete its task
    cnt = 0
    while thread_name.is_alive():
        cnt += 1
        chatbot[-1] = (
            i_say_show_user,
            f"[Local Message] {mutable[1]}waiting gpt response {cnt}/{TIMEOUT_SECONDS*2*(MAX_RETRY+1)}"
            + "".join(["."] * (cnt % 4)),
        )
        yield chatbot, history, "normal"
        time.sleep(1)
    # Take the output of gpt from mutable
    gpt_say = mutable[0]
    return gpt_say


def write_results_to_file(history, file_name=None):
    """Write the conversation record history to the file in Markdown format. If no file name is specified, the file name is generated using the current time."""

    if file_name is None:
        file_name = (
            time.strftime("chatGPT analysis report%Y-%m-%d-%H-%M-%S", time.localtime())
            + ".md"
        )
    os.makedirs("./gpt_log/", exist_ok=True)
    with open(f"./gpt_log/{file_name}", "w") as f:
        f.write("# chatGPT analysis report\n")
        for i, content in enumerate(history):
            if i % 2 == 0:
                f.write("## ")
            f.write(content)
            f.write("\n\n")
    res = "The above materials have been written to" + os.path.abspath(
        f"./gpt_log/{file_name}"
    )
    logger.info(res)
    return res


def regular_txt_to_markdown(text):
    """Convert plain text to Markdown format."""
    text = text.replace("\n", "\n\n")
    text = text.replace("\n\n\n", "\n\n")
    text = text.replace("\n\n\n", "\n\n")
    return text


def catch_exception(f):
    """Decorator function, catch the exception in function f and encapsulate it into a generator to return, and display it in the chat."""

    @wraps(f)
    def decorated(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT):
        try:
            yield from f(
                txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT
            )
        except Exception as e:
            import traceback

            from check_proxy import check_proxy

            try:
                from config_private import proxies
            except ModuleNotFoundError:
                from config import proxies
            tb_str = regular_txt_to_markdown(traceback.format_exc())
            chatbot[-1] = (
                chatbot[-1][0],
                f"[Local Message] Experimental function call error: \n\n {tb_str} \n\n Current proxy availability: \n\n {check_proxy(proxies)}",
            )
            yield chatbot, history, f"exception {e}"

    return decorated


def report_execption(chatbot, history, a, b):
    """Add error information to chatbot."""
    chatbot.append((a, b))
    history.append(a)
    history.append(b)


def text_divide_paragraph(text):
    """Split the text into paragraphs according to the paragraph separator and generate HTML code with paragraph tags."""
    if "```" in text:
        # careful input
        return text
    else:
        # wtf input
        lines = text.split("\n")
        for i, _line in enumerate(lines):
            if i != 0:
                lines[i] = "<p>" + lines[i].replace(" ", "&nbsp;") + "</p>"
        text = "".join(lines)
        return text


def markdown_convertion(txt):
    """Convert Markdown format text to HTML format. If it contains mathematical formulas, convert the formulas to HTML format first."""
    if ("$" in txt) and ("```" not in txt):
        return (
            markdown.markdown(txt, extensions=["fenced_code", "tables"])
            + "<br><br>"
            + markdown.markdown(
                convert_math(txt, splitParagraphs=False),
                extensions=["fenced_code", "tables"],
            )
        )
    else:
        return markdown.markdown(txt, extensions=["fenced_code", "tables"])


def format_io(self, y):
    """Parse the input and output into HTML format. Paragraphize the input part of the last item in y, and convert the Markdown and mathematical formulas in the output part to HTML format."""
    if y is None:
        return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask)  # The input part is too free, pre-processing
    y[-1] = (
        None
        if i_ask is None
        else markdown.markdown(i_ask, extensions=["fenced_code", "tables"]),
        None if gpt_reply is None else markdown_convertion(gpt_reply),
    )
    return y


def find_free_port():
    """Return the unused port in the current system."""
    import socket
    from contextlib import closing

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
