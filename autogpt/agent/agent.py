from colorama import Fore, Style

from autogpt.app import execute_command, get_command
from autogpt.chat import chat_with_ai, create_chat_message
from autogpt.config import Config
from autogpt.json_utils.json_fix_llm import fix_json_using_multiple_techniques
from autogpt.json_utils.utilities import validate_json
from autogpt.logs import logger, print_assistant_thoughts
from autogpt.speech import say_text
from autogpt.spinner import Spinner
from autogpt.utils import clean_input
from autogpt.workspace import Workspace


class Agent:
    """Agent class for interacting with Auto-GPT.

    Attributes:
        ai_name: The name of the agent.
        memory: The memory object to use.
        full_message_history: The full message history.
        next_action_count: The number of actions to execute.
        system_prompt: The system prompt is the initial prompt that defines everything
          the AI needs to know to achieve its task successfully.
        Currently, the dynamic and customizable information in the system prompt are
          ai_name, description and goals.

        triggering_prompt: The last sentence the AI will see before answering.
            For Auto-GPT, this prompt is:
            Determine which next command to use, and respond using the format specified
              above:
            The triggering prompt is not part of the system prompt because between the
              system prompt and the triggering
            prompt we have contextual information that can distract the AI and make it
              forget that its goal is to find the next task to achieve.
            SYSTEM PROMPT
            CONTEXTUAL INFORMATION (memory, previous conversations, anything relevant)
            TRIGGERING PROMPT

        The triggering prompt reminds the AI about its short term meta task
        (defining the next task)
    """

    def __init__(
            self,
            ai_name,
            memory,
            full_message_history,
            next_action_count,
            command_registry,
            config,
            system_prompt,
            triggering_prompt,
            workspace_directory,
    ):
        self.cfg = Config()
        self.ai_name = ai_name
        self.memory = memory
        self.full_message_history = full_message_history
        self.next_action_count = next_action_count
        self.command_registry = command_registry
        self.config = config
        self.system_prompt = system_prompt
        self.triggering_prompt = triggering_prompt
        self.workspace = Workspace(workspace_directory, self.cfg.restrict_to_workspace)
        self.loop_count = 0
        self.command_name = None
        self.sarguments = None
        self.user_input = ""
        self.cfg = Config()

    def start_interaction_loop(self):
        # Discontinue if continuous limit is reached
        self.loop_count += 1
        if (
                self.cfg.continuous_mode
                and self.cfg.continuous_limit > 0
                and self.loop_count > self.cfg.continuous_limit
        ):
            logger.typewriter_log(
                "Continuous Limit Reached: ", Fore.YELLOW, f"{self.cfg.continuous_limit}"
            )
            # break

        # Send message to AI, get response
        with Spinner("Thinking... "):
            self.assistant_reply = chat_with_ai(
                self,
                self.system_prompt,
                self.triggering_prompt,
                self.full_message_history,
                self.memory,
                self.cfg.fast_token_limit,
            )  # TODO: This hardcodes the model to use GPT3.5. Make this an argument

        self.assistant_reply_json = fix_json_using_multiple_techniques(self.assistant_reply)
        for plugin in self.cfg.plugins:
            if not plugin.can_handle_post_planning():
                continue
            self.assistant_reply_json = plugin.post_planning(self, self.assistant_reply_json)

        # Print Assistant thoughts
        if self.assistant_reply_json != {}:
            validate_json(self.assistant_reply_json, "llm_response_format_1")
            # Get command name and self.arguments
            try:
                print_assistant_thoughts(self.ai_name, self.assistant_reply_json)
                self.command_name, self.arguments = get_command(self.assistant_reply_json)
                if self.cfg.speak_mode:
                    say_text(f"I want to execute {self.command_name}")
                self.arguments = self._resolve_pathlike_command_args(self.arguments)

            except Exception as e:
                logger.error("Error: \n", str(e))

        if not self.cfg.continuous_mode and self.next_action_count == 0:
            # ### GET USER AUTHORIZATION TO EXECUTE COMMAND ###
            # Get key press: Prompt the user to press enter to continue or escape
            # to exit
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {self.command_name}"
                f"ARGUMENTS = {self.arguments}",
            )
            logger.typewriter_log(
                "",
                "",
                "Enter 'y' to authorise command, 'y -N' to run N continuous "
                "commands, 'n' to exit program, or enter feedback for "
                f"{self.ai_name}...",
            )

    def start_interaction_next(self, cookie, chatbot, history, msg, _input, obj):
        console_input = _input
        if console_input.lower().strip() == "y":
            self.user_input = "GENERATE NEXT COMMAND JSON"
        elif console_input.lower().strip() == "":
            print("Invalid input format.")
            return
        elif console_input.lower().startswith("y -"):
            try:
                self.next_action_count = abs(
                    int(console_input.split(" ")[1])
                )
                self.user_input = "GENERATE NEXT COMMAND JSON"
            except ValueError:
                print(
                    "Invalid input format. Please enter 'y -n' where n is"
                    " the number of continuous tasks."
                )

                return
        elif console_input.lower() == "n":
            self.user_input = "EXIT"
            return
        else:
            self.user_input = console_input
            self.command_name = "human_feedback"
            return

        if self.user_input == "GENERATE NEXT COMMAND JSON":
            logger.typewriter_log(
                "-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=",
                Fore.MAGENTA,
                "",
            )
        elif self.user_input == "EXIT":
            print("Exiting...", flush=True)
            # break  这里需要注意
        else:
            # Print command
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {Fore.CYAN}{self.command_name}{Style.RESET_ALL}"
                f"  ARGUMENTS = {Fore.CYAN}{self.arguments}{Style.RESET_ALL}",
            )

        # Execute command
        if self.command_name is not None and self.command_name.lower().startswith("error"):
            result = (
                f"Command {self.command_name} threw the following error: {self.arguments}"
            )
        elif self.command_name == "human_feedback":
            result = f"Human feedback: {self.user_input}"
        else:
            for plugin in self.cfg.plugins:
                if not plugin.can_handle_pre_command():
                    continue
                self.command_name, self.arguments = plugin.pre_command(
                    self.command_name, self.arguments
                )
            command_result = execute_command(
                self.command_registry,
                self.command_name,
                self.arguments,
                self.config.prompt_generator,
            )
            result = f"Command {self.command_name} returned: " f"{command_result}"

            for plugin in self.cfg.plugins:
                if not plugin.can_handle_post_command():
                    continue
                result = plugin.post_command(self.command_name, result)
            if self.next_action_count > 0:
                self.next_action_count -= 1
        if self.command_name != "do_nothing":
            memory_to_add = (
                f"Assistant Reply: {self.assistant_reply} "
                f"\nResult: {result} "
                f"\nHuman Feedback: {self.user_input} "
            )

            self.memory.add(memory_to_add)

            # Check if there's a result from the command append it to the message
            # history
            if result is not None:
                self.full_message_history.append(
                    create_chat_message("system", result)
                )
                logger.typewriter_log("SYSTEM: ", Fore.YELLOW, result)
            else:
                self.full_message_history.append(
                    create_chat_message("system", "Unable to execute command")
                )
                logger.typewriter_log(
                    "SYSTEM: ", Fore.YELLOW, "Unable to execute command"
                )

    def _resolve_pathlike_command_args(self, command_args):
        if "directory" in command_args and command_args["directory"] in {"", "/"}:
            command_args["directory"] = str(self.workspace.root)
        else:
            for pathlike in ["filename", "directory", "clone_path"]:
                if pathlike in command_args:
                    command_args[pathlike] = str(
                        self.workspace.get_path(command_args[pathlike])
                    )
        return command_args
