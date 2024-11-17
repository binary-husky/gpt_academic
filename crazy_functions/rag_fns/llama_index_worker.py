import llama_index
import os
import atexit
from loguru import logger
from typing import List
from llama_index.core import Document
from llama_index.core.schema import TextNode
from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
from shared_utils.connect_void_terminal import get_chat_default_kwargs
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
from llama_index.core.ingestion import run_transformations
from llama_index.core import PromptTemplate
from llama_index.core.response_synthesizers import TreeSummarize

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


class SaveLoad():

    def does_checkpoint_exist(self, checkpoint_dir=None):
        import os, glob
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if not os.path.exists(checkpoint_dir): return False
        if len(glob.glob(os.path.join(checkpoint_dir, "*.json"))) == 0: return False
        return True

    def save_to_checkpoint(self, checkpoint_dir=None):
        logger.info(f'saving vector store to: {checkpoint_dir}')
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        self.vs_index.storage_context.persist(persist_dir=checkpoint_dir)

    def load_from_checkpoint(self, checkpoint_dir=None):
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if self.does_checkpoint_exist(checkpoint_dir=checkpoint_dir):
            logger.info('loading checkpoint from disk')
            from llama_index.core import StorageContext, load_index_from_storage
            storage_context = StorageContext.from_defaults(persist_dir=checkpoint_dir)
            self.vs_index = load_index_from_storage(storage_context, embed_model=self.embed_model)
            return self.vs_index
        else:
            return self.create_new_vs()

    def create_new_vs(self):
        return GptacVectorStoreIndex.default_vector_store(embed_model=self.embed_model)

    def purge(self):
        import shutil
        shutil.rmtree(self.checkpoint_dir, ignore_errors=True)
        self.vs_index = self.create_new_vs()


class LlamaIndexRagWorker(SaveLoad):
    def __init__(self, user_name, llm_kwargs, auto_load_checkpoint=True, checkpoint_dir=None) -> None:
        self.debug_mode = True
        self.embed_model = OpenAiEmbeddingModel(llm_kwargs)
        self.user_name = user_name
        self.checkpoint_dir = checkpoint_dir

        # 确保checkpoint_dir存在
        if checkpoint_dir:
            os.makedirs(checkpoint_dir, exist_ok=True)

        logger.info(f"Initializing LlamaIndexRagWorker with checkpoint_dir: {checkpoint_dir}")

        # 初始化向量存储
        if auto_load_checkpoint and self.does_checkpoint_exist():
            logger.info("Loading existing vector store from checkpoint")
            self.vs_index = self.load_from_checkpoint()
        else:
            logger.info("Creating new vector store")
            self.vs_index = self.create_new_vs()

        # 注册退出时保存
        atexit.register(self.save_to_checkpoint)

    def add_text_to_vector_store(self, text: str) -> None:
        """添加文本到向量存储"""
        try:
            logger.info(f"Adding text to vector store (first 100 chars): {text[:100]}...")
            node = TextNode(text=text)
            nodes = run_transformations(
                [node],
                self.vs_index._transformations,
                show_progress=True
            )
            self.vs_index.insert_nodes(nodes)

            # 立即保存
            self.save_to_checkpoint()

            if self.debug_mode:
                self.inspect_vector_store()

        except Exception as e:
            logger.error(f"Error adding text to vector store: {str(e)}")
            raise

    def save_to_checkpoint(self, checkpoint_dir=None):
        """保存向量存储到检查点"""
        try:
            if checkpoint_dir is None:
                checkpoint_dir = self.checkpoint_dir
            logger.info(f'Saving vector store to: {checkpoint_dir}')
            if checkpoint_dir:
                self.vs_index.storage_context.persist(persist_dir=checkpoint_dir)
                logger.info('Vector store saved successfully')
            else:
                logger.warning('No checkpoint directory specified, skipping save')
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            raise


    def assign_embedding_model(self):
        pass

    def inspect_vector_store(self):
        # This function is for debugging
        self.vs_index.storage_context.index_store.to_dict()
        docstore = self.vs_index.storage_context.docstore.docs
        vector_store_preview = "\n".join([f"{_id} | {tn.text}" for _id, tn in docstore.items()])
        logger.info('\n++ --------inspect_vector_store begin--------')
        logger.info(vector_store_preview)
        logger.info('oo --------inspect_vector_store end--------')
        return vector_store_preview

    def add_documents_to_vector_store(self, document_list):
        documents = [Document(text=t) for t in document_list]
        documents_nodes = run_transformations(
            documents,  # type: ignore
            self.vs_index._transformations,
            show_progress=True
        )
        self.vs_index.insert_nodes(documents_nodes)
        if self.debug_mode: self.inspect_vector_store()

    def remember_qa(self, question, answer):
        formatted_str = QUESTION_ANSWER_RECORD.format(question=question, answer=answer)
        self.add_text_to_vector_store(formatted_str)

    def retrieve_from_store_with_query(self, query):
        if self.debug_mode: self.inspect_vector_store()
        retriever = self.vs_index.as_retriever()
        return retriever.retrieve(query)

    def build_prompt(self, query, nodes):
        context_str = self.generate_node_array_preview(nodes)
        return DEFAULT_QUERY_GENERATION_PROMPT.format(context_str=context_str, query_str=query)

    def generate_node_array_preview(self, nodes):
        buf = "\n".join(([f"(No.{i + 1} | score {n.score:.3f}): {n.text}" for i, n in enumerate(nodes)]))
        if self.debug_mode: logger.info(buf)
        return buf
