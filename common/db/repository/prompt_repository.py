import json
import os

from common.db.session import session_scope
from common.logger_handler import logger
from common.path_handler import init_path
from sqlalchemy.orm import Query
from sqlalchemy import desc, and_, or_
from common.db.models.prompt_model import PromptModel, func

# 管理员账户，无条件的开放和访问PromptModel
_sys = ['spike', '127.0.0.1', None]


def _read_user_auth(source):
    return or_(PromptModel.source == source, source in _sys, PromptModel.source.in_(_sys))


def add_prompt(in_class, name, value, source):
    old_prompt = query_prompt(name, in_class, source)
    if old_prompt:
        if update_prompt(in_class, name, value, source, old_prompt):
            return True, f'更新[{name}]提示词成功'
    elif not old_prompt:
        with session_scope() as session:
            prompt = PromptModel(name=name, value=value, in_class=in_class, source=source)
            session.add(prompt)
        return True, f'插入[{name}]提示词成功'
    logger.warning(f'无法完成写入【{name}】提示词')
    return False, f'无法完成写入【{name}】提示词'


def batch_import_prompt_list(data_list: list, in_class, source=None):
    with session_scope() as session:
        for i in data_list:
            if i.get('source'):
                source = i.get('source')
            elif source:
                source = source
            else:
                source = 'spike'
            p = PromptModel(name=i['act'], value=i['prompt'], in_class=in_class, source=source)
            prompt_ = query_prompt(name=i['act'], in_class=in_class, source=source)
            if prompt_:
                update_prompt(name=i['act'], value=i['prompt'], in_class=in_class, source=source, old_prompt=prompt_)
                logger.warning(f"【{in_class}】分类更新`{i['act']}` 提示词")
            else:
                session.add(p)


def batch_import_prompt_dir():
    json_path = init_path.prompt_export_path
    for json_ in os.listdir(json_path):
        with open(os.path.join(json_path, json_), 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        in_class = os.path.basename(os.path.join(json_path, json_)).split('.')[0]
        batch_import_prompt_list(data_list, in_class)


def batch_export_path():
    prompt_all = get_all_prompt()
    file_dict = {}
    for prompt in prompt_all:
        if not file_dict.get(prompt.in_class):
            file_dict[prompt.in_class] = []
        file_dict[prompt.in_class].append(
            {
                "act": prompt.name,
                "prompt": prompt.value,
                "source": prompt.source
            }
        )
    for source in file_dict:
        with open(os.path.join(init_path.prompt_export_path, f"{source}.json"), mode='w', encoding='utf-8') as f:
            f.write(json.dumps(file_dict, indent=4, ensure_ascii=False))
            print(f'{source}已导出', os.path.join(init_path.prompt_export_path, f"{source}.json"))


def query_prompt(name, in_class, source=None, quote_num: bool = None) -> PromptModel | None:
    with session_scope() as session:
        prompt_query: Query = session.query(PromptModel).filter(
            and_(
                PromptModel.name == name,
                PromptModel.in_class == in_class,
                _read_user_auth(source)
            )
        )
        prompt: PromptModel = prompt_query.order_by(desc(PromptModel.update_time)).first()
        if prompt and quote_num:
            prompt.quote_num += 1
        return prompt


def update_prompt(in_class, name, value, source, old_prompt: PromptModel):
    if old_prompt.source == source or source in _sys:
        old_prompt.in_class = in_class
        old_prompt.name = name
        old_prompt.value = value
        old_prompt.update_time = func.now()
        with session_scope() as session:
            session.add(old_prompt)
            logger.info(f'`{source}`成功更新【{name}】提示词')
        return True
    else:
        logger.info(f'`{source}`无法【{name}】提示词, 因为该提示词属于`{old_prompt.source}`')
        return False


def deleted_prompt(name, in_class, source):
    prompt = query_prompt(name, in_class, source)
    if prompt:
        if prompt.source == source or source in _sys:
            with session_scope() as session:
                session.delete(prompt)
                return True, '删除成功'
        return False, '无法删除不属于你的提示词'
    return False, '提示词不存在'


def get_all_prompt():
    with session_scope() as session:
        prompt_all = session.query(PromptModel).all()
        return prompt_all


def __for_get_dict(p, prompt_dict):
    if not prompt_dict.get(p.in_class):
        prompt_dict[p.in_class] = {}
    prompt_dict[p.in_class].update({p.name: p.value})


def get_all_prompt_dict():
    prompt = get_all_prompt()
    prompt_dict = {}
    for p in prompt:
        __for_get_dict(p, prompt_dict)
    return prompt_dict


def get_user_prompt_dict(user):
    prompt_dict = {}
    with session_scope() as session:
        prompt_all: Query = session.query(PromptModel).filter(PromptModel.source == user)
        for p in prompt_all.all():
            __for_get_dict(p, prompt_dict)
    return prompt_dict


def get_class_prompt_dict(in_class):
    prompt_dict = {}
    with session_scope() as session:
        prompt_all: Query = session.query(PromptModel).filter(PromptModel.in_class == in_class)
        for p in prompt_all.all():
            __for_get_dict(p, prompt_dict)
    return prompt_dict


def get_all_class():
    with session_scope() as session:
        prompt_all = session.query(PromptModel.in_class).distinct().all()
        class_list = [record[0] for record in prompt_all]
        return class_list


if __name__ == '__main__':
    from common.db.base import Base, engine
    Base.metadata.create_all(bind=engine)
    batch_export_path()

