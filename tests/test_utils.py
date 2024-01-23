from toolbox import get_conf
from toolbox import set_conf
from toolbox import set_multi_conf
from toolbox import get_plugin_handle
from toolbox import get_plugin_default_kwargs
from toolbox import get_chat_handle
from toolbox import get_chat_default_kwargs
from functools import wraps
import sys
import os


def chat_to_markdown_str(chat):
    result = ""
    for i, cc in enumerate(chat):
        result += f"\n\n{cc[0]}\n\n{cc[1]}"
        if i != len(chat) - 1:
            result += "\n\n---"
    return result


def silence_stdout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        sys.stdout.reconfigure(encoding="utf-8")
        for q in func(*args, **kwargs):
            sys.stdout = _original_stdout
            yield q
            sys.stdout = open(os.devnull, "w")
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.close()
        sys.stdout = _original_stdout

    return wrapper


def silence_stdout_fn(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        sys.stdout.reconfigure(encoding="utf-8")
        result = func(*args, **kwargs)
        sys.stdout.close()
        sys.stdout = _original_stdout
        return result

    return wrapper


class VoidTerminal:
    def __init__(self) -> None:
        pass


vt = VoidTerminal()
vt.get_conf = silence_stdout_fn(get_conf)
vt.set_conf = silence_stdout_fn(set_conf)
vt.set_multi_conf = silence_stdout_fn(set_multi_conf)
vt.get_plugin_handle = silence_stdout_fn(get_plugin_handle)
vt.get_plugin_default_kwargs = silence_stdout_fn(get_plugin_default_kwargs)
vt.get_chat_handle = silence_stdout_fn(get_chat_handle)
vt.get_chat_default_kwargs = silence_stdout_fn(get_chat_default_kwargs)
vt.chat_to_markdown_str = chat_to_markdown_str
(
    proxies,
    WEB_PORT,
    LLM_MODEL,
    CONCURRENT_COUNT,
    AUTHENTICATION,
    CHATBOT_HEIGHT,
    LAYOUT,
    API_KEY,
) = vt.get_conf(
    "proxies",
    "WEB_PORT",
    "LLM_MODEL",
    "CONCURRENT_COUNT",
    "AUTHENTICATION",
    "CHATBOT_HEIGHT",
    "LAYOUT",
    "API_KEY",
)


def plugin_test(main_input, plugin, advanced_arg=None, debug=True):
    from rich.live import Live
    from rich.markdown import Markdown

    vt.set_conf(key="API_KEY", value=API_KEY)
    vt.set_conf(key="LLM_MODEL", value=LLM_MODEL)

    plugin = vt.get_plugin_handle(plugin)
    plugin_kwargs = vt.get_plugin_default_kwargs()
    plugin_kwargs["main_input"] = main_input
    if advanced_arg is not None:
        plugin_kwargs["plugin_kwargs"] = advanced_arg
    if debug:
        my_working_plugin = (plugin)(**plugin_kwargs)
    else:
        my_working_plugin = silence_stdout(plugin)(**plugin_kwargs)

    with Live(Markdown(""), auto_refresh=False, vertical_overflow="visible") as live:
        for cookies, chat, hist, msg in my_working_plugin:
            md_str = vt.chat_to_markdown_str(chat)
            md = Markdown(md_str)
            live.update(md, refresh=True)
