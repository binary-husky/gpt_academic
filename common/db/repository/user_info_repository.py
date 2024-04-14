from common.db.session import session_scope
from sqlalchemy.orm import Query
from common.db.models.user_info_model import UserInfoModel


def add_user_info(user_name, pass_word):
    with session_scope() as session:
        user_info = UserInfoModel(user_name, pass_word)
        session.add(user_info)


def get_user_info(user_name) -> UserInfoModel | None:
    with session_scope() as session:
        user: Query = session.query(UserInfoModel).filter(UserInfoModel.user_name == user_name)
        return user.first()