# 如何使用其他大语言模型

## 1. 先运行text-generation
``` sh
# 下载模型
git clone https://github.com/oobabooga/text-generation-webui.git

# 安装text-generation的额外依赖
pip install accelerate bitsandbytes flexgen gradio llamacpp markdown numpy peft requests rwkv safetensors sentencepiece tqdm datasets git+https://github.com/huggingface/transformers

# 切换路径
cd text-generation-webui

# 下载模型
python download-model.py facebook/opt-1.3b

# 其他可选如 facebook/galactica-1.3b
#           facebook/galactica-6.7b
#           facebook/galactica-120b

# Pymalion 6B is a proof-of-concept dialogue model based on EleutherAI's GPT-J-6B.
#           facebook/pygmalion-1.3b

# 启动text-generation，注意把模型的斜杠改成下划线
python server.py --cpu --listen --listen-port 7860 --model facebook_galactica-1.3b
```

## 2. 修改config.py
```
# LLM_MODEL格式为     [模型]@[ws地址] @[ws端口]
LLM_MODEL = "pygmalion-1.3b@localhost@7860"
```


## 3. 运行！
```
cd chatgpt-academic
python main.py
```
