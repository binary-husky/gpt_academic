# 网络问题排查

网络问题是使用 GPT Academic 过程中最常见的障碍之一，尤其对于需要访问 OpenAI、Google 等境外服务的国内用户。本文将从代理配置的基础知识出发，系统性地介绍如何诊断和解决各类网络问题，帮助您建立起清晰的排查思路。

---

## 理解代理机制

在深入排查问题之前，我们需要先理解 GPT Academic 的网络请求机制。项目中并非所有请求都需要代理——事实上，只有特定类型的请求才会使用代理网络。

### 何时使用代理

项目通过 `WHEN_TO_USE_PROXY` 配置项控制代理的使用范围。默认情况下，以下场景会启用代理：

| 场景标识 | 说明 |
|---------|------|
| `Connect_OpenAI` | 连接 OpenAI API（包括 GPT、DALL-E 等） |
| `Download_LLM` | 下载大模型文件 |
| `Download_Gradio_Theme` | 从 HuggingFace 下载 Gradio 主题 |
| `Connect_Grobid` | 连接 GROBID 服务解析 PDF |
| `Warmup_Modules` | 预热模块时的网络请求 |
| `Nougat_Download` | 下载 Nougat OCR 模型 |
| `Connect_OpenAI_Embedding` | 连接 OpenAI Embedding API |

这意味着，如果您使用国产模型（如通义千问、智谱 GLM），通常不需要配置代理，因为这些服务在国内可以直接访问。只有当您使用 OpenAI、Claude 等境外服务时，才需要正确配置代理。

### 代理配置结构

GPT Academic 的代理配置位于 `config.py` 或 `config_private.py` 中，由两个关键参数组成：

```python
USE_PROXY = True  # 是否启用代理
proxies = {
    "http":  "socks5h://localhost:11284",
    "https": "socks5h://localhost:11284",
}
```

`USE_PROXY` 是总开关。当设置为 `False` 时，无论 `proxies` 如何配置都不会生效。`proxies` 字典定义了具体的代理服务器地址，需要同时配置 `http` 和 `https` 两个键。

---

## 代理配置详解

正确配置代理需要了解三个要素：协议、地址和端口。这些信息需要从您的代理软件中获取。

### 协议选择

代理协议决定了数据的传输方式，常见的有以下几种：

| 协议 | 适用软件 | 配置示例 |
|-----|---------|---------|
| `http` | Clash、SSR | `http://127.0.0.1:7890` |
| `socks5` | V2Ray、SS | `socks5://localhost:10808` |
| `socks5h` | V2Ray、SS | `socks5h://localhost:10808` |

!!! tip "socks5 与 socks5h 的区别"
    `socks5` 会在本地解析域名，然后通过代理发送 IP 请求；`socks5h` 则将域名解析也交给代理服务器处理。如果您的 DNS 被污染，建议使用 `socks5h`。

不同代理软件的默认协议不同：

- **Clash / ClashX / ClashVerge**：通常使用 `http` 协议，默认端口 `7890`
- **V2Ray / V2RayN / V2RayNG**：通常使用 `socks5` 协议，默认端口 `10808`
- **Shadowsocks**：使用 `socks5` 协议，默认端口 `1080`

### 地址配置

地址通常是 `localhost` 或 `127.0.0.1`，表示代理软件运行在本机上。在某些特殊情况下，您可能需要填写其他地址：

- **代理运行在其他设备**：填写该设备的局域网 IP，如 `192.168.1.100`
- **Docker 容器内访问宿主机代理**：
  - Linux 使用 host 网络模式时：`127.0.0.1`
  - Windows/macOS 使用端口映射时：`host.docker.internal`

### 端口查找

端口号需要在代理软件的设置中查找。以 Clash 为例，通常在「设置」或「常规」页面可以看到「HTTP 端口」或「混合端口」的配置。请确保代理软件已开启「允许局域网连接」选项，这是代理生效的前提。

<!-- IMAGE: trouble_01_proxy_port.png -->
<!-- 描述: 代理软件（如 Clash）的设置界面，用红框标注端口号所在位置，同时标注"允许局域网连接"选项 -->
<!-- 标注: 1. 红框标注 HTTP 端口（如 7890）2. 红框标注"允许局域网连接"开关 -->
<!-- 尺寸建议: 800px -->
![代理端口位置](../images/trouble_01_proxy_port.png)

---

## 验证代理配置

配置完成后，您可以通过以下方法验证代理是否正常工作。

### 方法一：启动日志检查

GPT Academic 在启动时会自动检测代理状态并输出到控制台。正常情况下，您会看到类似以下的日志：

```
[PROXY] 网络代理状态：已配置。配置信息如下：{'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
代理配置 http://127.0.0.1:7890, 代理所在地：Japan
```

日志中显示了代理服务器的出口位置。如果显示的国家是您代理节点所在的位置（如 Japan、United States 等），说明代理配置正确。

如果看到以下提示，则说明代理未正确配置：

```
[PROXY] 网络代理状态：未配置。无代理状态下很可能无法访问OpenAI家族的模型。
```

这通常是因为 `USE_PROXY` 仍为 `False`，或者 `proxies` 字典格式不正确。

### 方法二：手动测试脚本

您也可以运行项目提供的代理检测脚本进行验证：

```bash
python check_proxy.py
```

脚本会向 `https://ipapi.co/json/` 发送请求，检测代理是否生效。如果输出包含非中国大陆的国家信息，说明代理工作正常。

### 方法三：命令行测试

如果您熟悉命令行，还可以使用 curl 直接测试代理：

```bash
# HTTP 代理
curl -x http://127.0.0.1:7890 https://ipapi.co/json/

# SOCKS5 代理
curl -x socks5h://127.0.0.1:10808 https://ipapi.co/json/
```

如果返回的 JSON 数据中 `country` 字段不是 "China"，说明代理生效。

---

## 常见问题诊断

### 问题一：连接超时（Connection Timeout）

**症状**：发送消息后长时间无响应，最终提示连接超时。

**排查步骤**：

1. **确认代理软件正在运行**：检查系统托盘图标，确保代理软件已启动且处于连接状态。

2. **验证代理端口**：打开代理软件的设置，确认端口号与配置文件中的一致。

3. **检查防火墙设置**：某些安全软件可能会阻止网络连接。尝试临时关闭防火墙进行测试。

4. **测试代理节点可用性**：在代理软件中切换到其他节点，有时特定节点可能因为各种原因不可用。

5. **检查协议是否匹配**：确保配置的协议（http/socks5h）与代理软件提供的协议一致。

### 问题二：代理已配置但仍无法访问

**症状**：日志显示代理已配置，但访问 OpenAI 时仍然失败。

**可能原因**：

- **代理节点不支持 HTTPS**：某些低质量的代理可能不完整支持 HTTPS 流量。尝试更换节点或代理服务商。

- **代理软件未开启系统代理**：部分代理软件区分「系统代理」和「TUN 模式」，GPT Academic 需要的是后者或手动配置的方式。

- **环境变量冲突**：如果系统中设置了 `HTTP_PROXY`、`HTTPS_PROXY` 或 `no_proxy` 环境变量，可能会与程序配置冲突。尝试清除这些环境变量：

  ```bash
  unset HTTP_PROXY HTTPS_PROXY no_proxy
  ```

### 问题三：部分功能可用，部分不可用

**症状**：普通对话正常，但某些插件（如联网搜索、Arxiv 翻译）失败。

**原因分析**：

不同功能可能访问不同的服务器。例如：
- 对话功能访问 OpenAI API
- Arxiv 翻译需要访问 arxiv.org 和 OpenAI
- 联网搜索需要访问 Google 或 Searxng

**解决方案**：

检查 `WHEN_TO_USE_PROXY` 配置，确保涵盖了所需的场景。如果您需要让所有网络请求都走代理，可以修改此配置：

```python
WHEN_TO_USE_PROXY = ["Connect_OpenAI", "Download_LLM", "Download_Gradio_Theme",
                     "Connect_Grobid", "Warmup_Modules", "Nougat_Download",
                     "AutoGen", "Connect_OpenAI_Embedding"]
```

### 问题四：API 密钥错误提示

**症状**：提示 "Invalid API key" 或 "Incorrect API key provided"。

**排查要点**：

这通常不是网络问题，而是 API 密钥配置问题：

1. **检查密钥格式**：OpenAI 密钥以 `sk-` 开头，确保完整复制且没有多余空格。

2. **检查配置文件位置**：如果同时存在 `config.py` 和 `config_private.py`，后者的优先级更高。确保修改的是正确的文件。

3. **检查环境变量**：如果通过环境变量配置了 API_KEY，它的优先级高于配置文件。

### 问题五：SSL 证书错误

**症状**：提示 SSL certificate error 或 certificate verify failed。

**解决方案**：

这通常是代理软件的 HTTPS 拦截功能导致的。尝试以下方法：

1. **在代理软件中关闭 HTTPS 解密**（又称 MitM 或中间人模式）

2. **如果必须使用 HTTPS 解密**，需要信任代理软件的根证书。具体方法因代理软件而异，请参考相应文档。

---

## 特殊场景配置

### Docker 环境中的代理

在 Docker 容器中配置代理需要特别注意网络模式的差异。

**Linux 主机使用 host 网络模式**：

容器直接共享宿主机网络，代理地址使用 `127.0.0.1`：

```yaml
environment:
  USE_PROXY: 'True'
  proxies: '{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}'
network_mode: "host"
```

**Windows/macOS 使用端口映射**：

容器拥有独立网络，需要使用特殊地址访问宿主机：

```yaml
environment:
  USE_PROXY: 'True'
  proxies: '{"http": "http://host.docker.internal:7890", "https": "http://host.docker.internal:7890"}'
ports:
  - "12345:12345"
```

### 企业内网代理

在企业环境中，您可能需要通过公司的代理服务器访问外网。这种情况下，代理地址通常由 IT 部门提供：

```python
USE_PROXY = True
proxies = {
    "http":  "http://proxy.company.com:8080",
    "https": "http://proxy.company.com:8080",
}
```

如果代理需要认证，可以在 URL 中包含用户名和密码：

```python
proxies = {
    "http":  "http://username:password@proxy.company.com:8080",
    "https": "http://username:password@proxy.company.com:8080",
}
```

### 使用 API 代理服务

如果您不想配置本地代理，还可以使用第三方 API 代理服务。这些服务将 OpenAI 的 API 请求转发到国内可访问的服务器上。

配置方法是使用 `API_URL_REDIRECT` 重定向 API 地址：

```python
USE_PROXY = False  # 不需要本地代理
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-proxy-service.com/v1/chat/completions"
}
```

!!! warning "安全提示"
    使用第三方 API 代理服务意味着您的 API 密钥和对话内容会经过该服务。请选择可信赖的服务商，并注意保护您的隐私。

---

## 网络诊断工具箱

当遇到网络问题时，以下工具可以帮助您定位问题：

| 工具 | 用途 | 命令示例 |
|-----|------|---------|
| ping | 测试基本连通性 | `ping api.openai.com` |
| curl | 测试 HTTP 请求 | `curl -v https://api.openai.com` |
| traceroute | 追踪网络路由 | `traceroute api.openai.com` |
| nslookup | DNS 解析测试 | `nslookup api.openai.com` |

结合这些工具的输出，您通常可以判断问题出在 DNS 解析、网络路由还是目标服务器本身。

---

## 相关文档

- [配置详解](../get_started/configuration.md) — 了解所有配置选项
- [Docker 部署](../deployment/docker.md) — Docker 环境中的代理配置
- [常见问题](faq.md) — 其他常见问题解答
- [模型错误排查](model_errors.md) — API 调用相关的错误排查
