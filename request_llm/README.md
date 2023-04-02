# 如何使用其他大语言模型（dev分支测试中）

## 1. 先运行text-generation
``` sh
# 下载模型（ text-generation 这么牛的项目，别忘了给人家star ）
git clone https://github.com/oobabooga/text-generation-webui.git

# 安装text-generation的额外依赖
pip install accelerate bitsandbytes flexgen gradio llamacpp markdown numpy peft requests rwkv safetensors sentencepiece tqdm datasets git+https://github.com/huggingface/transformers

# 切换路径
cd text-generation-webui

# 下载模型
python download-model.py facebook/galactica-1.3b
# 其他可选如 facebook/opt-1.3b
#           facebook/galactica-6.7b
#           facebook/galactica-120b
#           facebook/pygmalion-1.3b 等
# 详情见 https://github.com/oobabooga/text-generation-webui

# 启动text-generation，注意把模型的斜杠改成下划线
python server.py --cpu --listen --listen-port 7860 --model facebook_galactica-1.3b
```

## 2. 修改config.py
``` sh
# LLM_MODEL格式较复杂   TGUI:[模型]@[ws地址]:[ws端口] ,   端口要和上面给定的端口一致
LLM_MODEL = "TGUI:galactica-1.3b@localhost:7860"
```

## 3. 运行！
``` sh
cd chatgpt-academic
python main.py
```
