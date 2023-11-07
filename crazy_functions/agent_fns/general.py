from toolbox import trimmed_format_exc, get_conf, ProxyNetworkActivate
from crazy_functions.agent_fns.pipe import PluginMultiprocessManager, PipeCom
from request_llms.bridge_all import predict_no_ui_long_connection
import time

def gpt_academic_generate_oai_reply(
    self,
    messages,
    sender,
    config,
):
    from .bridge_autogen import Completion
    llm_config = self.llm_config if config is None else config
    if llm_config is False:
        return False, None
    if messages is None:
        messages = self._oai_messages[sender]

    response = Completion.create(
        context=messages[-1].pop("context", None), messages=self._oai_system_message + messages, **llm_config
    )
    return True, Completion.extract_text_or_function_call(response)[0]

class AutoGenGeneral(PluginMultiprocessManager):
    def gpt_academic_print_override(self, user_proxy, message, sender):
        # ⭐⭐ run in subprocess
        self.child_conn.send(PipeCom("show", sender.name + "\n\n---\n\n" + message["content"]))

    def gpt_academic_get_human_input(self, user_proxy, message):
        # ⭐⭐ run in subprocess
        patience = 300
        begin_waiting_time = time.time()
        self.child_conn.send(PipeCom("interact", message))
        while True:
            time.sleep(0.5)
            if self.child_conn.poll():
                wait_success = True
                break
            if time.time() - begin_waiting_time > patience:
                self.child_conn.send(PipeCom("done", ""))
                wait_success = False
                break
        if wait_success:
            return self.child_conn.recv().content
        else:
            raise TimeoutError("等待用户输入超时")

    # def gpt_academic_generate_oai_reply(self, agent, messages, sender, config):
    #     from .bridge_autogen import Completion
    #     if messages is None:
    #         messages = agent._oai_messages[sender]

    #     def instantiate(
    #         cls,
    #         template: Union[str, None],
    #         context: Optional[Dict] = None,
    #         allow_format_str_template: Optional[bool] = False,
    #     ):
    #         if not context or template is None:
    #             return template
    #         if isinstance(template, str):
    #             return template.format(**context) if allow_format_str_template else template
    #         return template(context)

    #     res = predict_no_ui_long_connection(
    #         messages[-1].pop("context", None), 
    #         llm_kwargs=self.llm_kwargs, 
    #         history=messages, 
    #         sys_prompt=agent._oai_system_message,
    #         observe_window=None, 
    #         console_slience=False)
    #     return True, res

    def define_agents(self):
        raise NotImplementedError

    def exe_autogen(self, input):
        # ⭐⭐ run in subprocess
        input = input.content
        with ProxyNetworkActivate("AutoGen"):
            code_execution_config = {"work_dir": self.autogen_work_dir, "use_docker": self.use_docker}
            agents = self.define_agents()
            user_proxy = None
            assistant = None
            for agent_kwargs in agents:
                agent_cls = agent_kwargs.pop('cls')
                kwargs = {
                    'llm_config':{},
                    'code_execution_config':code_execution_config
                }
                kwargs.update(agent_kwargs)
                agent_handle = agent_cls(**kwargs)
                agent_handle._print_received_message = lambda a,b: self.gpt_academic_print_override(agent_kwargs, a, b)
                for d in agent_handle._reply_func_list:
                    if hasattr(d['reply_func'],'__name__') and d['reply_func'].__name__ == 'generate_oai_reply':
                        d['reply_func'] = gpt_academic_generate_oai_reply
                if agent_kwargs['name'] == 'user_proxy':
                    agent_handle.get_human_input = lambda a: self.gpt_academic_get_human_input(user_proxy, a)
                    user_proxy = agent_handle
                if agent_kwargs['name'] == 'assistant': assistant = agent_handle
            try:
                if user_proxy is None or assistant is None: raise Exception("用户代理或助理代理未定义")
                user_proxy.initiate_chat(assistant, message=input)
            except Exception as e:
                tb_str = '```\n' + trimmed_format_exc() + '```'
                self.child_conn.send(PipeCom("done", "AutoGen 执行失败: \n\n" + tb_str))

    def subprocess_worker(self, child_conn):
        # ⭐⭐ run in subprocess
        self.child_conn = child_conn
        while True:
            msg = self.child_conn.recv()  # PipeCom
            self.exe_autogen(msg)


class AutoGenGroupChat(AutoGenGeneral):
    def exe_autogen(self, input):
        # ⭐⭐ run in subprocess
        import autogen

        input = input.content
        with ProxyNetworkActivate("AutoGen"):
            code_execution_config = {"work_dir": self.autogen_work_dir, "use_docker": self.use_docker}
            agents = self.define_agents()
            agents_instances = []
            for agent_kwargs in agents:
                agent_cls = agent_kwargs.pop("cls")
                kwargs = {"code_execution_config": code_execution_config}
                kwargs.update(agent_kwargs)
                agent_handle = agent_cls(**kwargs)
                agent_handle._print_received_message = lambda a, b: self.gpt_academic_print_override(agent_kwargs, a, b)
                agents_instances.append(agent_handle)
                if agent_kwargs["name"] == "user_proxy":
                    user_proxy = agent_handle
                    user_proxy.get_human_input = lambda a: self.gpt_academic_get_human_input(user_proxy, a)
            try:
                groupchat = autogen.GroupChat(agents=agents_instances, messages=[], max_round=50)
                manager = autogen.GroupChatManager(groupchat=groupchat, **self.define_group_chat_manager_config())
                manager._print_received_message = lambda a, b: self.gpt_academic_print_override(agent_kwargs, a, b)
                manager.get_human_input = lambda a: self.gpt_academic_get_human_input(manager, a)
                if user_proxy is None:
                    raise Exception("user_proxy is not defined")
                user_proxy.initiate_chat(manager, message=input)
            except Exception:
                tb_str = "```\n" + trimmed_format_exc() + "```"
                self.child_conn.send(PipeCom("done", "AutoGen exe failed: \n\n" + tb_str))

    def define_group_chat_manager_config(self):
        raise NotImplementedError
