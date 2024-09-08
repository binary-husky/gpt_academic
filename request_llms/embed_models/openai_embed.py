from llama_index.embeddings.openai import OpenAIEmbedding
from openai import OpenAI
from toolbox import get_conf
from toolbox import CatchException, update_ui, get_conf, select_api_key, get_log_folder, ProxyNetworkActivate
from shared_utils.key_pattern_manager import select_api_key_for_embed_models
from typing import List, Any

import numpy as np

def mean_agg(embeddings):
    """Mean aggregation for embeddings."""
    return np.array(embeddings).mean(axis=0).tolist()

class EmbeddingModel():

    def get_agg_embedding_from_queries(
        self,
        queries: List[str],
        agg_fn = None,
    ):
        """Get aggregated embedding from multiple queries."""
        query_embeddings = [self.get_query_embedding(query) for query in queries]
        agg_fn = agg_fn or mean_agg
        return agg_fn(query_embeddings)

    def get_text_embedding_batch(
            self,
            texts: List[str],
            show_progress: bool = False,
        ):
            return self.compute_embedding(texts, batch_mode=True)


class OpenAiEmbeddingModel(EmbeddingModel):

    def __init__(self, llm_kwargs:dict=None):
        self.llm_kwargs = llm_kwargs

    def get_query_embedding(self, query: str):
        return self.compute_embedding(query)

    def compute_embedding(self, text="这是要计算嵌入的文本", llm_kwargs:dict=None, batch_mode=False):
        from .bridge_all_embed import embed_model_info

        # load kwargs
        if llm_kwargs is None:
            llm_kwargs = self.llm_kwargs
        if llm_kwargs is None:
            raise RuntimeError("llm_kwargs is not provided!")

        # setup api and req url
        api_key = select_api_key_for_embed_models(llm_kwargs['api_key'], llm_kwargs['embed_model'])
        embed_model = llm_kwargs['embed_model']
        base_url = embed_model_info[llm_kwargs['embed_model']]['embed_endpoint'].replace('embeddings', '')

        # send and compute
        with ProxyNetworkActivate("Connect_OpenAI_Embedding"):
            self.oai_client = OpenAI(api_key=api_key, base_url=base_url)
            if batch_mode:
                input = text
                assert isinstance(text, list)
            else:
                input = [text]
                assert isinstance(text, str)
            res = self.oai_client.embeddings.create(input=input, model=embed_model)

        # parse result
        if batch_mode:
            embedding = [d.embedding for d in res.data]
        else:
            embedding = res.data[0].embedding
        return embedding

    def embedding_dimension(self, llm_kwargs=None):
        # load kwargs
        if llm_kwargs is None:
            llm_kwargs = self.llm_kwargs
        if llm_kwargs is None:
            raise RuntimeError("llm_kwargs is not provided!")

        from .bridge_all_embed import embed_model_info
        return embed_model_info[llm_kwargs['embed_model']]['embed_dimension']

if __name__ == "__main__":
    pass