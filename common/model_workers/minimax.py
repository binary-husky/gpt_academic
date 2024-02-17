from fastchat.conversation import Conversation
from common.model_workers.base import *
from fastchat import conversation as conv
import sys
import json
from common.model_workers.base import ApiEmbeddingsParams
from common.utils import get_httpx_client
from typing import List, Dict
from  common.api_configs import logger, log_verbose


class MiniMaxWorker(ApiModelWorker):
    DEFAULT_EMBED_MODEL = "embo-01"

    def __init__(
        self,
        *,
        model_names: List[str] = ["minimax-api"],
        controller_addr: str = None,
        worker_addr: str = None,
        version: str = "abab5.5-chat",
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)
        super().__init__(**kwargs)
        self.version = version

    def validate_messages(self, messages: List[Dict]) -> List[Dict]:
        role_maps = {
            "USER": self.user_role,
            "assistant": self.ai_role,
            "system": "system",
        }
        messages = [{"sender_type": role_maps[x["role"]], "text": x["content"]} for x in messages]
        return messages

    def do_chat(self, params: ApiChatParams) -> Dict:
        # 按照官网推荐，直接调用abab 5.5模型
        params.load_config(self.model_names[0])

        url = 'https://api.minimax.chat/v1/text/chatcompletion{pro}?GroupId={group_id}'
        pro = "_pro" if params.is_pro else ""
        headers = {
            "Authorization": f"Bearer {params.api_key}",
            "Content-Type": "application/json",
        }
        messages = self.validate_messages(params.messages)
        data = {
            "model": params.version,
            "stream": True,
            "mask_sensitive_info": True,
            "messages": messages,
            "temperature": params.temperature,
            "top_p": params.top_p,
            "tokens_to_generate": params.max_tokens or 1024,
            # 以下参数为minimax特有，传入空值会出错。
            # "prompt": params.system_message or self.conv.system_message,
            # "bot_setting": [],
            # "role_meta": params.role_meta,
        }
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:data: {data}')
            logger.info(f'{self.__class__.__name__}:url: {url.format(pro=pro, group_id=params.group_id)}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')

        with get_httpx_client() as client:
            response = client.stream("POST",
                                    url.format(pro=pro, group_id=params.group_id),
                                    headers=headers,
                                    json=data)
            with response as r:
                text = ""
                for e in r.iter_text():
                    if not e.startswith("data: "):
                        data = {
                                "error_code": 500,
                                "text": f"minimax返回错误的结果：{e}",
                                "error": {
                                    "message":  f"minimax返回错误的结果：{e}",
                                    "type": "invalid_request_error",
                                    "param": None,
                                    "code": None,
                                }
                        }
                        self.logger.error(f"请求 MiniMax API 时发生错误：{data}")
                        yield data
                        continue

                    data = json.loads(e[6:])
                    if data.get("usage"):
                        break

                    if choices := data.get("choices"):
                        if chunk := choices[0].get("delta", ""):
                            text += chunk
                            yield {"error_code": 0, "text": text}

    def do_embeddings(self, params: ApiEmbeddingsParams) -> Dict:
        params.load_config(self.model_names[0])
        url = f"https://api.minimax.chat/v1/embeddings?GroupId={params.group_id}"

        headers = {
            "Authorization": f"Bearer {params.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": params.embed_model or self.DEFAULT_EMBED_MODEL,
            "texts": [],
            "type": "query" if params.to_query else "db",
        }
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:data: {data}')
            logger.info(f'{self.__class__.__name__}:url: {url}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')

        with get_httpx_client() as client:
            result = []
            i = 0
            batch_size = 10
            while i < len(params.texts):
                texts = params.texts[i:i+batch_size]
                data["texts"] = texts
                r = client.post(url, headers=headers, json=data).json()
                if embeddings := r.get("vectors"):
                    result += embeddings
                elif error := r.get("base_resp"):
                    data = {
                                "code": error["status_code"],
                                "msg": error["status_msg"],
                                "error": {
                                    "message":  error["status_msg"],
                                    "type": "invalid_request_error",
                                    "param": None,
                                    "code": None,
                                }
                            }
                    self.logger.error(f"请求 MiniMax API 时发生错误：{data}")
                    return data
                i += batch_size
            return {"code": 200, "data": result}

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是MiniMax自主研发的大型语言模型，回答问题简洁有条理。",
            messages=[],
            roles=["USER", "BOT"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = MiniMaxWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21002",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21002)
