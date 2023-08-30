import os
from unittest.mock import patch

import pytest
import requests

from autogpt.utils import (
    get_bulletin_from_web,
    get_current_git_branch,
    get_latest_bulletin,
    readable_file_size,
    validate_yaml_file,
)
from tests.utils import skip_in_ci


def test_validate_yaml_file_valid():
    with open("valid_test_file.yaml", "w") as f:
        f.write("setting: value")
    result, message = validate_yaml_file("valid_test_file.yaml")
    os.remove("valid_test_file.yaml")

    assert result == True
    assert "Successfully validated" in message


def test_validate_yaml_file_not_found():
    result, message = validate_yaml_file("non_existent_file.yaml")

    assert result == False
    assert "wasn't found" in message


def test_validate_yaml_file_invalid():
    with open("invalid_test_file.yaml", "w") as f:
        f.write(
            "settings:\n  first_setting: value\n  second_setting: value\n    nested_setting: value\n  third_setting: value\nunindented_setting: value"
        )
    result, message = validate_yaml_file("invalid_test_file.yaml")
    os.remove("invalid_test_file.yaml")
    print(result)
    print(message)
    assert result == False
    assert "There was an issue while trying to read" in message


def test_readable_file_size():
    size_in_bytes = 1024 * 1024 * 3.5  # 3.5 MB
    readable_size = readable_file_size(size_in_bytes)

    assert readable_size == "3.50 MB"


@patch("requests.get")
def test_get_bulletin_from_web_success(mock_get):
    expected_content = "Test bulletin from web"

    mock_get.return_value.status_code = 200
    mock_get.return_value.text = expected_content
    bulletin = get_bulletin_from_web()

    assert expected_content in bulletin
    mock_get.assert_called_with(
        "https://raw.githubusercontent.com/Significant-Gravitas/Auto-GPT/master/BULLETIN.md"
    )


@patch("requests.get")
def test_get_bulletin_from_web_failure(mock_get):
    mock_get.return_value.status_code = 404
    bulletin = get_bulletin_from_web()

    assert bulletin == ""


@patch("requests.get")
def test_get_bulletin_from_web_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    bulletin = get_bulletin_from_web()

    assert bulletin == ""


def test_get_latest_bulletin_no_file():
    if os.path.exists("data/CURRENT_BULLETIN.md"):
        os.remove("data/CURRENT_BULLETIN.md")

    bulletin, is_new = get_latest_bulletin()
    assert is_new


def test_get_latest_bulletin_with_file():
    expected_content = "Test bulletin"
    with open("data/CURRENT_BULLETIN.md", "w", encoding="utf-8") as f:
        f.write(expected_content)

    with patch("autogpt.utils.get_bulletin_from_web", return_value=""):
        bulletin, is_new = get_latest_bulletin()
        assert expected_content in bulletin
        assert is_new == False

    os.remove("data/CURRENT_BULLETIN.md")


def test_get_latest_bulletin_with_new_bulletin():
    with open("data/CURRENT_BULLETIN.md", "w", encoding="utf-8") as f:
        f.write("Old bulletin")

    expected_content = "New bulletin from web"
    with patch("autogpt.utils.get_bulletin_from_web", return_value=expected_content):
        bulletin, is_new = get_latest_bulletin()
        assert "::NEW BULLETIN::" in bulletin
        assert expected_content in bulletin
        assert is_new

    os.remove("data/CURRENT_BULLETIN.md")


def test_get_latest_bulletin_new_bulletin_same_as_old_bulletin():
    expected_content = "Current bulletin"
    with open("data/CURRENT_BULLETIN.md", "w", encoding="utf-8") as f:
        f.write(expected_content)

    with patch("autogpt.utils.get_bulletin_from_web", return_value=expected_content):
        bulletin, is_new = get_latest_bulletin()
        assert expected_content in bulletin
        assert is_new == False

    os.remove("data/CURRENT_BULLETIN.md")


@skip_in_ci
def test_get_current_git_branch():
    branch_name = get_current_git_branch()

    # Assuming that the branch name will be non-empty if the function is working correctly.
    assert branch_name != ""


@patch("autogpt.utils.Repo")
def test_get_current_git_branch_success(mock_repo):
    mock_repo.return_value.active_branch.name = "test-branch"
    branch_name = get_current_git_branch()

    assert branch_name == "test-branch"


@patch("autogpt.utils.Repo")
def test_get_current_git_branch_failure(mock_repo):
    mock_repo.side_effect = Exception()
    branch_name = get_current_git_branch()

    assert branch_name == ""


if __name__ == "__main__":
    pytest.main()
from comm_tools.toolbox import get_conf
from comm_tools.toolbox import set_conf
from comm_tools.toolbox import set_multi_conf
from comm_tools.toolbox import get_plugin_handle
from comm_tools.toolbox import get_plugin_default_kwargs
from comm_tools.toolbox import get_chat_handle
from comm_tools.toolbox import get_chat_default_kwargs
from functools import wraps
import sys
import os

def chat_to_markdown_str(chat):
    result = ""
    for i, cc in enumerate(chat):
        result += f'\n\n{cc[0]}\n\n{cc[1]}'
        if i != len(chat)-1:
            result += '\n\n---'
    return result

def silence_stdout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        sys.stdout.reconfigure(encoding='utf-8')
        for q in func(*args, **kwargs):
            sys.stdout = _original_stdout
            yield q
            sys.stdout = open(os.devnull, 'w')
            sys.stdout.reconfigure(encoding='utf-8')
        sys.stdout.close()
        sys.stdout = _original_stdout
    return wrapper

def silence_stdout_fn(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        sys.stdout.reconfigure(encoding='utf-8')
        result = func(*args, **kwargs)
        sys.stdout.close()
        sys.stdout = _original_stdout
        return result
    return wrapper

class VoidTerminal():
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
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT, API_KEY = \
    vt.get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT', 'API_KEY')

def plugin_test(main_input, plugin, advanced_arg=None):
    from rich.live import Live
    from rich.markdown import Markdown

    vt.set_conf(key="API_KEY", value=API_KEY)
    vt.set_conf(key="LLM_MODEL", value=LLM_MODEL)

    plugin = vt.get_plugin_handle(plugin)
    plugin_kwargs = vt.get_plugin_default_kwargs()
    plugin_kwargs['main_input'] = main_input
    if advanced_arg is not None:
        plugin_kwargs['plugin_kwargs'] = advanced_arg
    my_working_plugin = silence_stdout(plugin)(**plugin_kwargs)

    with Live(Markdown(""), auto_refresh=False) as live:
        for cookies, chat, hist, msg in my_working_plugin:
            md_str = vt.chat_to_markdown_str(chat)
            md = Markdown(md_str)
            live.update(md, refresh=True)
