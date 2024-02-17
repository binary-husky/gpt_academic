import json
import time
import hashlib

from fastchat.conversation import Conversation
from common.model_workers.base import *
from common.utils import get_httpx_client
from fastchat import conversation as conv
import json
from typing import List, Literal, Dict
import requests


class TianGongWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str = None,
            worker_addr: str = None,
            model_names: List[str] = ["tiangong-api"],
            version: Literal["SkyChat-MegaVerse"] = "SkyChat-MegaVerse",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])

        url = 'https://sky-api.singularity-ai.com/saas/api/v4/generate'
        data = {
            "messages": params.messages,
            "model": "SkyChat-MegaVerse"
        }
        timestamp = str(int(time.time()))
        sign_content = params.api_key + params.secret_key + timestamp
        sign_result = hashlib.md5(sign_content.encode('utf-8')).hexdigest()
        headers = {
            "app_key": params.api_key,
            "timestamp": timestamp,
            "sign": sign_result,
            "Content-Type": "application/json",
            "stream": "true"  # or change to "false" 不处理流式返回内容
        }

        # 发起请求并获取响应
        response = requests.post(url, headers=headers, json=data, stream=True)

        text = ""
        # 处理响应流
        for line in response.iter_lines(chunk_size=None, decode_unicode=True):
            if line:
                # 处理接收到的数据
                # print(line.decode('utf-8'))
                resp = json.loads(line)
                if resp["code"] == 200:
                    text += resp['resp_data']['reply']
                    yield {
                        "error_code": 0,
                        "text": text
                    }
                else:
                    data = {
                        "error_code": resp["code"],
                        "text": resp["code_msg"]
                    }
                    self.logger.error(f"请求天工 API 时出错：{data}")
                    yield data

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "system"],
            sep="\n### ",
            stop_str="###",
        )
