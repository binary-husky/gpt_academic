#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
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
        self.__cursor.execute(f"CREATE TABLE `{self.__table}` ('prompt' TEXT UNIQUE, 'result' TEXT)")

    def get_tables(self):
        all_tab = []
        result = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        for tab in result:
            all_tab.append(tab[0])
        return all_tab

    def get_prompt_value(self, find=None):
        temp_all = {}
        if find:
            result = self.__cursor.execute(f"SELECT prompt, result FROM `{self.__table}` WHERE prompt LIKE '%{find}%'").fetchall()
        else:
            result = self.__cursor.execute(f"SELECT prompt, result FROM `{self.__table}`").fetchall()
        for row in result:
            temp_all[row[0]] = row[1]
        return temp_all

    def inset_prompt(self, prompt: dict):
        for key in prompt:
            self.__cursor.execute(f"REPLACE INTO `{self.__table}` (prompt, result) VALUES (?, ?);", (str(key), str(prompt[key])))
        self.__connect.commit()

    def delete_prompt(self, name):
        self.__cursor.execute(f"DELETE from `{self.__table}` where prompt LIKE '{name}'")
        self.__connect.commit()

    def delete_tabls(self, tab):
        self.__cursor.execute(f"DROP TABLE `{tab}`;")
        self.__connect.commit()

    def find_prompt_result(self, name):
        query = self.__cursor.execute(f"SELECT result FROM `{self.__table}` WHERE prompt LIKE '{name}'").fetchall()
        if query == []:
            query = self.__cursor.execute(f"SELECT result FROM `prompt_127.0.0.1` WHERE prompt LIKE '{name}'").fetchall()
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

def inset_127_prompt():
    sql_handle = sqlite_handle(table='prompt_127.0.0.1')
    prompt_json = os.path.join(sql_handle.prompt_path, 'prompts-PlexPt.json')
    data_list = func_box.JsonHandle(prompt_json).load()
    for i in data_list:
        sql_handle.inset_prompt(prompt={i['act']: i['prompt']})

sqlite_handle = SqliteHandle
if __name__ == '__main__':
    cp_db_data()