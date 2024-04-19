from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer


class BaseModel:
    """
    基础模型
    """
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    create_time = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    update_time = Column(DateTime, default=None, onupdate=datetime.utcnow, comment="更新时间")
    create_by = Column(String, default=None, comment="创建者")
    update_by = Column(String, default=None, comment="更新者")
