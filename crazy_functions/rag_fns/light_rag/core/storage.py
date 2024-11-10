from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union, TypeVar, Generic, Tuple, Any
import os
import json
import networkx as nx
import numpy as np
from loguru import logger
import html
from datetime import datetime

from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker

T = TypeVar('T')

@dataclass 
class StorageBase:
    """Base class for all storage implementations"""
    namespace: str
    working_dir: str
    
    async def index_done_callback(self):
        """Hook called after indexing operations"""
        pass
    
    async def query_done_callback(self):
        """Hook called after query operations"""  
        pass


@dataclass
class JsonKVStorage(StorageBase, Generic[T]):
    """
    Key-Value storage using JSON files
    
    Attributes:
        namespace (str): Storage namespace
        working_dir (str): Working directory for storage files
        _file_name (str): JSON file path
        _data (Dict[str, T]): In-memory storage
    """
    
    def __post_init__(self):
        """Initialize storage file and load data"""
        self._file_name = os.path.join(self.working_dir, f"kv_{self.namespace}.json")
        self._data: Dict[str, T] = {}
        self.load()
        
    def load(self):
        """Load data from JSON file"""
        if os.path.exists(self._file_name):
            with open(self._file_name, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
                logger.info(f"Loaded {len(self._data)} items from {self._file_name}")
                
    async def save(self):
        """Save data to JSON file"""
        os.makedirs(os.path.dirname(self._file_name), exist_ok=True)
        with open(self._file_name, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
            
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get item by ID"""
        return self._data.get(id)
        
    async def get_by_ids(self, ids: List[str], fields: Optional[Set[str]] = None) -> List[Optional[T]]:
        """Get multiple items by IDs with optional field filtering"""
        if fields is None:
            return [self._data.get(id) for id in ids]
        return [{k: v for k, v in self._data[id].items() if k in fields}
                if id in self._data else None
                for id in ids]
                
    async def filter_keys(self, keys: List[str]) -> Set[str]:
        """Return keys that don't exist in storage"""
        return set(k for k in keys if k not in self._data)
        
    async def upsert(self, data: Dict[str, T]):
        """Insert or update items"""
        self._data.update(data)
        await self.save()
        
    async def drop(self):
        """Clear all data"""
        self._data = {}
        if os.path.exists(self._file_name):
            os.remove(self._file_name)

    async def all_keys(self) -> List[str]:
        """Get all keys in storage"""
        return list(self._data.keys())

    async def index_done_callback(self):
        """Save after indexing"""
        await self.save()


@dataclass
class VectorStorage(StorageBase):
    """
    Vector storage using LlamaIndex
    
    Attributes:
        namespace (str): Storage namespace
        working_dir (str): Working directory for storage files
        llm_kwargs (dict): LLM configuration
        embedding_func (OpenAiEmbeddingModel): Embedding function
        meta_fields (Set[str]): Additional fields to store
        cosine_better_than_threshold (float): Similarity threshold
    """
    llm_kwargs: dict
    embedding_func: OpenAiEmbeddingModel
    meta_fields: Set[str] = field(default_factory=set)
    cosine_better_than_threshold: float = 0.2
    
    def __post_init__(self):
        """Initialize LlamaIndex worker"""
        checkpoint_dir = os.path.join(self.working_dir, f"vector_{self.namespace}")
        self.vector_store = LlamaIndexRagWorker(
            user_name=self.namespace,
            llm_kwargs=self.llm_kwargs,
            checkpoint_dir=checkpoint_dir,
            auto_load_checkpoint=True  # 自动加载检查点
        )
        
    async def query(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Query vectors by similarity
        
        Args:
            query: Query text
            top_k: Maximum number of results
            
        Returns:
            List of similar documents with scores
        """
        nodes = self.vector_store.retrieve_from_store_with_query(query)
        results = [{
            "id": node.node_id,
            "text": node.text,
            "score": node.score,
            **{k: getattr(node, k) for k in self.meta_fields if hasattr(node, k)}
        } for node in nodes[:top_k]]
        return [r for r in results if r.get('score', 0) > self.cosine_better_than_threshold]
    
    async def upsert(self, data: Dict[str, dict]):
        """
        Insert or update vectors
        
        Args:
            data: Dictionary of documents to insert/update
        """
        for id, item in data.items():
            content = item["content"]
            metadata = {k: item[k] for k in self.meta_fields if k in item}
            self.vector_store.add_text_with_metadata(content, metadata=metadata)
            
    async def index_done_callback(self):
        """Save after indexing"""
        self.vector_store.save_to_checkpoint()


@dataclass
class NetworkStorage(StorageBase):
    """
    Graph storage using NetworkX
    
    Attributes:
        namespace (str): Storage namespace
        working_dir (str): Working directory for storage files
    """
    
    def __post_init__(self):
        """Initialize graph and storage file"""
        self._file_name = os.path.join(self.working_dir, f"graph_{self.namespace}.graphml")
        self._graph = self._load_graph() or nx.Graph()
        
    def _load_graph(self) -> Optional[nx.Graph]:
        """Load graph from GraphML file"""
        if os.path.exists(self._file_name):
            try:
                return nx.read_graphml(self._file_name)
            except Exception as e:
                logger.error(f"Error loading graph from {self._file_name}: {e}")
                return None
        return None
        
    async def save_graph(self):
        """Save graph to GraphML file"""
        os.makedirs(os.path.dirname(self._file_name), exist_ok=True)
        logger.info(f"Saving graph with {self._graph.number_of_nodes()} nodes, {self._graph.number_of_edges()} edges")
        nx.write_graphml(self._graph, self._file_name)
        
    async def has_node(self, node_id: str) -> bool:
        """Check if node exists"""
        return self._graph.has_node(node_id)
        
    async def has_edge(self, source_id: str, target_id: str) -> bool:
        """Check if edge exists"""
        return self._graph.has_edge(source_id, target_id)
        
    async def get_node(self, node_id: str) -> Optional[dict]:
        """Get node attributes"""
        if not self._graph.has_node(node_id):
            return None
        return dict(self._graph.nodes[node_id])
        
    async def get_edge(self, source_id: str, target_id: str) -> Optional[dict]:
        """Get edge attributes"""
        if not self._graph.has_edge(source_id, target_id):
            return None
        return dict(self._graph.edges[source_id, target_id])
        
    async def node_degree(self, node_id: str) -> int:
        """Get node degree"""
        return self._graph.degree(node_id)
        
    async def edge_degree(self, source_id: str, target_id: str) -> int:
        """Get sum of degrees of edge endpoints"""
        return self._graph.degree(source_id) + self._graph.degree(target_id)
        
    async def get_node_edges(self, source_id: str) -> Optional[List[Tuple[str, str]]]:
        """Get all edges connected to node"""
        if not self._graph.has_node(source_id):
            return None
        return list(self._graph.edges(source_id))
        
    async def upsert_node(self, node_id: str, node_data: Dict[str, str]):
        """Insert or update node"""
        # Clean and normalize node data
        cleaned_data = {k: html.escape(str(v).upper().strip()) for k, v in node_data.items()}
        self._graph.add_node(node_id, **cleaned_data)
        
    async def upsert_edge(self, source_id: str, target_id: str, edge_data: Dict[str, str]):
        """Insert or update edge"""
        # Clean and normalize edge data
        cleaned_data = {k: html.escape(str(v).strip()) for k, v in edge_data.items()}
        self._graph.add_edge(source_id, target_id, **cleaned_data)
        
    async def index_done_callback(self):
        """Save after indexing"""
        await self.save_graph()

    def get_largest_connected_component(self) -> nx.Graph:
        """Get the largest connected component of the graph"""
        if not self._graph:
            return nx.Graph()
        
        components = list(nx.connected_components(self._graph))
        if not components:
            return nx.Graph()
            
        largest_component = max(components, key=len)
        return self._graph.subgraph(largest_component).copy()
        
    async def embed_nodes(self, algorithm: str, **kwargs) -> Tuple[np.ndarray, List[str]]:
        """
        Embed nodes using specified algorithm
        
        Args:
            algorithm: Node embedding algorithm name
            **kwargs: Additional algorithm parameters
            
        Returns:
            Tuple of (node embeddings, node IDs)
        """
        if algorithm == "node2vec":
            from node2vec import Node2Vec
            
            # Create node2vec model
            node2vec = Node2Vec(
                self._graph,
                dimensions=kwargs.get('dimensions', 128),
                walk_length=kwargs.get('walk_length', 30),
                num_walks=kwargs.get('num_walks', 200),
                workers=kwargs.get('workers', 4)
            )
            
            # Train model
            model = node2vec.fit(
                window=kwargs.get('window', 10),
                min_count=kwargs.get('min_count', 1)
            )
            
            # Get embeddings
            node_ids = list(self._graph.nodes())
            embeddings = np.array([model.wv[node] for node in node_ids])
            
            return embeddings, node_ids
        else:
            raise ValueError(f"Unsupported embedding algorithm: {algorithm}")
