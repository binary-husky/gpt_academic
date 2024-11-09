from typing import Dict, List, Optional
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
import numpy as np
import os
from toolbox import get_conf
import openai

class RagHandler:
    def __init__(self):
        # 初始化工作目录
        self.working_dir = os.path.join(get_conf('ARXIV_CACHE_DIR'), 'rag_cache')
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)
            
        # 初始化 LightRAG
        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=self._llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=1536,  # OpenAI embedding 维度
                max_token_size=8192,
                func=self._embedding_func,
            ),
        )
        
    async def _llm_model_func(self, prompt: str, system_prompt: str = None, 
                            history_messages: List = None, **kwargs) -> str:
        """LLM 模型函数"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        return response.choices[0].message.content

    async def _embedding_func(self, texts: List[str]) -> np.ndarray:
        """Embedding 函数"""
        response = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=texts
        )
        embeddings = [item["embedding"] for item in response["data"]]
        return np.array(embeddings)

    def process_paper_content(self, paper_content: Dict) -> None:
        """处理论文内容，构建知识图谱"""
        # 处理标题和摘要
        content_list = []
        if paper_content['title']:
            content_list.append(f"Title: {paper_content['title']}")
        if paper_content['abstract']:
            content_list.append(f"Abstract: {paper_content['abstract']}")
            
        # 添加分段内容
        content_list.extend(paper_content['segments'])
        
        # 插入到 RAG 系统
        self.rag.insert(content_list)

    def query(self, question: str, mode: str = "hybrid") -> str:
        """查询论文内容
        mode: 查询模式，可选 naive/local/global/hybrid
        """
        try:
            response = self.rag.query(
                question, 
                param=QueryParam(
                    mode=mode,
                    top_k=5,  # 返回相关度最高的5个结果
                    max_token_for_text_unit=2048,  # 每个文本单元的最大token数
                    response_type="detailed"  # 返回详细回答
                )
            )
            return response
        except Exception as e:
            return f"查询出错: {str(e)}"