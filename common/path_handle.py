# encoding: utf-8
# @Time   : 2023/12/26
# @Author : Spike
# @Descr   :
import os


class InitPath:

    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.prompt_path = os.path.join(self.base_path, 'users_data')
        self.knowledge_path = os.path.join(self.prompt_path, 'knowledge')
        self.users_path = os.path.join(self.base_path, 'private_upload')
        self.logs_path = os.path.join(self.base_path, 'gpt_log')
        self.history_path = os.path.join(self.logs_path, 'history')
        self.assets_path = os.path.join(self.base_path, 'docs', 'assets')

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
