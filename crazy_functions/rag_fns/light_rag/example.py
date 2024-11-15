from typing import List, Dict, Optional, Tuple
import asyncio
import os
from datetime import datetime
from pprint import pprint
import json
from loguru import logger
import numpy as np

from core.prompt_templates import PromptTemplates
from core.extractor import EntityRelationExtractor, PromptInfo
from core.storage import JsonKVStorage, VectorStorage, NetworkStorage
from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel

from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("API_URL"))


class ExtractionExample:
    """Example class demonstrating comprehensive RAG system functionality"""

    def __init__(self):
        """Initialize RAG system components"""
        # 设置工作目录
        self.working_dir = f"crazy_functions/rag_fns/LightRAG/rag_cache_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        os.makedirs(self.working_dir, exist_ok=True)
        logger.info(f"Working directory: {self.working_dir}")

        # 初始化embedding
        self.llm_kwargs = {
            'api_key': os.getenv("one_api_key"),
            'client_ip': '127.0.0.1',
            'embed_model': 'text-embedding-3-small',
            'llm_model': 'one-api-Qwen2.5-72B-Instruct',
            'max_length': 4096,
            'most_recent_uploaded': None,
            'temperature': 1,
            'top_p': 1
        }
        self.embedding_func = OpenAiEmbeddingModel(self.llm_kwargs)

        # 初始化提示模板和抽取器
        self.prompt_templates = PromptTemplates()
        self.extractor = EntityRelationExtractor(
            prompt_templates=self.prompt_templates,
            required_prompts={'entity_extraction'},
            entity_extract_max_gleaning=1
        )

        # 初始化存储系统
        self._init_storage_system()

        # 对话历史
        self.conversation_history = {}

    def _init_storage_system(self):
        """Initialize storage components"""
        # KV存储 - 用于原始文本和分块
        self.text_chunks = JsonKVStorage[dict](
            namespace="text_chunks",
            working_dir=self.working_dir
        )

        self.full_docs = JsonKVStorage[dict](
            namespace="full_docs",
            working_dir=self.working_dir
        )

        # 向量存储 - 用于实体、关系和文本块的向量表示
        self.entities_vdb = VectorStorage(
            namespace="entities",
            working_dir=self.working_dir,
            llm_kwargs=self.llm_kwargs,
            embedding_func=self.embedding_func,
            meta_fields={"entity_name", "entity_type"}
        )

        self.relationships_vdb = VectorStorage(
            namespace="relationships",
            working_dir=self.working_dir,
            llm_kwargs=self.llm_kwargs,
            embedding_func=self.embedding_func,
            meta_fields={"src_id", "tgt_id"}
        )

        self.chunks_vdb = VectorStorage(
            namespace="chunks",
            working_dir=self.working_dir,
            llm_kwargs=self.llm_kwargs,
            embedding_func=self.embedding_func
        )

        # 图存储 - 用于实体关系
        self.graph_store = NetworkStorage(
            namespace="chunk_entity_relation",
            working_dir=self.working_dir
        )

    async def simulate_llm_call(self, prompt: str, prompt_info: PromptInfo) -> str:
        """Simulate LLM call with conversation history"""
        # 获取当前chunk的对话历史
        chunk_history = self.conversation_history.get(prompt_info.chunk_key, [])

        messages = [
            {"role": "system",
             "content": "You are a helpful assistant specialized in entity and relationship extraction."}
        ]

        # 添加历史对话
        for msg in chunk_history:
            messages.append(msg)

        # 添加当前prompt
        messages.append({"role": "user", "content": prompt})

        try:
            # 调用LLM
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )

            response_content = response.choices[0].message.content

            # 更新对话历史
            chunk_history.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response_content}
            ])
            self.conversation_history[prompt_info.chunk_key] = chunk_history

            logger.info(f"\nProcessing chunk: {prompt_info.chunk_key}")
            logger.info(f"Phase: {prompt_info.prompt_type}")
            logger.info(f"Response: {response_content[:200]}...")

            return response_content

        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            raise

    async def process_document(self, content: str) -> Tuple[Dict, Dict]:
        """Process a single document through the RAG pipeline"""
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 存储原始文档
        await self.full_docs.upsert({
            doc_id: {"content": content}
        })

        # 文档分块
        from core.chunking import chunk_document
        chunks = chunk_document(content)
        chunk_dict = {
            f"{doc_id}_chunk_{i}": {"content": chunk, "doc_id": doc_id}
            for i, chunk in enumerate(chunks)
        }

        # 存储分块
        await self.text_chunks.upsert(chunk_dict)

        # 处理分块并提取实体关系
        nodes, edges = await self.process_chunk_batch(chunk_dict)

        return nodes, edges

    async def process_chunk_batch(self, chunks: Dict[str, dict]):
        """Process text chunks and store results"""
        try:
            # 向量存储
            logger.info("Adding chunks to vector store...")
            await self.chunks_vdb.upsert(chunks)

            # 初始化对话历史
            self.conversation_history = {chunk_key: [] for chunk_key in chunks.keys()}

            # 提取实体和关系
            logger.info("Extracting entities and relationships...")
            prompts = self.extractor.initialize_extraction(chunks)

            while prompts:
                # 处理prompts
                responses = await asyncio.gather(
                    *[self.simulate_llm_call(p.prompt, p) for p in prompts]
                )

                # 处理响应
                next_prompts = []
                for response, prompt_info in zip(responses, prompts):
                    next_batch = self.extractor.process_response(response, prompt_info)
                    next_prompts.extend(next_batch)

                prompts = next_prompts

            # 获取结果
            nodes, edges = self.extractor.get_results()

            # 存储实体到向量数据库和图数据库
            for node_name, node_instances in nodes.items():
                for node in node_instances:
                    # 存储到向量数据库
                    await self.entities_vdb.upsert({
                        f"entity_{node_name}": {
                            "content": f"{node_name}: {node['description']}",
                            "entity_name": node_name,
                            "entity_type": node['entity_type']
                        }
                    })
                    # 存储到图数据库
                    await self.graph_store.upsert_node(node_name, node)

            # 存储关系到向量数据库和图数据库
            for (src, tgt), edge_instances in edges.items():
                for edge in edge_instances:
                    # 存储到向量数据库
                    await self.relationships_vdb.upsert({
                        f"rel_{src}_{tgt}": {
                            "content": f"{edge['description']} | {edge['keywords']}",
                            "src_id": src,
                            "tgt_id": tgt
                        }
                    })
                    # 存储到图数据库
                    await self.graph_store.upsert_edge(src, tgt, edge)

            return nodes, edges

        except Exception as e:
            logger.error(f"Error in processing chunks: {e}")
            raise

    async def query_knowledge_base(self, query: str, top_k: int = 5):
        """Query the knowledge base using various methods"""
        try:
            # 向量相似度搜索 - 文本块
            chunk_results = await self.chunks_vdb.query(query, top_k=top_k)

            # 向量相似度搜索 - 实体
            entity_results = await self.entities_vdb.query(query, top_k=top_k)

            # 获取相关文本块
            chunk_ids = [r["id"] for r in chunk_results]
            chunks = await self.text_chunks.get_by_ids(chunk_ids)

            # 获取实体相关的图结构信息
            relevant_edges = []
            for entity in entity_results:
                if "entity_name" in entity:
                    entity_name = entity["entity_name"]
                    if await self.graph_store.has_node(entity_name):
                        edges = await self.graph_store.get_node_edges(entity_name)
                        if edges:
                            edge_data = []
                            for edge in edges:
                                edge_info = await self.graph_store.get_edge(edge[0], edge[1])
                                if edge_info:
                                    edge_data.append({
                                        "source": edge[0],
                                        "target": edge[1],
                                        "data": edge_info
                                    })
                            relevant_edges.extend(edge_data)

            return {
                "chunks": chunks,
                "entities": entity_results,
                "relationships": relevant_edges
            }

        except Exception as e:
            logger.error(f"Error in querying knowledge base: {e}")
            raise

    def export_knowledge_base(self, export_dir: str):
        """Export the entire knowledge base"""
        os.makedirs(export_dir, exist_ok=True)

        try:
            # 导出统计信息
            storage_stats = {
                "chunks": {
                    "total": len(self.text_chunks._data),
                    "vector_stats": self.chunks_vdb.get_statistics()
                },
                "entities": {
                    "vector_stats": self.entities_vdb.get_statistics()
                },
                "relationships": {
                    "vector_stats": self.relationships_vdb.get_statistics()
                },
                "graph": {
                    "total_nodes": len(list(self.graph_store._graph.nodes())),
                    "total_edges": len(list(self.graph_store._graph.edges())),
                    "node_degrees": dict(self.graph_store._graph.degree()),
                    "largest_component_size": len(self.graph_store.get_largest_connected_component())
                }
            }

            # 导出统计
            with open(os.path.join(export_dir, "storage_stats.json"), "w") as f:
                json.dump(storage_stats, f, indent=2)

        except Exception as e:
            logger.error(f"Error in exporting knowledge base: {e}")
            raise

    def print_extraction_results(self, nodes: Dict[str, List[dict]], edges: Dict[tuple, List[dict]]):
        """Print extraction results and statistics"""
        print("\nExtracted Entities:")
        print("-" * 50)
        for entity_name, entity_instances in nodes.items():
            print(f"\nEntity: {entity_name}")
            for inst in entity_instances:
                pprint(inst, indent=2)

        print("\nExtracted Relationships:")
        print("-" * 50)
        for (src, tgt), rel_instances in edges.items():
            print(f"\nRelationship: {src} -> {tgt}")
            for inst in rel_instances:
                pprint(inst, indent=2)

        print("\nStorage Statistics:")
        print("-" * 50)
        print(f"Working Directory: {self.working_dir}")
        print(f"Number of Documents: {len(self.full_docs._data)}")
        print(f"Number of Chunks: {len(self.text_chunks._data)}")
        print(f"Conversation Turns: {sum(len(h) // 2 for h in self.conversation_history.values())}")

        # 打印图统计
        print("\nGraph Statistics:")
        print("-" * 50)
        print(f"Total Nodes: {len(list(self.graph_store._graph.nodes()))}")
        print(f"Total Edges: {len(list(self.graph_store._graph.edges()))}")


async def main():
    """Run comprehensive RAG example"""
    # 测试文档
    documents = {
        "tech_news": """
        Apple Inc. announced new iPhone models today in Cupertino. 
        Tim Cook, the CEO, presented the keynote. The presentation highlighted 
        the company's commitment to innovation and sustainability. The new iPhone 
        features groundbreaking AI capabilities.
        """,
    }

    try:
        # 创建RAG系统实例
        example = ExtractionExample()

        # 处理文档
        all_nodes = {}
        all_edges = {}

        for doc_name, content in documents.items():
            logger.info(f"\nProcessing document: {doc_name}")
            nodes, edges = await example.process_document(content)
            all_nodes.update(nodes)
            all_edges.update(edges)

        # 打印结果
        example.print_extraction_results(all_nodes, all_edges)

        # 测试查询
        query = "What are the latest developments in AI?"
        logger.info(f"\nTesting query: {query}")
        results = await example.query_knowledge_base(query)

        print("\nQuery Results:")
        print("-" * 50)
        pprint(results)

        # 导出知识库
        export_dir = os.path.join(example.working_dir, "export")
        print("\nExporting knowledge base...")
        logger.info(f"\nExporting knowledge base to: {export_dir}")
        example.export_knowledge_base(export_dir)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


def run_example():
    """Run the example"""
    asyncio.run(main())


if __name__ == "__main__":
    run_example()