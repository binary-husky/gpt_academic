import json
from typing import List, Dict, Optional

from langchain.schema import Document
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from sqlalchemy import text

from common.api_configs import kbs_config

from common.knowledge_base.kb_service.base import SupportedVSType, KBService, EmbeddingsFunAdapter, \
    score_threshold_process
from common.knowledge_base.utils import KnowledgeFile
import shutil
import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session


class PGKBService(KBService):
    engine: Engine = sqlalchemy.create_engine(kbs_config.get("pg").get("connection_uri"), pool_size=10)

    def _load_pg_vector(self):
        self.pg_vector = PGVector(embedding_function=EmbeddingsFunAdapter(self.embed_model),
                                  collection_name=self.kb_name,
                                  distance_strategy=DistanceStrategy.EUCLIDEAN,
                                  connection=PGKBService.engine,
                                  connection_string=kbs_config.get("pg").get("connection_uri"))

    def get_doc_by_ids(self, ids: List[str]) -> List[Document]:
        with Session(PGKBService.engine) as session:
            stmt = text("SELECT document, cmetadata FROM langchain_pg_embedding WHERE collection_id in :ids")
            results = [Document(page_content=row[0], metadata=row[1]) for row in
                       session.execute(stmt, {'ids': ids}).fetchall()]
            return results
    def del_doc_by_ids(self, ids: List[str]) -> bool:
        return super().del_doc_by_ids(ids)

    def do_init(self):
        self._load_pg_vector()

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.PG

    def do_drop_kb(self):
        with Session(PGKBService.engine) as session:
            session.execute(text(f'''
                    -- 删除 langchain_pg_embedding 表中关联到 langchain_pg_collection 表中 的记录
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id IN (
                      SELECT uuid FROM langchain_pg_collection WHERE name = '{self.kb_name}'
                    );
                    -- 删除 langchain_pg_collection 表中 记录
                    DELETE FROM langchain_pg_collection WHERE name = '{self.kb_name}';
            '''))
            session.commit()
            shutil.rmtree(self.kb_path)

    def do_search(self, query: str, top_k: int, score_threshold: float):
        embed_func = EmbeddingsFunAdapter(self.embed_model)
        embeddings = embed_func.embed_query(query)
        docs = self.pg_vector.similarity_search_with_score_by_vector(embeddings, top_k)
        return score_threshold_process(score_threshold, top_k, docs)

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        ids = self.pg_vector.add_documents(docs)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        with Session(PGKBService.engine) as session:
            filepath = kb_file.filepath.replace('\\', '\\\\')
            session.execute(
                text(
                    ''' DELETE FROM langchain_pg_embedding WHERE cmetadata::jsonb @> '{"source": "filepath"}'::jsonb;'''.replace(
                        "filepath", filepath)))
            session.commit()

    def do_clear_vs(self):
        self.pg_vector.delete_collection()
        self.pg_vector.create_collection()


if __name__ == '__main__':
    from common.db.base import Base, engine

    # Base.metadata.create_all(bind=engine)
    pGKBService = PGKBService("test")
    # pGKBService.create_kb()
    # pGKBService.add_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.delete_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.drop_kb()
    print(pGKBService.get_doc_by_ids(["f1e51390-3029-4a19-90dc-7118aaa25772"]))
    # print(pGKBService.search_docs("如何启动api服务"))
