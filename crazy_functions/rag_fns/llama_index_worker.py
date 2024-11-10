import atexit
from typing import List, Dict, Optional, Any, Tuple

from llama_index.core import Document
from llama_index.core.ingestion import run_transformations
from llama_index.core.schema import TextNode, NodeWithScore
from loguru import logger

from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
import json
import numpy as np
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



    """
    以下是添加的新方法，原有方法保持不变
    """

    def add_text_with_metadata(self, text: str, metadata: dict) -> str:
        """
        添加带元数据的文本到向量存储

        Args:
            text: 文本内容
            metadata: 元数据字典

        Returns:
            添加的节点ID
        """
        node = TextNode(text=text, metadata=metadata)
        nodes = run_transformations(
            [node],
            self.vs_index._transformations,
            show_progress=True
        )
        self.vs_index.insert_nodes(nodes)
        return nodes[0].node_id if nodes else None

    def batch_add_texts_with_metadata(self, texts: List[Tuple[str, dict]]) -> List[str]:
        """
        批量添加带元数据的文本

        Args:
            texts: (text, metadata)元组列表

        Returns:
            添加的节点ID列表
        """
        nodes = [TextNode(text=t, metadata=m) for t, m in texts]
        transformed_nodes = run_transformations(
            nodes,
            self.vs_index._transformations,
            show_progress=True
        )
        if transformed_nodes:
            self.vs_index.insert_nodes(transformed_nodes)
            return [node.node_id for node in transformed_nodes]
        return []

    def get_node_metadata(self, node_id: str) -> Optional[dict]:
        """
        获取节点的元数据

        Args:
            node_id: 节点ID

        Returns:
            节点的元数据字典
        """
        node = self.vs_index.storage_context.docstore.docs.get(node_id)
        return node.metadata if node else None

    def update_node_metadata(self, node_id: str, metadata: dict, merge: bool = True) -> bool:
        """
        更新节点的元数据

        Args:
            node_id: 节点ID
            metadata: 新的元数据
            merge: 是否与现有元数据合并

        Returns:
            是否更新成功
        """
        docstore = self.vs_index.storage_context.docstore
        if node_id in docstore.docs:
            node = docstore.docs[node_id]
            if merge:
                node.metadata.update(metadata)
            else:
                node.metadata = metadata
            return True
        return False

    def filter_nodes_by_metadata(self, filters: Dict[str, Any]) -> List[TextNode]:
        """
        按元数据过滤节点

        Args:
            filters: 元数据过滤条件

        Returns:
            符合条件的节点列表
        """
        docstore = self.vs_index.storage_context.docstore
        results = []
        for node in docstore.docs.values():
            if all(node.metadata.get(k) == v for k, v in filters.items()):
                results.append(node)
        return results

    def retrieve_with_metadata_filter(
            self,
            query: str,
            metadata_filters: Dict[str, Any],
            top_k: int = 5
    ) -> List[NodeWithScore]:
        """
        结合元数据过滤的检索

        Args:
            query: 查询文本
            metadata_filters: 元数据过滤条件
            top_k: 返回结果数量

        Returns:
            检索结果节点列表
        """
        retriever = self.vs_index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)

        # 应用元数据过滤
        filtered_nodes = []
        for node in nodes:
            if all(node.metadata.get(k) == v for k, v in metadata_filters.items()):
                filtered_nodes.append(node)

        return filtered_nodes

    def get_node_stats(self, node_id: str) -> dict:
        """
        获取单个节点的统计信息

        Args:
            node_id: 节点ID

        Returns:
            节点统计信息字典
        """
        node = self.vs_index.storage_context.docstore.docs.get(node_id)
        if not node:
            return {}

        return {
            "text_length": len(node.text),
            "token_count": len(node.text.split()),
            "has_embedding": node.embedding is not None,
            "metadata_keys": list(node.metadata.keys()),
        }

    def get_nodes_by_content_pattern(self, pattern: str) -> List[TextNode]:
        """
        按内容模式查找节点

        Args:
            pattern: 正则表达式模式

        Returns:
            匹配的节点列表
        """
        import re
        docstore = self.vs_index.storage_context.docstore
        matched_nodes = []
        for node in docstore.docs.values():
            if re.search(pattern, node.text):
                matched_nodes.append(node)
        return matched_nodes
    def export_nodes(
            self,
            output_file: str,
            format: str = "json",
            include_embeddings: bool = False
    ) -> None:
        """
        Export nodes to file

        Args:
            output_file: Output file path
            format: "json" or "csv"
            include_embeddings: Whether to include embeddings
        """
        docstore = self.vs_index.storage_context.docstore

        data = []
        for node_id, node in docstore.docs.items():
            node_data = {
                "node_id": node_id,
                "text": node.text,
                "metadata": node.metadata,
            }
            if include_embeddings and node.embedding is not None:
                node_data["embedding"] = node.embedding.tolist()
            data.append(node_data)

        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif format == "csv":
            import csv
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        docstore = self.vs_index.storage_context.docstore
        docs = list(docstore.docs.values())

        return {
            "total_nodes": len(docs),
            "total_tokens": sum(len(node.text.split()) for node in docs),
            "avg_text_length": np.mean([len(node.text) for node in docs]) if docs else 0,
            "embedding_dimension": len(docs[0].embedding) if docs and docs[0].embedding is not None else 0
        }