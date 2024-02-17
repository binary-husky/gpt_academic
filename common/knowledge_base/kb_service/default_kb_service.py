from typing import List

from langchain.embeddings.base import Embeddings
from langchain.schema import Document

from common.knowledge_base.kb_service.base import KBService


class DefaultKBService(KBService):
    def do_create_kb(self):
        pass

    def do_drop_kb(self):
        pass

    def do_add_doc(self, docs: List[Document]):
        pass

    def do_clear_vs(self):
        pass

    def vs_type(self) -> str:
        return "default"

    def do_init(self):
        pass

    def do_search(self):
        pass

    def do_insert_multi_knowledge(self):
        pass

    def do_insert_one_knowledge(self):
        pass

    def do_delete_doc(self):
        pass
