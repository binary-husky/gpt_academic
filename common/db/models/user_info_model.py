from sqlalchemy import Column, Integer, String, DateTime, JSON, func, BLOB
from common.db.base import Base


class UserInfoModel(Base):
    """
    用户信息模型
    """
    __tablename__ = 'user_info'
    id = Column(String(32), primary_key=True, autoincrement=True, comment='用户ID')
    user_name = Column(String(50), comment='用户名称')
    pass_word = Column(String(50), comment='用户密码')
    email = Column(String(50), comment='绑定邮箱地址')
    avatar_img = Column(BLOB(), comment='用户头像')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return (f"<UserInfo(id='{self.id}', user_name='{self.user_name}', pass_word='{self.pass_word}',"
                f"email='{self.email}', avatar_img='{self.avatar_img}'"
                f"create_time='{self.create_time}')>")
