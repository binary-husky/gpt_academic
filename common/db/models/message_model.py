from sqlalchemy import Column, Integer, String, DateTime, JSON, func

from common.db.base import Base


class MessageModel(Base):
    """
    聊天记录模型
    """
    __tablename__ = 'message'
    id = Column(String(32), primary_key=True, comment='聊天记录ID')
    conversation_id = Column(String(32), default=None, index=True, comment='对话框ID')
    # chat/agent_chat等
    chat_type = Column(String(50), comment='聊天类型')
    query = Column(String(4096), comment='用户问题')
    response = Column(String(4096), comment='模型回答')
    # 记录知识库id等，以便后续扩展
    meta_data = Column(JSON, default={})
    # 满分100 越高表示评价越好
    feedback_score = Column(Integer, default=-1, comment='用户评分')
    feedback_reason = Column(String(255), default="", comment='用户评分理由')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<message(id='{self.id}', conversation_id='{self.conversation_id}', chat_type='{self.chat_type}', query='{self.query}', response='{self.response}',meta_data='{self.meta_data}',feedback_score='{self.feedback_score}',feedback_reason='{self.feedback_reason}', create_time='{self.create_time}')>"
