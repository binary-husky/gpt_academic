# 反向代理配置

在生产环境中部署 GPT Academic 时，使用反向代理是一种常见且推荐的做法。反向代理可以为您的服务提供 HTTPS 加密、域名绑定、负载均衡等企业级功能，同时隐藏后端服务的实际端口和架构细节。本文档将指导您使用 Nginx 配置反向代理，并介绍如何启用 HTTPS 安全连接。

---

## 为什么需要反向代理

直接将 GPT Academic 暴露在公网上存在一些局限性。首先，Gradio 默认使用 HTTP 协议，数据传输未加密，在公网环境下存在安全风险。其次，用户需要通过 `http://ip:端口` 的方式访问，不够友好且难以记忆。此外，单实例服务难以应对高并发场景。

通过配置反向代理，您可以获得以下优势：使用 HTTPS 加密保护用户数据传输安全；绑定自定义域名提升专业形象；在多实例部署时实现负载均衡；利用缓存和压缩优化访问速度。

---

## 前置条件

在开始配置之前，请确保您已具备以下条件：

- GPT Academic 已成功部署并可通过 `http://localhost:端口` 访问
- 拥有一台具有公网 IP 的服务器
- 已安装 Nginx（本文以 Nginx 为例，其他反向代理软件配置类似）
- （可选）已注册域名并完成 DNS 解析

如果您还没有安装 Nginx，可以通过以下命令快速安装：

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install nginx

# CentOS / RHEL
sudo yum install nginx

# 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 基础反向代理配置

### 确定 GPT Academic 端口

首先，您需要确定 GPT Academic 运行的端口。在 `config_private.py` 中设置一个固定端口，避免每次启动端口变化：

```python
WEB_PORT = 7860  # 设置固定端口
```

启动服务后，确认可以通过 `http://localhost:7860` 正常访问。

### Nginx 配置文件

创建 Nginx 配置文件。配置文件通常位于 `/etc/nginx/sites-available/` 目录（Debian/Ubuntu）或 `/etc/nginx/conf.d/` 目录（CentOS/RHEL）。

```bash
sudo nano /etc/nginx/sites-available/gpt-academic
```

输入以下配置内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或服务器 IP

    # 日志配置
    access_log /var/log/nginx/gpt-academic.access.log;
    error_log /var/log/nginx/gpt-academic.error.log;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;

        # WebSocket 支持（Gradio 需要）
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 传递真实客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置（大文件上传和长时间推理需要）
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # 禁用缓冲以支持流式输出
        proxy_buffering off;

        # 文件上传大小限制
        client_max_body_size 100M;
    }
}
```

上述配置中有几个关键点需要说明。WebSocket 支持配置（`Upgrade` 和 `Connection` 头）是 Gradio 实时通信的必要条件，缺少这些配置会导致界面无法正常交互。超时时间设置较长是为了适应大模型推理可能需要的等待时间。禁用缓冲（`proxy_buffering off`）确保流式输出能够实时显示。

### 启用配置

创建符号链接并重启 Nginx：

```bash
# Debian/Ubuntu
sudo ln -s /etc/nginx/sites-available/gpt-academic /etc/nginx/sites-enabled/

# 测试配置语法
sudo nginx -t

# 重新加载配置
sudo systemctl reload nginx
```

现在您应该可以通过 `http://your-domain.com` 访问 GPT Academic 了。

---

## HTTPS 配置

### 使用 Let's Encrypt 免费证书

Let's Encrypt 提供免费的 SSL/TLS 证书，配合 Certbot 工具可以实现证书的自动申请和续期。这是目前最便捷的 HTTPS 配置方案。

首先安装 Certbot：

```bash
# Ubuntu / Debian
sudo apt install certbot python3-certbot-nginx

# CentOS / RHEL
sudo yum install certbot python3-certbot-nginx
```

然后执行证书申请命令，Certbot 会自动修改 Nginx 配置：

```bash
sudo certbot --nginx -d your-domain.com
```

按照提示完成操作后，Certbot 会自动配置 HTTPS 并设置 HTTP 到 HTTPS 的重定向。证书有效期为 90 天，Certbot 会自动配置定时任务进行续期。

### 手动配置 HTTPS

如果您已有证书文件（如企业证书或从其他 CA 购买的证书），可以手动配置。将证书文件放置到合适的位置：

```bash
sudo mkdir -p /etc/nginx/ssl
sudo cp your_certificate.crt /etc/nginx/ssl/
sudo cp your_private.key /etc/nginx/ssl/
```

修改 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    # HTTP 重定向到 HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/your_certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/your_private.key;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志配置
    access_log /var/log/nginx/gpt-academic.access.log;
    error_log /var/log/nginx/gpt-academic.error.log;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;

        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 传递真实客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时和缓冲设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
        client_max_body_size 100M;
    }
}
```

---

## 二级路径部署

如果您希望在同一域名下部署多个服务，可以将 GPT Academic 配置在二级路径下运行。例如通过 `https://your-domain.com/gpt/` 访问。

首先在 GPT Academic 配置中设置二级路径：

```python
CUSTOM_PATH = "/gpt"
```

然后修改 Nginx 配置：

```nginx
location /gpt/ {
    proxy_pass http://127.0.0.1:7860/gpt/;
    proxy_http_version 1.1;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    proxy_buffering off;
    client_max_body_size 100M;
}
```

---

## 负载均衡配置

当单个 GPT Academic 实例无法满足访问需求时，可以部署多个实例并使用 Nginx 进行负载均衡。

首先在不同端口启动多个 GPT Academic 实例（或在不同服务器上部署），然后配置 Nginx upstream：

```nginx
upstream gpt_academic_cluster {
    # 轮询策略（默认）
    server 127.0.0.1:7860;
    server 127.0.0.1:7861;
    server 127.0.0.1:7862;

    # 可选：启用会话保持（基于 IP）
    # ip_hash;

    # 可选：按权重分配
    # server 127.0.0.1:7860 weight=3;
    # server 127.0.0.1:7861 weight=2;
    # server 127.0.0.1:7862 weight=1;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 配置省略...

    location / {
        proxy_pass http://gpt_academic_cluster;
        # 其他 proxy 配置同上...
    }
}
```

!!! warning "会话保持"
    GPT Academic 的对话历史存储在用户会话中。如果不启用 `ip_hash` 等会话保持策略，用户可能会被分配到不同的后端实例，导致对话历史丢失。建议在负载均衡场景下启用会话保持。

---

## 使用 Caddy 作为替代方案

Caddy 是一款现代化的 Web 服务器，以自动 HTTPS 著称。如果您觉得 Nginx 配置繁琐，Caddy 是一个更简洁的选择。

安装 Caddy：

```bash
# Ubuntu / Debian
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

创建 Caddyfile（通常位于 `/etc/caddy/Caddyfile`）：

```
your-domain.com {
    reverse_proxy localhost:7860
}
```

就是这么简单。Caddy 会自动申请和续期 Let's Encrypt 证书，无需任何额外配置。启动 Caddy：

```bash
sudo systemctl start caddy
sudo systemctl enable caddy
```

---

## 配置验证

完成配置后，您可以通过以下步骤验证：

1. **访问测试**：在浏览器中访问您配置的域名，确认能够正常加载 GPT Academic 界面
2. **HTTPS 检查**：确认浏览器地址栏显示安全锁图标
3. **功能测试**：尝试发送消息，确认对话功能正常（这会验证 WebSocket 配置）
4. **文件上传测试**：上传一个文件，确认上传功能正常

<!-- IMAGE: deploy_01_nginx_https.png -->
<!-- 描述: 浏览器访问 GPT Academic 的 HTTPS 页面，地址栏显示安全锁图标 -->
<!-- 标注: 用红框标注浏览器地址栏的安全锁图标和 https:// 前缀 -->
<!-- 尺寸建议: 800px -->
![HTTPS 配置成功](../images/deploy_01_nginx_https.png)

---

## 常见问题

???+ question "WebSocket 连接失败，界面无响应"
    这通常是因为 Nginx 配置中缺少 WebSocket 支持。请确保配置了以下两行：
    ```nginx
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    ```
    修改配置后执行 `sudo nginx -t && sudo systemctl reload nginx`。

???+ question "上传大文件失败"
    Nginx 默认限制请求体大小为 1MB。请在配置中添加或增大 `client_max_body_size` 的值：
    ```nginx
    client_max_body_size 100M;  # 允许上传最大 100MB 的文件
    ```

???+ question "HTTPS 证书申请失败"
    常见原因包括：

    - 域名 DNS 未正确解析到服务器 IP
    - 服务器 80 端口被防火墙阻止
    - 域名已达到 Let's Encrypt 的速率限制

    请检查 DNS 解析和防火墙设置。如果遇到速率限制，可以等待一小时后重试，或在测试阶段使用 `--staging` 参数。

???+ question "响应很慢或经常超时"
    对于大模型推理，响应时间可能较长。请适当增加超时时间：
    ```nginx
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    ```

---

## 相关文档

- [Docker 部署](docker.md) — 容器化部署方案
- [配置详解](../get_started/configuration.md) — 了解 WEB_PORT、CUSTOM_PATH 等配置项
- [配置参考](../reference/config_reference.md) — 所有配置项速查
