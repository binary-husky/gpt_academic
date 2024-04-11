# 使用VLLM


## 1. 首先启动 VLLM，自行选择模型

```
python -m vllm.entrypoints.openai.api_server --model /home/hmp/llm/cache/Qwen1___5-32B-Chat --tensor-parallel-size 2 --dtype=half
```

这里使用了存储在 `/home/hmp/llm/cache/Qwen1___5-32B-Chat` 的本地模型，可以根据自己的需求更改。

## 2. 测试 VLLM

```
curl http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "/home/hmp/llm/cache/Qwen1___5-32B-Chat",
  "messages": [
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "怎么实现一个去中心化的控制器?"}
  ]
}'
```

## 3. 配置本项目

```
API_KEY = "sk-123456789xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx123456789"
LLM_MODEL = "vllm-/home/hmp/llm/cache/Qwen1___5-32B-Chat(max_token=4096)"
API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "http://localhost:8000/v1/chat/completions"}
```

```
"vllm-/home/hmp/llm/cache/Qwen1___5-32B-Chat(max_token=4096)"
其中
  "vllm-"                                     是前缀（必要）
  "/home/hmp/llm/cache/Qwen1___5-32B-Chat"    是模型名（必要）
  "(max_token=6666)"                          是配置（非必要）
```

## 4. 启动！

```
python main.py
```
