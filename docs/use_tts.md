# 使用TTS文字转语音


## 1. 使用EDGE-TTS（简单）

将本项目配置项修改如下即可

```
TTS_TYPE = "EDGE_TTS"
EDGE_TTS_VOICE = "zh-CN-XiaoxiaoNeural"
```

## 2. 使用SoVITS（需要有显卡）

使用以下docker-compose.yml文件，先启动SoVITS服务API

  1. 创建以下文件夹结构
      ```shell
      .
      ├── docker-compose.yml
      └── reference
          ├── clone_target_txt.txt
          └── clone_target_wave.mp3
      ```
  2. 其中`docker-compose.yml`为
      ```yaml
      version: '3.8'
      services:
        gpt-sovits:
          image: fuqingxu/sovits_gptac_trim:latest
          container_name: sovits_gptac_container
          working_dir: /workspace/gpt_sovits_demo
          environment:
            - is_half=False
            - is_share=False
          volumes:
            - ./reference:/reference
          ports:
            - "19880:9880"  # 19880 为 sovits api 的暴露端口，记住它
          shm_size: 16G
          deploy:
            resources:
              reservations:
                devices:
                - driver: nvidia
                  count: "all"
                  capabilities: [gpu]
          command: bash -c "python3 api.py"
      ```
  3. 其中`clone_target_wave.mp3`为需要克隆的角色音频，`clone_target_txt.txt`为该音频对应的文字文本（ https://wiki.biligame.com/ys/%E8%A7%92%E8%89%B2%E8%AF%AD%E9%9F%B3 ）
  4. 运行`docker-compose up`
  5. 将本项目配置项修改如下即可
      (19880 为 sovits api 的暴露端口，与docker-compose.yml中的端口对应)
      ```
      TTS_TYPE = "LOCAL_SOVITS_API"
      GPT_SOVITS_URL = "http://127.0.0.1:19880"
      ```
  6. 启动本项目