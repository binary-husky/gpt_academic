# 使用音频交互功能


## 1. 安装额外依赖
```
pip install --upgrade pyOpenSSL webrtcvad scipy git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git
```

如果因为特色网络问题导致上述命令无法执行：
1. git clone alibabacloud-nls-python-sdk这个项目（或者直接前往Github对应网址下载压缩包）.
命令行输入： `git clone https://github.com/aliyun/alibabacloud-nls-python-sdk.git`
1. 进入alibabacloud-nls-python-sdk目录命令行输入：`python setup.py install`


## 2. 配置音频功能开关 和 阿里云APPKEY（config.py/config_private.py/环境变量）

- 注册阿里云账号
- 开通 智能语音交互 （有免费白嫖时长）
- 获取token和appkey
- 未来将逐步用其他更廉价的云服务取代阿里云

```
ENABLE_AUDIO = True
ALIYUN_TOKEN = "554a50fcd0bb476c8d07bb630e94d20c"    # 此token已经失效
ALIYUN_APPKEY = "RoPlZrM88DnAFkZK"   # 此appkey已经失效
```

参考 https://help.aliyun.com/document_detail/450255.html
先有阿里云开发者账号，登录之后，需要开通 智能语音交互 的功能，可以免费获得一个token，然后在 全部项目 中，创建一个项目，可以获得一个appkey.

- 进阶功能
进一步填写ALIYUN_ACCESSKEY和ALIYUN_SECRET实现自动获取ALIYUN_TOKEN
```
ALIYUN_APPKEY = "RoP1ZrM84DnAFkZK"
ALIYUN_TOKEN = ""
ALIYUN_ACCESSKEY = "LTAI5q6BrFUzoRXVGUWnekh1"
ALIYUN_SECRET = "eHmI20AVWIaQZ0CiTD2bGQVsaP9i68"
```


## 3.启动

启动gpt-academic `python main.py`

## 4.点击record from microphe，授权音频采集

I 如果需要监听自己说话（不监听电脑音频），直接在浏览器中选择对应的麦即可

II 如果需要监听电脑音频（不监听自己说话），需要安装`VB-Audio VoiceMeeter`，打开声音控制面板(sound control panel)
- 1 `[把电脑的所有外放声音用VoiceMeeter截留]` 在输出区（playback）选项卡，把VoiceMeeter Input虚拟设备set as default设为默认播放设备。
- 2 `[把截留的声音释放到gpt-academic]` 打开gpt-academic主界面，授权音频采集后，在浏览器地址栏或者类似的地方会出现一个麦克风图标，打开后，按照浏览器的提示，选择VoiceMeeter虚拟麦克风。然后刷新页面，重新授权音频采集。
- 3 `[把截留的声音同时释放到耳机或音响]` 完成第一步之后，您应处于听不到电脑声音的状态。为了在截获音频的同时，避免影响正常使用，请完成这最后一步配置。在声音控制面板(sound control panel)输入区（recording）选项卡，把VoiceMeeter Output虚拟设备set as default。双击进入VoiceMeeter Output虚拟设备的设置。
  - 3-1 进入VoiceMeeter Output虚拟设备子菜单，打开listen选项卡。
  - 3-2 勾选Listen to this device。
  - 3-3 在playback through this device下拉菜单中选择你的正常耳机或音响。

III `[把特殊软件（如腾讯会议）的外放声音用VoiceMeeter截留]` 在完成步骤II的基础上，在特殊软件（如腾讯会议）中，打开声音菜单，选择扬声器VoiceMeeter Input，选择麦克风为正常耳机麦。

VI 两种音频监听模式切换时，需要刷新页面才有效。

VII 非localhost运行+非https情况下无法打开录音功能的坑：https://blog.csdn.net/weixin_39461487/article/details/109594434

## 5.点击函数插件区“实时音频采集” 或者其他音频交互功能
