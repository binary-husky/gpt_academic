# OpenAI 接入指南

OpenAI 的 GPT 系列模型是目前最主流的大语言模型之一，以其强大的语言理解和生成能力著称。本指南将帮助您在 GPT Academic 中接入 OpenAI API，让您能够使用 GPT-4o、GPT-4、GPT-3.5 等模型进行学术写作、论文翻译、代码分析等任务。

---

## 准备工作

在开始配置之前，您需要准备以下内容：

| 必需项 | 说明 |
|-------|------|
| OpenAI 账号 | 用于获取和管理 API 密钥 |
| API Key | 在 OpenAI 平台创建的访问密钥 |
| 网络代理（国内用户） | OpenAI API 需要科学上网才能访问 |

如果您位于中国大陆且没有稳定的网络代理，建议优先考虑使用[国产模型](chinese_models.md)或通过[中转渠道](transit_api.md)接入。

---

## 获取 API Key

首先，您需要在 OpenAI 平台获取 API 密钥。这个密钥是访问 OpenAI 服务的凭证，请妥善保管。

登录 [OpenAI Platform](https://platform.openai.com/)，在左侧导航栏中点击 **API Keys** 进入密钥管理页面。如果这是您第一次使用，可能需要先设置付款方式。

在 API Keys 页面，点击 **Create new secret key** 按钮创建新密钥。您可以为密钥添加一个便于识别的名称，例如"GPT Academic"。点击创建后，页面会显示您的 API Key——这是唯一一次完整显示密钥的机会，请立即复制并安全保存。

<!-- IMAGE: model_openai_01_apikey.png -->
<!-- 描述: OpenAI Platform 的 API Keys 页面 -->
<!-- 标注: ① 左侧导航栏的 "API Keys" 入口 ② "Create new secret key" 按钮位置 ③ 显示新创建密钥的弹窗（密钥部分打码） -->
<!-- 尺寸建议: 1000px -->
![OpenAI API Keys 页面](../images/model_openai_01_apikey.png)

!!! warning "密钥安全"
    API Key 一旦创建后无法再次查看完整内容。如果丢失，您需要删除旧密钥并创建新的。请勿将密钥提交到 Git 仓库或分享给他人。

---

## 配置 API Key

获取密钥后，您需要在 GPT Academic 中进行配置。推荐在项目根目录创建 `config_private.py` 文件来存放个人配置，这个文件不会被 Git 追踪，能有效保护您的密钥安全。

在 `config_private.py` 中添加以下配置：

```python title="config_private.py"
# OpenAI API 密钥
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 设置默认模型
LLM_MODEL = "gpt-4o-mini"

# 可用模型列表
AVAIL_LLM_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
]
```

OpenAI 的 API Key 通常以 `sk-` 开头，长度约 50 个字符。请确保复制时没有多余的空格或换行符。

### 多密钥负载均衡

如果您拥有多个 API Key（例如团队共享多个账号），可以将它们用英文逗号分隔配置在一起。系统会自动在多个密钥之间轮询，既能分摊使用额度，又能在单个密钥失效时保持服务可用：

```python
API_KEY = "sk-key1xxxxxxxx,sk-key2xxxxxxxx,sk-key3xxxxxxxx"
```

---

## 配置网络代理

对于位于中国大陆的用户，直接访问 OpenAI API 通常会遇到网络问题。您需要配置代理才能正常使用。

在 `config_private.py` 中添加代理配置：

```python title="config_private.py"
# 启用代理
USE_PROXY = True

# 代理地址配置
proxies = {
    "http":  "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
```

这里的 `127.0.0.1:7890` 需要替换为您的代理软件实际监听的地址和端口。不同的代理软件有不同的默认端口，您需要打开代理软件的设置界面查看具体信息。

常见代理软件的默认配置参考：

| 代理软件 | 协议 | 默认端口 | 配置示例 |
|---------|------|---------|---------|
| Clash | HTTP | 7890 | `http://127.0.0.1:7890` |
| V2Ray | SOCKS5 | 10808 | `socks5h://127.0.0.1:10808` |
| Shadowsocks | SOCKS5 | 1080 | `socks5h://127.0.0.1:1080` |

!!! tip "协议选择"
    如果您不确定代理协议，可以先尝试 `http://` 格式。大多数代理软件同时支持 HTTP 和 SOCKS5 协议。如果 HTTP 不工作，再尝试 `socks5h://` 格式。

**海外服务器部署**：如果您的 GPT Academic 部署在海外服务器上，可以直接访问 OpenAI API，无需配置代理。保持 `USE_PROXY = False`（默认值）即可。

---

## 选择模型

OpenAI 提供了多种模型，各有特点。以下是主要模型的对比，帮助您根据需求选择：

| 模型 | 特点 | 推荐场景 |
|-----|------|---------|
| **gpt-4o** | 最强多模态模型，支持图像理解 | 复杂推理、图像分析、重要文档处理 |
| **gpt-4o-mini** | 性价比最高，速度快 | 日常对话、一般翻译、代码辅助 |
| **gpt-4-turbo** | 128K 超长上下文 | 长文档分析、完整论文翻译 |
| **gpt-3.5-turbo** | 成本最低，响应快 | 简单任务、大批量处理 |
| **o1** / **o1-mini** | 推理增强模型 | 数学推导、复杂逻辑分析 |

对于学术场景，我们的建议是：

- **论文翻译**：优先使用 `gpt-4o` 或 `gpt-4-turbo`，翻译质量更高
- **日常问答**：使用 `gpt-4o-mini`，响应速度快且成本较低
- **代码分析**：`gpt-4o` 或 `gpt-4o-mini` 均可胜任
- **长文档处理**：选择 `gpt-4-turbo`，其 128K 上下文能处理完整论文

---

## 验证配置

完成上述配置后，启动 GPT Academic 验证是否配置成功：

```bash
python main.py
```

应用启动后，在浏览器中打开显示的地址（通常是 `http://localhost:端口号`）。界面左上角的模型下拉菜单中应该显示您配置的 OpenAI 模型。选择一个模型，在输入框中输入测试消息，例如"你好"，然后点击提交。

如果收到正常回复，说明配置成功。如果遇到错误，请参考下方的常见问题排查。

---

## 高级配置

对于有特殊需求的用户，GPT Academic 还提供了一些高级配置选项。

### API URL 重定向

如果您使用第三方 OpenAI 兼容服务（如 Azure OpenAI 或 API 中转服务），可以通过 URL 重定向将请求指向自定义地址：

```python
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-custom-endpoint.com/v1/chat/completions"
}
```

### 组织 ID 配置

在极少数情况下（通常是企业账号），您可能需要在请求中附带组织 ID：

```python
API_ORG = "org-xxxxxxxxxxxxxxxxxxxxxxxx"
```

大多数个人用户无需配置此项。

### 请求超时设置

如果您的网络环境不稳定，可以调整请求超时时间：

```python
TIMEOUT_SECONDS = 60  # 默认 30 秒
```

### 并发数配置

在使用论文翻译等多线程插件时，并发请求数会影响处理速度。免费试用账户的速率限制较低，付费账户可以适当提高：

```python
# 免费账户建议设为 3
# 付费账户可设为 8-16 或更高
DEFAULT_WORKER_NUM = 8
```

---

## 常见问题

???+ question "提示 'API Key 无效' 或 'Invalid API Key'"
    这通常是密钥配置问题。请检查以下几点：

    1. 确认密钥已正确复制，没有多余空格或换行
    2. 检查密钥格式是否以 `sk-` 开头
    3. 确认密钥未被撤销（在 OpenAI 平台检查）
    4. 如果使用多密钥配置，确保用英文逗号分隔

???+ question "提示 '连接超时' 或 'Connection Timeout'"
    这是网络连接问题，国内用户最常遇到。解决方法：

    1. 确认 `USE_PROXY = True` 已设置
    2. 检查代理软件是否正常运行
    3. 验证 `proxies` 中的端口号是否正确
    4. 尝试在命令行中运行 `curl https://api.openai.com` 测试连通性

???+ question "提示 'Rate limit exceeded'"
    这表示 API 调用频率超过限制。处理方法：

    - 等待一段时间后重试
    - 降低 `DEFAULT_WORKER_NUM` 的值
    - 配置多个 API Key 分摊请求

???+ question "提示 'Insufficient quota' 或 '余额不足'"
    您的 OpenAI 账户额度已用完。需要在 [OpenAI Billing](https://platform.openai.com/account/billing) 页面充值。

???+ question "模型下拉菜单中没有显示我配置的模型"
    请检查 `AVAIL_LLM_MODELS` 配置是否正确，并确保 `LLM_MODEL` 的值包含在 `AVAIL_LLM_MODELS` 列表中。

---

## 相关文档

- [配置详解](../get_started/configuration.md) — 了解配置系统的完整说明
- [中转渠道接入](transit_api.md) — 使用 OpenRouter 等中转服务接入 OpenAI
- [国产模型接入](chinese_models.md) — 通义千问、智谱等国内替代方案
- [Azure OpenAI 接入](azure.md) — 使用 Azure 提供的 OpenAI 服务
