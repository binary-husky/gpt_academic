import numpy as np
from scipy import interpolate

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
        self.max_len = 1024*1024
        self.rate = 48000   # 只读，每秒采样数量

    def clean_up(self):
        self.data = {}

    def feed(self, uuid, audio):
        self.rate, audio_ = audio
        # print('feed', len(audio_), audio_[-25:])
        if uuid not in self.data:
            self.data[uuid] = audio_
        else:
            new_arr = np.concatenate((self.data[uuid], audio_))
            if len(new_arr) > self.max_len: new_arr = new_arr[-self.max_len:]
            self.data[uuid] = new_arr

    def read(self, uuid):
        if uuid in self.data:
            res = self.data.pop(uuid)
            # print('\r read-', len(res), '-', max(res), end='', flush=True)
        else:
            res = None
        return res

def change_sample_rate(audio, old_sr, new_sr):
    duration = audio.shape[0] / old_sr

    time_old  = np.linspace(0, duration, audio.shape[0])
    time_new  = np.linspace(0, duration, int(audio.shape[0] * new_sr / old_sr))

    interpolator = interpolate.interp1d(time_old, audio.T)
    new_audio = interpolator(time_new).T
    return new_audio.astype(np.int16)