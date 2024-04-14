from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from common.db.base import Base


class PromptModel(Base):
    """
    提示词模型
    """
    __tablename__ = 'prompt'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='提示词ID')
    name = Column(String(50), comment='提示词名称')
    value = Column(String(4096), comment='提示词内容')
    in_class = Column(String(100), comment='提示词分类')
    source = Column(String(100), default='spike', comment='所属用户, spike、127.0.0.1 为默认管理员，拥有最高权限')
    quote_num = Column(Integer, default=0, comment='引用次数')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), comment='更新时间')

    def __repr__(self):
        return (f"<Prompt(id='{self.id}', "
                f"name='{self.name}', value='{self.value}', "
                f"in_class='{self.in_class}', source='{self.source}', "
                f"quote_num='{self.quote_num}', create_time='{self.create_time}, "
                f"update_time='{self.update_time}')>")
