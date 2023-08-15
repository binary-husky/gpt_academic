#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import json
import os.path
import sqlite3
import functools
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
            result = self.__cursor.execute(f"SELECT prompt, result, source FROM `{self.__table}` WHERE prompt LIKE ?",
                                           (f"%{find}%",)).fetchall()
        else:
            result = self.__cursor.execute(f"SELECT prompt, result, source FROM `{self.__table}`").fetchall()
        for row in result:
            temp_all[row[0]] = row[1]
            source = row[2]
        return temp_all, source

    def get_prompt_value_temp(self):
        temp_all = {}
        ss = self.__table
        result = self.__cursor.execute(f"SELECT prompt, result FROM `{self.__table}`").fetchall()
        for row in result:
            temp_all[row[0]] = row[1]
        return temp_all

    def query_table_columns(self):
        result = self.__cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='table' AND name='{self.__table}';").fetchall()
        return result

    def add_column_type(self, column, column_type='TEXT'):
        # 检查要添加的列是否已存在
        existing_columns = self.__cursor.execute(f"PRAGMA table_info(`{self.__table}`)").fetchall()
        existing_column_names = [column[1] for column in existing_columns]
        if column not in existing_column_names:
            # 执行添加列的操作
            self.__cursor.execute(f"ALTER TABLE `{self.__table}` ADD COLUMN {column} {column_type};")
            self.__connect.commit()

    def inset_prompt(self, prompt: dict, source=''):
        error_status = ''
        for key in prompt:
            _, user_info = self.get_prompt_value(key)
            if not user_info: user_info = ''  # 增加保障
            if source in user_info or not user_info:
                self.__cursor.execute(f"REPLACE INTO `{self.__table}` (prompt, result, source)"
                                      f"VALUES (?, ?, ?);", (str(key), str(prompt[key]), user_info))
            else:
                error_status += f'【{key}】权限不足，该分类下已有其他人保存重名的提示词，请更改提示词名称后再提交～'
                print(f'{source} 保存名称为[key]的提示词失败，因为该分类下已有其他人保存重名的提示词')
        self.__connect.commit()
        return error_status

    def delete_prompt(self, name):
        self.__cursor.execute(f"DELETE from `{self.__table}` where prompt LIKE '{name}'")
        self.__connect.commit()

    def delete_tables(self, tab):
        self.__cursor.execute(f"DROP TABLE `{tab}`;")
        self.__connect.commit()

    def rename_tables(self, old, new):
        self.__cursor.execute(f"ALTER TABLE `{old}` RENAME TO `{new}`;")
        self.__connect.commit()

    def find_prompt_result(self, name, individual_priority=False):
        query = []
        if individual_priority:
            query = self.__cursor.execute(f"SELECT result FROM `prompt_{individual_priority}` WHERE prompt LIKE '{name}'").fetchall()
        if not query:
            query = self.__cursor.execute(f"SELECT result FROM `{self.__table}` WHERE prompt LIKE '{name}'").fetchall()
            return query[0][0]
        else:
            return query[0][0]

    def update_value(self, new_source):
        query = f"UPDATE {self.__table} SET source=source || ' ' || ?"
        self.__cursor.execute(query, (new_source,))
        self.__connect.commit()


def cp_db_data(incloud_tab='prompt_'):
    sql_ll = sqlite_handle(database='ai_prompt_cp.db')
    tabs = sql_ll.get_tables()
    for i in tabs:
        if str(i).startswith(incloud_tab):
            old_data = sqlite_handle(table=i, database='ai_prompt_cp.db').get_prompt_value_temp()
            source = str(i).replace(incloud_tab, '')
            sqlite_handle(table=i).inset_prompt(old_data, source)


def batch_inset_prompt(json_path):
    for json_ in os.listdir(json_path):
        with open(os.path.join(json_path, json_), 'r') as f:
            data_list = json.load(f)
        for i in data_list:
            source = os.path.basename(os.path.join(json_path, json_)).split('.')[0]
            sqlite_handle(table=f"prompt_{source}_sys", database='ai_prompt_cp.db').inset_prompt(prompt={i['act']: i['prompt']}, source=source)


def batch_add_source():
    sql_ll = sqlite_handle(database='ai_prompt_cp.db')
    tabs = sql_ll.get_tables()
    for t in tabs:
        sqlite_handle(table=t, database='ai_prompt_cp.db').add_column_type('source')


def batch_export_prompt(incloud_tab='prompt_'):
    sql_ll = sqlite_handle(database='ai_prompt_cp.db')
    tabs = sql_ll.get_tables()
    for i in tabs:
        if str(i).startswith(incloud_tab):
            source = i.split('_')[-1]
            result = sqlite_handle(table=i, database='ai_prompt_cp.db').get_prompt_value_temp()
            file_dict = []
            for k in result:
                file_dict.append({'act': k, 'prompt': result[k]})
            if file_dict:
                file_path = os.path.join('/Users/kilig/Job/Python-project/kso_gpt/users_data/export_prompt')
                os.makedirs(file_path, exist_ok=True)
                with open(os.path.join(file_path, f"{source}.json"), mode='w', encoding='utf-8') as f:
                    f.write(json.dumps(file_dict, ensure_ascii=False))
                    print(f'{source}已导出', os.path.join(file_path, f"{source}.json"))


def batch_migration_data_table():
    sql_ll = sqlite_handle(database='ai_prompt.db')
    tabs = sql_ll.get_tables()
    for t in tabs:
        if str(t).startswith('ai_private_'):
            sql_ll.delete_tables(t)
    for t in tabs:
        if str(t).startswith('ai_common_'):
            new = str(t).split('_')[-1]
            sql_ll.rename_tables(t, new=f'ai_private_{new}')


def batch_delete_data_table():
    sql_ll = sqlite_handle(database='ai_prompt_2.db')
    tabs = sql_ll.get_tables()
    for t in tabs:
        if not str(t).endswith('sys'):
            sql_ll.delete_tables(t)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='数据库命令行操作')
    parser.add_argument('--database', metavar='text', help='指定数据库，默认ai_prompt.db')
    parser.add_argument('--tab', metavar='text', help='指定数据表, 默认prompt_插件定制_sys')
    parser.add_argument('--source', metavar='text', help='**增加source')
    args = parser.parse_args()

    if args.source:
        if not args.tab:
            args.tab = 'prompt_插件定制_sys'
        if not args.database:
            args.database = 'ai_prompt.db'
        SqliteHandle(table=args.tab, database=args.database).update_value(new_source=args.source)
    else:
        print('带**的必填呀撒比')

sqlite_handle = SqliteHandle
if __name__ == '__main__':
    main()