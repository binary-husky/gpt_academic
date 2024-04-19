from fastapi import Body
from sse_starlette.sse import EventSourceResponse

import json
from common.knowledge_base.kb_service.base import KBServiceFactory
from typing import Optional
from common.db.repository import knowledge_metadata_repository
from common.knowledge_base.kb_summary.metadata_chuck import SummaryMetadata
from common.toolbox import get_conf


def summary_kb(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        kb_name: str = Body(default='test.pdf'),
        llm_kwargs: dict = Body(default={'llm_model': 'gpt-3.5-turbo', 'api_key': get_conf('API_KEY')}),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    """
    # 单个知识库文件摘要
    Args:
        knowledge_base_name: 知识库名称
        kb_name: 知识库文件名
        llm_kwargs: 模型参数
        max_tokens: 最大片段
    Returns:
    """
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    summary = SummaryMetadata(llm_kwargs, max_tokens)
    kb_summary = {}
    if kb.exists():
        fragment_result = summary.from_kb_summary_(knowledge_base_name, kb_name)
        for i in fragment_result:
            kb_summary = {
                'code': 0, 'data': i
            }
            yield kb_summary
        yield {'code': -1, 'msg': '没有向量数据'}
    else:
        yield {'code': -1, 'msg': '没有找到知识库'}
    if kb_summary.get('data'):
        summary_infos = json.dumps(kb_summary.update({
            'doc_ids': summary.doc_ids,
            "meta_data": {
                "llm_model": llm_kwargs.get('llm_model'),
                "max_token": max_tokens,
            }
        }))
        knowledge_metadata_repository.add_summary_to_db(kb_name, summary_infos)


def summary_file(
        summary_tag,
        files: list = Body(default=['./text.pdf']),
        llm_kwargs: dict = Body(default={'llm_model': 'gpt-3.5-turbo', 'api_key': get_conf('API_KEY')}),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    """
    Args:
        summary_tag:
        files:
        llm_kwargs:
        max_tokens:
    Returns:
    """
    summary = SummaryMetadata(llm_kwargs, max_tokens)
    fragment_result = summary.from_file_summary_(files)
    kb_summary = {}
    for i in fragment_result:
        kb_summary = {
            'code': 0, 'data': i
        }
        yield
    if kb_summary.get('data'):
        summary_infos = json.dumps(kb_summary.update({
            'doc_ids': 'files',
            "meta_data": {
                "llm_model": llm_kwargs.get('llm_model'),
                "max_token": max_tokens,
            }
        }))
        knowledge_metadata_repository.add_summary_to_db(summary_tag, summary_infos)


def recreate_summary_kb(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        kb_name: str = Body(default='test.pdf'),
        llm_kwargs: dict = Body(default={'llm_model': 'gpt-3.5-turbo', 'api_key': get_conf('API_KEY')}),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    return EventSourceResponse(summary_kb(knowledge_base_name, kb_name, llm_kwargs, max_tokens))


def recreate_summary_file(
        summary_tag,
        files: list = Body(default=['./text.pdf']),
        llm_kwargs: dict = Body(default={'llm_model': 'gpt-3.5-turbo', 'api_key': get_conf('API_KEY')}),
        max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
):
    return EventSourceResponse(summary_file(summary_tag, files, llm_kwargs, max_tokens))


if __name__ == '__main__':
    pass
