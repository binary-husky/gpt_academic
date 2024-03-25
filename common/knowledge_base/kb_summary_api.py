from fastapi import Body
from common.configs import (DEFAULT_VS_TYPE, EMBEDDING_MODEL,
                            OVERLAP_SIZE)
from common.logger_handler import logger
from common.knowledge_base.utils import (list_files_from_folder)
from sse_starlette import EventSourceResponse
import json
from common.knowledge_base.kb_service.base import KBServiceFactory
from typing import List, Optional
from common.knowledge_base.kb_summary.base import KBSummaryService
from common.knowledge_base.kb_summary.summary_chunk import SummaryAdapter
from common.utils import BaseResponse, get_ChatOpenAI
from common.configs import LLM_MODELS
from common.knowledge_base.kb_document_model import DocumentWithVSId


def recreate_summary_vector_store(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        allow_empty_kb: bool = Body(True),
        vs_type: str = Body(DEFAULT_VS_TYPE),
        embed_model: str = Body(EMBEDDING_MODEL),
        file_description: str = Body(''),
        model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
        temperature: float = Body(1, description="LLM 采样温度", ge=0.0, le=1.0),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    """
    重建单个知识库文件摘要
    :param max_tokens:
    :param model_name:
    :param temperature:
    :param file_description:
    :param knowledge_base_name:
    :param allow_empty_kb:
    :param vs_type:
    :param embed_model:
    :return:
    """

    def output():

        kb = KBServiceFactory.get_service(knowledge_base_name, vs_type, embed_model)
        if not kb.exists() and not allow_empty_kb:
            yield {"code": 404, "msg": f"未找到知识库 ‘{knowledge_base_name}’"}
        else:
            # 重新创建知识库
            kb_summary = KBSummaryService(knowledge_base_name, embed_model)
            kb_summary.drop_kb_summary()
            kb_summary.create_kb_summary()

            llm = get_ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            reduce_llm = get_ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # 文本摘要适配器
            summary = SummaryAdapter.form_summary(llm=llm,
                                                  reduce_llm=reduce_llm,
                                                  overlap_size=OVERLAP_SIZE)
            files = list_files_from_folder(knowledge_base_name)

            i = 0
            for i, file_name in enumerate(files):

                doc_infos = kb.list_docs(file_name=file_name)
                docs = summary.summarize(file_description=file_description,
                                         docs=doc_infos)

                status_kb_summary = kb_summary.add_kb_summary(summary_combine_docs=docs)
                if status_kb_summary:
                    logger.info(f"({i + 1} / {len(files)}): {file_name} 总结完成")
                    yield json.dumps({
                        "code": 200,
                        "msg": f"({i + 1} / {len(files)}): {file_name}",
                        "total": len(files),
                        "finished": i + 1,
                        "doc": file_name,
                    }, ensure_ascii=False)
                else:

                    msg = f"知识库'{knowledge_base_name}'总结文件‘{file_name}’时出错。已跳过。"
                    logger.error(msg)
                    yield json.dumps({
                        "code": 500,
                        "msg": msg,
                    })
                i += 1

    return EventSourceResponse(output())


def summary_file_to_vector_store(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        file_name: str = Body(..., examples=["test.pdf"]),
        allow_empty_kb: bool = Body(True),
        vs_type: str = Body(DEFAULT_VS_TYPE),
        embed_model: str = Body(EMBEDDING_MODEL),
        file_description: str = Body(''),
        model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
        temperature: float = Body(1, description="LLM 采样温度", ge=0.0, le=1.0),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    """
    单个知识库根据文件名称摘要
    :param model_name:
    :param max_tokens:
    :param temperature:
    :param file_description:
    :param file_name:
    :param knowledge_base_name:
    :param allow_empty_kb:
    :param vs_type:
    :param embed_model:
    :return:
    """

    def output():
        kb = KBServiceFactory.get_service(knowledge_base_name, vs_type, embed_model)
        if not kb.exists() and not allow_empty_kb:
            yield {"code": 404, "msg": f"未找到知识库 ‘{knowledge_base_name}’"}
        else:
            # 重新创建知识库
            kb_summary = KBSummaryService(knowledge_base_name, embed_model)
            kb_summary.create_kb_summary()

            llm = get_ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            reduce_llm = get_ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # 文本摘要适配器
            summary = SummaryAdapter.form_summary(llm=llm,
                                                  reduce_llm=reduce_llm,
                                                  overlap_size=OVERLAP_SIZE)

            doc_infos = kb.list_docs(file_name=file_name)
            docs = summary.summarize(file_description=file_description,
                                     docs=doc_infos)

            status_kb_summary = kb_summary.add_kb_summary(summary_combine_docs=docs)
            if status_kb_summary:
                logger.info(f" {file_name} 总结完成")
                yield json.dumps({
                    "code": 200,
                    "msg": f"{file_name} 总结完成",
                    "doc": file_name,
                }, ensure_ascii=False)
            else:

                msg = f"知识库'{knowledge_base_name}'总结文件‘{file_name}’时出错。已跳过。"
                logger.error(msg)
                yield json.dumps({
                    "code": 500,
                    "msg": msg,
                })

    return output()


def summary_doc_ids_to_vector_store(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        doc_ids: List = Body([], examples=[["uuid"]]),
        vs_type: str = Body(DEFAULT_VS_TYPE),
        embed_model: str = Body(EMBEDDING_MODEL),
        file_description: str = Body(''),
        model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
        temperature: float = Body(1, description="LLM 采样温度", ge=0.0, le=1.0),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
) -> BaseResponse:
    """
    单个知识库根据doc_ids摘要
    :param knowledge_base_name:
    :param doc_ids:
    :param model_name:
    :param max_tokens:
    :param temperature:
    :param file_description:
    :param vs_type:
    :param embed_model:
    :return:
    """
    kb = KBServiceFactory.get_service(knowledge_base_name, vs_type, embed_model)
    if not kb.exists():
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data={})
    else:
        llm = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        reduce_llm = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # 文本摘要适配器
        summary = SummaryAdapter.form_summary(llm=llm,
                                              reduce_llm=reduce_llm,
                                              overlap_size=OVERLAP_SIZE)

        doc_infos = kb.get_doc_by_ids(ids=doc_ids)
        # doc_infos转换成DocumentWithVSId包装的对象
        doc_info_with_ids = [DocumentWithVSId(**doc.dict(), id=with_id) for with_id, doc in zip(doc_ids, doc_infos)]

        docs = summary.summarize(file_description=file_description,
                                 docs=doc_info_with_ids)

        # 将docs转换成dict
        resp_summarize = [{**doc.dict()} for doc in docs]

        return BaseResponse(code=200, msg="总结完成", data={"summarize": resp_summarize})



if __name__ == '__main__':
    summary = summary_file_to_vector_store('增长需求文档',
                                           '【用户增长】新增Whatsapp优先发送策略【跟包】.docx',
                                           True, 'faiss', 'bge-large-zh-v1.5',
                                           '', LLM_MODELS[0], temperature=1, max_tokens=None)

    for s in summary:
        print(s)
