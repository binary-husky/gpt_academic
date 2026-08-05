# Azure OpenAI 接入

对于企业用户和需要更高稳定性的场景，微软 Azure 提供的 OpenAI 服务是一个值得考虑的选择。相比直接使用 OpenAI API，Azure OpenAI 在国内网络环境下通常具有更好的连接稳定性，同时提供企业级的安全合规保障。

本文将引导您完成 Azure OpenAI 服务的申请和配置。整个过程包括在 Azure 平台创建资源、部署模型，以及在 GPT Academic 中配置连接参数。

---

## 前置准备

在开始之前，您需要准备以下内容：

| 项目 | 说明 |
|-----|------|
| 微软账号 | 用于登录 Azure 门户 |
| Azure 订阅 | 可使用免费试用或付费订阅 |
| OpenAI 服务访问权限 | 需要申请并获得批准 |

!!! note "关于访问权限"
    Azure OpenAI 服务目前需要单独申请访问权限。新用户在创建 Azure 账户后，需要填写申请表格，通常在 1-5 个工作日内获得批准。申请地址：[aka.ms/oai/access](https://aka.ms/oai/access)

---

## 创建 Azure OpenAI 资源

获得访问权限后，登录 [Azure 门户](https://portal.azure.com)，按照以下步骤创建 OpenAI 资源。

首先，在门户顶部的搜索栏中输入"OpenAI"，从搜索结果中选择"Azure OpenAI"服务。进入服务页面后，点击"创建"按钮开始创建新资源。

在创建页面中，您需要填写以下关键信息：

- **订阅**：选择您的 Azure 订阅
- **资源组**：选择现有资源组或创建新的资源组
- **区域**：选择距离您较近的区域（如 East US、Japan East 等）
- **名称**：为资源指定一个唯一名称，这将成为您 API 终结点的一部分

完成填写后，点击"查看 + 创建"，确认信息无误后点击"创建"。部署通常需要几分钟时间。

---

## 部署模型

资源创建完成后，需要在其中部署具体的模型才能使用。点击资源页面中的"转到资源"，然后选择"模型部署"或直接访问 [Azure OpenAI Studio](https://oai.azure.com/)。

在 Azure OpenAI Studio 中，点击左侧导航栏的"部署"，然后点击"创建新部署"。在弹出的对话框中选择要部署的模型（如 gpt-4、gpt-35-turbo 等），并为部署指定一个名称。

<!-- IMAGE: model_azure_01_deployment.png -->
<!-- 描述: Azure OpenAI Studio 的模型部署界面，展示选择模型和填写部署名称的对话框 -->
<!-- 标注: 用红框标注"模型"下拉菜单和"部署名"输入框 -->
<!-- 尺寸建议: 800px -->
![模型部署](../images/model_azure_01_deployment.png)

!!! warning "重要：记录部署名称"
    请务必记录您填写的**部署名称**（Deployment Name），后续配置时需要使用。注意：部署名称不是模型名称，而是您自己指定的名称。

部署完成后，返回 Azure 门户的资源页面，在"资源管理"→"密钥和终结点"中，您可以找到后续配置所需的三个关键信息：

- **密钥**（KEY 1 或 KEY 2，任选其一）
- **终结点**（Endpoint）
- **部署名**（您刚才创建时指定的名称）

---

## 配置方式一：单模型部署

如果您只需要使用一个 Azure OpenAI 模型，可以使用这种简单的配置方式。在 `config_private.py` 中添加以下内容：

```python
# Azure OpenAI 单模型配置
LLM_MODEL = "azure-gpt-35-turbo"  # 模型标识必须以 azure- 开头

# Azure 连接参数
AZURE_ENDPOINT = "https://你的资源名称.openai.azure.com/"  # 替换为您的终结点
AZURE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"         # 替换为您的密钥
AZURE_ENGINE = "你的部署名称"                               # 替换为您的部署名
AZURE_API_VERSION = "2024-02-15-preview"                   # API 版本，一般无需修改

# 将模型添加到可用列表
AVAIL_LLM_MODELS = ["azure-gpt-35-turbo", "azure-gpt-4"]
```

几点重要说明：

`LLM_MODEL` 的值必须以 `azure-` 开头，后面跟随的名称可以自定义，通常使用与 OpenAI 模型名相近的命名以便识别。

`AZURE_ENDPOINT` 是您资源的终结点 URL，格式为 `https://{资源名称}.openai.azure.com/`。注意末尾的斜杠不要遗漏。

`AZURE_ENGINE` 是您在 Azure OpenAI Studio 中创建部署时指定的**部署名称**，而不是模型名称（如 gpt-4）。这是配置中最容易出错的地方。

---

## 配置方式二：多模型部署

如果您在 Azure 上部署了多个模型（如同时部署了 GPT-3.5 和 GPT-4），可以使用 `AZURE_CFG_ARRAY` 配置，实现在界面上动态切换模型。

```python
# Azure OpenAI 多模型配置
AZURE_CFG_ARRAY = {
    # 第一个模型：GPT-3.5
    "azure-gpt-35-turbo": {
        "AZURE_ENDPOINT": "https://你的资源名称.openai.azure.com/",
        "AZURE_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "AZURE_ENGINE": "gpt35-deployment",      # 第一个部署的名称
        "AZURE_MODEL_MAX_TOKEN": 4096,           # 模型最大 token 数
    },

    # 第二个模型：GPT-4
    "azure-gpt-4": {
        "AZURE_ENDPOINT": "https://你的资源名称.openai.azure.com/",
        "AZURE_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "AZURE_ENGINE": "gpt4-deployment",       # 第二个部署的名称
        "AZURE_MODEL_MAX_TOKEN": 8192,
    },

    # 第三个模型：GPT-4 32K（如果有）
    "azure-gpt-4-32k": {
        "AZURE_ENDPOINT": "https://你的资源名称.openai.azure.com/",
        "AZURE_API_KEY": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",  # 可以使用不同的密钥
        "AZURE_ENGINE": "gpt4-32k-deployment",
        "AZURE_MODEL_MAX_TOKEN": 32768,
    },
}

# 设置默认模型
LLM_MODEL = "azure-gpt-35-turbo"

# 将所有 Azure 模型添加到可用列表
AVAIL_LLM_MODELS = ["azure-gpt-35-turbo", "azure-gpt-4", "azure-gpt-4-32k"]
```

使用这种配置方式时，每个模型都需要单独配置完整的连接参数。字典的键（如 `"azure-gpt-35-turbo"`）将作为模型标识符，出现在界面的模型下拉菜单中。

!!! tip "混合使用多种 API"
    您可以在 `AVAIL_LLM_MODELS` 中同时包含 Azure 模型和其他模型（如 OpenAI、国产模型等），实现在同一界面上灵活切换不同来源的模型：

    ```python
    AVAIL_LLM_MODELS = [
        "azure-gpt-4",         # Azure
        "gpt-4o",              # OpenAI 直连
        "qwen-max",            # 通义千问
        "deepseek-chat",       # DeepSeek
    ]
    ```

---

## 验证配置

完成配置后，启动 GPT Academic 验证连接是否正常：

```bash
python main.py
```

在浏览器中打开界面，从模型下拉菜单中选择您配置的 Azure 模型（如 `azure-gpt-35-turbo`），然后发送一条测试消息。如果收到正常回复，说明配置成功。

如果遇到错误，请检查终端输出的错误信息。常见问题包括：

- **401 Unauthorized**：API 密钥错误或已失效
- **404 Not Found**：部署名称（AZURE_ENGINE）错误
- **Resource not found**：终结点 URL 错误

---

## 常见问题

### 连接超时

???+ question "请求 Azure OpenAI 时频繁超时"
    Azure OpenAI 的服务器位于海外，国内用户可能偶尔遇到网络波动。您可以尝试：

    1. 选择距离较近的 Azure 区域（如 Japan East）
    2. 适当增加超时时间，在 `config_private.py` 中设置：
       ```python
       TIMEOUT_SECONDS = 60  # 默认 30 秒
       ```

### 配额限制

???+ question "提示 Rate limit exceeded"
    Azure OpenAI 对每分钟请求数（RPM）和每分钟 token 数（TPM）有配额限制。免费试用和低级别订阅的配额较低。

    解决方案：

    1. 在 Azure 门户中申请提升配额
    2. 在 GPT Academic 中降低并发请求数
    3. 升级 Azure 订阅等级

### 模型不可用

???+ question "某些模型显示不可用"
    Azure OpenAI 的模型可用性因区域而异。例如，GPT-4 可能在某些区域尚未开放。请查阅 [Azure OpenAI 模型可用性](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability) 文档，确认您选择的区域支持所需模型。

---

## 关于费用

Azure OpenAI 采用按量计费模式，费用与直接使用 OpenAI API 相近。主要计费项目包括：

- 输入 token 费用
- 输出 token 费用
- 部分高级模型可能有额外费用

新用户注册 Azure 通常可获得一定额度的免费试用金（约 $200），足够进行初步测试和评估。具体定价请参阅 [Azure OpenAI 定价页面](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)。

---

## 下一步

Azure OpenAI 配置完成后，您可以：

- 了解更多 [配置详解](../get_started/configuration.md) 中的高级选项
- 探索 [多模型询问](../features/conversation/multi_model_query.md) 功能，对比 Azure 与其他模型的表现
- 如果您的企业需要更复杂的部署方案，请参阅 [Docker 部署](../deployment/docker.md) 文档
