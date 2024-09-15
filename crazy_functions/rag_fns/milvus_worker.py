import llama_index
import os
import atexit
from typing import List
from loguru import logger
from llama_index.core import Document
from llama_index.core.schema import TextNode
from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
from shared_utils.connect_void_terminal import get_chat_default_kwargs
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
from llama_index.core.ingestion import run_transformations
from llama_index.core import PromptTemplate
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core import StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore
from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker

DEFAULT_QUERY_GENERATION_PROMPT = """\
Now, you have context information as below:
---------------------
{context_str}
---------------------
Answer the user request below (use the context information if necessary, otherwise you can ignore them):
---------------------
{query_str}
"""

QUESTION_ANSWER_RECORD = """\
{{
    "type": "This is a previous conversation with the user",
    "question": "{question}",
    "answer": "{answer}",
}}
"""


class MilvusSaveLoad():

    def does_checkpoint_exist(self, checkpoint_dir=None):
        import os, glob
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if not os.path.exists(checkpoint_dir): return False
        if len(glob.glob(os.path.join(checkpoint_dir, "*.json"))) == 0: return False
        return True

    def save_to_checkpoint(self, checkpoint_dir=None):
        logger.info(f'saving vector store to: {checkpoint_dir}')
        # if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        # self.vs_index.storage_context.persist(persist_dir=checkpoint_dir)

    def load_from_checkpoint(self, checkpoint_dir=None):
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if self.does_checkpoint_exist(checkpoint_dir=checkpoint_dir):
            logger.info('loading checkpoint from disk')
            from llama_index.core import StorageContext, load_index_from_storage
            storage_context = StorageContext.from_defaults(persist_dir=checkpoint_dir)
            try:
                self.vs_index = load_index_from_storage(storage_context, embed_model=self.embed_model)
                return self.vs_index
            except:
                return self.create_new_vs(checkpoint_dir)
        else:
            return self.create_new_vs(checkpoint_dir)

    def create_new_vs(self, checkpoint_dir, overwrite=False):
        vector_store = MilvusVectorStore(
            uri=os.path.join(checkpoint_dir, "milvus_demo.db"), 
            dim=self.embed_model.embedding_dimension(),
            overwrite=overwrite
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = GptacVectorStoreIndex.default_vector_store(storage_context=storage_context, embed_model=self.embed_model)
        return index

    def purge(self):
        self.vs_index = self.create_new_vs(self.checkpoint_dir, overwrite=True)

class MilvusRagWorker(MilvusSaveLoad, LlamaIndexRagWorker):

    def __init__(self, user_name, llm_kwargs, auto_load_checkpoint=True, checkpoint_dir=None) -> None:
        self.debug_mode = True
        self.embed_model = OpenAiEmbeddingModel(llm_kwargs)
        self.user_name = user_name
        self.checkpoint_dir = checkpoint_dir
        if auto_load_checkpoint:
            self.vs_index = self.load_from_checkpoint(checkpoint_dir)
        else:
            self.vs_index = self.create_new_vs(checkpoint_dir)
        atexit.register(lambda: self.save_to_checkpoint(checkpoint_dir))

    def inspect_vector_store(self):
        # This function is for debugging
        try:
            self.vs_index.storage_context.index_store.to_dict()
            docstore = self.vs_index.storage_context.docstore.docs
            if not docstore.items():
                raise ValueError("cannot inspect")
            vector_store_preview = "\n".join([ f"{_id} | {tn.text}" for _id, tn in docstore.items() ])
        except:
            dummy_retrieve_res: List["NodeWithScore"] = self.vs_index.as_retriever().retrieve(' ')
            vector_store_preview = "\n".join(
                [f"{node.id_} | {node.text}" for node in dummy_retrieve_res]
            )
        logger.info('\n++ --------inspect_vector_store begin--------')
        logger.info(vector_store_preview)
        logger.info('oo --------inspect_vector_store end--------')
        return vector_store_preview
