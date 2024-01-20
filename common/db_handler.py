# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import json
import os.path
import shutil
import sqlite3
import psutil
from common.path_handler import init_path
from pydantic import BaseModel, FilePath
from typing import Dict, AnyStr, Union


def ipaddr():
    # 获取本地ipx
    ip = psutil.net_if_addrs()
    for i in ip:
        if ip[i][0][3]:
            return ip[i][0][1]
    return '127.0.0.1'


class Database(BaseModel):
    """
    Args:
        database: 指定的数据库目录
        table： 链接的表
    """
    database: Union[str, FilePath]
    table: AnyStr | None = None


class SqliteHandler:
    def __init__(self, config: Database):
        self.database = config.database
        self.table = config.table
        self.__connect = sqlite3.connect(self.database)
        self.__cursor = self.__connect.cursor()

    def get_tables(self):
        all_tab = []
        result = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        for tab in result:
            all_tab.append(tab[0])
        return all_tab

    def get_table_columns(self):
        result = self.__cursor.execute(
            f"SELECT name, sql FROM sqlite_master WHERE type='table' AND name='{self.table}';").fetchall()
        return result

    def execute_query(self, query: AnyStr):
        # 获取查询结果并返回
        self.__cursor.execute(query)
        result = self.__cursor.fetchall()
        return result

    def execute_dml_tcl(self, query: AnyStr):
        """创建ddl : 增删改查操作语句 执行tcl: 事务控制语句"""
        self.__cursor.execute(query)
        self.__connect.commit()

    def execute_ddl_create(self, create: AnyStr):
        if create.upper().strip().startswith('CREATE'):
            self.__cursor.execute(create)

    def execute_ddl_delete(self, delete):
        if delete.upper().strip().startswith('DROP'):
            self.__cursor.execute(delete)
            self.__cursor.execute('VACUUM;')
            self.__connect.commit()

    def func_rename_tables(self, old, new):
        self.__cursor.execute(f"ALTER TABLE `{old}` RENAME TO `{new}`;")
        self.__connect.commit()


class PromptDb(SqliteHandler):

    def __init__(self, table):
        self.database_path = os.path.join(init_path.private_db_path, 'prompt.db')
        date_base = Database(database=self.database_path, table=table)
        super().__init__(date_base)
        if self.table and self.table not in self.get_tables():
            # 如果访问的表不存在，则创建表
            create_sql = f"CREATE TABLE `{self.table}` ('prompt' TEXT UNIQUE, 'result' TEXT, 'source' TEXT)"
            self.execute_ddl_create(create_sql)

    def get_prompt_value(self, find=None):
        temp_all = {}
        source = ''
        if find:
            result = self.execute_query(f"SELECT prompt, result, source FROM `{self.table}` WHERE prompt LIKE ? (f"%{find}%",)")
        else:
            result = self.execute_query(f"SELECT prompt, result, source FROM `{self.table}`")
        for row in result:
            temp_all[row[0]] = row[1]
            source = row[2]
        return temp_all, source

    def get_prompt_value_temp(self):
        temp_all = {}
        result = self.execute_query(f"SELECT prompt, result FROM `{self.table}`")
        for row in result:
            temp_all[row[0]] = row[1]
        return temp_all

    def find_prompt_result(self, name, individual_priority=False):
        query = []
        if individual_priority:
            try:
                query = f"SELECT result FROM `prompt_{individual_priority}` WHERE prompt LIKE '{name}'"
                self.execute_query(query)
            except:
                pass
        if not query:
            query = f"SELECT result FROM `{self.table}` WHERE prompt LIKE '{name}'"
            self.execute_query(query)
            return query[0][0]
        else:
            return query[0][0]

    def inset_prompt(self, prompt: dict, source=''):
        error_status = ''
        for key in prompt:
            _, user_info = self.get_prompt_value(key)
            if not user_info:
                user_info = source  # 增加保障
            if source in user_info or not user_info or '127.0.0.1' == source or 'spike' == source:
                replace = f"""
                            REPLACE INTO `{self.table}` (prompt, result, source)
                            VALUES ('{key}', '{prompt[key]}', '{user_info}')
                          """
                self.execute_dml_tcl(replace)
            else:
                error_status += f'【{key}】权限不足，该分类下已有其他人保存重名的提示词，请更改提示词名称后再提交～'
                print(f'{source} 保存名称为[key]的提示词失败，因为该分类下已有其他人保存重名的提示词')
        return error_status

    def delete_prompt(self, name):
        self.execute_ddl_delete(f"DELETE from `{self.table}` where prompt = '{name}'")

    def update_value(self, new_source):
        query = f"UPDATE {self.table} SET source=source || ' ' || '{new_source}'"
        self.execute_dml_tcl(query)


class OcrCacheDb(SqliteHandler):

    def __init__(self):
        self.database_path = os.path.join(init_path.private_db_path, 'ocr_cache.db')
        date_base = Database(database=self.database_path, table='data_results')
        super().__init__(date_base)
        if self.table not in self.get_tables():
            # 如果访问的表不存在，则创建表
            create_sql = f"""
            CREATE TABLE `{self.table}` 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 'tag' TEXT UNIQUE, 'result' TEXT)
            """
            self.execute_ddl_create(create_sql)

    def get_cashed(self, tag):
        result = self.execute_query(f"SELECT result FROM `{self.table}` WHERE tag = '{tag}'")
        if result:
            return result[0][0]
        else:
            return None

    def get_map_cashed(self, tag_dict: Dict):
        result = {}
        for tag in tag_dict:
            result[tag] = self.get_cashed(tag)
        return result

    def update_cashed(self, tag, result):
        self.execute_dml_tcl(f"REPLACE INTO `{self.table}` (tag, result) VALUES ('{tag}', '{result}')")


class UserDb(SqliteHandler):

    def __init__(self):
        self.database_path = os.path.join(init_path.private_db_path, 'user_data.db')
        date_base = Database(database=self.database_path, table='user_info')
        super().__init__(date_base)
        if self.table not in self.get_tables():
            # 如果访问的表不存在，则创建表
            create_sql = f"""
            CREATE TABLE  `{self.table}` (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                avatar BLOB
            );
            """
            self.execute_ddl_create(create_sql)

    def get_user_account(self, user):
        user_account = {}
        query = f"SELECT username, password FROM `{self.table}` WHERE `username` = '{user}'"
        result = self.execute_query(query)
        for row in result:
            user_account['user'] = row[0]
            user_account['password'] = row[1]
        return user_account

    def update_user(self, username, password):
        self.execute_dml_tcl(f"REPLACE INTO `{self.table}` (username, username) VALUES ('{username}', '{password}')")


class DatabaseSqlite:
    #  废弃的东西
    def __init__(self, table='ai_common', database='ai_private.db', auto=True):
        ...


def __prompt_database_rename():
    db_obj = PromptDb(table=None)
    shutil.copy(db_obj.database_path, db_obj.database_path+'.backups')
    for tab in db_obj.get_tables():
        if tab.startswith('prompt_'):
            new_tab = tab.replace("prompt_", "")
            print(f'{tab} rename to `{new_tab}`')
            db_obj.func_rename_tables(tab, new_tab)
    print(db_obj.get_tables())


def __batch_inset_prompt(json_path=None):
    if not json_path:
        json_path = init_path.prompt_export_path
    for json_ in os.listdir(json_path):
        with open(os.path.join(json_path, json_), 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        for i in data_list:
            source = os.path.basename(os.path.join(json_path, json_)).split('.')[0]
            source_addr = 'spike'  # 嘻嘻，加上管理员权限
            PromptDb(table=f"{source}_sys").inset_prompt(prompt={i['act']: i['prompt']}, source=source_addr)


def __batch_export_prompt():
    sql_ll = PromptDb(table=None)
    tabs_list = sql_ll.get_tables()
    for i in tabs_list:
        if str(i).endswith('sys'):
            source = i.split('_')[0]
            result = PromptDb(table=i).get_prompt_value_temp()
            file_dict = []
            for k in result:
                file_dict.append({'act': k, 'prompt': result[k]})
            with open(os.path.join(init_path.prompt_export_path, f"{source}.json"), mode='w', encoding='utf-8') as f:
                f.write(json.dumps(file_dict, indent=4, ensure_ascii=False))
                print(f'{source}已导出', os.path.join(init_path.prompt_export_path, f"{source}.json"))


def main_argument():
    import argparse
    parser = argparse.ArgumentParser(description='数据库命令行操作')
    parser.add_argument('--export', action='store_true', help='导出提示词')
    parser.add_argument('--imports', action='store_true', help='导入提示词')
    parser.add_argument('--init_name', action='store_true', help='迁移初始化，这个给@spike用的')
    args = parser.parse_args()
    if args.export:
        # 执行导出操作
        __batch_export_prompt()
    elif args.imports:
        # 执行导入操作
        __batch_inset_prompt()
    elif args.init_name:
        # 执行迁移初始化操作
        __prompt_database_rename()
    else:
        # 如果没有输入任何参数，则显示可选参数和帮助信息
        parser.print_help()


if __name__ == '__main__':
    main_argument()
    # prompt_database_rename()

