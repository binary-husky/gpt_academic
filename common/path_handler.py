# encoding: utf-8
# @Time   : 2023/12/26
# @Author : Spike
# @Descr   :
import os


class InitPath:

    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.docs_path = os.path.join(self.base_path, 'docs')
        self.assets_path = os.path.join(self.docs_path, 'assets')
        self.prompt_export_path = os.path.join(self.docs_path, 'prompt_export')
        self.logs_path = os.path.join(self.base_path, 'gpt_log')
        self.users_private_path = os.path.join(self.base_path, 'users_private')
        self.private_knowledge_path = os.path.join(self.users_private_path, 'knowledge')
        self.private_upload_path = os.path.join(self.users_private_path, 'upload')
        self.private_history_path = os.path.join(self.users_private_path, 'history')
        self.private_db_path = os.path.join(self.users_private_path, 'db')

    def __getattribute__(self, name):
        """
        如果文件夹路径不存在，则自动创建
        """
        attr = object.__getattribute__(self, name)
        if 'path' in name and not os.path.exists(attr):
            if not os.path.exists(attr):
                os.makedirs(attr, exist_ok=True)
        return attr


init_path = InitPath()

if __name__ == '__main__':
    print(init_path.s3url_path)
