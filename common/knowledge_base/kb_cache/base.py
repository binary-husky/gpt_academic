from langchain.embeddings.base import Embeddings
from langchain.vectorstores.faiss import FAISS
import threading
from common.configs import (EMBEDDING_MODEL, CHUNK_SIZE)
from common.utils import embedding_device, get_model_path
from contextlib import contextmanager
from collections import OrderedDict
from typing import List, Any, Union, Tuple
from common.logger_handler import logger


class ThreadSafeObject:
    def __init__(self, key: Union[str, Tuple], obj: Any = None, pool: "CachePool" = None):
        self._obj = obj
        self._key = key
        self._pool = pool
        self._lock = threading.RLock()
        self._loaded = threading.Event()

    def __repr__(self) -> str:
        cls = type(self).__name__
        return f"<{cls}: key: {self.key}, obj: {self._obj}>"

    @property
    def key(self):
        return self._key

    @contextmanager
    def acquire(self, owner: str = "", msg: str = "") -> FAISS:
        owner = owner or f"thread {threading.get_native_id()}"
        try:
            self._lock.acquire()
            if self._pool is not None:
                self._pool._cache.move_to_end(self.key)
                logger.info(f"{owner} 开始操作：{self.key}。{msg}")
            yield self._obj
        finally:
            logger.info(f"{owner} 结束操作：{self.key}。{msg}")
        self._lock.release()

    def start_loading(self):
        self._loaded.clear()

    def finish_loading(self):
        self._loaded.set()

    def wait_for_loading(self):
        self._loaded.wait()

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, val: Any):
        self._obj = val


class CachePool:
    def __init__(self, cache_num: int = -1):
        self._cache_num = cache_num
        self._cache = OrderedDict()
        self.atomic = threading.RLock()

    def keys(self) -> List[str]:
        return list(self._cache.keys())

    def _check_count(self):
        if isinstance(self._cache_num, int) and self._cache_num > 0:
            while len(self._cache) > self._cache_num:
                self._cache.popitem(last=False)

    def get(self, key: str) -> ThreadSafeObject:
        if cache := self._cache.get(key):
            cache.wait_for_loading()
            return cache

    def set(self, key: str, obj: ThreadSafeObject) -> ThreadSafeObject:
        self._cache[key] = obj
        self._check_count()
        return obj

    def pop(self, key: str = None) -> ThreadSafeObject:
        if key is None:
            return self._cache.popitem(last=False)
        else:
            return self._cache.pop(key, None)

    def acquire(self, key: Union[str, Tuple], owner: str = "", msg: str = ""):
        cache = self.get(key)
        if cache is None:
            raise RuntimeError(f"请求的资源 {key} 不存在")
        elif isinstance(cache, ThreadSafeObject):
            self._cache.move_to_end(key)
            return cache.acquire(owner=owner, msg=msg)
        else:
            return cache

    def load_kb_embeddings(
            self,
            kb_name: str,
            embed_device: str = embedding_device(),
            default_embed_model: str = EMBEDDING_MODEL,
    ) -> Embeddings:
        from common.db.repository.knowledge_base_repository import get_kb_detail
        from common.knowledge_base.kb_service.base import EmbeddingsFunAdapter

        kb_detail = get_kb_detail(kb_name)
        embed_model = kb_detail.get("embed_model", default_embed_model)

        # if embed_model in list_online_embed_models():
        #     return EmbeddingsFunAdapter(embed_model)
        # else:
        return embeddings_pool.load_embeddings(model=embed_model, device=embed_device)


class EmbeddingsPool(CachePool):
    def load_embeddings(self, model: str = None, device: str = None) -> Embeddings:
        self.atomic.acquire()
        model = model or EMBEDDING_MODEL
        device = embedding_device()
        key = (model, device)
        if not self.get(key):
            item = ThreadSafeObject(key, pool=self)
            self.set(key, item)
            with item.acquire(msg="初始化"):
                self.atomic.release()
                if model == "text-embedding-ada-002":  # openai text-embedding-ada-002
                    from langchain.embeddings.openai import OpenAIEmbeddings
                    embeddings = OpenAIEmbeddings(model=model,
                                                  openai_api_key=get_model_path(model),
                                                  chunk_size=CHUNK_SIZE)
                elif 'bge-' in model:
                    from langchain.embeddings import HuggingFaceBgeEmbeddings
                    if 'zh' in model:
                        # for chinese model
                        query_instruction = "为这个句子生成表示以用于检索相关文章："
                    elif 'en' in model:
                        # for english model
                        query_instruction = "Represent this sentence for searching relevant passages:"
                    else:
                        # maybe ReRanker or else, just use empty string instead
                        query_instruction = ""
                    embeddings = HuggingFaceBgeEmbeddings(model_name=get_model_path(model),
                                                          model_kwargs={'device': device},
                                                          query_instruction=query_instruction)
                    if model == "bge-large-zh-noinstruct":  # bge large -noinstruct embedding
                        embeddings.query_instruction = ""
                else:
                    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
                    embeddings = HuggingFaceEmbeddings(model_name=get_model_path(model),
                                                       model_kwargs={'device': device})
                item.obj = embeddings
                item.finish_loading()
        else:
            self.atomic.release()
        return self.get(key).obj


embeddings_pool = EmbeddingsPool(cache_num=1)
