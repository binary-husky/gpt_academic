from contextlib import contextmanager

import httpx
from fastchat.conversation import Conversation
from httpx_sse import EventSource

from common.model_workers.base import *
from fastchat import conversation as conv
import sys
from typing import List, Dict, Iterator, Literal, Any
import jwt
import time


@contextmanager
def connect_sse(client: httpx.Client, method: str, url: str, **kwargs: Any):
    with client.stream(method, url, **kwargs) as response:
        yield EventSource(response)


def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


class ChatGLMWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            model_names: List[str] = ["zhipu-api"],
            controller_addr: str = None,
            worker_addr: str = None,
            version: Literal["glm-4"] = "glm-4",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 4096)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Iterator[Dict]:
        params.load_config(self.model_names[0])
        token = generate_token(params.api_key, 60)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "model": params.version,
            "messages": params.messages,
            "max_tokens": params.max_tokens,
            "temperature": params.temperature,
            "stream": False
        }

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        with httpx.Client(headers=headers) as client:
            response = client.post(url, json=data)
            response.raise_for_status()
            chunk = response.json()
            print(chunk)
            yield {"error_code": 0, "text": chunk["choices"][0]["message"]["content"]}

            # with connect_sse(client, "POST", url, json=data) as event_source:
            #     for sse in event_source.iter_sse():
            #         chunk = json.loads(sse.data)
            #         if len(chunk["choices"]) != 0:
            #             text += chunk["choices"][0]["delta"]["content"]
            #             yield {"error_code": 0, "text": text}



    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是智谱AI小助手，请根据用户的提示来完成任务",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n###",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)
