"""
========================================================================
第一部分：来自EdgeGPT.py
https://github.com/acheong08/EdgeGPT
========================================================================
"""


import argparse
import asyncio
import json
import os
import random
import re
import ssl
import sys
import uuid
from enum import Enum
from typing import Generator
from typing import Literal
from typing import Optional
from typing import Union
import certifi
import httpx
import websockets.client as websockets

DELIMITER = "\x1e"


# Generate random IP between range 13.104.0.0/14
FORWARDED_IP = (
    f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
)

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not_A Brand";v="99", "Microsoft Edge";v="110", "Chromium";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"109.0.1518.78"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": FORWARDED_IP,
}

HEADERS_INIT_CONVER = {
    "authority": "edgeservices.bing.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"110.0.1587.69"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
    "x-edge-shopping-flag": "1",
    "x-forwarded-for": FORWARDED_IP,
}

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class NotAllowedToAccess(Exception):
    pass


class ConversationStyle(Enum):
    creative = "h3imaginative,clgalileo,gencontentv3"
    balanced = "galileo"
    precise = "h3precise,clgalileo"


CONVERSATION_STYLE_TYPE = Optional[
    Union[ConversationStyle, Literal["creative", "balanced", "precise"]]
]


def _append_identifier(msg: dict) -> str:
    """
    Appends special character to end of message to identify end of message
    """
    # Convert dict to json string
    return json.dumps(msg) + DELIMITER


def _get_ran_hex(length: int = 32) -> str:
    """
    Returns random hex string
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(length))


class _ChatHubRequest:
    """
    Request object for ChatHub
    """

    def __init__(
        self,
        conversation_signature: str,
        client_id: str,
        conversation_id: str,
        invocation_id: int = 0,
    ) -> None:
        self.struct: dict = {}

        self.client_id: str = client_id
        self.conversation_id: str = conversation_id
        self.conversation_signature: str = conversation_signature
        self.invocation_id: int = invocation_id

    def update(
        self,
        prompt,
        conversation_style,
        options,
    ) -> None:
        """
        Updates request object
        """
        if options is None:
            options = [
                "deepleo",
                "enable_debug_commands",
                "disable_emoji_spoken_text",
                "enablemm",
            ]
        if conversation_style:
            if not isinstance(conversation_style, ConversationStyle):
                conversation_style = getattr(ConversationStyle, conversation_style)
            options = [
                "nlu_direct_response_filter",
                "deepleo",
                "disable_emoji_spoken_text",
                "responsible_ai_policy_235",
                "enablemm",
                conversation_style.value,
                "dtappid",
                "cricinfo",
                "cricinfov2",
                "dv3sugg",
            ]
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "sliceIds": [
                        "222dtappid",
                        "225cricinfo",
                        "224locals0",
                    ],
                    "traceId": _get_ran_hex(32),
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                },
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }
        self.invocation_id += 1


class _Conversation:
    """
    Conversation API
    """

    def __init__(
        self,
        cookies,
        proxy,
    ) -> None:
        self.struct: dict = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.proxy = proxy
        proxy = (
            proxy
            or os.environ.get("all_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or None
        )
        if proxy is not None and proxy.startswith("socks5h://"):
            proxy = "socks5://" + proxy[len("socks5h://") :]
        self.session = httpx.Client(
            proxies=proxy,
            timeout=30,
            headers=HEADERS_INIT_CONVER,
        )
        for cookie in cookies:
            self.session.cookies.set(cookie["name"], cookie["value"])

        # Send GET request
        response = self.session.get(
            url=os.environ.get("BING_PROXY_URL")
            or "https://edgeservices.bing.com/edgesvc/turing/conversation/create",
        )
        if response.status_code != 200:
            response = self.session.get(
                "https://edge.churchless.tech/edgesvc/turing/conversation/create",
            )
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)
            print(response.url)
            raise Exception("Authentication failed")
        try:
            self.struct = response.json()
        except (json.decoder.JSONDecodeError, NotAllowedToAccess) as exc:
            raise Exception(
                "Authentication failed. You have not been accepted into the beta.",
            ) from exc
        if self.struct["result"]["value"] == "UnauthorizedRequest":
            raise NotAllowedToAccess(self.struct["result"]["message"])


class _ChatHub:
    """
    Chat API
    """

    def __init__(self, conversation) -> None:
        self.wss = None
        self.request: _ChatHubRequest
        self.loop: bool
        self.task: asyncio.Task
        print(conversation.struct)
        self.request = _ChatHubRequest(
            conversation_signature=conversation.struct["conversationSignature"],
            client_id=conversation.struct["clientId"],
            conversation_id=conversation.struct["conversationId"],
        )

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()
        # Check if websocket is closed
        self.wss = await websockets.connect(
            wss_link,
            extra_headers=HEADERS,
            max_size=None,
            ssl=ssl_context,
        )
        await self._initial_handshake()
        # Construct a ChatHub request
        self.request.update(
            prompt=prompt,
            conversation_style=conversation_style,
            options=options,
        )
        # Send request
        await self.wss.send(_append_identifier(self.request.struct))
        final = False
        while not final:
            objects = str(await self.wss.recv()).split(DELIMITER)
            for obj in objects:
                if obj is None or not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") != 2 and raw:
                    yield False, response
                elif response.get("type") == 1 and response["arguments"][0].get(
                    "messages",
                ):
                    resp_txt = response["arguments"][0]["messages"][0]["adaptiveCards"][
                        0
                    ]["body"][0].get("text")
                    yield False, resp_txt
                elif response.get("type") == 2:
                    final = True
                    yield True, response

    async def _initial_handshake(self) -> None:
        await self.wss.send(_append_identifier({"protocol": "json", "version": 1}))
        await self.wss.recv()

    async def close(self) -> None:
        """
        Close the connection
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()


class Chatbot:
    """
    Combines everything to make it seamless
    """

    def __init__(
        self,
        cookies,
        proxy
    ) -> None:
        if cookies is None:
            cookies = {}
        self.cookies = cookies
        self.proxy = proxy
        self.chat_hub: _ChatHub = _ChatHub(
            _Conversation(self.cookies, self.proxy),
        )

    async def ask(
        self,
        prompt: str,
        wss_link: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        options: dict = None,
    ) -> dict:
        """
        Ask a question to the bot
        """
        async for final, response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            options=options,
        ):
            if final:
                return response
        await self.chat_hub.wss.close()
        return None

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        async for response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            raw=raw,
            options=options,
        ):
            yield response

    async def close(self) -> None:
        """
        Close the connection
        """
        await self.chat_hub.close()

    async def reset(self) -> None:
        """
        Reset the conversation
        """
        await self.close()
        self.chat_hub = _ChatHub(_Conversation(self.cookies, self.proxy))



load_message = "等待NewBing响应。"

"""
========================================================================
第二部分：子进程Worker（调用主体）
========================================================================
"""
import time
import importlib
from toolbox import update_ui, get_conf, trimmed_format_exc
from multiprocessing import Process, Pipe

class GetNewBingHandle(Process):
    def __init__(self):
        super().__init__(daemon=True)
        self.parent, self.child = Pipe()
        self.newbing_model = None
        self.info = ""
        self.success = True
        self.local_history = []
        self.check_dependency()
        self.start()
        
    def check_dependency(self):
        try:
            self.success = False
            import rich
            self.info = "依赖检测通过，等待NewBing响应。注意目前不能多人同时调用NewBing接口，否则将导致每个人的NewBing问询历史互相渗透。调用NewBing时，会自动使用已配置的代理。"
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
                self.newbing_model = Chatbot(proxy=self.proxies_https, cookies=cookies)
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
        return
    

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
        newbing_handle = GetNewBingHandle()
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
        newbing_handle = GetNewBingHandle()
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

