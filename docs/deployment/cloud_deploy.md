# 云服务部署

对于没有本地服务器或希望快速体验的用户，云服务部署是一个极具吸引力的选择。通过云平台提供的容器化服务，您可以在几分钟内完成部署，无需关心底层运维，甚至可以获得免费的计算资源。本文将介绍几种主流的云部署方案，帮助您选择最适合自己的方式。

---

## 部署方案概览

不同的云平台有各自的特点和适用场景。在选择之前，您可以参考下表进行比较：

| 平台 | 免费额度 | 部署难度 | 特点 | 适用场景 |
|------|---------|---------|------|---------|
| Sealos | 赠送余额 | ⭐ 简单 | 国内访问快，支持自定义域名 | 国内用户首选 |
| HuggingFace Spaces | 免费 | ⭐ 简单 | 社区活跃，可直接 Fork | 快速体验、学习 |
| Railway | 免费额度 | ⭐⭐ 中等 | 自动部署，GitHub 集成 | 开发测试 |
| Render | 免费额度 | ⭐⭐ 中等 | 支持后台任务 | 长期运行服务 |

对于大多数国内用户，我们推荐使用 **Sealos** 进行部署，它提供了友好的中文界面和稳定的国内访问速度。如果您希望快速体验或参与社区交流，**HuggingFace Spaces** 是另一个不错的选择。

---

## Sealos 部署

Sealos 是一个基于 Kubernetes 的云操作系统，提供了开箱即用的容器部署能力。它对国内用户非常友好，网络访问稳定，新用户注册即可获得免费余额。

### 注册账号

访问 [Sealos 官网](https://sealos.io/) 并完成注册。您可以使用 GitHub、微信或手机号登录。注册完成后，系统会自动赠送一定的免费额度，足够您运行 GPT Academic 数天。

### 创建应用

登录后进入控制台，点击「应用管理」进入应用部署界面。Sealos 支持直接使用 Docker 镜像部署，这意味着您可以复用项目官方提供的镜像，无需重新构建。

在创建新应用时，填写以下核心配置：

**基础配置**：

- **应用名称**：`gpt-academic`（或任意您喜欢的名称）
- **镜像地址**：`ghcr.io/binary-husky/gpt_academic_nolocal:master`
- **CPU / 内存**：推荐 1 核 2GB，足够日常使用

**环境变量**：

这是最关键的配置部分。您需要添加以下环境变量来配置 API 密钥和模型选项：

```
API_KEY=sk-your-openai-key-here
LLM_MODEL=gpt-3.5-turbo
AVAIL_LLM_MODELS=["gpt-3.5-turbo", "gpt-4", "qwen-max"]
WEB_PORT=12345
```

如果您使用国产模型（推荐国内用户），配置如下：

```
DASHSCOPE_API_KEY=sk-your-dashscope-key
LLM_MODEL=qwen-max
AVAIL_LLM_MODELS=["qwen-max", "qwen-turbo", "gpt-3.5-turbo"]
WEB_PORT=12345
```

!!! tip "使用国产模型的优势"
    在 Sealos 上部署时，使用通义千问等国产模型无需配置代理，可以直接访问，配置更简单、响应更快。

**网络配置**：

- **容器端口**：`12345`（与 `WEB_PORT` 环境变量一致）
- **开启外网访问**：勾选此选项，Sealos 会自动分配一个公网域名

### 启动与访问

完成配置后点击「部署应用」，Sealos 会自动拉取镜像并启动容器。整个过程通常需要 1-3 分钟。部署成功后，您可以在应用详情页看到系统分配的访问地址，点击即可打开 GPT Academic 界面。

如果您有自己的域名，还可以在「网络配置」中绑定自定义域名，使访问地址更加简洁易记。

---

## HuggingFace Spaces 部署

HuggingFace Spaces 是 AI 社区最受欢迎的应用托管平台之一。它允许用户免费部署 Gradio 和 Streamlit 应用，并且可以直接 Fork 他人的 Space 进行二次开发。

### Fork 官方 Space

最快速的方式是直接复制一个已有的 GPT Academic Space：

1. 访问 [HuggingFace Spaces](https://huggingface.co/spaces)，搜索 `gpt_academic`
2. 选择一个活跃的 Space，点击右上角的「Duplicate this Space」
3. 在弹出的对话框中设置您的 Space 名称和可见性

Fork 完成后，您就拥有了一个属于自己的 GPT Academic 实例。但此时它还无法正常工作，因为您需要配置 API 密钥。

### 配置 Secrets

为了安全地存储 API 密钥，HuggingFace 提供了 Secrets 功能。进入您的 Space 设置页面，找到「Repository secrets」部分，添加以下密钥：

| Secret 名称 | 值 | 说明 |
|------------|---|------|
| `API_KEY` | `sk-xxx` | OpenAI API 密钥 |
| `DASHSCOPE_API_KEY` | `sk-xxx` | 通义千问密钥（可选） |

添加完成后，重新启动 Space，系统会自动读取这些 Secrets 作为环境变量。

!!! warning "隐私提示"
    请注意 HuggingFace Space 默认是公开的，任何人都可以访问。如果您担心隐私问题，可以将 Space 设置为私有（需要付费账户），或者使用 `AUTHENTICATION` 环境变量设置访问密码：
    ```
    AUTHENTICATION=[["username", "password"]]
    ```

### 自定义部署

如果您希望从头创建 Space 或进行深度定制，可以使用 Dockerfile 方式部署：

1. 创建一个新的 Space，选择「Docker」作为 SDK
2. 在 Space 的文件管理器中上传项目的 `Dockerfile` 和必要文件
3. 或者直接将您的 GitHub 仓库连接到 Space，实现自动同步

HuggingFace 会根据 Dockerfile 自动构建镜像并部署。由于免费版资源有限（2 vCPU，16GB RAM），建议使用轻量级镜像，避免加载本地模型。

---

## Railway 部署

Railway 是一个面向开发者的云平台，以简洁的界面和 GitHub 集成著称。它提供每月 5 美元的免费额度，支持 Docker 镜像部署。

### 快速部署流程

1. 访问 [Railway](https://railway.app/) 并使用 GitHub 账号登录
2. 点击「New Project」→「Deploy from Docker Image」
3. 输入镜像地址：`ghcr.io/binary-husky/gpt_academic_nolocal:master`
4. 在「Variables」标签页添加环境变量（与 Sealos 配置相同）
5. 在「Settings」中配置公开端口和域名

Railway 的一大特点是支持直接从 GitHub 仓库部署。如果您 Fork 了 GPT Academic 仓库并进行了自定义修改，可以选择「Deploy from GitHub Repo」，Railway 会自动检测项目中的 Dockerfile 并构建部署。每次您向仓库推送代码，Railway 都会自动触发重新部署，非常适合开发迭代。

---

## Render 部署

Render 是另一个受欢迎的云托管平台，提供免费的 Web 服务托管。与 Railway 类似，它也支持 Docker 镜像和 GitHub 仓库部署。

### 部署步骤

1. 注册 [Render](https://render.com/) 账号
2. 创建新的「Web Service」
3. 选择部署方式：
   - **Docker 镜像**：填入 `ghcr.io/binary-husky/gpt_academic_nolocal:master`
   - **GitHub 仓库**：连接您 Fork 的仓库
4. 配置环境变量
5. 设置实例类型（免费版足够体验）

!!! note "冷启动问题"
    Render 免费版实例在闲置 15 分钟后会休眠，下次访问时需要等待约 30 秒的冷启动时间。如果您需要服务始终在线，需要升级到付费方案。

---

## 部署后配置

无论选择哪个云平台，部署完成后您可能还需要进行一些额外配置。

### 设置访问密码

在公开的云环境中，建议设置访问密码保护您的服务。添加环境变量：

```
AUTHENTICATION=[["admin", "your-secure-password"]]
```

设置后，访问页面时需要输入用户名和密码才能使用。您可以设置多组账号密码，用于分享给不同的用户。

### 配置多个模型

如果您同时拥有多个模型的 API 密钥，可以在 `AVAIL_LLM_MODELS` 中列出所有可用模型：

```
AVAIL_LLM_MODELS=["qwen-max", "gpt-4o", "gpt-3.5-turbo", "deepseek-chat", "glm-4"]
```

同时配置相应的 API 密钥：

```
DASHSCOPE_API_KEY=sk-xxx
API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
ZHIPUAI_API_KEY=xxx
```

这样用户就可以在界面中自由切换不同的模型，体验各家大模型的能力差异。

### 绑定自定义域名

大多数云平台都支持绑定自定义域名。以 Sealos 为例：

1. 在应用的网络配置中，添加您的域名（如 `chat.example.com`）
2. 在您的域名 DNS 管理面板中，添加 CNAME 记录，指向平台提供的地址
3. 等待 DNS 生效（通常几分钟到几小时）

绑定自定义域名后，您可以使用更简洁的地址访问服务，也便于分享给他人。

---

## 常见问题

### Q: 部署后无法访问，提示连接超时

请检查以下几点：
1. 容器是否正常运行（查看平台的日志输出）
2. 端口配置是否正确（`WEB_PORT` 环境变量与暴露端口一致）
3. 网络配置是否开启了公网访问

### Q: 使用 OpenAI 模型时响应很慢

在国内云平台上使用 OpenAI 等境外服务可能会有网络延迟。解决方案：
- 切换为国产模型（如通义千问、智谱 GLM），响应更快且无需代理
- 如果必须使用 OpenAI，考虑配置 API 代理服务

### Q: 免费额度用完了怎么办

各平台的收费标准不同，您可以：
- 新注册账号获取新的免费额度
- 升级到付费方案，通常每月几美元即可
- 考虑本地部署或使用自己的服务器

---

## 相关文档

- [Docker 部署](docker.md) — 在自己的服务器上使用 Docker 部署
- [配置详解](../get_started/configuration.md) — 了解所有可用的配置选项
- [反向代理](reverse_proxy.md) — 使用 Nginx 配置反向代理和 HTTPS
