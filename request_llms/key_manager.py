import random
import os
from toolbox import get_log_folder

def Singleton(cls):
    _instance = {}
 
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
 
    return _singleton


@Singleton
class ApiKeyManager():
    """
    只把失效的key保存在内存中
    """
    def __init__(self, mode='blacklist') -> None:
        # self.key_avail_list = []
        self.key_black_list = []
        self.debug = False
        self.log = True
        self.remain_keys = []
    
    def add_key_to_blacklist(self, key):
        self.key_black_list.append(key)
        if self.debug: print('black list key added', key)
        if self.log:
            with open(
                os.path.join(get_log_folder(user='admin', plugin_name='api_key_manager'), 'invalid_key.log'), 'a+', encoding='utf8') as f:
                summary = 'num blacklist keys' + len(self.key_black_list) + 'num valid keys' + len(self.remain_keys)
                f.write('\n\n' + summary + '\n')
                f.write('---- <add blacklist key> ----\n')
                f.write(key)
                f.write('\n')
                f.write('---- <all blacklist keys> ----\n')
                f.write(str(self.key_black_list))
                f.write('\n')
                f.write('---- <remain keys> ----\n')
                f.write(str(self.remain_keys))
                f.write('\n')

    def select_avail_key(self, key_list):
        # select key from key_list, but avoid keys also in self.key_black_list, raise error if no key can be found
        available_keys = [key for key in key_list if key not in self.key_black_list]
        if not available_keys:
            raise KeyError("所有API KEY都被OPENAI拒绝了")
        selected_key = random.choice(available_keys)
        if self.debug: print('total keys', len(key_list), 'valid keys', len(available_keys))
        if self.log: self.remain_keys = available_keys
        return selected_key