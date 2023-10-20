# 本源代码中, ⭐ = 关键步骤
"""
测试：
    - 裁剪图像，保留下半部分
    - 交换图像的蓝色通道和红色通道
    - 将图像转为灰度图像
    - 将csv文件转excel表格

Testing: 
    - Crop the image, keeping the bottom half. 
    - Swap the blue channel and red channel of the image. 
    - Convert the image to grayscale. 
    - Convert the CSV file to an Excel spreadsheet.
"""


from toolbox import CatchException, update_ui, gen_time_str, trimmed_format_exc, ProxyNetworkActivate
from toolbox import report_execption, get_log_folder, update_ui_lastest_msg, Singleton
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, get_plugin_arg
from crazy_functions.crazy_utils import input_clipping, try_install_deps
from crazy_functions.agent_fns.persistent import GradioMultiuserManagerForPersistentClasses
from crazy_functions.agent_fns.pipe import PluginMultiprocessManager, PipeCom
from crazy_functions.agent_fns.echo_agent import EchoDemo
import time

class AutoGenWorker(PluginMultiprocessManager):

    def gpt_academic_print_override(self, user_proxy, message, sender):
        self.child_conn.send(PipeCom("show", sender.name + '\n\n---\n\n' + message['content']))

    def gpt_academic_get_human_input(self, user_proxy, message):
        # ⭐⭐ 子进程
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

    def do_audogen(self, input):
        # ⭐⭐ 子进程
        input = input.content
        with ProxyNetworkActivate("AutoGen"):
            from autogen import AssistantAgent, UserProxyAgent
            config_list = [{
                'model': 'gpt-3.5-turbo-16k', 
                'api_key': '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',
            },]


            autogen_work_dir = get_log_folder('autogen')
            code_execution_config={"work_dir": autogen_work_dir, "use_docker":True}
            # create an AssistantAgent instance named "assistant"
            assistant = AssistantAgent(
                name="assistant",
                llm_config={
                    "config_list": config_list,
                }
            )
            # create a UserProxyAgent instance named "user_proxy"
            user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="ALWAYS",
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            )

            # assistant = AssistantAgent("assistant", llm_config={"config_list": config_list}, code_execution_config=code_execution_config)
            # user_proxy = UserProxyAgent("user_proxy", code_execution_config=code_execution_config)
            
            user_proxy._print_received_message = lambda a,b: self.gpt_academic_print_override(user_proxy, a, b)
            assistant._print_received_message = lambda a,b: self.gpt_academic_print_override(user_proxy, a, b)
            user_proxy.get_human_input = lambda a: self.gpt_academic_get_human_input(user_proxy, a)
            # user_proxy.initiate_chat(assistant, message=input)
            try:
                user_proxy.initiate_chat(assistant, message=input)
            except Exception as e:
                tb_str = '```\n' + trimmed_format_exc() + '```'
                self.child_conn.send(PipeCom("done", "AutoGen 执行失败: \n\n" + tb_str))

    def subprocess_worker(self, child_conn):
        # ⭐⭐ 子进程
        self.child_conn = child_conn
        while True:
            msg = self.child_conn.recv() # PipeCom
            self.do_audogen(msg)

@CatchException
def 多智能体终端(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import autogen
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pyautogen```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    chatbot.get_cookies()['lock_plugin'] = None
    persistent_class_multi_user_manager = GradioMultiuserManagerForPersistentClasses()
    user_uuid = chatbot.get_cookies().get('uuid')
    persistent_key = f"{user_uuid}->多智能体终端"
    if persistent_class_multi_user_manager.already_alive(persistent_key):
        # 当已经存在一个正在运行的多智能体终端时，直接将用户输入传递给它，而不是再次启动一个新的多智能体终端
        print('[debug] feed new user input')
        executor = persistent_class_multi_user_manager.get(persistent_key)
        exit_reason = yield from executor.main_process_ui_control(txt, create_or_resume="resume")
    else:
        # 运行多智能体终端 (首次)
        print('[debug] create new executor instance')
        history = []
        chatbot.append(["正在启动: 多智能体终端", "插件动态生成, 执行开始, 作者 Microsoft & Binary-Husky."])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        executor = AutoGenWorker(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
        persistent_class_multi_user_manager.set(persistent_key, executor)
        exit_reason = yield from executor.main_process_ui_control(txt, create_or_resume="create")

    if exit_reason == "wait_feedback":
        # 当用户点击了“等待反馈”按钮时，将executor存储到cookie中，等待用户的再次调用
        executor.chatbot.get_cookies()['lock_plugin'] = 'crazy_functions.多智能体->多智能体终端'
    else:
        executor.chatbot.get_cookies()['lock_plugin'] = None
    yield from update_ui(chatbot=executor.chatbot, history=executor.history) # 更新状态
