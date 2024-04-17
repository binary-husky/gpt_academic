import os

from langchain.docstore.document import Document
from common.configs import EMBEDDING_MODEL
from common.logger_handler import logger
from common.utils import BaseResponse, get_model_worker_config, list_embed_models
from fastapi import Body
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, root_validator
from typing import Dict, List, Optional
from common.func_box import get_env_proxy_network


class ApiConfigParams(BaseModel):
    '''
    在线API配置参数，未提供的值会自动从model_config.ONLINE_LLM_MODEL中读取
    '''
    api_base_url: Optional[str] = None
    api_proxy: Optional[str] = None
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    group_id: Optional[str] = None  # for minimax
    is_pro: bool = False  # for minimax

    APPID: Optional[str] = None  # for xinghuo
    APISecret: Optional[str] = None  # for xinghuo
    is_v2: bool = False  # for xinghuo

    worker_name: Optional[str] = None

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def validate_config(cls, v: Dict) -> Dict:
        if config := get_model_worker_config(v.get("worker_name")):
            for n in cls.__fields__:
                if n in config:
                    v[n] = config[n]
        return v

    def load_config(self, worker_name: str):
        self.worker_name = worker_name
        if config := get_model_worker_config(worker_name):
            for n in self.__fields__:
                if n in config:
                    setattr(self, n, config[n])
        return self


class ApiEmbeddingsParams(ApiConfigParams):
    texts: List[str]
    embed_model: Optional[str] = None
    to_query: bool = False  # for minimax


online_embed_models = ...


def embed_texts(
        texts: List[str],
        embed_model: str = EMBEDDING_MODEL,
        to_query: bool = False,
) -> BaseResponse:
    '''
    对文本进行向量化。返回数据格式：BaseResponse(data=List[List[float]])
    '''
    try:
        if embed_model in list_embed_models():  # 使用本地Embeddings模型
            from common.utils import load_local_embeddings

            embeddings = load_local_embeddings(model=embed_model)
            return BaseResponse(data=embeddings.embed_documents(texts))

        if embed_model in []:  # 使用在线API
            config = get_model_worker_config(embed_model)
            worker_class = config.get("worker_class")
            embed_model = config.get("embed_model")
            worker = worker_class()
            if worker_class.can_embedding():
                params = ApiEmbeddingsParams(texts=texts, to_query=to_query, embed_model=embed_model)
                resp = worker.do_embeddings(params)
                return BaseResponse(**resp)

        return BaseResponse(code=500, msg=f"指定的模型 {embed_model} 不支持 Embeddings 功能。")
    except Exception as e:
        logger.error(e)
        return BaseResponse(code=500, msg=f"文本向量化过程中出现错误：{e}")


async def aembed_texts(
        texts: List[str],
        embed_model: str = EMBEDDING_MODEL,
        to_query: bool = False,
) -> BaseResponse:
    '''
    对文本进行向量化。返回数据格式：BaseResponse(data=List[List[float]])
    '''
    try:
        if embed_model in list_embed_models():  # 使用本地Embeddings模型
            from common.utils import load_local_embeddings

            embeddings = load_local_embeddings(model=embed_model)
            return BaseResponse(data=await embeddings.aembed_documents(texts))

        if embed_model in []:  # 使用在线API
            return await run_in_threadpool(embed_texts,
                                           texts=texts,
                                           embed_model=embed_model,
                                           to_query=to_query)
    except Exception as e:
        logger.error(e)
        return BaseResponse(code=500, msg=f"文本向量化过程中出现错误：{e}")


def embed_texts_endpoint(
        texts: List[str] = Body(..., description="要嵌入的文本列表", examples=[["hello", "world"]]),
        embed_model: str = Body(EMBEDDING_MODEL,
                                description=f"使用的嵌入模型，除了本地部署的Embedding模型，也支持在线API({online_embed_models})提供的嵌入服务。"),
        to_query: bool = Body(False, description="向量是否用于查询。有些模型如Minimax对存储/查询的向量进行了区分优化。"),
) -> BaseResponse:
    '''
    对文本进行向量化，返回 BaseResponse(data=List[List[float]])
    '''
    return embed_texts(texts=texts, embed_model=embed_model, to_query=to_query)


def embed_documents(
        docs: List[Document],
        embed_model: str = EMBEDDING_MODEL,
        to_query: bool = False,
) -> Dict:
    """
    将 List[Document] 向量化，转化为 VectorStore.add_embeddings 可以接受的参数
    """
    texts = [x.page_content for x in docs]
    metadatas = [x.metadata for x in docs]
    embeddings = embed_texts(texts=texts, embed_model=embed_model, to_query=to_query).data
    if embeddings is not None:
        return {
            "texts": texts,
            "embeddings": embeddings,
            "metadatas": metadatas,
        }


def embed_download(model_name='BAAI/bge-large-zh-v1.5'):
    # 模型下载
    from common.func_box import Shell
    cmd_args = ['python3', '-c',
                f"from langchain.embeddings import HuggingFaceBgeEmbeddings; "
                f"print(HuggingFaceBgeEmbeddings(model_name='{model_name}'))"]
    env = os.environ.copy()
    proxy_env = get_env_proxy_network()
    if proxy_env and 'no_proxy' in env:
        env.pop('no_proxy')
    env.update(proxy_env)
    shell = Shell(cmd_args, env=env)
    return shell, shell.stream_start()


def embed_download2py(model_name='BAAI/bge-m3'):
    from langchain.embeddings import HuggingFaceBgeEmbeddings
    from common.utils import embedding_device
    device = embedding_device()
    embeddings = HuggingFaceBgeEmbeddings(model_name=model_name,
                                          model_kwargs={'device': device},
                                          query_instruction='Represent this sentence for searching relevant passages:')
    print(embeddings)


if __name__ == '__main__':
    pass