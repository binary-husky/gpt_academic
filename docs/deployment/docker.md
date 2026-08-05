# Docker 部署指南

Docker 是部署 GPT Academic 的推荐方式，它将应用及其所有依赖打包在一个容器中，避免了环境配置问题，实现了真正的"开箱即用"。无论您是想在服务器上长期运行服务，还是快速搭建一个隔离的测试环境，Docker 都能满足需求。

本文将引导您完成从镜像选择到服务启动的完整流程，并针对不同操作系统和使用场景提供相应的配置方案。

---

## 前置条件

在开始之前，请确保您的系统已经安装了 Docker 和 Docker Compose。如果尚未安装，请参考以下官方文档完成安装：

- **Docker Engine**: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
- **Docker Compose**: 新版 Docker Desktop 已内置，Linux 用户请参考 [官方安装指南](https://docs.docker.com/compose/install/)

安装完成后，在终端运行以下命令验证安装是否成功：

```bash
docker --version
docker compose version
```

如果两条命令都正常输出版本号，说明环境已准备就绪。

---

## 选择合适的镜像

GPT Academic 提供了多个预构建的 Docker 镜像，针对不同的使用场景进行了优化。选择合适的镜像可以避免下载不必要的依赖，节省磁盘空间和启动时间。

| 镜像 | 体积 | 适用场景 | 特点 |
|-----|------|---------|------|
| `ghcr.io/binary-husky/gpt_academic_nolocal:master` | ~2GB | 纯在线模型 | 最轻量，支持 OpenAI、通义千问、星火等在线 API |
| `ghcr.io/binary-husky/gpt_academic_with_latex:master` | ~4GB | 论文翻译 | 包含完整 LaTeX 环境，支持 PDF 编译输出 |
| `ghcr.io/binary-husky/gpt_academic_chatglm_moss:master` | ~15GB | 本地模型 | 包含 ChatGLM、MOSS 等本地模型运行环境 |
| `ghcr.io/binary-husky/gpt_academic_with_all_capacity:master` | ~20GB | 全功能 | 包含所有能力，含 CUDA 和 LaTeX |

!!! tip "新手推荐"
    如果您只使用 OpenAI、通义千问等在线模型，选择 `gpt_academic_nolocal` 镜像即可。如果您需要翻译论文并生成 PDF，选择 `gpt_academic_with_latex` 镜像。

---

## 快速启动

最简单的启动方式是使用 `docker run` 命令。以下命令会拉取轻量级镜像并启动服务：

=== "Linux"

    ```bash
    docker run -d \
      --name gpt-academic \
      --net=host \
      -e API_KEY="sk-your-openai-key-here" \
      -e LLM_MODEL="gpt-3.5-turbo" \
      -e WEB_PORT="12345" \
      ghcr.io/binary-husky/gpt_academic_nolocal:master
    ```

=== "Windows / macOS"

    ```bash
    docker run -d \
      --name gpt-academic \
      -p 12345:12345 \
      -e API_KEY="sk-your-openai-key-here" \
      -e LLM_MODEL="gpt-3.5-turbo" \
      -e WEB_PORT="12345" \
      ghcr.io/binary-husky/gpt_academic_nolocal:master
    ```

启动后，打开浏览器访问 `http://localhost:12345` 即可使用。

!!! warning "网络模式差异"
    Linux 系统支持 `--net=host` 模式，容器直接使用宿主机网络，代理配置更方便。Windows 和 macOS 不支持此模式，需要使用 `-p` 端口映射。

---

## 使用 Docker Compose 部署

对于生产环境或需要持久化配置的场景，推荐使用 Docker Compose。项目根目录已提供 `docker-compose.yml` 文件，包含了多种预设方案。

### 准备配置文件

首先复制示例配置文件：

```bash
cp docker-compose.yml docker-compose.override.yml
```

然后编辑 `docker-compose.override.yml`，只保留您需要的方案。项目提供了以下预设方案：

- **方案一**：纯在线模型（推荐大多数用户）
- **方案二**：在线模型 + ChatGLM 本地模型
- **方案三**：在线模型 + RWKV/LLaMA 本地模型
- **方案四**：在线模型 + LaTeX 环境
- **方案五**：在线模型 + 语音助手

### 配置环境变量

在选定的方案中，修改 `environment` 部分的配置项。以方案一（纯在线模型）为例：

```yaml
version: '3'
services:
  gpt_academic:
    image: ghcr.io/binary-husky/gpt_academic_nolocal:master
    environment:
      API_KEY:          'sk-your-openai-key-here'
      LLM_MODEL:        'gpt-3.5-turbo'
      AVAIL_LLM_MODELS: '["gpt-3.5-turbo", "gpt-4", "qwen-max"]'
      WEB_PORT:         '12345'
      # 代理配置（国内用户可能需要）
      # USE_PROXY:      'True'
      # proxies:        '{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}'
    network_mode: "host"  # Linux 用户使用此模式
    # ports:              # Windows/macOS 用户改用端口映射
    #   - "12345:12345"
    command: bash -c "python3 -u main.py"
```

### 启动服务

配置完成后，在项目根目录运行：

```bash
docker compose up -d
```

使用 `-d` 参数让容器在后台运行。首次启动时会自动拉取镜像，可能需要几分钟时间。

查看运行日志：

```bash
docker compose logs -f
```

看到类似 `Running on local URL: http://0.0.0.0:12345` 的输出时，说明服务已成功启动。

---

## 配置代理

如果您在国内使用 OpenAI 等境外服务，需要配置代理。在 Docker 环境中，代理配置需要特别注意网络模式的影响。

**使用 host 网络模式（Linux）**：容器共享宿主机网络，代理地址使用 `localhost` 或 `127.0.0.1`：

```yaml
environment:
  USE_PROXY:  'True'
  proxies:    '{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}'
```

**使用端口映射模式（Windows/macOS）**：容器有独立网络，需要使用宿主机的局域网 IP 或 Docker 特殊地址：

```yaml
environment:
  USE_PROXY:  'True'
  proxies:    '{"http": "http://host.docker.internal:7890", "https": "http://host.docker.internal:7890"}'
```

!!! info "`host.docker.internal`"
    这是 Docker 提供的特殊 DNS 名称，在容器内部指向宿主机。仅在 Docker Desktop（Windows/macOS）中可用。

---

## 使用 LaTeX 环境

如果您需要翻译论文并生成 PDF 文件，需要使用包含 LaTeX 环境的镜像。

### 选择 LaTeX 镜像

将镜像改为支持 LaTeX 的版本：

```yaml
services:
  gpt_academic:
    image: ghcr.io/binary-husky/gpt_academic_with_latex:master
    # ... 其他配置保持不变
```

ARM64 架构（如 Apple Silicon Mac）用户请使用专门的镜像：

```yaml
image: ghcr.io/binary-husky/gpt_academic_with_latex_arm:master
```

### 验证 LaTeX 功能

启动服务后，尝试使用 Arxiv 论文翻译功能。如果翻译完成后能正常生成 PDF 文件，说明 LaTeX 环境配置正确。

---

## 使用 GPU 加速

如果您需要运行本地大模型（如 ChatGLM），可以配置 GPU 支持以获得更好的性能。这需要安装 NVIDIA Container Toolkit。

### 前置条件

1. 安装 [NVIDIA 驱动](https://www.nvidia.com/Download/index.aspx)
2. 安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### 配置 GPU 访问

在 `docker-compose.yml` 中添加 GPU 相关配置：

```yaml
services:
  gpt_academic:
    image: ghcr.io/binary-husky/gpt_academic_chatglm_moss:master
    environment:
      LOCAL_MODEL_DEVICE: 'cuda'
      # ... 其他环境变量
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

或者使用更简单的 `devices` 方式直接映射 GPU：

```yaml
services:
  gpt_academic:
    # ...
    runtime: nvidia
    devices:
      - /dev/nvidia0:/dev/nvidia0
```

---

## 数据持久化

默认情况下，容器内的数据会在容器删除时丢失。如果您需要保留对话历史、上传的文件或自定义配置，可以挂载数据卷。

```yaml
services:
  gpt_academic:
    # ...
    volumes:
      - ./gpt_log:/gpt/gpt_log           # 日志和缓存
      - ./private_upload:/gpt/private_upload  # 上传的文件
```

这样配置后，日志和上传文件会保存在宿主机的当前目录下，即使重建容器也不会丢失。

---

## 常用命令参考

| 操作 | 命令 |
|------|------|
| 启动服务 | `docker compose up -d` |
| 停止服务 | `docker compose down` |
| 查看日志 | `docker compose logs -f` |
| 重启服务 | `docker compose restart` |
| 更新镜像 | `docker compose pull && docker compose up -d` |
| 进入容器 | `docker compose exec gpt_academic bash` |

---

## 常见问题

### Q: 启动后无法访问页面

首先检查容器是否正常运行：`docker compose ps`。如果状态显示 `Exited`，查看日志排查原因：`docker compose logs`。

常见原因包括：
- 端口被占用：修改 `WEB_PORT` 为其他端口
- API KEY 格式错误：确保 KEY 正确且没有多余空格

### Q: 代理配置不生效

确认代理软件允许局域网连接。在 `proxies` 配置中，使用正确的协议（`http` 或 `socks5h`）和地址。对于 Docker Desktop 用户，记得使用 `host.docker.internal` 而非 `localhost`。

### Q: 如何添加新的环境变量

所有 `config.py` 中的配置项都可以通过环境变量覆盖。变量名保持一致，值使用字符串格式。例如配置通义千问：

```yaml
environment:
  DASHSCOPE_API_KEY: 'sk-your-dashscope-key'
  LLM_MODEL: 'qwen-max'
```

---

## 相关文档

- [安装指南](../get_started/installation.md) — 本地直接运行的安装方式
- [配置详解](../get_started/configuration.md) — 了解所有可用的配置选项
- [云服务部署](cloud_deploy.md) — 在云平台上部署
- [反向代理](reverse_proxy.md) — 使用 Nginx 配置反向代理
