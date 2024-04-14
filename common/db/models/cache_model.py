# encoding: utf-8
# @Time   : 2024/4/14
# @Author : Spike
# @Descr   :
from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from common.db.base import Base


class CacheModel(Base):
    """
    缓存模型
    """
    __tablename__ = 'cache'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='缓存ID')
    key = Column(String(1024), comment='缓存key，用于提取缓存内容')
    result = Column(String(1024 * 8), comment='缓存内容')
    source = Column(String(100), default='spike', comment='所属用户, spike、127.0.0.1 为默认管理员，拥有最高权限，在缓存中没屁用')
    status = Column(Integer, default=0, comment='缓存状态, -1失效, 0启用, 99过期')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')
    update_time = Column(DateTime, default=func.now(), comment='更新时间')

    def __repr__(self):
        return (f"<Cache(id='{self.id}', key='{self.key}', result='{self.result}',"
                f"source='{self.source}', status='{self.status}',"
                f"create_time='{self.create_time}', update_time='{self.update_time}')>")
