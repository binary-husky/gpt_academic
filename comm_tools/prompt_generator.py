#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import json
import os.path
import sqlite3
import functools
from comm_tools import func_box
# 连接到数据库



def connect_db_close(cls_method):
    @functools.wraps(cls_method)
    def wrapper(cls=None, *args, **kwargs):
        cls._connect_db()
        result = cls_method(cls, *args, **kwargs)
        cls._close_db()
        return result
    return wrapper


class SqliteHandle:
    def __init__(self, table='ai_common', database='ai_prompt.db'):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.prompt_path = os.path.join(self.base_path, 'users_data')
        self.__database = database
        self.__connect = sqlite3.connect(os.path.join(self.prompt_path, self.__database))
        self.__cursor = self.__connect.cursor()
        self.__table = table
        if self.__table not in self.get_tables():
            self.create_tab()

    def new_connect_db(self):
        """多线程操作时，每个线程新建独立的connect"""
        self.__connect = sqlite3.connect(os.path.join(self.prompt_path, self.__database))
        self.__cursor = self.__connect.cursor()

    def new_close_db(self):
        self.__cursor.close()
        self.__connect.close()

    def create_tab(self):
        self.__cursor.execute(f"CREATE TABLE `{self.__table}` ('prompt' TEXT UNIQUE, 'result' TEXT, 'source' TEXT)")

    def get_tables(self):
        all_tab = []
        result = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        for tab in result:
            all_tab.append(tab[0])
        return all_tab

    def get_prompt_value(self, find=None):
        temp_all = {}
        source = ''
        if find:
            result = self.__cursor.execute(f"SELECT prompt, result, source FROM `{self.__table}` WHERE prompt LIKE '%{find}%'").fetchall()
        else:
            result = self.__cursor.execute(f"SELECT prompt, result, source FROM `{self.__table}`").fetchall()
        for row in result:
            temp_all[row[0]] = row[1]
            source = row[2]
        return temp_all, source

    def query_table_columns(self):
        result = self.__cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='table' AND name='{self.__table}';").fetchall()
        return result

    def add_colum_type(self, colum, type='TEXT'):
        self.__cursor.execute(f"ALTER TABLE `{self.__table}` ADD COLUMN {colum} {type};")
        self.__connect.commit()

    def inset_prompt(self, prompt: dict, source=''):
        error_status = ''
        for key in prompt:
            _, user_info = self.get_prompt_value(key)
            if user_info in source:
                self.__cursor.execute(f"REPLACE INTO `{self.__table}` (prompt, result, source)"
                                      f"VALUES (?, ?, ?);", (str(key), str(prompt[key]), source))
            else:
                error_status += f'【{key}】该分类下已有其他人保存重名的提示词，请更改提示词名称后再提交～'
                print(f'{source} 保存名称为[key]的提示词失败，因为该分类下已有其他人保存重名的提示词')
        self.__connect.commit()
        return error_status

    def delete_prompt(self, name):
        self.__cursor.execute(f"DELETE from `{self.__table}` where prompt LIKE '{name}'")
        self.__connect.commit()

    def delete_tabls(self, tab):
        self.__cursor.execute(f"DROP TABLE `{tab}`;")
        self.__connect.commit()

    def find_prompt_result(self, name, tabs='prompt_127.0.0.1'):
        query = self.__cursor.execute(f"SELECT result FROM `{self.__table}` WHERE prompt LIKE '{name}'").fetchall()
        if query == []:
            query = self.__cursor.execute(f"SELECT result FROM `{tabs}` WHERE prompt LIKE '{name}'").fetchall()
            return query[0][0]
        else:
            return query[0][0]

def cp_db_data(incloud_tab='prompt'):
    sql_ll = sqlite_handle(database='ai_prompt_cp.db')
    tabs = sql_ll.get_tables()
    for i in tabs:
        if str(i).startswith(incloud_tab):
            old_data = sqlite_handle(table=i, database='ai_prompt_cp.db').get_prompt_value()
            sqlite_handle(table=i).inset_prompt(old_data)

def batch_inset_prompt(json_path, tables):
    sql_handle = sqlite_handle(table=tables)
    data_list = func_box.JsonHandle(json_path).load()
    for i in data_list:
        source = os.path.basename(json_path).split('.')[0]
        sql_handle.inset_prompt(prompt={i['act']: i['prompt']}, source=source)

def batch_add_source():
    sql_ll = sqlite_handle(database='ai_prompt.db')
    tabs = sql_ll.get_tables()
    for t in tabs:
        sqlite_handle(table=t).add_colum_type('source')

def batch_export_prompt(incloud_tab='prompt'):
    sql_ll = sqlite_handle(database='ai_prompt.db')
    tabs = sql_ll.get_tables()
    for i in tabs:
        if str(i).startswith(incloud_tab):
            source = i.split('_')[-1]
            result = sqlite_handle(i).get_prompt_value()
            file_dict = []
            for k in result:
                file_dict.append({'act': k, 'prompt': result[k]})
            if file_dict:
                file_path = os.path.join(func_box.prompt_path, 'export_prompt')
                os.makedirs(file_path, exist_ok=True)
                with open(os.path.join(file_path, f"{source}.json"), mode='w', encoding='utf-8') as f:
                    f.write(json.dumps(file_dict, ensure_ascii=False))
                    print(f'{source}已导出', os.path.join(file_path, f"{source}.json"))

sqlite_handle = SqliteHandle
if __name__ == '__main__':
    sqlite_handle().delete_tabls('prompt_新建分类_sys')