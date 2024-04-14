# encoding: utf-8
# @Time   : 2024/4/14
# @Author : Spike
# @Descr   :
from datetime import datetime, timedelta

from common.db.session import session_scope
from common.logger_handler import logger
from common.path_handler import init_path
from sqlalchemy.orm import Query
from sqlalchemy import desc, and_, or_
from common.db.models.cache_model import CacheModel


def add_cache(key, result, source):
    with session_scope() as session:
        c = CacheModel(key=key, result=result, source=source)
        session.add(c)


def get_cache(key):
    with session_scope() as session:
        cache_query: Query = session.query(CacheModel).filter(and_(
            CacheModel.key == key, CacheModel.status == 0,
            # CacheModel.source == source  # 这个就不做管理员限制
        ))
        cache: CacheModel = cache_query.order_by(desc(CacheModel.update_time)).first()
        if cache:
            if cache.update_time < datetime.utcnow() - timedelta(days=10):  # 10天过期
                cache.status = 99
                session.add(cache)
                return False
            return cache.result
        return False


def disabled_source_cache(source):
    with session_scope() as session:
        cache_query: Query = session.query(CacheModel).filter_by(source=source, status=0)
        cache_query.update({CacheModel.status: -1})
        logger.info(f'【{source}】失效所有缓存数据')


if __name__ == '__main__':
    # from common.db.base import Base, engine
    # Base.metadata.create_all(bind=engine)
    # add_cache('tetafa', '12431231', '141412412411412421')
    print(disabled_source_cache('141412412411412421'))