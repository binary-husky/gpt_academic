# 配置详解

本文档详细介绍 GPT Academic 的配置系统和各项配置参数。通过合理配置，您可以充分发挥项目的潜力，打造符合自己需求的工作环境。

---

## 配置机制

### 配置文件层级

GPT Academic 采用三层配置机制，读取优先级从高到低依次为：

| 优先级 | 配置方式 | 使用场景 |
|:-----:|---------|---------|
| 高 | 环境变量 | Docker 部署、CI/CD 环境 |
| 中 | `config_private.py` | **推荐**：本地开发和个人使用 |
| 低 | `config.py` | 默认配置，通常无需修改 |

这种设计使得您可以在不修改原始配置文件的情况下进行个性化配置，便于代码更新和版本管理。

### 创建私密配置文件

在项目根目录创建 `config_private.py`，只需在其中覆盖您需要修改的配置项：

```python title="config_private.py"
# 只需要写您想要覆盖的配置
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
LLM_MODEL = "gpt-4o"
USE_PROXY = False
```

!!! tip "文件安全"
    `config_private.py` 已被添加到 `.gitignore`，不会被 Git 追踪，您的密钥不会意外提交到版本库。

---

## 核心配置项

### API 密钥配置

这是最重要的配置，决定了您能使用哪些模型。

```python
# OpenAI API 密钥（也适用于 OpenAI 兼容的中转服务）
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# 通义千问 API 密钥
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"

# DeepSeek API 密钥
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"

# 智谱 AI API 密钥
ZHIPUAI_API_KEY = "xxxxxxxxxxxxxxxx"
```

您可以同时配置多个服务的密钥，系统会根据您选择的模型自动使用对应的密钥。

**多密钥负载均衡**：对于同一类型的 API，可以配置多个密钥实现负载均衡和容错：

```python
API_KEY = "sk-key1,sk-key2,sk-key3"  # 用英文逗号分隔
```

### 模型配置

```python
# 默认使用的模型（必须包含在 AVAIL_LLM_MODELS 中）
LLM_MODEL = "gpt-4o-mini"

# 可用模型列表（界面下拉菜单中显示的模型）
AVAIL_LLM_MODELS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo",
    "qwen-max", "qwen-turbo",
    "deepseek-chat", "deepseek-reasoner",
    "glm-4", "glm-3-turbo",
]
```

??? info "支持的模型前缀"
    除了标准模型名称，GPT Academic 还支持以下前缀格式接入更多模型：

    | 前缀 | 说明 | 示例 |
    |-----|------|------|
    | `openrouter-` | OpenRouter 路由服务 | `openrouter-openai/gpt-4o` |
    | `one-api-` | One-API 兼容服务 | `one-api-gpt-4(max_token=8000)` |
    | `azure-` | Azure OpenAI 服务 | `azure-gpt-4` |
    | `ollama-` | 本地 Ollama 模型 | `ollama-llama3(max_token=4096)` |

### 代理配置

如果您使用需要代理才能访问的服务（如 OpenAI 官方 API），需要配置代理：

```python
# 是否启用代理
USE_PROXY = True

# 代理设置（仅当 USE_PROXY = True 时生效）
proxies = {
    "http":  "http://127.0.0.1:7890",   # HTTP 代理
    "https": "http://127.0.0.1:7890",   # HTTPS 代理
}
```

!!! warning "代理格式"
    代理地址格式为 `[协议]://[地址]:[端口]`，请确保格式正确。常见协议有 `http`、`socks5h` 等，需要与您的代理软件匹配。

### URL 重定向

用于将请求重定向到中转服务或自建服务：

```python
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-proxy.com/v1/chat/completions"
}
```

---

## 界面配置

### 主题与布局

```python
# 颜色主题
THEME = "Default"
AVAIL_THEMES = ["Default", "Chuanhu-Small-and-Beautiful", "High-Contrast"]

# 窗口布局："LEFT-RIGHT"（左右布局）或 "TOP-DOWN"（上下布局）
LAYOUT = "LEFT-RIGHT"

# 暗色模式
DARK_MODE = True

# 对话窗口高度（仅 TOP-DOWN 布局生效）
CHATBOT_HEIGHT = 1115
```

### 输入行为

```python
# 是否在提交后自动清空输入框
AUTO_CLEAR_TXT = False

# 是否启用代码高亮
CODE_HIGHLIGHT = True
```

---

## 网络配置

```python
# Web 服务端口（-1 表示随机端口）
WEB_PORT = -1

# 是否自动打开浏览器
AUTO_OPEN_BROWSER = True

# 请求超时时间（秒）
TIMEOUT_SECONDS = 30

# 请求失败重试次数
MAX_RETRY = 2
```

---

## 高级配置

### 插件与功能

```python
# 默认显示的插件分类
DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']

# 多模型询问功能使用的模型（用 & 分隔）
MULTI_QUERY_LLM_MODELS = "gpt-4o&qwen-max"

# 并发线程数（免费用户建议设为 3）
DEFAULT_WORKER_NUM = 8

# 自定义按钮数量上限
NUM_CUSTOM_BASIC_BTN = 4
```

### 系统提示词

```python
# 默认的系统提示词
INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."
```

### 文档解析服务

以下配置与 PDF 论文翻译功能相关：

```python
# GROBID 服务地址（用于 PDF 解析）
# 公共服务可直接使用，也可自建私有实例
GROBID_URLS = [
    "https://qingxu98-grobid.hf.space",
    "https://qingxu98-grobid2.hf.space",
]

# Doc2X API 密钥（高质量 PDF 解析，推荐）
# 注册地址：https://doc2x.noedgeai.com/
DOC2X_API_KEY = ""

# Mathpix API 凭证（LaTeX 公式识别，可选）
MATHPIX_APPID = ""
MATHPIX_APPKEY = ""
```

### Arxiv 论文缓存

```python
# 翻译后的 Arxiv 论文缓存路径
ARXIV_CACHE_DIR = "gpt_log/arxiv_cache"
```

已翻译的 Arxiv 论文会被缓存到此目录，再次请求相同论文时直接返回缓存结果，节省时间和 API 费用。

---

## 环境变量配置

在 Docker 部署或需要通过环境变量配置时，变量名与配置项名称相同：

```bash
# 示例：通过环境变量配置
export API_KEY="sk-xxxxxxxx"
export LLM_MODEL="gpt-4o"
export USE_PROXY="False"
```

Docker Compose 配置示例：

```yaml title="docker-compose.yml"
services:
  gpt-academic:
    image: ghcr.io/binary-husky/gpt_academic
    environment:
      - API_KEY=sk-xxxxxxxx
      - LLM_MODEL=gpt-4o
      - USE_PROXY=False
    ports:
      - "7860:7860"
```

---

## 配置关系图

以下是主要配置项之间的依赖关系：

```
在线大模型配置
│
├── OpenAI 系列 (gpt-*)
│   ├── API_KEY
│   ├── USE_PROXY + proxies（国内需要）
│   └── API_URL_REDIRECT（中转时需要）
│
├── 通义千问 (qwen-*)
│   └── DASHSCOPE_API_KEY
│
├── DeepSeek (deepseek-*)
│   └── DEEPSEEK_API_KEY
│
├── 智谱 AI (glm-*)
│   └── ZHIPUAI_API_KEY
│
└── 中转服务 (one-api-*, openrouter-*)
    ├── API_KEY
    └── API_URL_REDIRECT
```

---

## 相关文档

- [快速上手](quickstart.md) — 配置第一个 API 并开始使用
- [基础操作](../features/basic_operations.md) — 了解界面交互和文件上传
- [中转渠道接入](../models/transit_api.md) — 使用第三方中转服务
- [Arxiv 论文翻译](../features/academic/arxiv_translation.md) — 一键翻译 Arxiv 论文
- [PDF 论文翻译](../features/academic/pdf_translation.md) — 翻译本地 PDF 文档
