import json
import time
import hashlib

from fastchat.conversation import Conversation
from common.model_workers.base import *
from common.utils import get_httpx_client
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal, Dict
from  common.api_configs import logger, log_verbose

def calculate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    encrypted = md5.hexdigest()
    return encrypted


class BaiChuanWorker(ApiModelWorker):
    def __init__(
        self,
        *,
        controller_addr: str = None,
        worker_addr: str = None,
        model_names: List[str] = ["baichuan-api"],
        version: Literal["Baichuan2-53B"] = "Baichuan2-53B",
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])

        url = "https://api.baichuan-ai.com/v1/stream/chat"
        data = {
            "model": params.version,
            "messages": params.messages,
            "parameters": {"temperature": params.temperature}
        }

        json_data = json.dumps(data)
        time_stamp = int(time.time())
        signature = calculate_md5(params.secret_key + json_data + str(time_stamp))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + params.api_key,
            "X-BC-Request-Id": "your requestId",
            "X-BC-Timestamp": str(time_stamp),
            "X-BC-Signature": signature,
            "X-BC-Sign-Algo": "MD5",
        }

        text = ""
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:json_data: {json_data}')
            logger.info(f'{self.__class__.__name__}:url: {url}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')

        with get_httpx_client() as client:
            with client.stream("POST", url, headers=headers, json=data) as response:
                for line in response.iter_lines():
                    if not line.strip():
                        continue
                    resp = json.loads(line)
                    if resp["code"] == 0:
                        text += resp["data"]["messages"][-1]["content"]
                        yield {
                            "error_code": resp["code"],
                            "text": text
                            }
                    else:
                        data = {
                            "error_code": resp["code"],
                            "text": resp["msg"],
                            "error": {
                                "message": resp["msg"],
                                "type": "invalid_request_error",
                                "param": None,
                                "code": None,
                            }
                        }
                        self.logger.error(f"请求百川 API 时发生错误：{data}")
                        yield data

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = BaiChuanWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21007",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21007)
    # do_request()
