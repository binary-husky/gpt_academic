import random

def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class OpenAI_ApiKeyManager():
    def __init__(self, mode='blacklist') -> None:
        # self.key_avail_list = []
        self.key_black_list = []

    def add_key_to_blacklist(self, key):
        self.key_black_list.append(key)

    def select_avail_key(self, key_list):
        # select key from key_list, but avoid keys also in self.key_black_list, raise error if no key can be found
        available_keys = [key for key in key_list if key not in self.key_black_list]
        if not available_keys:
            raise KeyError("No available key found.")
        selected_key = random.choice(available_keys)
        return selected_key