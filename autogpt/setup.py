"""Set up the AI and its goals"""
import re

from colorama import Fore, Style

from autogpt import utils
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.llm_utils import create_chat_completion
from autogpt.logs import logger

CFG = Config()


def prompt_user(input_kwargs: dict, _is) -> AIConfig:
    """Prompt the user for input

    Returns:
        AIConfig: The AIConfig object tailored to the user's input
    """
    ai_name = input_kwargs.get('name')
    ai_role = input_kwargs.get('role')
    ai_goals = input_kwargs.get('goals')
    ai_budget = input_kwargs.get('budget')
    ai_config = None
    if _is:
        return generate_aiconfig_manual(ai_name, ai_role, ai_goals, ai_budget)
    else:
        # Construct the prompt
        logger.typewriter_log(
            "Welcome to Auto-GPT! ",
            Fore.GREEN,
            "run with '--help' for more information.",
            speak_text=True,
        )

        # Get user desire
        logger.typewriter_log(
            "Create an AI-Assistant:",
            Fore.GREEN,
            "input '--manual' to enter manual mode.",
            speak_text=True,
        )
        user_desire = utils.clean_input(
            f"{Fore.MAGENTA}I want Auto-GPT to{Style.RESET_ALL}: "
        )

        if user_desire == "":
            user_desire = "Write a wikipedia style article about the project: https://github.com/significant-gravitas/Auto-GPT"  # Default prompt

        # If user desire contains "--manual"
        if "--manual" in user_desire:
            logger.typewriter_log(
                "Manual Mode Selected",
                Fore.GREEN,
                speak_text=True,
            )
            return generate_aiconfig_manual(ai_name, ai_role, ai_goals, ai_budget)

        else:
            try:
                return generate_aiconfig_automatic(user_desire)
            except Exception as e:
                logger.typewriter_log(
                    "Unable to automatically generate AI Config based on user desire.",
                    Fore.RED,
                    "Falling back to manual mode.",
                    speak_text=True,
                )

                return generate_aiconfig_manual(ai_name, ai_role, ai_goals, ai_budget)


def generate_aiconfig_manual(name, role, goals, budget) -> AIConfig:
    """
    Interactively create an AI configuration by prompting the user to provide the name, role, and goals of the AI.

    This function guides the user through a series of prompts to collect the necessary information to create
    an AIConfig object. The user will be asked to provide a name and role for the AI, as well as up to five
    goals. If the user does not provide a value for any of the fields, default values will be used.

    Returns:
        AIConfig: An AIConfig object containing the user-defined or default AI name, role, and goals.
    """
    # Manual Setup Intro
    logger.typewriter_log(
        "Create an AI-Assistant:",
        Fore.GREEN,
        "The Ai robot you set up is already loaded.",
        speak_text=True,
    )
    ai_name = name
    if not ai_name:
        ai_name = "Entrepreneur-GPT"
    logger.typewriter_log(
        f"{ai_name} here!", Fore.MAGENTA, "I am at your service.", speak_text=True
    )
    ai_role = role
    if not ai_role:
        logger.typewriter_log(
            f"{ai_role} Cannot be empty!", Fore.RED,
            "Please feel free to give me your needs, I can't serve you without them.", speak_text=True
        )
    else:
        pass
    ai_goals = []
    if goals:
        for k in goals:
            ai_goals.append(k[0])
    # Get API Budget from User
    api_budget_input = budget
    if not api_budget_input:
        api_budget = 0.0
    else:
        try:
            api_budget = float(api_budget_input.replace("$", ""))
        except ValueError:
            api_budget = 0.0
            logger.typewriter_log(
                "Invalid budget input. Setting budget to unlimited.", Fore.RED, api_budget
            )
    return AIConfig(ai_name, ai_role, ai_goals, api_budget)


def generate_aiconfig_automatic(user_prompt) -> AIConfig:
    """Generates an AIConfig object from the given string.

    Returns:
    AIConfig: The AIConfig object tailored to the user's input
    """

    system_prompt = """
Your task is to devise up to 5 highly effective goals and an appropriate role-based name (_GPT) for an autonomous agent, ensuring that the goals are optimally aligned with the successful completion of its assigned task.

The user will provide the task, you will provide only the output in the exact format specified below with no explanation or conversation.

Example input:
Help me with marketing my business

Example output:
Name: CMOGPT
Description: a professional digital marketer AI that assists Solopreneurs in growing their businesses by providing world-class expertise in solving marketing problems for SaaS, content products, agencies, and more.
Goals:
- Engage in effective problem-solving, prioritization, planning, and supporting execution to address your marketing needs as your virtual Chief Marketing Officer.

- Provide specific, actionable, and concise advice to help you make informed decisions without the use of platitudes or overly wordy explanations.

- Identify and prioritize quick wins and cost-effective campaigns that maximize results with minimal time and budget investment.

- Proactively take the lead in guiding you and offering suggestions when faced with unclear information or uncertainty to ensure your marketing strategy remains on track.
"""

    # Call LLM with the string as user input
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"Task: '{user_prompt}'\nRespond only with the output in the exact format specified in the system prompt, with no explanation or conversation.\n",
        },
    ]
    output = create_chat_completion(messages, CFG.fast_llm_model)

    # Debug LLM Output
    logger.debug(f"AI Config Generator Raw Output: {output}")

    # Parse the output
    ai_name = re.search(r"Name(?:\s*):(?:\s*)(.*)", output, re.IGNORECASE).group(1)
    ai_role = (
        re.search(
            r"Description(?:\s*):(?:\s*)(.*?)(?:(?:\n)|Goals)",
            output,
            re.IGNORECASE | re.DOTALL,
        )
        .group(1)
        .strip()
    )
    ai_goals = re.findall(r"(?<=\n)-\s*(.*)", output)
    api_budget = 0.0  # TODO: parse api budget using a regular expression

    return AIConfig(ai_name, ai_role, ai_goals, api_budget)

