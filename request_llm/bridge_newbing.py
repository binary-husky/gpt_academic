"""
========================================================================
第一部分：来自EdgeGPT.py
https://github.com/acheong08/EdgeGPT
========================================================================
"""
from .edge_gpt import NewbingChatbot
load_message = "等待NewBing响应。"

"""
========================================================================
第二部分：子进程Worker（调用主体）
========================================================================
"""
import time
import json
import re
import asyncio
import importlib
import threading
from toolbox import update_ui, get_conf, trimmed_format_exc
from multiprocessing import Process, Pipe

def preprocess_newbing_out(s):
    pattern = r'\^(\d+)\^' # 匹配^数字^
    sub = lambda m: '\['+m.group(1)+'\]' # 将匹配到的数字作为替换值
    result = re.sub(pattern, sub, s) # 替换操作
    if '[1]' in result:
        result += '\n\n```\n' + "\n".join([r for r in result.split('\n') if r.startswith('[')]) + '\n```\n'
    return result

def preprocess_newbing_out_simple(result):
    if '[1]' in result:
        result += '\n\n```\n' + "\n".join([r for r in result.split('\n') if r.startswith('[')]) + '\n```\n'
    return result

class NewBingHandle(Process):
    def __init__(self):
        super().__init__(daemon=True)
        self.parent, self.child = Pipe()
        self.newbing_model = None
        self.info = ""
        self.success = True
        self.local_history = []
        self.check_dependency()
        self.start()
        self.threadLock = threading.Lock()
        
    def check_dependency(self):
        try:
            self.success = False
            import certifi, httpx, rich
            self.info = "依赖检测通过，等待NewBing响应。注意目前不能多人同时调用NewBing接口（有线程锁），否则将导致每个人的NewBing问询历史互相渗透。调用NewBing时，会自动使用已配置的代理。"
            self.success = True
        except:
            self.info = "缺少的依赖，如果要使用Newbing，除了基础的pip依赖以外，您还需要运行`pip install -r request_llm/requirements_newbing.txt`安装Newbing的依赖。"
            self.success = False

    def ready(self):
        return self.newbing_model is not None

    async def async_run(self):
        # 读取配置
        NEWBING_STYLE, = get_conf('NEWBING_STYLE')
        from request_llm.bridge_all import model_info
        endpoint = model_info['newbing']['endpoint']
        while True:
            # 等待
            kwargs = self.child.recv()
            question=kwargs['query']
            history=kwargs['history']
            system_prompt=kwargs['system_prompt']

            # 是否重置
            if len(self.local_history) > 0 and len(history)==0:
                await self.newbing_model.reset()
                self.local_history = []

            # 开始问问题
            prompt = ""
            if system_prompt not in self.local_history:
                self.local_history.append(system_prompt)
                prompt += system_prompt + '\n'

            # 追加历史
            for ab in history:
                a, b = ab
                if a not in self.local_history:
                    self.local_history.append(a)
                    prompt += a + '\n'
                if b not in self.local_history:
                    self.local_history.append(b)
                    prompt += b + '\n'

            # 问题
            prompt += question
            self.local_history.append(question)
            
            # 提交
            async for final, response in self.newbing_model.ask_stream(
                prompt=question,
                conversation_style=NEWBING_STYLE,     # ["creative", "balanced", "precise"]
                wss_link=endpoint,                      # "wss://sydney.bing.com/sydney/ChatHub"
            ):
                if not final:
                    print(response)
                    self.child.send(str(response))
                else:
                    print('-------- receive final ---------')
                    self.child.send('[Finish]')
            
    
    def run(self):
        """
        这个函数运行在子进程
        """
        # 第一次运行，加载参数
        self.success = False
        self.local_history = []
        if (self.newbing_model is None) or (not self.success):
            # 代理设置
            proxies, = get_conf('proxies')
            if proxies is None: 
                self.proxies_https = None
            else: 
                self.proxies_https = proxies['https']
            # cookie
            NEWBING_COOKIES, = get_conf('NEWBING_COOKIES')
            try:
                cookies = json.loads(NEWBING_COOKIES)
            except:
                self.success = False
                tb_str = '\n```\n' + trimmed_format_exc() + '\n```\n'
                self.child.send(f'[Local Message] 不能加载Newbing组件。NEWBING_COOKIES未填写或有格式错误。')
                self.child.send('[Fail]')
                self.child.send('[Finish]')
                raise RuntimeError(f"不能加载Newbing组件。NEWBING_COOKIES未填写或有格式错误。")

            try:
                self.newbing_model = NewbingChatbot(proxy=self.proxies_https, cookies=cookies)
            except:
                self.success = False
                tb_str = '\n```\n' + trimmed_format_exc() + '\n```\n'
                self.child.send(f'[Local Message] 不能加载Newbing组件。{tb_str}')
                self.child.send('[Fail]')
                self.child.send('[Finish]')
                raise RuntimeError(f"不能加载Newbing组件。")

        self.success = True
        try:
            # 进入任务等待状态
            asyncio.run(self.async_run())
        except Exception:
            tb_str = '```\n' + trimmed_format_exc() + '```'
            self.child.send(f'[Local Message] Newbing失败 {tb_str}.')
            self.child.send('[Fail]')
            self.child.send('[Finish]')
        
    def stream_chat(self, **kwargs):
        """
        这个函数运行在主进程
        """
        self.threadLock.acquire()
        self.parent.send(kwargs)    # 发送请求到子进程
        while True:
            res = self.parent.recv()    # 等待newbing回复的片段
            if res == '[Finish]':
                break       # 结束
            elif res == '[Fail]':
                self.success = False
                break
            else:
                yield res   # newbing回复的片段
        self.threadLock.release()


"""
========================================================================
第三部分：主进程统一调用函数接口
========================================================================
"""
global newbing_handle
newbing_handle = None

def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=None, console_slience=False):
    """
        多线程方法
        函数的说明请见 request_llm/bridge_all.py
    """
    global newbing_handle
    if (newbing_handle is None) or (not newbing_handle.success):
        newbing_handle = NewBingHandle()
        observe_window[0] = load_message + "\n\n" + newbing_handle.info
        if not newbing_handle.success: 
            error = newbing_handle.info
            newbing_handle = None
            raise RuntimeError(error)

    # 没有 sys_prompt 接口，因此把prompt加入 history
    history_feedin = []
    for i in range(len(history)//2):
        history_feedin.append([history[2*i], history[2*i+1]] )

    watch_dog_patience = 5 # 看门狗 (watchdog) 的耐心, 设置5秒即可
    response = ""
    observe_window[0] = "[Local Message]: 等待NewBing响应中 ..."
    for response in newbing_handle.stream_chat(query=inputs, history=history_feedin, system_prompt=sys_prompt, max_length=llm_kwargs['max_length'], top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        observe_window[0] = preprocess_newbing_out_simple(response)
        if len(observe_window) >= 2:  
            if (time.time()-observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
    return preprocess_newbing_out_simple(response)

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        单线程方法
        函数的说明请见 request_llm/bridge_all.py
    """
    chatbot.append((inputs, "[Local Message]: 等待NewBing响应中 ..."))

    global newbing_handle
    if (newbing_handle is None) or (not newbing_handle.success):
        newbing_handle = NewBingHandle()
        chatbot[-1] = (inputs, load_message + "\n\n" + newbing_handle.info)
        yield from update_ui(chatbot=chatbot, history=[])
        if not newbing_handle.success: 
            newbing_handle = None
            return

    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)    # 热更新prompt
        core_functional = core_functional.get_core_functions()
        if "PreProcess" in core_functional[additional_fn]: inputs = core_functional[additional_fn]["PreProcess"](inputs)  # 获取预处理函数（如果有的话）
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]

    history_feedin = []
    for i in range(len(history)//2):
        history_feedin.append([history[2*i], history[2*i+1]] )

    chatbot[-1] = (inputs, "[Local Message]: 等待NewBing响应中 ...")
    yield from update_ui(chatbot=chatbot, history=history, msg="NewBing响应缓慢，尚未完成全部响应，请耐心完成后再提交新问题。")
    for response in newbing_handle.stream_chat(query=inputs, history=history_feedin, system_prompt=system_prompt, max_length=llm_kwargs['max_length'], top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        chatbot[-1] = (inputs, preprocess_newbing_out(response))
        yield from update_ui(chatbot=chatbot, history=history, msg="NewBing响应缓慢，尚未完成全部响应，请耐心完成后再提交新问题。")

    history.extend([inputs, preprocess_newbing_out(response)])
    yield from update_ui(chatbot=chatbot, history=history, msg="完成全部响应，请提交新问题。")

