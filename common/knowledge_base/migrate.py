from common.api_configs import (
    EMBEDDING_MODEL, DEFAULT_VS_TYPE, ZH_TITLE_ENHANCE,
    CHUNK_SIZE, OVERLAP_SIZE,
    logger, log_verbose, TEXT_SPLITTER_NAME
)
from common.knowledge_base.utils import (
    get_file_path, list_kbs_from_folder,
    list_files_from_folder, files2docs_in_thread,
    KnowledgeFile
)
from common.knowledge_base.kb_service.base import KBServiceFactory

from common.db.base import Base, engine
from common.db.session import session_scope
import os
from dateutil.parser import parse
from typing import Literal, List


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_tables():
    Base.metadata.drop_all(bind=engine)
    create_tables()


def import_from_db(
        sqlite_path: str = None,
        # csv_path: str = None,
) -> bool:
    """
    在知识库与向量库无变化的情况下，从备份数据库中导入数据到 info.db。
    适用于版本升级时，info.db 结构变化，但无需重新向量化的情况。
    请确保两边数据库表名一致，需要导入的字段名一致
    当前仅支持 sqlite
    """
    import sqlite3 as sql
    from pprint import pprint

    models = list(Base.registry.mappers)

    try:
        con = sql.connect(sqlite_path)
        con.row_factory = sql.Row
        cur = con.cursor()
        tables = [x["name"] for x in cur.execute("select name from sqlite_master where type='table'").fetchall()]
        for model in models:
            table = model.local_table.fullname
            if table not in tables:
                continue
            print(f"processing table: {table}")
            with session_scope() as session:
                for row in cur.execute(f"select * from {table}").fetchall():
                    data = {k: row[k] for k in row.keys() if k in model.columns}
                    if "create_time" in data:
                        data["create_time"] = parse(data["create_time"])
                    pprint(data)
                    session.add(model.class_(**data))
        con.close()
        return True
    except Exception as e:
        print(f"无法读取备份数据库：{sqlite_path}。错误信息：{e}")
        return False


def file_to_kbfile(kb_name: str, files: List[str], text_splitter_name) -> List[KnowledgeFile]:
    kb_files = []
    for file in files:
        try:
            kb_file = KnowledgeFile(filename=file, knowledge_base_name=kb_name,
                                    text_splitter_name=text_splitter_name)
            kb_files.append(kb_file)
        except Exception as e:
            msg = f"{e}，已跳过"
            logger.error(f'{e.__class__.__name__}: {msg}',
                         exc_info=e if log_verbose else None)
    return kb_files


def folder2db(
        kb_names: List[str],
        mode: Literal["recreate_vs", "update_in_db", "increment"],
        vs_type: Literal["faiss", "milvus", "pg", "chromadb"] = DEFAULT_VS_TYPE,
        embed_model: str = EMBEDDING_MODEL,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        loader_enhance: list = ZH_TITLE_ENHANCE,
        text_splitter_name: str = TEXT_SPLITTER_NAME
):
    """
    use existed files in local folder to populate database and/or vector store.
    set parameter `mode` to:
        recreate_vs: recreate all vector store and fill info to database using existed files in local folder
        fill_info_only(disabled): do not create vector store, fill info to db using existed files only
        update_in_db: update vector store and database info using local files that existed in database only
        increment: create vector store and database info for local files that not existed in database only
    """

    def files2vs(kb_name: str, kb_files: List[KnowledgeFile]):
        for success, result in files2docs_in_thread(kb_files,
                                                    chunk_size=chunk_size,
                                                    chunk_overlap=chunk_overlap,
                                                    loader_enhance=loader_enhance):
            if success:
                _, filename, docs = result
                print(f"正在将 {kb_name}/{filename} 添加到向量库，共包含{len(docs)}条文档")
                kb_file = KnowledgeFile(filename=filename, knowledge_base_name=kb_name,
                                        text_splitter_name=text_splitter_name, loader_enhance=loader_enhance)
                kb_file.splited_docs = docs
                kb.add_doc(kb_file=kb_file, not_refresh_vs_cache=True)
            else:
                print(result)

    kb_names = kb_names or list_kbs_from_folder()
    for kb_name in kb_names:
        kb = KBServiceFactory.get_service(kb_name, vs_type, embed_model)
        if not kb.exists():
            kb.create_kb()

        # 清除向量库，从本地文件重建
        if mode == "recreate_vs":
            kb.clear_vs()
            kb.create_kb()
            kb_files = file_to_kbfile(kb_name, list_files_from_folder(kb_name), text_splitter_name)
            files2vs(kb_name, kb_files)
            kb.save_vector_store()
        # # 不做文件内容的向量化，仅将文件元信息存到数据库
        # # 由于现在数据库存了很多与文本切分相关的信息，单纯存储文件信息意义不大，该功能取消。
        # elif mode == "fill_info_only":
        #     files = list_files_from_folder(kb_name)
        #     kb_files = file_to_kbfile(kb_name, files)
        #     for kb_file in kb_files:
        #         add_file_to_db(kb_file)
        #         print(f"已将 {kb_name}/{kb_file.filename} 添加到数据库")
        # 以数据库中文件列表为基准，利用本地文件更新向量库
        elif mode == "update_in_db":
            files = kb.list_files()
            kb_files = file_to_kbfile(kb_name, files, text_splitter_name)
            files2vs(kb_name, kb_files)
            kb.save_vector_store()
        # 对比本地目录与数据库中的文件列表，进行增量向量化
        elif mode == "increment":
            db_files = kb.list_files()
            folder_files = list_files_from_folder(kb_name)
            files = list(set(folder_files) - set(db_files))
            kb_files = file_to_kbfile(kb_name, files, text_splitter_name)
            files2vs(kb_name, kb_files)
            kb.save_vector_store()
        else:
            print(f"unsupported migrate mode: {mode}")


def prune_db_docs(kb_names: List[str]):
    """
    delete docs in database that not existed in local folder.
    it is used to delete database docs after user deleted some doc files in file browser
    """
    for kb_name in kb_names:
        kb = KBServiceFactory.get_service_by_name(kb_name)
        if kb is not None:
            files_in_db = kb.list_files()
            files_in_folder = list_files_from_folder(kb_name)
            files = list(set(files_in_db) - set(files_in_folder))
            kb_files = file_to_kbfile(kb_name, files)
            for kb_file in kb_files:
                kb.delete_doc(kb_file, not_refresh_vs_cache=True)
                print(f"success to delete docs for file: {kb_name}/{kb_file.filename}")
            kb.save_vector_store()


def prune_folder_files(kb_names: List[str]):
    """
    delete doc files in local folder that not existed in database.
    it is used to free local disk space by delete unused doc files.
    """
    for kb_name in kb_names:
        kb = KBServiceFactory.get_service_by_name(kb_name)
        if kb is not None:
            files_in_db = kb.list_files()
            files_in_folder = list_files_from_folder(kb_name)
            files = list(set(files_in_folder) - set(files_in_db))
            for file in files:
                os.remove(get_file_path(kb_name, file))
                print(f"success to delete file: {kb_name}/{file}")
