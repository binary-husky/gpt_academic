# 如何使用其他大语言模型（v3.0分支测试中）

## ChatGLM

- 安装依赖 `pip install -r request_llm/requirements_chatglm.txt`
- 修改配置，在config.py中将LLM_MODEL的值改为"chatglm"

``` sh
LLM_MODEL = "chatglm"
```
- 运行！
``` sh
`python main.py`
``` 


---
## Text-Generation-UI (TGUI)

### 1. 部署TGUI
``` sh
# 1 下载模型
git clone https://github.com/oobabooga/text-generation-webui.git
# 2 这个仓库的最新代码有问题，回滚到几周之前
git reset --hard fcda3f87767e642d1c0411776e549e1d3894843d
# 3 切换路径
cd text-generation-webui
# 4 安装text-generation的额外依赖
pip install accelerate bitsandbytes flexgen gradio llamacpp markdown numpy peft requests rwkv safetensors sentencepiece tqdm datasets git+https://github.com/huggingface/transformers
# 5 下载模型
python download-model.py facebook/galactica-1.3b
# 其他可选如 facebook/opt-1.3b
#           facebook/galactica-1.3b
#           facebook/galactica-6.7b
#           facebook/galactica-120b
#           facebook/pygmalion-1.3b 等
# 详情见 https://github.com/oobabooga/text-generation-webui

# 6 启动text-generation
python server.py --cpu --listen --listen-port 7865 --model facebook_galactica-1.3b
```

### 2. 修改config.py

``` sh
# LLM_MODEL格式:   tgui:[模型]@[ws地址]:[ws端口] ,   端口要和上面给定的端口一致
LLM_MODEL = "tgui:galactica-1.3b@localhost:7860"
```

### 3. 运行！
``` sh
cd chatgpt-academic
python main.py
```
