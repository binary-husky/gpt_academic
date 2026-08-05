# 中转渠道接入指南

在某些场景下，您可能无法直接访问 OpenAI 等模型提供商的官方 API，或者希望通过统一的接口管理多种模型。这时，使用第三方中转服务是一个实用的解决方案。本指南将详细介绍如何在 GPT Academic 中配置和使用中转渠道。

---

## 什么是中转渠道

中转渠道（也称为 API 代理或 API 中转）是一类提供 **OpenAI 兼容接口** 的第三方服务。这些服务通常具有以下特点：

- **统一接口**：使用与 OpenAI 相同的 API 格式，无需修改调用代码
- **多模型聚合**：通过一个 API Key 访问多种大模型（GPT、Claude、Gemini 等）
- **网络优化**：提供国内可直接访问的节点，无需配置代理
- **成本优势**：部分服务提供更优惠的价格或免费额度

常见的中转服务包括：[OpenRouter](https://openrouter.ai/)、[One-API](https://github.com/songquanpeng/one-api)、[API2D](https://api2d.com/) 等。

---

## 接入方式概览

GPT Academic 提供了三种灵活的中转接入方式，您可以根据实际需求选择：

| 方式 | 适用场景 | 复杂度 |
|-----|---------|-------|
| **OpenRouter 前缀** | 使用 OpenRouter 服务 | ⭐ 简单 |
| **One-API 前缀** | 自建 One-API 或类似服务 | ⭐⭐ 中等 |
| **API_URL_REDIRECT** | 任意 OpenAI 兼容服务 | ⭐⭐ 中等 |

下面我们将逐一介绍每种方式的配置方法。

---

## 方式一：OpenRouter 接入

[OpenRouter](https://openrouter.ai/) 是一个流行的 AI 模型路由服务，聚合了 OpenAI、Anthropic、Google、Meta 等多家提供商的模型。通过 OpenRouter，您可以用一个 API Key 访问上百种模型。

### 获取 API Key

首先，访问 [OpenRouter](https://openrouter.ai/) 注册账户并获取 API Key。在 [Keys 页面](https://openrouter.ai/keys) 点击 **Create Key** 创建新密钥。

### 配置步骤

在 `config_private.py` 中添加以下配置：

```python
# OpenRouter API Key
API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 将 OpenRouter 模型添加到可用模型列表
AVAIL_LLM_MODELS = [
    "openrouter-openai/gpt-4o-mini",
    "openrouter-anthropic/claude-3.5-sonnet",
    "openrouter-google/gemini-pro-1.5",
    "openrouter-meta-llama/llama-3.1-70b-instruct",
    # 添加更多您需要的模型...
]

# 设置默认模型
LLM_MODEL = "openrouter-openai/gpt-4o-mini"
```

### 模型命名规则

使用 OpenRouter 时，模型名称需要遵循以下格式：

```
openrouter-{provider}/{model-name}
```

其中 `{provider}/{model-name}` 是 OpenRouter 上的模型标识符。您可以在 [OpenRouter Models](https://openrouter.ai/models) 页面浏览所有可用模型，复制模型 ID 后加上 `openrouter-` 前缀即可使用。

??? example "常用 OpenRouter 模型示例"
    | 模型名称 | GPT Academic 中的配置 |
    |---------|---------------------|
    | GPT-4o | `openrouter-openai/gpt-4o` |
    | GPT-4o Mini | `openrouter-openai/gpt-4o-mini` |
    | Claude 3.5 Sonnet | `openrouter-anthropic/claude-3.5-sonnet` |
    | Claude 3 Opus | `openrouter-anthropic/claude-3-opus` |
    | Gemini 1.5 Pro | `openrouter-google/gemini-pro-1.5` |
    | Llama 3.1 70B | `openrouter-meta-llama/llama-3.1-70b-instruct` |
    | DeepSeek V3 | `openrouter-deepseek/deepseek-chat` |

---

## 方式二：One-API 接入

[One-API](https://github.com/songquanpeng/one-api) 是一个开源的 API 管理和分发系统，支持自托管部署。如果您自己部署了 One-API 或使用基于 One-API 的第三方服务，可以通过 `one-api-` 前缀接入。

### 配置步骤

在 `config_private.py` 中添加以下配置：

```python
# One-API 服务的 API Key
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# 配置 URL 重定向，将请求指向您的 One-API 服务地址
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-one-api.com/v1/chat/completions"
}

# 添加模型到可用列表，格式为：one-api-{模型名}(max_token={最大token数})
AVAIL_LLM_MODELS = [
    "one-api-gpt-4o(max_token=128000)",
    "one-api-claude-3-sonnet-20240229(max_token=100000)",
    "one-api-gemini-1.5-pro(max_token=1000000)",
    # 添加更多您的 One-API 支持的模型...
]

# 设置默认模型
LLM_MODEL = "one-api-gpt-4o(max_token=128000)"
```

### 模型命名规则

One-API 模型的命名格式为：

```
one-api-{模型名}(max_token={最大token数})
```

其中：

- `{模型名}`：您在 One-API 后台配置的模型名称
- `(max_token=xxx)`：可选参数，指定模型的最大 Token 限制，用于自动裁剪上下文

!!! tip "关于 max_token 参数"
    `max_token` 参数帮助系统了解模型的上下文窗口大小，从而在对话过长时自动裁剪历史记录。如果不指定，系统会使用默认值。建议根据您使用的具体模型设置准确的值。

---

## 方式三：API_URL_REDIRECT 通用重定向

对于任何提供 OpenAI 兼容接口的服务，您都可以使用 `API_URL_REDIRECT` 配置进行 URL 重定向。这是最灵活的接入方式，适用于各种第三方中转服务。

### 配置方法

在 `config_private.py` 中设置 URL 重定向映射：

```python
# API 密钥（使用中转服务提供的密钥）
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# URL 重定向配置
API_URL_REDIRECT = {
    # 将 OpenAI 官方地址重定向到中转服务地址
    "https://api.openai.com/v1/chat/completions": "https://your-proxy.com/v1/chat/completions"
}

# 使用标准 OpenAI 模型名称
LLM_MODEL = "gpt-4o-mini"
AVAIL_LLM_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
```

### 多端点重定向

如果您需要同时重定向多个服务的端点，可以在字典中添加多个映射：

```python
API_URL_REDIRECT = {
    # OpenAI 聊天接口重定向
    "https://api.openai.com/v1/chat/completions": "https://proxy.example.com/v1/chat/completions",

    # Claude 接口重定向（如果需要）
    "https://api.anthropic.com/v1/messages": "https://proxy.example.com/anthropic/v1/messages",

    # Embedding 接口也会自动重定向
}
```

!!! warning "安全提示"
    使用 `API_URL_REDIRECT` 时，您的 API Key 和对话内容将发送到您指定的中转服务器。请确保您信任该服务提供商，并了解其隐私政策。

---

## 完整配置示例

以下是一个使用 OpenRouter 接入多种模型的完整配置示例：

```python title="config_private.py"
# ============ API 密钥配置 ============
# OpenRouter API Key
API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ============ 模型配置 ============
# 默认使用的模型
LLM_MODEL = "openrouter-openai/gpt-4o-mini"

# 可用模型列表
AVAIL_LLM_MODELS = [
    # OpenRouter 模型
    "openrouter-openai/gpt-4o-mini",
    "openrouter-openai/gpt-4o",
    "openrouter-anthropic/claude-3.5-sonnet",
    "openrouter-google/gemini-pro-1.5",
    "openrouter-deepseek/deepseek-chat",
]

# ============ 其他配置 ============
# 无需配置代理（OpenRouter 国内可直接访问）
USE_PROXY = False
```

---

## 验证配置

配置完成后，启动 GPT Academic 并进行测试：

1. 运行 `python main.py` 启动应用
2. 在界面左上角的模型下拉菜单中确认您配置的模型已显示
3. 选择一个模型，发送一条测试消息
4. 如果收到正常回复，说明配置成功

<!-- IMAGE: model_01_transit_verify.png -->
<!-- 描述: 界面左上角的模型下拉菜单展开状态，显示配置的中转模型列表 -->
<!-- 标注: 用红框标注模型下拉菜单位置，用箭头指向其中的 openrouter 或 one-api 模型 -->
<!-- 尺寸建议: 600px -->
![验证中转配置](../images/model_01_transit_verify.png)

---

## 常见问题

???+ question "OpenRouter 模型调用失败，提示 API Key 无效"
    请确认：

    1. API Key 格式正确（OpenRouter 的 Key 通常以 `sk-or-` 开头）
    2. Key 已在配置文件中正确设置
    3. OpenRouter 账户余额充足

???+ question "One-API 模型无法使用"
    请检查：

    1. `API_URL_REDIRECT` 中的地址是否正确（注意末尾不要有多余的斜杠）
    2. 模型名称是否与 One-API 后台配置的名称一致
    3. One-API 服务是否正常运行

???+ question "如何知道中转服务支持哪些模型？"
    这取决于您使用的具体中转服务：

    - **OpenRouter**：访问 [OpenRouter Models](https://openrouter.ai/models) 查看完整模型列表
    - **One-API**：在您的 One-API 后台查看已配置的渠道和模型
    - **其他服务**：参考服务商的文档或联系客服

---

## 相关文档

- [配置详解](../get_started/configuration.md) — 了解所有配置项的详细说明
- [模型概览](overview.md) — 查看所有支持的模型及其特点
- [OpenAI 接入](openai.md) — 直接使用 OpenAI 官方 API
