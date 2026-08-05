# 模型支持概览

GPT Academic 的核心优势之一是对多种大语言模型的广泛支持。无论您希望使用 OpenAI 的 GPT 系列、国内的通义千问和智谱 GLM，还是在本地部署开源模型，GPT Academic 都提供了统一的接入方式。本文将帮助您了解各类模型的特点，并选择最适合您需求的配置方案。

---

## 模型分类

根据部署方式的不同，GPT Academic 支持的模型可分为**在线模型**和**本地模型**两大类。在线模型通过 API 调用云端服务，配置简单、无需显卡；本地模型运行在您自己的机器上，适合对数据隐私有要求的场景。

### 在线模型一览

下表列出了主要的在线模型服务商及其代表性模型：

| 服务商 | 代表模型 | 配置难度 | 特点 |
|-------|---------|:-------:|------|
| OpenAI | `gpt-4o`, `gpt-4-turbo`, `o1` | ⭐⭐ | 综合能力最强，需要海外网络或代理 |
| 通义千问 | `qwen-max`, `qwen-turbo` | ⭐ | 国内直连，中文理解优秀 |
| 智谱 AI | `glm-4`, `glm-4v`, `glm-3-turbo` | ⭐ | 国内直连，支持多模态 |
| DeepSeek | `deepseek-chat`, `deepseek-reasoner` | ⭐ | 推理能力突出，性价比高 |
| Azure OpenAI | `azure-gpt-4`, `azure-gpt-3.5` | ⭐⭐⭐ | 企业级服务，合规性好 |
| Google | `gemini-1.5-pro`, `gemini-1.5-flash` | ⭐⭐ | 超长上下文支持 |
| Anthropic | `claude-3-opus`, `claude-3-sonnet` | ⭐⭐ | 对话安全性高，长文本处理好 |
| 百度千帆 | `ERNIE-Bot-4`, `ERNIE-Bot` | ⭐⭐ | 国内直连，企业服务支持 |
| 讯飞星火 | `sparkv4`, `sparkv3.5` | ⭐⭐ | 国内直连，语音能力强 |
| 月之暗面 | `moonshot-v1-128k` | ⭐ | 超长上下文，适合长文档 |
| 零一万物 | `yi-large`, `yi-medium` | ⭐ | 开源血统，性价比高 |
| 火山引擎 | `volcengine-deepseek-r1` | ⭐ | DeepSeek 托管服务 |

### 本地模型支持

如果您有足够的硬件资源，可以在本地部署开源模型。本地模型的优势是数据完全不出本地，适合处理敏感信息：

| 模型 | 显存需求 | 配置难度 | 说明 |
|-----|:-------:|:-------:|------|
| ChatGLM4-9B | 24GB+ | ⭐⭐⭐ | 智谱开源模型，中文效果好 |
| ChatGLM3-6B | 13GB+ | ⭐⭐⭐ | 资源需求较低，适合入门 |
| Qwen-Local | 依版本 | ⭐⭐⭐ | 通义千问开源版本 |
| DeepSeek-Coder | 16GB+ | ⭐⭐⭐ | 代码生成专用模型 |
| LLaMA 2 | 依版本 | ⭐⭐⭐⭐ | Meta 开源模型 |
| MOSS | 16GB+ | ⭐⭐⭐⭐ | 复旦大学开源模型 |

!!! warning "硬件要求"
    本地模型对显卡显存有较高要求。以 ChatGLM4-9B 为例，FP16 精度需要约 24GB 显存，INT4 量化版本则可降至 8GB 左右。如果您没有高性能显卡，建议优先选择在线模型服务。

---

## 模型选择建议

面对众多模型选项，如何选择最适合自己的配置？以下是针对不同场景的推荐方案。

### 场景一：国内用户快速上手

如果您身处中国大陆，希望无需配置代理就能快速开始使用，**通义千问**是最佳选择。阿里云百炼平台提供了慷慨的免费额度，注册后即可获取 API KEY，配置过程只需一步：

```python
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"
LLM_MODEL = "qwen-max"
```

通义千问在中文理解和生成方面表现优异，能够胜任大部分学术写作和代码分析任务。如果追求更快的响应速度，可以将 `LLM_MODEL` 改为 `qwen-turbo`。

### 场景二：追求最强能力

当您需要处理复杂的推理任务、进行高质量的论文翻译或代码分析时，**GPT-4o** 或 **DeepSeek-R1** 是更好的选择。GPT-4o 在各类评测中名列前茅，尤其擅长长文本理解和多步推理；DeepSeek-R1 则在数学推理方面表现突出。

使用 GPT-4o 需要配置 OpenAI API KEY 和代理：

```python
API_KEY = "sk-xxxxxxxxxxxxxxxx"
LLM_MODEL = "gpt-4o"
USE_PROXY = True
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
```

DeepSeek 则可以直连，配置更为简单：

```python
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"
LLM_MODEL = "deepseek-reasoner"  # 推理增强版本
```

### 场景三：数据安全优先

如果您处理的是敏感数据，不希望内容发送到云端，本地部署模型是唯一选择。ChatGLM 系列是最成熟的方案：

```python
LLM_MODEL = "chatglm4"
CHATGLM_LOCAL_MODEL_PATH = "THUDM/glm-4-9b-chat"
LOCAL_MODEL_DEVICE = "cuda"
```

本地模型的详细部署教程请参阅 [本地模型部署](local_models.md) 文档。

### 场景四：多模态任务

如果您需要让 AI 分析图片内容（如图表解读、公式识别），必须选择支持视觉能力的多模态模型：

- `gpt-4o` / `gpt-4o-mini`（OpenAI）
- `gpt-4-vision-preview`（OpenAI）
- `glm-4v`（智谱 AI）
- `qwen-vl-max`（通义千问，需单独配置）

---

## 配置多个模型

GPT Academic 支持同时配置多个模型，并在使用时通过界面切换。这让您可以根据任务特点灵活选择最合适的模型。

### 配置 AVAIL_LLM_MODELS

在 `config_private.py` 中，通过 `AVAIL_LLM_MODELS` 列表定义可用的模型：

```python
AVAIL_LLM_MODELS = [
    "qwen-max",           # 通义千问
    "gpt-4o",             # OpenAI GPT-4o
    "gpt-3.5-turbo",      # OpenAI GPT-3.5
    "deepseek-chat",      # DeepSeek
    "glm-4",              # 智谱 GLM-4
]
```

配置后，这些模型会出现在界面左上角的模型下拉菜单中。`LLM_MODEL` 指定的是默认选中的模型，它必须包含在 `AVAIL_LLM_MODELS` 列表中。

### 配置对应的 API KEY

每类模型需要配置对应的 API KEY：

```python
# OpenAI 系列
API_KEY = "sk-openai-key"

# 通义千问
DASHSCOPE_API_KEY = "sk-dashscope-key"

# 智谱 AI
ZHIPUAI_API_KEY = "zhipu-key"

# DeepSeek
DEEPSEEK_API_KEY = "sk-deepseek-key"
```

如果某个模型的 API KEY 未配置，在切换到该模型时会收到错误提示。

### 使用 One-API 统一管理

对于需要管理多个 API 的高级用户，可以部署 [One-API](https://github.com/songquanpeng/one-api) 或类似的 API 管理服务，将所有模型统一为 OpenAI 兼容格式，然后通过前缀方式接入：

```python
AVAIL_LLM_MODELS = [
    "one-api-gpt-4o(max_token=128000)",
    "one-api-claude-3-opus(max_token=200000)",
]
```

---

## 模型能力对比

为帮助您做出选择，下表对比了主流模型在几个关键维度上的表现：

| 模型 | 中文能力 | 代码能力 | 推理能力 | 响应速度 | 成本 |
|-----|:-------:|:-------:|:-------:|:-------:|:----:|
| GPT-4o | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★☆ | 高 |
| GPT-3.5-Turbo | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ | 低 |
| Qwen-Max | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | 中 |
| DeepSeek-R1 | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | 低 |
| GLM-4 | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | 中 |
| Claude-3-Opus | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | 高 |

!!! info "评分说明"
    以上评分基于公开评测数据和用户反馈，仅供参考。实际表现可能因具体任务而异，建议根据您的实际需求进行测试比较。

---

## 常见问题

??? question "如何判断当前使用的是哪个模型？"
    界面左上角的下拉菜单显示了当前选中的模型。此外，每次对话开始时，系统也会在内部记录使用的模型信息。

??? question "切换模型后历史记录会清空吗？"
    不会。切换模型只影响后续的对话请求，之前的历史记录会保留。但请注意，不同模型对上下文的理解可能存在差异。

??? question "为什么有些模型响应很慢？"
    响应速度受多个因素影响：模型本身的推理速度、服务商的负载情况、网络延迟等。GPT-4 系列和 Claude Opus 等大模型通常比 GPT-3.5 慢。如果追求速度，可以选择 `gpt-3.5-turbo` 或 `qwen-turbo`。

??? question "可以使用 Ollama 或 vLLM 部署的模型吗？"
    可以。GPT Academic 支持通过前缀方式接入非标准部署的模型，例如：
    ```python
    AVAIL_LLM_MODELS = [
        "ollama-llama3(max_token=8192)",
        "vllm-qwen2(max_token=32000)",
    ]
    ```
    您需要同时配置 `API_URL_REDIRECT` 将请求指向正确的服务地址。

---

## 相关文档

- [OpenAI / GPT 接入](openai.md) — 详细的 OpenAI 配置教程
- [国产模型接入](chinese_models.md) — 通义、智谱、DeepSeek 等国产模型配置
- [本地模型部署](local_models.md) — ChatGLM 等本地模型的部署方法
- [配置详解](../get_started/configuration.md) — 完整的配置项说明
