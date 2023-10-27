from comm_tools.toolbox import CatchException, update_ui, gen_time_str, trimmed_format_exc, ProxyNetworkActivate
from comm_tools.toolbox import report_execption, get_log_folder, update_ui_lastest_msg, Singleton
from crazy_functions.agent_fns.pipe import PluginMultiprocessManager, PipeCom
import time


class AutoGenGeneral(PluginMultiprocessManager):

    def gpt_academic_print_override(self, user_proxy, message, sender):
        # ⭐⭐ 子进程执行
        self.child_conn.send(PipeCom("show", sender.name + '\n\n---\n\n' + message['content']))

    def gpt_academic_get_human_input(self, user_proxy, message):
        # ⭐⭐ 子进程执行
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

    def define_agents(self):
        raise NotImplementedError

    def do_audogen(self, input):
        # ⭐⭐ 子进程执行
        input = input.content
        with ProxyNetworkActivate("AutoGen"):
            from autogen import AssistantAgent, UserProxyAgent
            config_list = [{
                'model': self.llm_kwargs['llm_model'], 
                'api_key': self.llm_kwargs['api_key'],
            },]
            code_execution_config={"work_dir": self.autogen_work_dir, "use_docker":True}
            agents = self.define_agents()
            user_proxy = None
            assistant = None
            for agent_kwargs in agents:
                agent_cls = agent_kwargs.pop('cls')
                kwargs = {
                    'llm_config':{
                        "config_list": config_list,
                    },
                    'code_execution_config':code_execution_config
                }
                kwargs.update(agent_kwargs)
                agent_handle = agent_cls(**kwargs)
                agent_handle._print_received_message = lambda a,b: self.gpt_academic_print_override(agent_kwargs, a, b)
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
        # ⭐⭐ 子进程执行
        self.child_conn = child_conn
        while True:
            msg = self.child_conn.recv() # PipeCom
            self.do_audogen(msg)
