import time, threading, json


class AliyunASR():

    def test_on_sentence_begin(self, message, *args):
        print("test_on_sentence_begin:{}".format(message))

    def test_on_sentence_end(self, message, *args):
        print("test_on_sentence_end:{}".format(message))
        message = json.loads(message)
        self.parsed_sentence = message['payload']['result']
        self.event_on_entence_end.set()

    def test_on_start(self, message, *args):
        print("test_on_start:{}".format(message))

    def test_on_error(self, message, *args):
        print("on_error args=>{}".format(args))

    def test_on_close(self, *args):
        print("on_close: args=>{}".format(args))

    def test_on_result_chg(self, message, *args):
        print("test_on_chg:{}".format(message))
        message = json.loads(message)
        self.parsed_text = message['payload']['result']
        self.event_on_result_chg.set()

    def test_on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))


    def audio_convertion_thread(self, uuid):
        # 在一个异步线程中采集音频
        import nls  # pip install git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git
        from scipy import io
        from .audio_io import change_sample_rate
        NEW_SAMPLERATE = 16000
        from .audio_io import RealtimeAudioDistribution
        rad = RealtimeAudioDistribution()
        import tempfile
        temp_folder = tempfile.gettempdir()

        URL="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"
        TOKEN="f37f30e0f9934c34a992f6f64f7eba4f"    # 参考https://help.aliyun.com/document_detail/450255.html获取token
        APPKEY="RoPlZrM88DnAFkZK"                   # 获取Appkey请前往控制台：https://nls-portal.console.aliyun.com/applist
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

        r = sr.start(aformat="pcm",
                enable_intermediate_result=True,
                enable_punctuation_prediction=True,
                enable_inverse_text_normalization=True)

        while not self.stop:
            # time.sleep(self.capture_interval)
            audio = rad.read(uuid.hex) 
            if audio is not None:
                # convert to pcm file
                temp_file = f'{temp_folder}/{uuid.hex}.pcm' # 
                dsdata = change_sample_rate(audio, rad.rate, NEW_SAMPLERATE) # 48000 --> 16000
                io.wavfile.write(temp_file, NEW_SAMPLERATE, dsdata)
                # read pcm binary
                with open(temp_file, "rb") as f: data = f.read()
                print('audio len:', len(audio), '\t ds len:', len(dsdata), '\t need n send:', len(data)//640)
                slices = zip(*(iter(data),) * 640)    # 640个字节为一组
                for i in slices: sr.send_audio(bytes(i))
            else:
                time.sleep(0.1)
        r = sr.stop()
