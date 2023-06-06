#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import os.path
import sqlite3
import threading
import functools
import func_box
# 连接到数据库
base_path = os.path.dirname(__file__)
prompt_path = os.path.join(base_path, 'prompt_users')


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
        self.__database = database
        self.__connect = sqlite3.connect(os.path.join(prompt_path, self.__database))
        self.__cursor = self.__connect.cursor()
        self.__table = table
        if self.__table not in self.get_tables():
            self.create_tab()

    def new_connect_db(self):
        """多线程操作时，每个线程新建独立的connect"""
        self.__connect = sqlite3.connect(os.path.join(prompt_path, self.__database))
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

    def delete_prompt(self):
        self.__cursor.execute(f"DELETE from `{self.__table}` where id BETWEEN 1 AND 21")
        self.__connect.commit()

sqlite_handle = SqliteHandle
if __name__ == '__main__':
    sql_ll = sqlite_handle(database='ai_prompt_cp.db')
    tabs = sql_ll.get_tables()
    for i in tabs:
        old_data = sqlite_handle(table=i, database='ai_prompt_cp.db').get_prompt_value()
        sqlite_handle(table=i).inset_prompt(old_data)
