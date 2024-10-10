import atexit
from loguru import logger
from typing import List

from llama_index.core import Document
from llama_index.core.ingestion import run_transformations
from llama_index.core.schema import TextNode

from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel

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
        self.vs_index = self.create_new_vs(self.checkpoint_dir)


class LlamaIndexRagWorker(SaveLoad):
    def __init__(self, user_name, llm_kwargs, auto_load_checkpoint=True, checkpoint_dir=None) -> None:
        self.debug_mode = True
        self.embed_model = OpenAiEmbeddingModel(llm_kwargs)
        self.user_name = user_name
        self.checkpoint_dir = checkpoint_dir
        if auto_load_checkpoint:
            self.vs_index = self.load_from_checkpoint(checkpoint_dir)
        else:
            self.vs_index = self.create_new_vs()
        atexit.register(lambda: self.save_to_checkpoint(checkpoint_dir))

    def assign_embedding_model(self):
        pass

    def inspect_vector_store(self):
        # This function is for debugging
        self.vs_index.storage_context.index_store.to_dict()
        docstore = self.vs_index.storage_context.docstore.docs
        vector_store_preview = "\n".join([ f"{_id} | {tn.text}" for _id, tn in docstore.items() ])
        logger.info('\n++ --------inspect_vector_store begin--------')
        logger.info(vector_store_preview)
        logger.info('oo --------inspect_vector_store end--------')
        return vector_store_preview

    def add_documents_to_vector_store(self, document_list: List[Document]):
        """
        Adds a list of Document objects to the vector store after processing.
        """
        documents = document_list
        documents_nodes = run_transformations(
            documents,  # type: ignore
            self.vs_index._transformations,
            show_progress=True
        )
        self.vs_index.insert_nodes(documents_nodes)
        if self.debug_mode:
            self.inspect_vector_store()

    def add_text_to_vector_store(self, text: str):
        node = TextNode(text=text)
        documents_nodes = run_transformations(
            [node],
            self.vs_index._transformations,
            show_progress=True
        )
        self.vs_index.insert_nodes(documents_nodes)
        if self.debug_mode:
            self.inspect_vector_store()

    def remember_qa(self, question, answer):
        formatted_str = QUESTION_ANSWER_RECORD.format(question=question, answer=answer)
        self.add_text_to_vector_store(formatted_str)

    def retrieve_from_store_with_query(self, query):
        if self.debug_mode:
            self.inspect_vector_store()
        retriever = self.vs_index.as_retriever()
        return retriever.retrieve(query)

    def build_prompt(self, query, nodes):
        context_str = self.generate_node_array_preview(nodes)
        return DEFAULT_QUERY_GENERATION_PROMPT.format(context_str=context_str, query_str=query)

    def generate_node_array_preview(self, nodes):
        buf = "\n".join(([f"(No.{i+1} | score {n.score:.3f}): {n.text}" for i, n in enumerate(nodes)]))
        if self.debug_mode: logger.info(buf)
        return buf

    def purge_vector_store(self):
        """
        Purges the current vector store and creates a new one.
        """
        self.purge()