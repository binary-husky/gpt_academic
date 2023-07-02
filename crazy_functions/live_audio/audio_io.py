import numpy as np

def Singleton(cls):
    _instance = {}
 
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
 
    return _singleton


@Singleton
class RealtimeAudioDistribution():
    def __init__(self) -> None:
        self.data = {}
        self.max_len = 1024*64
        self.rate = 48000   # 只读，每秒采样数量

    def feed(self, uuid, audio):
        print('feed')
        self.rate, audio_ = audio
        if uuid not in self.data:
            self.data[uuid] = audio_
        else:
            new_arr = np.concatenate((self.data[uuid], audio_))
            if len(new_arr) > self.max_len: new_arr = new_arr[-self.max_len:]
            self.data[uuid] = new_arr

    def read(self, uuid):
        if uuid in self.data:
            res = self.data.pop(uuid)
            print('read', len(res))
        else:
            res = None
        return res