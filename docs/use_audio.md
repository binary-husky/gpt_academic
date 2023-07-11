# 使用音频输入

### 1. 切换分支

```
git checkout improve_ui_master
```

### 2. 安装额外依赖
```
pip install --upgrade pyOpenSSL scipy git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git
```

### 3. 配置音频功能开关 和 阿里云APPKEY
```
ENABLE_AUDIO = True
ALIYUN_TOKEN="554a50fcd0bb476c8d07bb630e94d20c"    # 例如 f37f30e0f9934c34a992f6f64f7eba4f
ALIYUN_APPKEY="RoPlZrM88DnAFkZK"   # 例如 RoPlZrM88DnAFkZK
```

### 4.启动


### 5.点击record from microphe，授权音频采集

I 如果需要监听自己说话（不监听电脑音频），直接在浏览器中选择对应的麦即可

II 如果需要监听电脑音频（不监听自己说话），需要安装VB-Audio VoiceMeeter，打开声音控制面板
- 在输出区（playback）选择 VoiceMeeter虚拟设备（把电脑外放声音用VoiceMeeter虚拟设备截留）
- 在输入区（recording）选择 VoiceMeeter虚拟设备 的设置，进入其子菜单，子菜单playback中选中物理外放（将截留的声音释放出去）
- 在浏览器中选择VoiceMeeter创造的虚拟麦克风

III 二者切换时，需要刷新页面才有效 

### 6.点击函数插件区“实时音频采集”



