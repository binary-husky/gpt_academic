import time, logging, json


class AliyunASR():

    def test_on_sentence_begin(self, message, *args):
        # print("test_on_sentence_begin:{}".format(message))
        pass

    def test_on_sentence_end(self, message, *args):
        # print("test_on_sentence_end:{}".format(message))
        message = json.loads(message)
        self.parsed_sentence = message['payload']['result']
        self.event_on_entence_end.set()
        # print(self.parsed_sentence)

    def test_on_start(self, message, *args):
        # print("test_on_start:{}".format(message))
        pass

    def test_on_error(self, message, *args):
        logging.error("on_error args=>{}".format(args))
        pass

    def test_on_close(self, *args):
        self.aliyun_service_ok = False
        pass

    def test_on_result_chg(self, message, *args):
        # print("test_on_chg:{}".format(message))
        message = json.loads(message)
        self.parsed_text = message['payload']['result']
        self.event_on_result_chg.set()

    def test_on_completed(self, message, *args):
        # print("on_completed:args=>{} message=>{}".format(args, message))
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
                # print('audio len:', len(audio), '\t ds len:', len(dsdata), '\t need n send:', len(data)//640)
                slices = zip(*(iter(data),) * 640)    # 640个字节为一组
                for i in slices: sr.send_audio(bytes(i))
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
            print(response)
            jss = json.loads(response)
            if 'Token' in jss and 'Id' in jss['Token']:
                token = jss['Token']['Id']
                expireTime = jss['Token']['ExpireTime']
                print("token = " + token)
                print("expireTime = " + str(expireTime))
        except Exception as e:
            print(e)

        return token
