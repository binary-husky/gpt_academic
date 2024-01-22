"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第一部分：来自EdgeGPT.py
https://github.com/acheong08/EdgeGPT
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""
"""
Main.py
"""

import argparse
import asyncio
import json
import os
import random
import re
import ssl
import sys
import time
import uuid
from enum import Enum
from pathlib import Path
from typing import Generator
from typing import Literal
from typing import Optional
from typing import Union

import aiohttp
import certifi
import httpx
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.live import Live
from rich.markdown import Markdown

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
    creative = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "h3imaginative",
        "travelansgnd",
        "dv3sugg",
        "clgalileo",
        "gencontentv3",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
        "nojbfedge",
    ]
    balanced = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "galileo",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
        "nojbfedge",
    ]
    precise = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "galileo",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
        "h3precise",
        "clgalileo",
        "nojbfedge",
    ]


CONVERSATION_STYLE_TYPE = Optional[
    Union[ConversationStyle, Literal["creative", "balanced", "precise"]]
]


def _append_identifier(msg: dict) -> str:
    """
    Appends special character to end of message to identify end of message
    """
    # Convert dict to json string
    return json.dumps(msg, ensure_ascii=False) + DELIMITER


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
        prompt: str,
        conversation_style: CONVERSATION_STYLE_TYPE,
        options=None,
        webpage_context=None,
        search_result=False,
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
            options = conversation_style.value
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "allowedMessageTypes": [
                        "Chat",
                        "Disengaged",
                        "AdsQuery",
                        "SemanticSerp",
                        "GenerateContentQuery",
                        "SearchQuery",
                    ],
                    "sliceIds": [
                        "chk1cf",
                        "nopreloadsscf",
                        "winlongmsg2tf",
                        "perfimpcomb",
                        "sugdivdis",
                        "sydnoinputt",
                        "wpcssopt",
                        "wintone2tf",
                        "0404sydicnbs0",
                        "405suggbs0",
                        "scctl",
                        "330uaugs0",
                        "0329resp",
                        "udscahrfon",
                        "udstrblm5",
                        "404e2ewrt",
                        "408nodedups0",
                        "403tvlansgnd",
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
        if search_result:
            have_search_result = [
                "InternalSearchQuery",
                "InternalSearchResult",
                "InternalLoaderMessage",
                "RenderCardRequest",
            ]
            self.struct["arguments"][0]["allowedMessageTypes"] += have_search_result
        if webpage_context:
            self.struct["arguments"][0]["previousMessages"] = [
                {
                    "author": "user",
                    "description": webpage_context,
                    "contextType": "WebPage",
                    "messageType": "Context",
                    "messageId": "discover-web--page-ping-mriduna-----",
                },
            ]
        self.invocation_id += 1


class _Conversation:
    """
    Conversation API
    """

    def __init__(
        self,
        proxy=None,
        async_mode=False,
        cookies=None,
    ) -> None:
        if async_mode:
            return
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
        if cookies:
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

    @staticmethod
    async def create(
        proxy=None,
        cookies=None,
    ):
        self = _Conversation(async_mode=True)
        self.struct = {
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
        transport = httpx.AsyncHTTPTransport(retries=10)
        # Convert cookie format to httpx format
        formatted_cookies = None
        if cookies:
            formatted_cookies = httpx.Cookies()
            for cookie in cookies:
                formatted_cookies.set(cookie["name"], cookie["value"])
        async with httpx.AsyncClient(
            proxies=proxy,
            timeout=30,
            headers=HEADERS_INIT_CONVER,
            transport=transport,
            cookies=formatted_cookies,
        ) as client:
            # Send GET request
            response = await client.get(
                url=os.environ.get("BING_PROXY_URL")
                or "https://edgeservices.bing.com/edgesvc/turing/conversation/create",
            )
            if response.status_code != 200:
                response = await client.get(
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
        return self


class _ChatHub:
    """
    Chat API
    """

    def __init__(
        self,
        conversation: _Conversation,
        proxy=None,
        cookies=None,
    ) -> None:
        self.session = None
        self.wss = None
        self.request: _ChatHubRequest
        self.loop: bool
        self.task: asyncio.Task
        self.request = _ChatHubRequest(
            conversation_signature=conversation.struct["conversationSignature"],
            client_id=conversation.struct["clientId"],
            conversation_id=conversation.struct["conversationId"],
        )
        self.cookies = cookies
        self.proxy: str = proxy

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
        webpage_context=None,
        search_result: bool = False,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        req_header = HEADERS
        if self.cookies is not None:
            ws_cookies = []
            for cookie in self.cookies:
                ws_cookies.append(f"{cookie['name']}={cookie['value']}")
            req_header.update(
                {
                    "Cookie": ";".join(ws_cookies),
                }
            )

        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

        if self.wss and not self.wss.closed:
            await self.wss.close()
        # Check if websocket is closed
        self.wss = await self.session.ws_connect(
            wss_link,
            headers=req_header,
            ssl=ssl_context,
            proxy=self.proxy,
            autoping=False,
        )
        await self._initial_handshake()
        if self.request.invocation_id == 0:
            # Construct a ChatHub request
            self.request.update(
                prompt=prompt,
                conversation_style=conversation_style,
                options=options,
                webpage_context=webpage_context,
                search_result=search_result,
            )
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://sydney.bing.com/sydney/UpdateConversation/",
                    json={
                        "messages": [
                            {
                                "author": "user",
                                "description": webpage_context,
                                "contextType": "WebPage",
                                "messageType": "Context",
                            },
                        ],
                        "conversationId": self.request.conversation_id,
                        "source": "cib",
                        "traceId": _get_ran_hex(32),
                        "participant": {"id": self.request.client_id},
                        "conversationSignature": self.request.conversation_signature,
                    },
                )
            if response.status_code != 200:
                print(f"Status code: {response.status_code}")
                print(response.text)
                print(response.url)
                raise Exception("Update web page context failed")
            # Construct a ChatHub request
            self.request.update(
                prompt=prompt,
                conversation_style=conversation_style,
                options=options,
            )
        # Send request
        await self.wss.send_str(_append_identifier(self.request.struct))
        final = False
        draw = False
        resp_txt = ""
        result_text = ""
        resp_txt_no_link = ""
        while not final:
            msg = await self.wss.receive()
            try:
                objects = msg.data.split(DELIMITER)
            except:
                continue

            for obj in objects:
                if obj is None or not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") != 2 and raw:
                    yield False, response
                elif response.get("type") == 1 and response["arguments"][0].get(
                    "messages",
                ):
                    if not draw:
                        if (
                            response["arguments"][0]["messages"][0].get("messageType")
                            == "GenerateContentQuery"
                        ):
                            async with ImageGenAsync("", True) as image_generator:
                                images = await image_generator.get_images(
                                    response["arguments"][0]["messages"][0]["text"],
                                )
                            for i, image in enumerate(images):
                                resp_txt = resp_txt + f"\n![image{i}]({image})"
                            draw = True
                        if (
                            response["arguments"][0]["messages"][0]["contentOrigin"]
                            != "Apology"
                        ) and not draw:
                            resp_txt = result_text + response["arguments"][0][
                                "messages"
                            ][0]["adaptiveCards"][0]["body"][0].get("text", "")
                            resp_txt_no_link = result_text + response["arguments"][0][
                                "messages"
                            ][0].get("text", "")
                            if response["arguments"][0]["messages"][0].get(
                                "messageType",
                            ):
                                resp_txt = (
                                    resp_txt
                                    + response["arguments"][0]["messages"][0][
                                        "adaptiveCards"
                                    ][0]["body"][0]["inlines"][0].get("text")
                                    + "\n"
                                )
                                result_text = (
                                    result_text
                                    + response["arguments"][0]["messages"][0][
                                        "adaptiveCards"
                                    ][0]["body"][0]["inlines"][0].get("text")
                                    + "\n"
                                )
                        yield False, resp_txt

                elif response.get("type") == 2:
                    if response["item"]["result"].get("error"):
                        await self.close()
                        raise Exception(
                            f"{response['item']['result']['value']}: {response['item']['result']['message']}",
                        )
                    if draw:
                        cache = response["item"]["messages"][1]["adaptiveCards"][0][
                            "body"
                        ][0]["text"]
                        response["item"]["messages"][1]["adaptiveCards"][0]["body"][0][
                            "text"
                        ] = (cache + resp_txt)
                    if (
                        response["item"]["messages"][-1]["contentOrigin"] == "Apology"
                        and resp_txt
                    ):
                        response["item"]["messages"][-1]["text"] = resp_txt_no_link
                        response["item"]["messages"][-1]["adaptiveCards"][0]["body"][0][
                            "text"
                        ] = resp_txt
                        print(
                            "Preserved the message from being deleted",
                            file=sys.stderr,
                        )
                    final = True
                    await self.close()
                    yield True, response

    async def _initial_handshake(self) -> None:
        await self.wss.send_str(_append_identifier({"protocol": "json", "version": 1}))
        await self.wss.receive()

    async def close(self) -> None:
        """
        Close the connection
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()
        if self.session and not self.session.closed:
            await self.session.close()


class Chatbot:
    """
    Combines everything to make it seamless
    """

    def __init__(
        self,
        proxy=None,
        cookies=None,
    ) -> None:
        self.proxy = proxy
        self.chat_hub: _ChatHub = _ChatHub(
            _Conversation(self.proxy, cookies=cookies),
            proxy=self.proxy,
            cookies=cookies,
        )

    @staticmethod
    async def create(
        proxy=None,
        cookies=None,
    ):
        self = Chatbot.__new__(Chatbot)
        self.proxy = proxy
        self.chat_hub = _ChatHub(
            await _Conversation.create(self.proxy, cookies=cookies),
            proxy=self.proxy,
            cookies=cookies,
        )
        return self

    async def ask(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        options: dict = None,
        webpage_context=None,
        search_result: bool = False,
    ) -> dict:
        """
        Ask a question to the bot
        """
        async for final, response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            options=options,
            webpage_context=webpage_context,
            search_result=search_result,
        ):
            if final:
                return response
        await self.chat_hub.wss.close()
        return {}

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
        webpage_context=None,
        search_result: bool = False,
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
            webpage_context=webpage_context,
            search_result=search_result,
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
        self.chat_hub = _ChatHub(
            await _Conversation.create(self.proxy),
            proxy=self.proxy,
            cookies=self.chat_hub.cookies,
        )


async def _get_input_async(
    session: PromptSession = None,
    completer: WordCompleter = None,
) -> str:
    """
    Multiline input function.
    """
    return await session.prompt_async(
        completer=completer,
        multiline=True,
        auto_suggest=AutoSuggestFromHistory(),
    )


def _create_session() -> PromptSession:
    kb = KeyBindings()

    @kb.add("enter")
    def _(event):
        buffer_text = event.current_buffer.text
        if buffer_text.startswith("!"):
            event.current_buffer.validate_and_handle()
        else:
            event.current_buffer.insert_text("\n")

    @kb.add("escape")
    def _(event):
        if event.current_buffer.complete_state:
            # event.current_buffer.cancel_completion()
            event.current_buffer.text = ""

    return PromptSession(key_bindings=kb, history=InMemoryHistory())


def _create_completer(commands: list, pattern_str: str = "$"):
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


async def async_main(args: argparse.Namespace) -> None:
    """
    Main function
    """
    print("Initializing...")
    print("Enter `alt+enter` or `escape+enter` to send a message")
    # Read and parse cookies
    cookies = None
    if args.cookie_file:
        cookies = json.loads(open(args.cookie_file, encoding="utf-8").read())
    bot = await Chatbot.create(proxy=args.proxy, cookies=cookies)
    session = _create_session()
    completer = _create_completer(["!help", "!exit", "!reset"])
    initial_prompt = args.prompt

    while True:
        print("\nYou:")
        if initial_prompt:
            question = initial_prompt
            print(question)
            initial_prompt = None
        else:
            question = (
                input()
                if args.enter_once
                else await _get_input_async(session=session, completer=completer)
            )
        print()
        if question == "!exit":
            break
        if question == "!help":
            print(
                """
            !help - Show this help message
            !exit - Exit the program
            !reset - Reset the conversation
            """,
            )
            continue
        if question == "!reset":
            await bot.reset()
            continue
        print("Bot:")
        if args.no_stream:
            print(
                (
                    await bot.ask(
                        prompt=question,
                        conversation_style=args.style,
                        wss_link=args.wss_link,
                    )
                )["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"],
            )
        else:
            wrote = 0
            if args.rich:
                md = Markdown("")
                with Live(md, auto_refresh=False) as live:
                    async for final, response in bot.ask_stream(
                        prompt=question,
                        conversation_style=args.style,
                        wss_link=args.wss_link,
                    ):
                        if not final:
                            if wrote > len(response):
                                print(md)
                                print(Markdown("***Bing revoked the response.***"))
                            wrote = len(response)
                            md = Markdown(response)
                            live.update(md, refresh=True)
            else:
                async for final, response in bot.ask_stream(
                    prompt=question,
                    conversation_style=args.style,
                    wss_link=args.wss_link,
                ):
                    if not final:
                        if not wrote:
                            print(response, end="", flush=True)
                        else:
                            print(response[wrote:], end="", flush=True)
                        wrote = len(response)
                print()
    await bot.close()


def main() -> None:
    print(
        """
        EdgeGPT - A demo of reverse engineering the Bing GPT chatbot
        Repo: github.com/acheong08/EdgeGPT
        By: Antonio Cheong

        !help for help

        Type !exit to exit
    """,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--enter-once", action="store_true")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--rich", action="store_true")
    parser.add_argument(
        "--proxy",
        help="Proxy URL (e.g. socks5://127.0.0.1:1080)",
        type=str,
    )
    parser.add_argument(
        "--wss-link",
        help="WSS URL(e.g. wss://sydney.bing.com/sydney/ChatHub)",
        type=str,
        default="wss://sydney.bing.com/sydney/ChatHub",
    )
    parser.add_argument(
        "--style",
        choices=["creative", "balanced", "precise"],
        default="balanced",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="",
        required=False,
        help="prompt to start with",
    )
    parser.add_argument(
        "--cookie-file",
        type=str,
        default="",
        required=False,
        help="path to cookie file",
    )
    args = parser.parse_args()
    asyncio.run(async_main(args))


class Cookie:
    """
    Convenience class for Bing Cookie files, data, and configuration. This Class
    is updated dynamically by the Query class to allow cycling through >1
    cookie/credentials file e.g. when daily request limits (current 200 per
    account per day) are exceeded.
    """

    current_file_index = 0
    dirpath = Path("./").resolve()
    search_pattern = "bing_cookies_*.json"
    ignore_files = set()

    @classmethod
    def fetch_default(cls, path=None):
        from selenium import webdriver
        from selenium.webdriver.common.by import By

        driver = webdriver.Edge()
        driver.get("https://bing.com/chat")
        time.sleep(5)
        xpath = '//button[@id="bnp_btn_accept"]'
        driver.find_element(By.XPATH, xpath).click()
        time.sleep(2)
        xpath = '//a[@id="codexPrimaryButton"]'
        driver.find_element(By.XPATH, xpath).click()
        if path is None:
            path = Path("./bing_cookies__default.json")
            # Double underscore ensures this file is first when sorted
        cookies = driver.get_cookies()
        Path(path).write_text(json.dumps(cookies, indent=4), encoding="utf-8")
        # Path again in case supplied path is: str
        print(f"Cookies saved to: {path}")
        driver.quit()

    @classmethod
    def files(cls):
        """Return a sorted list of all cookie files matching .search_pattern"""
        all_files = set(cls.dirpath.glob(cls.search_pattern))
        return sorted(list(all_files - cls.ignore_files))

    @classmethod
    def import_data(cls):
        """
        Read the active cookie file and populate the following attributes:

          .current_filepath
          .current_data
          .image_token
        """
        try:
            cls.current_filepath = cls.files()[cls.current_file_index]
        except IndexError:
            print(
                "> Please set Cookie.current_filepath to a valid cookie file, then run Cookie.import_data()",
            )
            return
        print(f"> Importing cookies from: {cls.current_filepath.name}")
        with open(cls.current_filepath, encoding="utf-8") as file:
            cls.current_data = json.load(file)
        cls.image_token = [x for x in cls.current_data if x.get("name") == "_U"]
        cls.image_token = cls.image_token[0].get("value")

    @classmethod
    def import_next(cls):
        """
        Cycle through to the next cookies file.  Import it.  Mark the previous
        file to be ignored for the remainder of the current session.
        """
        cls.ignore_files.add(cls.current_filepath)
        if Cookie.current_file_index >= len(cls.files()):
            Cookie.current_file_index = 0
        Cookie.import_data()


class Query:
    """
    A convenience class that wraps around EdgeGPT.Chatbot to encapsulate input,
    config, and output all together.  Relies on Cookie class for authentication
    """

    def __init__(
        self,
        prompt,
        style="precise",
        content_type="text",
        cookie_file=0,
        echo=True,
        echo_prompt=False,
    ):
        """
        Arguments:

        prompt: Text to enter into Bing Chat
        style: creative, balanced, or precise
        content_type: "text" for Bing Chat; "image" for Dall-e
        cookie_file: Path, filepath string, or index (int) to list of cookie paths
        echo: Print something to confirm request made
        echo_prompt: Print confirmation of the evaluated prompt
        """
        self.index = []
        self.request_count = {}
        self.image_dirpath = Path("./").resolve()
        Cookie.import_data()
        self.index += [self]
        self.prompt = prompt
        files = Cookie.files()
        if isinstance(cookie_file, int):
            index = cookie_file if cookie_file < len(files) else 0
        else:
            if not isinstance(cookie_file, (str, Path)):
                message = "'cookie_file' must be an int, str, or Path object"
                raise TypeError(message)
            cookie_file = Path(cookie_file)
            if cookie_file in files():  # Supplied filepath IS in Cookie.dirpath
                index = files.index(cookie_file)
            else:  # Supplied filepath is NOT in Cookie.dirpath
                if cookie_file.is_file():
                    Cookie.dirpath = cookie_file.parent.resolve()
                if cookie_file.is_dir():
                    Cookie.dirpath = cookie_file.resolve()
                index = 0
        Cookie.current_file_index = index
        if content_type == "text":
            self.style = style
            self.log_and_send_query(echo, echo_prompt)
        if content_type == "image":
            self.create_image()

    def log_and_send_query(self, echo, echo_prompt):
        self.response = asyncio.run(self.send_to_bing(echo, echo_prompt))
        name = str(Cookie.current_filepath.name)
        if not self.request_count.get(name):
            self.request_count[name] = 1
        else:
            self.request_count[name] += 1

    def create_image(self):
        image_generator = ImageGen(Cookie.image_token)
        image_generator.save_images(
            image_generator.get_images(self.prompt),
            output_dir=self.image_dirpath,
        )

    async def send_to_bing(self, echo=True, echo_prompt=False):
        """Creat, submit, then close a Chatbot instance.  Return the response"""
        retries = len(Cookie.files())
        while retries:
            try:
                bot = await Chatbot.create()
                if echo_prompt:
                    print(f"> {self.prompt=}")
                if echo:
                    print("> Waiting for response...")
                if self.style.lower() not in "creative balanced precise".split():
                    self.style = "precise"
                response = await bot.ask(
                    prompt=self.prompt,
                    conversation_style=getattr(ConversationStyle, self.style),
                    # wss_link="wss://sydney.bing.com/sydney/ChatHub"
                    # What other values can this parameter take? It seems to be optional
                )
                return response
            except KeyError:
                print(
                    f"> KeyError [{Cookie.current_filepath.name} may have exceeded the daily limit]",
                )
                Cookie.import_next()
                retries -= 1
            finally:
                await bot.close()

    @property
    def output(self):
        """The response from a completed Chatbot request"""
        return self.response["item"]["messages"][1]["text"]

    @property
    def sources(self):
        """The source names and details parsed from a completed Chatbot request"""
        return self.response["item"]["messages"][1]["sourceAttributions"]

    @property
    def sources_dict(self):
        """The source names and details as a dictionary"""
        sources_dict = {}
        name = "providerDisplayName"
        url = "seeMoreUrl"
        for source in self.sources:
            if name in source.keys() and url in source.keys():
                sources_dict[source[name]] = source[url]
            else:
                continue
        return sources_dict

    @property
    def code(self):
        """Extract and join any snippets of Python code in the response"""
        code_blocks = self.output.split("```")[1:-1:2]
        code_blocks = ["\n".join(x.splitlines()[1:]) for x in code_blocks]
        return "\n\n".join(code_blocks)

    @property
    def languages(self):
        """Extract all programming languages given in code blocks"""
        code_blocks = self.output.split("```")[1:-1:2]
        return {x.splitlines()[0] for x in code_blocks}

    @property
    def suggestions(self):
        """Follow-on questions suggested by the Chatbot"""
        return [
            x["text"]
            for x in self.response["item"]["messages"][1]["suggestedResponses"]
        ]

    def __repr__(self):
        return f"<EdgeGPT.Query: {self.prompt}>"

    def __str__(self):
        return self.output


class ImageQuery(Query):
    def __init__(self, prompt, **kwargs):
        kwargs.update({"content_type": "image"})
        super().__init__(prompt, **kwargs)

    def __repr__(self):
        return f"<EdgeGPT.ImageQuery: {self.prompt}>"


if __name__ == "__main__":
    main()
