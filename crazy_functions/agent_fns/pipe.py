from toolbox import CatchException, update_ui, gen_time_str, trimmed_format_exc, is_the_upload_folder
import time

class PipeCom():
    def __init__(self, cmd, content) -> None:
        self.cmd = cmd
        self.content = content

class PluginMultiprocessManager():
    def __init__(self, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
        # ⭐ 主进程
        self.llm_kwargs = llm_kwargs
        self.plugin_kwargs = plugin_kwargs
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.web_port = web_port
        self.alive = True

    def is_alive(self):
        return self.alive

    def launch_subprocess_with_pipe(self):
        # ⭐ 主进程
        from multiprocessing import Process, Pipe
        parent_conn, child_conn = Pipe()
        self.p = Process(target=self.subprocess_worker, args=(child_conn,))
        self.p.daemon = True
        self.p.start()
        return parent_conn

    def terminate(self):
        self.p.terminate()
        self.alive = False
        print('[debug] instance terminated')

    def subprocess_worker(self, child_conn):
        # ⭐⭐ 子进程
        raise NotImplementedError

    def send_command(self, cmd):
        # ⭐ 主进程
        self.parent_conn.send(PipeCom("user_input", cmd))

    def main_process_ui_control(self, txt, create_or_resume) -> str:
        # ⭐ 主进程
        if create_or_resume == 'create':
            self.cnt = 1
            self.parent_conn = self.launch_subprocess_with_pipe() # ⭐⭐⭐
        self.send_command(txt)
        if txt == 'exit': 
            self.chatbot.append([f"结束", "结束信号已明确，终止AutoGen程序。"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            self.terminate()
            return "terminate"
        
        while True:
            time.sleep(0.5)
            if self.parent_conn.poll(): 
                if '[GPT-Academic] 等待中' in self.chatbot[-1][-1]:
                    self.chatbot.pop(-1)    # remove the last line
                msg = self.parent_conn.recv() # PipeCom
                if msg.cmd == "done":
                    self.chatbot.append([f"结束", msg.content]); self.cnt += 1
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                    self.terminate(); break
                if msg.cmd == "show":
                    self.chatbot.append([f"运行阶段-{self.cnt}", msg.content]); self.cnt += 1
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                if msg.cmd == "interact":
                    self.chatbot.append([f"程序抵达用户反馈节点.", msg.content + 
                                         "\n\n等待您的进一步指令. \n\n(1) 如果您没有什么想说的, 清空输入区,然后直接点击“提交”以继续. " +
                                         "\n\n(2) 如果您需要补充些什么, 输入要反馈的内容, 直接点击“提交”以继续. " +
                                         "\n\n(3) 如果您想终止程序, 输入exit, 直接点击“提交”以终止AutoGen并解锁. "
                                         ])
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                    # do not terminate here, leave the subprocess_worker instance alive
                    return "wait_feedback"
            else:
                if '[GPT-Academic] 等待中' not in self.chatbot[-1][-1]:
                    self.chatbot.append(["[GPT-Academic] 等待AutoGen执行结果 ...", "[GPT-Academic] 等待中"])
                self.chatbot[-1] = [self.chatbot[-1][0], self.chatbot[-1][1].replace("[GPT-Academic] 等待中", "[GPT-Academic] 等待中.")]
                yield from update_ui(chatbot=self.chatbot, history=self.history)

        self.terminate()
        return "terminate"

    def subprocess_worker_wait_user_feedback(self, wait_msg="wait user feedback"):
        # ⭐⭐ 子进程
        patience = 5 * 60
        begin_waiting_time = time.time()
        self.child_conn.send(PipeCom("interact", wait_msg))
        while True:
            time.sleep(0.5)
            if self.child_conn.poll(): 
                wait_success = True
                break
            if time.time() - begin_waiting_time > patience:
                self.child_conn.send(PipeCom("done", ""))
                wait_success = False
                break
        return wait_success

