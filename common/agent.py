#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/27
# @Author : Spike
# @Descr   :
from common import crazy_functional

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from common.toolbox import ProxyNetworkActivate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
text2vec_large_chinese = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")


ALL_TOOLS = crazy_functional.crazy_func_to_tool()
docs = [
    Document(page_content=t.description, metadata={"index": i})
    for i, t in enumerate(ALL_TOOLS)
]
vector_store = FAISS.from_documents(docs, text2vec_large_chinese)
retriever = vector_store.as_retriever()


def get_tools(query):
    docs = retriever.get_relevant_documents(query)
    return [ALL_TOOLS[d.metadata["index"]] for d in docs]


print(get_tools("编写客户端测试用例"))
