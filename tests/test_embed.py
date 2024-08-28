def validate_path():
    import os, sys
    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)

validate_path()  # validate path so you can run from base directory

# # """
# # Test 1
# # """

# # from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
# # from shared_utils.connect_void_terminal import get_chat_default_kwargs
# # oaiem = OpenAiEmbeddingModel()

# # chat_kwargs = get_chat_default_kwargs()
# # llm_kwargs = chat_kwargs['llm_kwargs']
# # llm_kwargs.update({
# #     'llm_model': "text-embedding-3-small"
# # })

# # res = oaiem.compute_embedding("你好", llm_kwargs)
# # print(res)

# """
# Test 2
# """

# from request_llms.embed_models.openai_embed import OpenAiEmbeddingModel
from shared_utils.connect_void_terminal import get_chat_default_kwargs
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from crazy_functions.rag_fns.vector_store_index import GptacVectorStoreIndex
# from llama_index.core.ingestion import run_transformations
# from llama_index.core import PromptTemplate
# from llama_index.core.response_synthesizers import TreeSummarize

# # NOTE: we add an extra tone_name variable here
# DEFAULT_QUESTION_GENERATION_PROMPT = """\
# Context information is below.
# ---------------------
# {context_str}
# ---------------------
# Given the context information and not prior knowledge.
# generate only questions based on the below query.
# {query_str}
# """


chat_kwargs = get_chat_default_kwargs()
llm_kwargs = chat_kwargs['llm_kwargs']
llm_kwargs.update({
    'llm_model': "text-embedding-3-small"
})
# embed_model = OpenAiEmbeddingModel(llm_kwargs)

# ## dir
# documents = SimpleDirectoryReader("private_upload/rag_test/").load_data()

# ## single files
# # from llama_index.core import Document
# # text_list = [text1, text2, ...]
# # documents = [Document(text=t) for t in text_list]
# vsi = GptacVectorStoreIndex.default_vector_store(embed_model=embed_model)
# documents_nodes = run_transformations(
#                         documents,  # type: ignore
#                         vsi._transformations,
#                         show_progress=True
#                     )
# index = vsi.insert_nodes(documents_nodes)
# retriever = vsi.as_retriever()

# query = "what is core_functional.py"

# res = retriever.retrieve(query)
# context_str = '\n'.join([r.text for r in res])
# query_str = query
# query = DEFAULT_QUESTION_GENERATION_PROMPT.format(context_str=context_str, query_str=query_str)
# print(res)
# print(res)


# # response = query_engine.query("Some question about the data should go here")
# # print(response)

from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker
rag_worker = LlamaIndexRagWorker('good-man-user', llm_kwargs, checkpoint_dir='./good_man_vector_store')

# rag_worker.add_text_to_vector_store("""
# 熊童子（Cotyledon tomentosa）是景天科，银波锦属的多年生肉质草本植物，植株多分枝，茎绿色，肉质叶肥厚，交互对生，卵圆形，绿色，密生白色短毛。叶端具红色爪样齿，二歧聚伞花序，小花黄色，花期7-9月。
# 该种原产于南非开普省。喜温暖干燥，阳光充足，通风良好的环境。夏季温度过高会休眠。忌寒冷和过分潮湿。繁殖方法有扦插。
# 该种叶形叶色较美，花朵玲珑小巧，叶片形似小熊的脚掌，形态奇特，十分可爱，观赏价值很高。
# 物种索引：IN4679748
# """)

# rag_worker.add_text_to_vector_store("""
# 碧光环是番杏科碧光玉属 [4]多年生肉质草本植物。 [5]碧光环叶表面有半透明的颗粒感，晶莹剔透；两片圆柱形的叶子，在生长初期像兔耳，非常可爱，长大后叶子会慢慢变长变粗，缺水时容易耷拉下来；具枝干，易群生。
# 碧光环原产于南非。碧光环喜温暖和散射光充足的环境，较耐寒，忌强光暴晒，夏季高温休眠明显。 [6]碧光环的繁殖方式有扦插和播种。 [7]
# 碧光环小巧饱满、圆滚滚的样子很可爱，长得好像长耳朵小兔，萌萌的样子让人爱不释手，而且养起来也不难，极具观赏价值。 [8]                        
# 物种索引：IN985654
# """)

# rag_worker.add_text_to_vector_store("""
# 福娘为景天科银波锦属的肉质草本植物。对生的叶片呈短棒状，叶色灰绿，表覆白粉，叶缘外围镶着紫红色，叶片外形多有变化有短圆形、厚厚的方形等不同叶形； [5]花期夏秋。 [6]
# 福娘原产于非洲西南部的纳米比亚，现世界多地均有栽培。性喜欢凉爽通风、日照充足的环境，较喜光照，喜肥，生长适温为15-25℃，冬季温度不低于5℃，生长期要见干见湿。 [7]在通风透气、排水良好的土壤上生长良好，一般可用泥炭土、蛭石和珍珠岩的混合土。繁殖方式一般为扦插繁殖，多用枝插，叶插的繁殖成功率不高。 [8]
# 因福娘的叶形叶色较美，所以具有一定的观赏价值，可盆栽放置于电视、电脑旁，吸收辐射，亦可栽植于室内以吸收甲醛等物质，净化空气。 [9]
# 物种索引：IN772
# """)

# rag_worker.add_text_to_vector_store("""
# 石莲（ Sinocrassula indica (Decne.) A. Berger）是景天科石莲属 [8]的二年生草本植物。基生叶莲座状，匙状长圆形；茎生叶互生，宽倒披针状线形或近倒卵形；花序圆锥状或近伞房状，萼片呈宽三角形，花瓣呈红色，披针形或卵形，雄蕊呈正方形；蓇葖果的喙反曲；种子平滑；花期9月；果期10月 [9]。锯叶石莲为石莲的变种，与原变种的不同处为叶上部有渐尖的锯齿。茎和花无毛，叶被毛 [10]。因叶子有棱有角，又似玉石，故而得名“石莲” [11]。
# 物种索引：IN455674
# """)

# rag_worker.add_text_to_vector_store("""
# 虹之玉锦（Sedum × rubrotinctum 'Aurora'） [1]是景天科景天属的多肉植物，为虹之玉的锦化品种。虹之玉锦与虹之玉的叶片大小没有特别大的变化，但颜色会稍有不同，虹之玉锦一般会有粉红色、中绿色等 [2]。生长速度较虹之玉慢很多 [3]。
# 物种索引：IN88
# """)
query = '福娘的物种'
nodes = rag_worker.retrieve_from_store_with_query(query)
build_prompt = rag_worker.build_prompt(query, nodes)
preview = rag_worker.generate_node_array_preview(nodes)
print(preview)
print(build_prompt)
print(nodes)

# vs = rag_worker.load_from_checkpoint('./good_man_vector_store')
# rag_worker.add_text_to_vector_store(r"I see that the (0.6.0) index persisted on disk contains: docstore.json, index_store.json and vector_store.json, but they don't seem to contain file paths or title metadata from the original documents, so maybe that's not captured and stored?")
# rag_worker.add_text_to_vector_store(r"Thanks! I'm trying to cluster (all) the vectors, then generate a description (label) for each cluster by sending (just) the vectors in each cluster to GPT to summarize, then associate the vectors with the original documents and classify each document by applying a sort of weighted sum of its cluster-labeled snippets. Not sure how useful that will be, but I want to try! I've got the vectors now (although I'm bit worried that the nested structure I'm getting them from might change without warning in the future!), and I'm able to cluster them, but I don't know how to associate the vectors (via their nodes) back to the original documents yet...")
# res = rag_worker.retrieve_from_store_with_query('cluster')
# rag_worker.save_to_checkpoint(checkpoint_dir = './good_man_vector_store')

# print(vs)
