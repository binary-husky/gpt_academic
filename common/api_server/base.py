# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :
from fastapi import FastAPI
from common.api_server import gradio_app
from starlette.middleware.sessions import SessionMiddleware
from common.utils import BaseResponse, ListResponse
from typing import List, Literal

from common.knowledge_base.kb_api import list_kbs, create_kb, delete_kb
from common.knowledge_base.kb_doc_api import (list_files, upload_docs, delete_docs,
                                              update_docs, download_doc, recreate_vector_store,
                                              search_docs, DocumentWithVSId, update_info,
                                              update_docs_by_id)

from common.knowledge_base.kb_summary_api import (recreate_summary_kb, recreate_summary_file)


def mount_knowledge_routes(app: FastAPI):
    # app.post("/chat/knowledge_base_chat",
    #          tags=["Chat"],
    #          summary="与知识库对话")(knowledge_base_chat)
    #
    # app.post("/chat/file_chat",
    #          tags=["Knowledge Base Management"],
    #          summary="文件对话"
    #          )(file_chat)
    #
    # app.post("/chat/agent_chat",
    #          tags=["Chat"],
    #          summary="与agent对话")(agent_chat)

    # Tag: Knowledge Base Management
    app.get("/knowledge_base/list_knowledge_bases",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库列表")(list_kbs)

    app.post("/knowledge_base/create_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="创建知识库"
             )(create_kb)

    app.post("/knowledge_base/delete_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库"
             )(delete_kb)

    app.get("/knowledge_base/list_files",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库内的文件列表"
            )(list_files)

    app.post("/knowledge_base/search_docs",
             tags=["Knowledge Base Management"],
             response_model=List[DocumentWithVSId],
             summary="搜索知识库"
             )(search_docs)

    app.post("/knowledge_base/update_docs_by_id",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="直接更新知识库文档"
             )(update_docs_by_id)

    app.post("/knowledge_base/upload_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="上传文件到知识库，并/或进行向量化"
             )(upload_docs)

    app.post("/knowledge_base/delete_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库内指定文件"
             )(delete_docs)

    app.post("/knowledge_base/update_info",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新知识库介绍"
             )(update_info)
    app.post("/knowledge_base/update_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新现有文件到知识库"
             )(update_docs)

    app.get("/knowledge_base/download_doc",
            tags=["Knowledge Base Management"],
            summary="下载对应的知识文件")(download_doc)

    app.post("/knowledge_base/recreate_vector_store",
             tags=["Knowledge Base Management"],
             summary="根据content中文档重建向量库，流式输出处理进度。"
             )(recreate_vector_store)


def mount_filename_summary_routes(app: FastAPI):
    app.post("/knowledge_base/kb_summary_api/summary_file_to_vector_store",
             tags=["Knowledge kb_summary_api Management"],
             summary="单个知识库根据文件名称摘要"
             )(recreate_summary_kb)
    app.post("/knowledge_base/kb_summary_api/summary_doc_ids_to_vector_store",
             tags=["Knowledge kb_summary_api Management"],
             summary="单个知识库根据file摘要",
             response_model=BaseResponse,
             )(recreate_summary_file)


def mount_app_routes(app: FastAPI):

    app.get(path='/favicon.ico', tags=['Gradio Mount'], summary='获取网站icon')(gradio_app.get_favicon)

    app.get(path='/logout', tags=['Gradio Mount'], summary='退出登陆')(gradio_app.logout)

    mount_knowledge_routes(app)

    mount_filename_summary_routes(app)


def create_app():
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="!secret")
    app.middleware('https')(gradio_app.redirect_authentication)

    mount_app_routes(app)

    return app


if __name__ == '__main__':
    pass
