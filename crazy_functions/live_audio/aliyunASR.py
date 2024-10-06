import time, json, sys, struct
import numpy as np
from loguru import logger as logging
from scipy.io.wavfile import WAVE_FORMAT

def write_numpy_to_wave(filename, rate, data, add_header=False):
    """
    Write a NumPy array as a WAV file.
    """
    def _array_tofile(fid, data):
        # ravel gives a c-contiguous buffer
        fid.write(data.ravel().view('b').data)

    if hasattr(filename, 'write'):
        fid = filename
    else:
        fid = open(filename, 'wb')

    fs = rate

    try:
        dkind = data.dtype.kind
        if not (dkind == 'i' or dkind == 'f' or (dkind == 'u' and
                                                 data.dtype.itemsize == 1)):
            raise ValueError("Unsupported data type '%s'" % data.dtype)

        header_data = b''

        header_data += b'RIFF'
        header_data += b'\x00\x00\x00\x00'
        header_data += b'WAVE'

        # fmt chunk
        header_data += b'fmt '
        if dkind == 'f':
            format_tag = WAVE_FORMAT.IEEE_FLOAT
        else:
            format_tag = WAVE_FORMAT.PCM
        if data.ndim == 1:
            channels = 1
        else:
            channels = data.shape[1]
        bit_depth = data.dtype.itemsize * 8
        bytes_per_second = fs*(bit_depth // 8)*channels
        block_align = channels * (bit_depth // 8)

        fmt_chunk_data = struct.pack('<HHIIHH', format_tag, channels, fs,
                                     bytes_per_second, block_align, bit_depth)
        if not (dkind == 'i' or dkind == 'u'):
            # add cbSize field for non-PCM files
            fmt_chunk_data += b'\x00\x00'

        header_data += struct.pack('<I', len(fmt_chunk_data))
        header_data += fmt_chunk_data

        # fact chunk (non-PCM files)
        if not (dkind == 'i' or dkind == 'u'):
            header_data += b'fact'
            header_data += struct.pack('<II', 4, data.shape[0])

        # check data size (needs to be immediately before the data chunk)
        if ((len(header_data)-4-4) + (4+4+data.nbytes)) > 0xFFFFFFFF:
            raise ValueError("Data exceeds wave file size limit")
        if add_header:
            fid.write(header_data)
            # data chunk
            fid.write(b'data')
            fid.write(struct.pack('<I', data.nbytes))
            if data.dtype.byteorder == '>' or (data.dtype.byteorder == '=' and
                                            sys.byteorder == 'big'):
                data = data.byteswap()
        _array_tofile(fid, data)

        if add_header:
            # Determine file size and place it in correct
            #  position at start of the file.
            size = fid.tell()
            fid.seek(4)
            fid.write(struct.pack('<I', size-8))

    finally:
        if not hasattr(filename, 'write'):
            fid.close()
        else:
            fid.seek(0)

def is_speaker_speaking(vad, data, sample_rate):
    # Function to detect if the speaker is speaking
    # The WebRTC VAD only accepts 16-bit mono PCM audio,
    # sampled at 8000, 16000, 32000 or 48000 Hz.
    # A frame must be either 10, 20, or 30 ms in duration:
    frame_duration = 30
    n_bit_each = int(sample_rate * frame_duration / 1000)*2 # x2 because audio is 16 bit (2 bytes)
    res_list = []
    for t in range(len(data)):
        if t!=0 and t % n_bit_each == 0:
            res_list.append(vad.is_speech(data[t-n_bit_each:t], sample_rate))

    info = ''.join(['^' if r else '.' for r in res_list])
    info = info[:10]
    if any(res_list):
        return True, info
    else:
        return False, info


class AliyunASR():

    def test_on_sentence_begin(self, message, *args):
        pass

    def test_on_sentence_end(self, message, *args):
        message = json.loads(message)
        self.parsed_sentence = message['payload']['result']
        self.event_on_entence_end.set()

    def test_on_start(self, message, *args):
        pass

    def test_on_error(self, message, *args):
        logging.error("on_error args=>{}".format(args))
        pass

    def test_on_close(self, *args):
        self.aliyun_service_ok = False
        pass

    def test_on_result_chg(self, message, *args):
        message = json.loads(message)
        self.parsed_text = message['payload']['result']
        self.event_on_result_chg.set()

    def test_on_completed(self, message, *args):
        pass

    def audio_convertion_thread(self, uuid):
        # 在一个异步线程中采集音频
        import nls  # pip install git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git
        import tempfile
        from scipy import io
        from toolbox import get_conf
        from .audio_io import change_sample_rate
        from .audio_io import RealtimeAudioDistribution
        NEW_SAMPLERATE = 16000
        rad = RealtimeAudioDistribution()
        rad.clean_up()
        temp_folder = tempfile.gettempdir()
        TOKEN, APPKEY = get_conf('ALIYUN_TOKEN', 'ALIYUN_APPKEY')
        if len(TOKEN) == 0:
            TOKEN = self.get_token()
        self.aliyun_service_ok = True
        URL="wss://nls-gateway.aliyuncs.com/ws/v1"
        sr = nls.NlsSpeechTranscriber(
                    url=URL,
                    token=TOKEN,
                    appkey=APPKEY,
                    on_sentence_begin=self.test_on_sentence_begin,
                    on_sentence_end=self.test_on_sentence_end,
                    on_start=self.test_on_start,
                    on_result_changed=self.test_on_result_chg,
                    on_completed=self.test_on_completed,
                    on_error=self.test_on_error,
                    on_close=self.test_on_close,
                    callback_args=[uuid.hex]
                )
        timeout_limit_second = 20
        r = sr.start(aformat="pcm",
                timeout=timeout_limit_second,
                enable_intermediate_result=True,
                enable_punctuation_prediction=True,
                enable_inverse_text_normalization=True)

        import webrtcvad
        vad = webrtcvad.Vad()
        vad.set_mode(1)

        is_previous_frame_transmitted = False   # 上一帧是否有人说话
        previous_frame_data = None
        echo_cnt = 0        # 在没有声音之后，继续向服务器发送n次音频数据
        echo_cnt_max = 4   # 在没有声音之后，继续向服务器发送n次音频数据
        keep_alive_last_send_time = time.time()
        while not self.stop:
            # time.sleep(self.capture_interval)
            audio = rad.read(uuid.hex)
            if audio is not None:
                # convert to pcm file
                temp_file = f'{temp_folder}/{uuid.hex}.pcm' #
                dsdata = change_sample_rate(audio, rad.rate, NEW_SAMPLERATE) # 48000 --> 16000
                write_numpy_to_wave(temp_file, NEW_SAMPLERATE, dsdata)
                # read pcm binary
                with open(temp_file, "rb") as f: data = f.read()
                is_speaking, info = is_speaker_speaking(vad, data, NEW_SAMPLERATE)

                if is_speaking or echo_cnt > 0:
                    # 如果话筒激活 / 如果处于回声收尾阶段
                    echo_cnt -= 1
                    if not is_previous_frame_transmitted:   # 上一帧没有人声，但是我们把上一帧同样加上
                        if previous_frame_data is not None: data = previous_frame_data + data
                    if is_speaking:
                        echo_cnt = echo_cnt_max
                    slices = zip(*(iter(data),) * 640)      # 640个字节为一组
                    for i in slices: sr.send_audio(bytes(i))
                    keep_alive_last_send_time = time.time()
                    is_previous_frame_transmitted = True
                else:
                    is_previous_frame_transmitted = False
                    echo_cnt = 0
                    # 保持链接激活，即使没有声音，也根据时间间隔，发送一些音频片段给服务器
                    if time.time() - keep_alive_last_send_time > timeout_limit_second/2:
                        slices = zip(*(iter(data),) * 640)    # 640个字节为一组
                        for i in slices: sr.send_audio(bytes(i))
                        keep_alive_last_send_time = time.time()
                        is_previous_frame_transmitted = True
                self.audio_shape = info
            else:
                time.sleep(0.1)

            if not self.aliyun_service_ok:
                self.stop = True
                self.stop_msg = 'Aliyun音频服务异常，请检查ALIYUN_TOKEN和ALIYUN_APPKEY是否过期。'
        r = sr.stop()

    def get_token(self):
        from toolbox import get_conf
        import json
        from aliyunsdkcore.request import CommonRequest
        from aliyunsdkcore.client import AcsClient
        AccessKey_ID, AccessKey_secret = get_conf('ALIYUN_ACCESSKEY', 'ALIYUN_SECRET')

        # 创建AcsClient实例
        client = AcsClient(
            AccessKey_ID,
            AccessKey_secret,
            "cn-shanghai"
        )

        # 创建request，并设置参数。
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')

        try:
            response = client.do_action_with_exception(request)
            logging.info(response)
            jss = json.loads(response)
            if 'Token' in jss and 'Id' in jss['Token']:
                token = jss['Token']['Id']
                expireTime = jss['Token']['ExpireTime']
                logging.info("token = " + token)
                logging.info("expireTime = " + str(expireTime))
        except Exception as e:
            logging.error(e)

        return token
