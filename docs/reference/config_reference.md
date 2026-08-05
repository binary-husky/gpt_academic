# 配置参考手册

本文档是 GPT Academic 所有配置项的完整参考手册。在实际使用中，您通常只需关注与当前需求相关的配置项。如果您是首次配置，建议先阅读 [快速上手](../get_started/quickstart.md) 和 [配置详解](../get_started/configuration.md)，本手册更适合作为查阅工具使用。

---

## 配置优先级

GPT Academic 支持三种配置方式，系统按以下优先级读取配置（高优先级会覆盖低优先级的同名配置）：

| 优先级 | 配置方式 | 典型场景 |
|:-----:|---------|---------|
| **最高** | 环境变量 | Docker 部署、服务器环境 |
| **中** | `config_private.py` | 本地开发、个人使用 |
| **最低** | `config.py` | 项目默认值 |

对于本地使用的用户，推荐在项目根目录创建 `config_private.py` 文件，仅覆盖需要修改的配置项。该文件已被 `.gitignore` 忽略，不会被 Git 追踪，可安全存放密钥信息。

---

## API 密钥配置

以下配置项用于接入各大模型服务商的 API。根据您要使用的模型，配置对应的密钥即可。

### 通用 API 密钥

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `API_KEY` | `str` | OpenAI 及兼容服务的 API 密钥。支持多密钥负载均衡，用英文逗号分隔，如 `"sk-key1,sk-key2"` |
| `API_ORG` | `str` | OpenAI 组织 ID（极少数账户需要），格式如 `org-xxxxxxxx` |

### 国产模型密钥

| 配置项 | 服务商 | 获取地址 |
|-------|-------|---------|
| `DASHSCOPE_API_KEY` | 阿里云百炼（通义千问） | [百炼控制台](https://dashscope.console.aliyun.com/) |
| `DEEPSEEK_API_KEY` | 深度求索（DeepSeek） | [DeepSeek 开放平台](https://platform.deepseek.com/) |
| `ZHIPUAI_API_KEY` | 智谱 AI（GLM 系列） | [智谱开放平台](https://open.bigmodel.cn/) |
| `MOONSHOT_API_KEY` | 月之暗面（Moonshot） | [Moonshot 控制台](https://platform.moonshot.cn/) |
| `YIMODEL_API_KEY` | 零一万物（Yi 模型） | [零一万物平台](https://platform.lingyiwanwu.com/) |

### 其他服务商密钥

| 配置项 | 服务商 | 说明 |
|-------|-------|------|
| `ANTHROPIC_API_KEY` | Anthropic | Claude 系列模型 |
| `GEMINI_API_KEY` | Google | Gemini 系列模型 |
| `GROK_API_KEY` | xAI | Grok 模型 |
| `ARK_API_KEY` | 火山引擎 | 用于接入火山引擎托管的模型（如 DeepSeek） |

### 百度千帆配置

百度千帆需要同时配置 API Key 和 Secret Key：

| 配置项 | 说明 |
|-------|------|
| `BAIDU_CLOUD_API_KEY` | 千帆平台 API Key |
| `BAIDU_CLOUD_SECRET_KEY` | 千帆平台 Secret Key |
| `BAIDU_CLOUD_QIANFAN_MODEL` | 使用的模型，如 `"ERNIE-Bot-4"` |

### 讯飞星火配置

讯飞星火需要三个凭证：

| 配置项 | 说明 |
|-------|------|
| `XFYUN_APPID` | 讯飞开放平台应用 ID |
| `XFYUN_API_SECRET` | API Secret |
| `XFYUN_API_KEY` | API Key |

### Azure OpenAI 配置

Azure OpenAI 提供两种配置方式。若只使用单个 Azure 部署，使用基础配置即可；若需要管理多个部署并动态切换，使用数组配置。

**基础配置**（单部署）：

| 配置项 | 说明 |
|-------|------|
| `AZURE_ENDPOINT` | Azure 服务端点，如 `"https://your-resource.openai.azure.com/"` |
| `AZURE_API_KEY` | Azure API 密钥 |
| `AZURE_ENGINE` | 部署名称（您在 Azure 中创建的部署名） |

**数组配置**（多部署动态切换）：

```python
AZURE_CFG_ARRAY = {
    "azure-gpt-4": {
        "AZURE_ENDPOINT": "https://resource1.openai.azure.com/",
        "AZURE_API_KEY": "your-key-1",
        "AZURE_ENGINE": "gpt4-deployment",
        "AZURE_MODEL_MAX_TOKEN": 8192
    },
    "azure-gpt-35": {
        "AZURE_ENDPOINT": "https://resource2.openai.azure.com/",
        "AZURE_API_KEY": "your-key-2",
        "AZURE_ENGINE": "gpt35-deployment",
        "AZURE_MODEL_MAX_TOKEN": 16385
    }
}
```

---

## 模型配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `LLM_MODEL` | `str` | `"gpt-3.5-turbo-16k"` | 默认选中的模型，必须包含在 `AVAIL_LLM_MODELS` 中 |
| `AVAIL_LLM_MODELS` | `list` | 见 config.py | 界面下拉菜单中可选的模型列表 |
| `EMBEDDING_MODEL` | `str` | `"text-embedding-3-small"` | Embedding 模型（用于向量检索） |

### 模型名称前缀

GPT Academic 支持通过前缀接入各种兼容服务：

| 前缀 | 用途 | 示例 |
|-----|------|------|
| `one-api-` | One-API 兼容服务 | `"one-api-gpt-4(max_token=8000)"` |
| `openrouter-` | OpenRouter 路由服务 | `"openrouter-openai/gpt-4o"` |
| `azure-` | Azure OpenAI | `"azure-gpt-4"` |
| `ollama-` | 本地 Ollama | `"ollama-llama3(max_token=4096)"` |
| `vllm-` | vLLM 服务 | `"vllm-qwen(max_token=8000)"` |
| `api2d-` | API2D 中转服务 | `"api2d-gpt-4"` |
| `volcengine-` | 火山引擎 | `"volcengine-deepseek-r1-250120"` |
| `dashscope-` | 阿里云百炼 | `"dashscope-deepseek-r1"` |

使用 `(max_token=N)` 后缀可以指定模型的上下文长度，帮助系统正确裁剪对话历史。

### 本地模型配置

| 配置项 | 说明 |
|-------|------|
| `CHATGLM_LOCAL_MODEL_PATH` | ChatGLM 本地模型路径，如 `"THUDM/glm-4-9b-chat"` |
| `CHATGLM_PTUNING_CHECKPOINT` | ChatGLM 微调模型 checkpoint 路径 |
| `QWEN_LOCAL_MODEL_SELECTION` | 本地 Qwen 模型选择 |
| `LOCAL_MODEL_DEVICE` | 本地模型运行设备：`"cpu"` 或 `"cuda"` |
| `LOCAL_MODEL_QUANT` | 模型量化方式：`"FP16"`、`"INT4"` 或 `"INT8"` |

---

## 代理与网络配置

### 代理设置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `USE_PROXY` | `bool` | `False` | 是否启用代理 |
| `proxies` | `dict` | `None` | 代理配置字典 |

代理配置格式为 `[协议]://[地址]:[端口]`，示例：

```python
USE_PROXY = True
proxies = {
    "http":  "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
# 或使用 socks5 协议
proxies = {
    "http":  "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080",
}
```

### API URL 重定向

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `API_URL_REDIRECT` | `dict` | 将官方 API 地址重定向到中转服务 |

```python
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-proxy.com/v1/chat/completions"
}
```

### 网络参数

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `TIMEOUT_SECONDS` | `int` | `30` | API 请求超时时间（秒） |
| `MAX_RETRY` | `int` | `2` | 请求失败重试次数 |
| `WHEN_TO_USE_PROXY` | `list` | 见 config.py | 指定哪些场景使用代理 |

---

## 界面配置

### 外观设置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `THEME` | `str` | `"Default"` | 颜色主题 |
| `AVAIL_THEMES` | `list` | 见 config.py | 可选主题列表 |
| `DARK_MODE` | `bool` | `True` | 是否启用暗色模式 |
| `LAYOUT` | `str` | `"LEFT-RIGHT"` | 布局方式：`"LEFT-RIGHT"` 或 `"TOP-DOWN"` |
| `CHATBOT_HEIGHT` | `int` | `1115` | 对话窗高度（仅 TOP-DOWN 布局生效） |
| `CODE_HIGHLIGHT` | `bool` | `True` | 是否启用代码高亮 |

### 字体设置

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `FONT` | `str` | 当前使用的字体 |
| `AVAIL_FONTS` | `list` | 可选字体列表，支持本地字体和网络字体 |

网络字体格式：`"字体昵称(字体英文真名@字体CSS下载链接)"`

### 行为设置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `AUTO_CLEAR_TXT` | `bool` | `False` | 提交后是否自动清空输入框 |
| `AUTO_OPEN_BROWSER` | `bool` | `True` | 启动时是否自动打开浏览器 |
| `ADD_WAIFU` | `bool` | `False` | 是否添加 Live2D 装饰 |

### 系统提示词

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `INIT_SYS_PROMPT` | `str` | 默认系统提示词，影响模型的行为风格 |

---

## 服务配置

### Web 服务

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `WEB_PORT` | `int` | `-1` | Web 服务端口，-1 表示随机端口 |
| `CUSTOM_PATH` | `str` | `"/"` | 二级路径，如 `"/gpt"` 使服务运行在 `http://ip:port/gpt/` |
| `SSL_KEYFILE` | `str` | `""` | HTTPS 私钥文件路径 |
| `SSL_CERTFILE` | `str` | `""` | HTTPS 证书文件路径 |

### 认证配置

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `AUTHENTICATION` | `list` | 用户认证列表，格式为 `[("用户名", "密码"), ...]` |

```python
AUTHENTICATION = [
    ("admin", "your-password"),
    ("user1", "password1"),
]
```

---

## 插件与功能配置

### 插件设置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `DEFAULT_FN_GROUPS` | `list` | `['对话', '编程', '学术', '智能体']` | 默认显示的插件分类 |
| `PLUGIN_HOT_RELOAD` | `bool` | `False` | 是否启用插件热加载 |
| `NUM_CUSTOM_BASIC_BTN` | `int` | `4` | 自定义按钮数量上限 |
| `DEFAULT_WORKER_NUM` | `int` | `8` | 并发线程数（免费用户建议设为 3） |

### 多模型对比

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `MULTI_QUERY_LLM_MODELS` | `str` | 多模型询问功能使用的模型，用 `&` 分隔 |

```python
MULTI_QUERY_LLM_MODELS = "gpt-4o&qwen-max&deepseek-chat"
```

### 上下文裁剪

| 配置项 | 类型 | 说明 |
|-------|------|------|
| `AUTO_CONTEXT_CLIP_ENABLE` | `bool` | 是否启用自动上下文裁剪 |
| `AUTO_CONTEXT_CLIP_TRIGGER_TOKEN_LEN` | `int` | 触发裁剪的 Token 长度阈值 |
| `AUTO_CONTEXT_MAX_ROUND` | `int` | 最多保留的对话轮数 |

---

## 外部服务配置

### 文档解析服务

| 配置项 | 说明 |
|-------|------|
| `GROBID_URLS` | GROBID 服务地址列表（用于 PDF 学术论文解析） |
| `DOC2X_API_KEY` | Doc2X API 密钥（高质量 PDF 解析） |
| `MATHPIX_APPID` / `MATHPIX_APPKEY` | Mathpix 凭证（LaTeX 公式 OCR） |

### 互联网搜索

| 配置项 | 说明 |
|-------|------|
| `SEARXNG_URLS` | SearXNG 搜索服务地址列表 |
| `JINA_API_KEY` | Jina Reader API 密钥（网页内容提取） |
| `SEMANTIC_SCHOLAR_KEY` | Semantic Scholar API 密钥（学术搜索） |

### 语音功能

| 配置项 | 说明 |
|-------|------|
| `ENABLE_AUDIO` | 是否启用语音识别功能 |
| `ALIYUN_TOKEN` | 阿里云语音服务 Token |
| `ALIYUN_APPKEY` | 阿里云语音服务 AppKey |
| `TTS_TYPE` | 语音合成类型：`"EDGE_TTS"`、`"LOCAL_SOVITS_API"` 或 `"DISABLE"` |
| `EDGE_TTS_VOICE` | Edge TTS 语音，如 `"zh-CN-XiaoxiaoNeural"` |
| `GPT_SOVITS_URL` | GPT-SoVITS 服务地址 |

### 其他服务

| 配置项 | 说明 |
|-------|------|
| `HUGGINGFACE_ACCESS_TOKEN` | HuggingFace Token（下载模型时使用） |
| `AUTOGEN_USE_DOCKER` | AutoGen 插件是否使用 Docker 运行代码 |
| `DAAS_SERVER_URLS` | 媒体智能体服务地址列表 |

---

## 路径配置

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| `PATH_PRIVATE_UPLOAD` | `"private_upload"` | 用户上传文件的临时存放路径 |
| `PATH_LOGGING` | `"gpt_log"` | 日志文件存放路径 |
| `ARXIV_CACHE_DIR` | `"gpt_log/arxiv_cache"` | Arxiv 论文翻译缓存路径 |

---

## 安全配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `ALLOW_RESET_CONFIG` | `bool` | `False` | 是否允许通过自然语言修改配置（有安全风险） |
| `CUSTOM_API_KEY_PATTERN` | `str` | `""` | 自定义 API Key 格式验证正则表达式 |

---

## 环境变量速查

在 Docker 或服务器环境中，所有配置项都可以通过同名环境变量设置。以下是常用配置的环境变量示例：

```bash
# API 配置
export API_KEY="sk-xxxxxxxxxxxxxxxx"
export DASHSCOPE_API_KEY="sk-xxxxxxxx"
export LLM_MODEL="gpt-4o"

# 代理配置
export USE_PROXY="True"
export proxies='{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}'

# 服务配置
export WEB_PORT="7860"
export THEME="Default"
export DARK_MODE="True"
```

!!! tip "布尔值格式"
    环境变量中的布尔值使用字符串形式：`"True"` 或 `"False"`。

---

## 相关文档

- [配置详解](../get_started/configuration.md) — 配置基础知识和推荐做法
- [快速上手](../get_started/quickstart.md) — 首次配置引导
- [Docker 部署](../deployment/docker.md) — 容器化部署配置
- [中转渠道接入](../models/transit_api.md) — 使用第三方中转服务
