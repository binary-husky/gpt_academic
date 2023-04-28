"""Main script for the autogpt package."""
# Put imports inside function to avoid importing everything when starting the CLI
import logging
import os.path
import sys
from pathlib import Path

import gradio
from colorama import Fore
from autogpt.agent.agent import Agent
from autogpt.commands.command import CommandRegistry
from autogpt.config import Config, check_openai_api_key
from autogpt.configurator import create_config
from autogpt.logs import logger
from autogpt.memory import get_memory
from autogpt.plugins import scan_plugins
from autogpt.prompts.prompt import construct_main_ai_config
from autogpt.utils import get_current_git_branch, get_latest_bulletin
from autogpt.workspace import Workspace
import func_box
from toolbox import update_ui
from toolbox import ChatBotWithCookies
def handle_config(kwargs_settings):
    kwargs_settings = {
                'continuous': False,   # Enable Continuous Mode
                'continuous_limit': None,  # Defines the number of times to run in continuous mode
                'ai_settings': None,   # Specifies which ai_settings.yaml file to use, will also automatically skip the re-prompt.
                'skip_reprompt': False,  # Skips the re-prompting messages at the beginning of the scrip
                'speak': False,  # Enable speak Mode
                'debug': False,  # Enable Debug Mode
                'gpt3only': False,  # Enable GPT3.5 Only Mode
                'gpt4only': False,  # Enable GPT4 Only Mode
                'memory_type': None,  # Defines which Memory backend to use
                'browser_name': None,  # Specifies which web-browser to use when using selenium to scrape the web.
                'allow_downloads': False,  # Dangerous: Allows Auto-GPT to download files natively.
                'skip_news': True,   # Specifies whether to suppress the output of latest news on startup.
                'workspace_directory': None  # TODO: this is a hidden option for now, necessary for integration testing. We should make this public once we're ready to roll out agent specific workspaces.
                }
    """
    Welcome to AutoGPT an experimental open-source application showcasing the capabilities of the GPT-4 pushing the boundaries of AI.
    Start an Auto-GPT assistant.
    """
    if kwargs_settings['workspace_directory']:
          kwargs_settings['ai_settings'] = os.path.join(kwargs_settings['workspace_directory'], 'ai_settings.yaml')
    # if ctx.invoked_subcommand is None:
    cfg = Config()
    # TODO: fill in llm values here
    check_openai_api_key()
    create_config(
        kwargs_settings['continuous'],
        kwargs_settings['continuous_limit'],
        kwargs_settings['ai_settings'],
        kwargs_settings['skip_reprompt'],
        kwargs_settings['speak'],
        kwargs_settings['debug'],
        kwargs_settings['gpt3only'],
        kwargs_settings['gpt4only'],
        kwargs_settings['memory_type'],
        kwargs_settings['browser_name'],
        kwargs_settings['allow_downloads'],
        kwargs_settings['skip_news'],
    )
    return cfg


def handle_news():
    motd = get_latest_bulletin()
    if motd:
        logger.typewriter_log("NEWS: ", Fore.GREEN, motd)
    git_branch = get_current_git_branch()
    if git_branch and git_branch != "stable":
        logger.typewriter_log(
            "WARNING: ",
            Fore.RED,
            f"You are running on `{git_branch}` branch "
            "- this is not a supported branch.",
        )
    if sys.version_info < (3, 10):
        logger.typewriter_log(
            "WARNING: ",
            Fore.RED,
            "You are running on an older version of Python. "
            "Some people have observed problems with certain "
            "parts of Auto-GPT with this version. "
            "Please consider upgrading to Python 3.10 or higher.",
        )


def handle_registry():
    # Create a CommandRegistry instance and scan default folder
    command_registry = CommandRegistry()
    command_registry.import_commands("autogpt.commands.analyze_code")
    command_registry.import_commands("autogpt.commands.audio_text")
    command_registry.import_commands("autogpt.commands.execute_code")
    command_registry.import_commands("autogpt.commands.file_operations")
    command_registry.import_commands("autogpt.commands.git_operations")
    command_registry.import_commands("autogpt.commands.google_search")
    command_registry.import_commands("autogpt.commands.image_gen")
    command_registry.import_commands("autogpt.commands.improve_code")
    command_registry.import_commands("autogpt.commands.twitter")
    command_registry.import_commands("autogpt.commands.web_selenium")
    command_registry.import_commands("autogpt.commands.write_tests")
    command_registry.import_commands("autogpt.app")
    return command_registry


def handle_workspace(user):
    # TODO: have this directory live outside the repository (e.g. in a user's
    #   home directory) and have it come in as a command line argument or part of
    #   the env file.
    if user is None:
        workspace_directory = Path(__file__).parent / "auto_gpt_workspace"
    else:
        workspace_directory = Path(__file__).parent / "auto_gpt_workspace" / user
    # TODO: pass in the ai_settings file and the env file and have them cloned into
    #   the workspace directory so we can bind them to the agent.
    workspace_directory = Workspace.make_workspace(workspace_directory)
    # HACK: doing this here to collect some globals that depend on the workspace.
    file_logger_path = workspace_directory / "file_logger.txt"
    if not file_logger_path.exists():
        with file_logger_path.open(mode="w", encoding="utf-8") as f:
            f.write("File Operation Logger ")

    return workspace_directory, file_logger_path


def update_obj(plugin_kwargs, _is=True):
    obj = plugin_kwargs['obj']
    start = plugin_kwargs['start']
    next_ = plugin_kwargs['next']
    text = plugin_kwargs['txt']
    if _is:
        start.update(visible=True)
        next_.update(visible=False)
        text.update(visible=False)
    else:
        start.update(visible=False)
        next_.update(visible=True)
        text.update(visible=True)
    return obj, start, next_, text


def agent_main(name, role, goals, budget,
               cookies, chatbot, history, obj,
                ipaddr: gradio.Request):
    # ai setup
    input_kwargs = {
        'name': name,
        'role': role,
        'goals': goals,
        'budget': budget
    }
    # chat setup
    logger.output_content = []
    chatbot_with_cookie = ChatBotWithCookies(cookies)
    chatbot_with_cookie.write_list(chatbot)
    history = []
    cfg = handle_config(None)
    logger.set_level(logging.DEBUG if cfg.debug_mode else logging.INFO)
    workspace_directory = ipaddr.client.host
    if not cfg.skip_news:
        handle_news()
    cfg.set_plugins(scan_plugins(cfg, cfg.debug_mode))
    command_registry = handle_registry()
    ai_config = construct_main_ai_config(input_kwargs)
    def update_stream_ui(user='', gpt='', msg='Done',
                         _start=obj['start'].update(), _next=obj['next'].update(), _text=obj['text'].update()):
        if user or gpt:
            temp = [user, gpt]
            if not chatbot_with_cookie:
                chatbot_with_cookie.append(temp)
            else:
                chatbot_with_cookie[-1] = [chatbot_with_cookie[-1][i] + temp[i] for i in range(len(chatbot_with_cookie[-1]))]
        yield chatbot_with_cookie.get_cookies(), chatbot_with_cookie, history, msg, obj, _start, _next, _text
    if not ai_config:
        msg = '### ROLE 不能为空'
        # yield chatbot_with_cookie.get_cookies(), chatbot_with_cookie, history, msg, obj, None, None, None
        yield from update_stream_ui(msg=msg)
        return
    ai_config.command_registry = command_registry
    next_action_count = 0
    # Make a constant:
    triggering_prompt = (
        "Determine which next command to use, and respond using the"
        " format specified above:"
    )
    workspace_directory, file_logger_path = handle_workspace(workspace_directory)
    cfg.workspace_path = str(workspace_directory)
    cfg.file_logger_path = str(file_logger_path)
    # Initialize memory and make sure it is empty.
    # this is particularly important for indexing and referencing pinecone memory
    memory = get_memory(cfg, init=True)
    logger.typewriter_log(
        "Using memory of type:", Fore.GREEN, f"{memory.__class__.__name__}"
    )
    logger.typewriter_log("Using Browser:", Fore.GREEN, cfg.selenium_web_browser)
    system_prompt = ai_config.construct_full_prompt()
    if cfg.debug_mode:
        logger.typewriter_log("Prompt:", Fore.GREEN, system_prompt)
    agent = Agent(
        ai_name=input_kwargs['name'],
        memory=memory,
        full_message_history=history,
        next_action_count=next_action_count,
        command_registry=command_registry,
        config=ai_config,
        system_prompt=system_prompt,
        triggering_prompt=triggering_prompt,
        workspace_directory=workspace_directory,
    )
    obj['obj'] = agent
    _start = obj['start'].update(visible=False)
    _next = obj['next'].update(visible=True)
    _text = obj['text'].update(visible=True, interactive=True)
    chat, his = func_box.chat_history(logger.output_content)
    yield from update_stream_ui(user='Auto-GPT Start!', gpt=chat, _start=_start, _next=_next, _text=_text)
    agent.start_interaction_loop()
    chat, his = func_box.chat_history(logger.output_content)
    yield from update_stream_ui(user='Auto-GPT Start!', gpt=chat, _start=_start, _next=_next, _text=_text)




def agent_start(cookie, chatbot, history, msg, obj):
    yield from obj['obj'].start_interaction_loop(cookie, chatbot, history, msg, obj)


if __name__ == "__main__":
    pass

