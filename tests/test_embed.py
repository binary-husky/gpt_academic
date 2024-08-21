def validate_path():
    import os, sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory


# """
# Test 1
# """

# from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
# from shared_utils.connect_void_terminal import get_chat_default_kwargs
# oaiem = OpenAiEmbeddingModel()

# chat_kwargs = get_chat_default_kwargs()
# llm_kwargs = chat_kwargs['llm_kwargs']
# llm_kwargs.update({
#     'llm_model': "text-embedding-3-small"
# })

# res = oaiem.compute_embedding("你好", llm_kwargs)
# print(res)



"""
Test 2
"""

from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
from shared_utils.connect_void_terminal import get_chat_default_kwargs
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
from llama_index.core.ingestion import run_transformations

chat_kwargs = get_chat_default_kwargs()
llm_kwargs = chat_kwargs['llm_kwargs']
llm_kwargs.update({
    'llm_model': "text-embedding-3-small"
})
embed_model = OpenAiEmbeddingModel(llm_kwargs)

## dir
documents = SimpleDirectoryReader("private_upload/rag_test/").load_data()

## single files
# from llama_index.core import Document
# text_list = [text1, text2, ...]
# documents = [Document(text=t) for t in text_list]
vsi = GptacVectorStoreIndex.default_vector_store(embed_model=embed_model)
documents_nodes = run_transformations(
                    documents,  # type: ignore
                    vsi._transformations,
                    show_progress=True
            )
index = vsi.insert_nodes(documents_nodes)


query_engine = index.as_query_engine()
response = query_engine.query("Some question about the data should go here")
print(response)

