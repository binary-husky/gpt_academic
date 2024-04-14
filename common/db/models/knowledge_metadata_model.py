from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, func

from common.db.base import Base


class SummaryChunkModel(Base):

    __tablename__ = 'summary_metadata'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    kb_name = Column(String(50), comment='知识库名称')
    summary_context = Column(String(255), comment='总结文本')
    fragment_name = Column(String(255), comment='所属片段名称')
    doc_ids = Column(String(1024), comment="向量库id关联列表")
    meta_data = Column(JSON, default={})


    def __repr__(self):
        return (f"<SummaryChunk(id='{self.id}', kb_name='{self.kb_name}', summary_context='{self.summary_context}',"
                f"fragment_name='{self.fragment_name}', doc_ids='{self.doc_ids}', meta_data='{self.meta_data}')>")
