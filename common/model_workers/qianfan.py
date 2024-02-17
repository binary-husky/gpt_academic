import sys
from fastchat.conversation import Conversation
from common.model_workers.base import *
from common.utils import get_httpx_client
from cachetools import cached, TTLCache
import json
from fastchat import conversation as conv
import sys
from common.model_workers.base import ApiEmbeddingsParams
from typing import List, Literal, Dict
from  common.api_configs import logger, log_verbose

MODEL_VERSIONS = {
    "ernie-bot-4": "completions_pro",
    "ernie-bot": "completions",
    "ernie-bot-turbo": "eb-instant",
    "bloomz-7b": "bloomz_7b1",
    "qianfan-bloomz-7b-c": "qianfan_bloomz_7b_compressed",
    "llama2-7b-chat": "llama_2_7b",
    "llama2-13b-chat": "llama_2_13b",
    "llama2-70b-chat": "llama_2_70b",
    "qianfan-llama2-ch-7b": "qianfan_chinese_llama_2_7b",
    "chatglm2-6b-32k": "chatglm2_6b_32k",
    "aquilachat-7b": "aquilachat_7b",
    # "linly-llama2-ch-7b": "", # 暂未发布
    # "linly-llama2-ch-13b": "", # 暂未发布
    # "chatglm2-6b": "", # 暂未发布
    # "chatglm2-6b-int4": "", # 暂未发布
    # "falcon-7b": "", # 暂未发布
    # "falcon-180b-chat": "", # 暂未发布
    # "falcon-40b": "", # 暂未发布
    # "rwkv4-world": "", # 暂未发布
    # "rwkv5-world": "", # 暂未发布
    # "rwkv4-pile-14b": "", # 暂未发布
    # "rwkv4-raven-14b": "", # 暂未发布
    # "open-llama-7b": "", # 暂未发布
    # "dolly-12b": "", # 暂未发布
    # "mpt-7b-instruct": "", # 暂未发布
    # "mpt-30b-instruct": "", # 暂未发布
    # "OA-Pythia-12B-SFT-4": "", # 暂未发布
    # "xverse-13b": "", # 暂未发布

    # # 以下为企业测试，需要单独申请
    # "flan-ul2": "",
    # "Cerebras-GPT-6.7B": ""
    # "Pythia-6.9B": ""
}


@cached(TTLCache(1, 1800))  # 经过测试，缓存的token可以使用，目前每30分钟刷新一次
def get_baidu_access_token(api_key: str, secret_key: str) -> str:
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    try:
        with get_httpx_client() as client:
            return client.get(url, params=params).json().get("access_token")
    except Exception as e:
        print(f"failed to get token from baidu: {e}")


class QianFanWorker(ApiModelWorker):
    """
    百度千帆
    """
    DEFAULT_EMBED_MODEL = "embedding-v1"

    def __init__(
            self,
            *,
            version: Literal["ernie-bot", "ernie-bot-turbo"] = "ernie-bot",
            model_names: List[str] = ["qianfan-api"],
            controller_addr: str = None,
            worker_addr: str = None,
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])
        BASE_URL = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat' \
                   '/{model_version}?access_token={access_token}'

        access_token = get_baidu_access_token(params.api_key, params.secret_key)
        if not access_token:
            yield {
                "error_code": 403,
                "text": f"failed to get access token. have you set the correct api_key and secret key?",
            }

        url = BASE_URL.format(
            model_version=params.version_url or MODEL_VERSIONS[params.version.lower()],
            access_token=access_token,
        )
        payload = {
            "messages": params.messages,
            "temperature": params.temperature,
            "stream": True
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        text = ""
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:data: {payload}')
            logger.info(f'{self.__class__.__name__}:url: {url}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')

        with get_httpx_client() as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                for line in response.iter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    resp = json.loads(line)

                    if "result" in resp.keys():
                        text += resp["result"]
                        yield {
                            "error_code": 0,
                            "text": text
                        }
                    else:
                        data = {
                            "error_code": resp["error_code"],
                            "text": resp["error_msg"],
                            "error": {
                                "message": resp["error_msg"],
                                "type": "invalid_request_error",
                                "param": None,
                                "code": None,
                            }
                        }
                        self.logger.error(f"请求千帆 API 时发生错误：{data}")
                        yield data

    def do_embeddings(self, params: ApiEmbeddingsParams) -> Dict:
        params.load_config(self.model_names[0])
        # import qianfan

        # embed = qianfan.Embedding(ak=params.api_key, sk=params.secret_key)
        # resp = embed.do(texts = params.texts, model=params.embed_model or self.DEFAULT_EMBED_MODEL)
        # if resp.code == 200:
        #     embeddings = [x.embedding for x in resp.body.get("data", [])]
        #     return {"code": 200, "embeddings": embeddings}
        # else:
        #     return {"code": resp.code, "msg": str(resp.body)}

        embed_model = params.embed_model or self.DEFAULT_EMBED_MODEL
        access_token = get_baidu_access_token(params.api_key, params.secret_key)
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/{embed_model}?access_token={access_token}"
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:url: {url}')

        with get_httpx_client() as client:
            result = []
            i = 0
            batch_size = 10
            while i < len(params.texts):
                texts = params.texts[i:i + batch_size]
                resp = client.post(url, json={"input": texts}).json()
                if "error_code" in resp:
                    data = {
                        "code": resp["error_code"],
                        "msg": resp["error_msg"],
                        "error": {
                            "message": resp["error_msg"],
                            "type": "invalid_request_error",
                            "param": None,
                            "code": None,
                        }
                    }
                    self.logger.error(f"请求千帆 API 时发生错误：{data}")
                    return data
                else:
                    embeddings = [x["embedding"] for x in resp.get("data", [])]
                    result += embeddings
                i += batch_size
            return {"code": 200, "data": result}

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明的助手，请根据用户的提示来完成任务",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from common.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = QianFanWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21004"
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21004)
