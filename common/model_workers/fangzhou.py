from fastchat.conversation import Conversation
from common.model_workers.base import *
from fastchat import conversation as conv
import sys
from typing import List, Literal, Dict
from  common.api_configs import logger, log_verbose


class FangZhouWorker(ApiModelWorker):
    """
    火山方舟
    """

    def __init__(
            self,
            *,
            model_names: List[str] = ["fangzhou-api"],
            controller_addr: str = None,
            worker_addr: str = None,
            version: Literal["chatglm-6b-model"] = "chatglm-6b-model",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        from volcengine.maas import MaasService

        params.load_config(self.model_names[0])
        maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
        maas.set_ak(params.api_key)
        maas.set_sk(params.secret_key)

        # document: "https://www.volcengine.com/docs/82379/1099475"
        req = {
            "model": {
                "name": params.version,
            },
            "parameters": {
                # 这里的参数仅为示例，具体可用的参数请参考具体模型的 API 说明
                "max_new_tokens": params.max_tokens,
                "temperature": params.temperature,
            },
            "messages": params.messages,
        }

        text = ""
        if log_verbose:
            self.logger.info(f'{self.__class__.__name__}:maas: {maas}')
        for resp in maas.stream_chat(req):
            if error := resp.error:
                if error.code_n > 0:
                    data = {
                        "error_code": error.code_n,
                        "text": error.message,
                        "error": {
                            "message": error.message,
                            "type": "invalid_request_error",
                            "param": None,
                            "code": None,
                        }
                    }
                    self.logger.error(f"请求方舟 API 时发生错误：{data}")
                    yield data
                elif chunk := resp.choice.message.content:
                    text += chunk
                    yield {"error_code": 0, "text": text}
            else:
                data = {
                    "error_code": 500,
                    "text": f"请求方舟 API 时发生未知的错误: {resp}"
                }
                self.logger.error(data)
                yield data
                break

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = FangZhouWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21005",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21005)
