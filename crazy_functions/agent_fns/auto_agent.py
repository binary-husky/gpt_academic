from comm_tools.toolbox import CatchException, update_ui, gen_time_str, trimmed_format_exc, ProxyNetworkActivate
from comm_tools.toolbox import report_execption, get_log_folder, update_ui_lastest_msg, Singleton
from crazy_functions.agent_fns.pipe import PluginMultiprocessManager, PipeCom
from crazy_functions.agent_fns.general import AutoGenGeneral
import time


class AutoGenMath(AutoGenGeneral):

    def define_agents(self):
        from autogen import AssistantAgent, UserProxyAgent
        return [
            {
                "name": "assistant",            # name of the agent.
                "cls":  AssistantAgent,         # class of the agent.
            },
            {
                "name": "user_proxy",           # name of the agent.
                "cls":  UserProxyAgent,         # class of the agent.
                "human_input_mode": "ALWAYS",   # always ask for human input.
                "llm_config": False,            # disables llm-based auto reply.
            },
        ]