from typing import List

from common.configs import (
    EMBEDDING_MODEL,
    KB_ROOT_PATH)

from abc import ABC, abstractmethod
from common.knowledge_base.kb_cache.faiss_cache import kb_faiss_pool, ThreadSafeFaiss
import os
import shutil
from common.db.repository.knowledge_metadata_repository import add_summary_to_db, delete_summary_from_db

from langchain.docstore.document import Document


class KBSummaryService(ABC):
    kb_name: str
    embed_model: str
    vs_path: str
    kb_path: str

    def __init__(self,
                 knowledge_base_name: str,
                 embed_model: str = EMBEDDING_MODEL
                 ):
        self.kb_name = knowledge_base_name
        self.embed_model = embed_model

        self.kb_path = self.get_kb_path()
        self.vs_path = self.get_vs_path()

        if not os.path.exists(self.vs_path):
            os.makedirs(self.vs_path)


    def get_vs_path(self):
        return os.path.join(self.get_kb_path(), "summary_vector_store")

    def get_kb_path(self):
        return os.path.join(KB_ROOT_PATH, self.kb_name)

    def load_vector_store(self) -> ThreadSafeFaiss:
        return kb_faiss_pool.load_vector_store(kb_name=self.kb_name,
                                               vector_name="summary_vector_store",
                                               embed_model=self.embed_model,
                                               create=True)

    def add_kb_summary(self, summary_combine_docs: List[Document]):
        with self.load_vector_store().acquire() as vs:
            ids = vs.add_documents(documents=summary_combine_docs)
            vs.save_local(self.vs_path)

        summary_infos = [{"summary_context": doc.page_content,
                          "summary_id": id,
                          "doc_ids": doc.metadata.get('doc_ids'),
                          "metadata": doc.metadata} for id, doc in zip(ids, summary_combine_docs)]
        status = add_summary_to_db(kb_name=self.kb_name, summary_infos=summary_infos)
        return status

    def create_kb_summary(self):
        """
        创建知识库chunk summary
        :return:
        """

        if not os.path.exists(self.vs_path):
            os.makedirs(self.vs_path)

    def drop_kb_summary(self):
        """
        删除知识库chunk summary
        :param kb_name:
        :return:
        """
        with kb_faiss_pool.atomic:
            kb_faiss_pool.pop(self.kb_name)
            shutil.rmtree(self.vs_path)
        delete_summary_from_db(kb_name=self.kb_name)
