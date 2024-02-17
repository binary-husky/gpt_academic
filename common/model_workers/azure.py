import sys
import os
from fastchat.conversation import Conversation
from common.model_workers.base import *
from common.utils import get_httpx_client
from fastchat import conversation as conv
import json
from typing import List, Dict
from  common.api_configs import logger, log_verbose


class AzureWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str = None,
            worker_addr: str = None,
            model_names: List[str] = ["azure-api"],
            version: str = "gpt-35-turbo",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])

        data = dict(
            messages=params.messages,
            temperature=params.temperature,
            max_tokens=params.max_tokens if params.max_tokens else None,
            stream=True,
        )
        url = ("https://{}.openai.azure.com/openai/deployments/{}/chat/completions?api-version={}"
               .format(params.resource_name, params.deployment_name, params.api_version))
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': params.api_key,
        }

        text = ""
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:url: {url}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')
            logger.info(f'{self.__class__.__name__}:data: {data}')

        with get_httpx_client() as client:
            with client.stream("POST", url, headers=headers, json=data) as response:
                print(data)
                for line in response.iter_lines():
                    if not line.strip() or "[DONE]" in line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    resp = json.loads(line)
                    if choices := resp["choices"]:
                        if chunk := choices[0].get("delta", {}).get("content"):
                            text += chunk
                            yield {
                                    "error_code": 0,
                                    "text": text
                                }
                        print(text)
                    else:
                        self.logger.error(f"请求 Azure API 时发生错误：{resp}")

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="You are a helpful, respectful and honest assistant.",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = AzureWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21008",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21008)