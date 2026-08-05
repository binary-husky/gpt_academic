# 常见问题 FAQ

本文整理了用户在安装、配置和使用 GPT Academic 过程中最常遇到的问题及解决方案。如果您的问题在这里没有找到答案，欢迎前往 [GitHub Issues](https://github.com/binary-husky/gpt_academic/issues) 搜索或提交新问题。

---

## 安装问题

### pip install 报错 "externally-managed-environment"

**现象描述**：在执行 `pip install -r requirements.txt` 时，系统提示 "externally-managed-environment" 错误。

**问题原因**：较新版本的 Linux 发行版（如 Ubuntu 23.04+、Debian 12+）默认启用了 PEP 668 保护机制，阻止直接在系统 Python 环境中安装第三方包。

**解决方案**：

使用虚拟环境是最推荐的做法：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 然后再安装依赖
pip install -r requirements.txt
```

如果您确实需要在系统环境安装，可以添加 `--break-system-packages` 参数（不推荐）：

```bash
pip install -r requirements.txt --break-system-packages
```

---

### 提示 Gradio 版本不匹配

**现象描述**：启动时报错 "使用项目内置Gradio获取最优体验"。

**问题原因**：GPT Academic 依赖特定版本的 Gradio（3.32.15），使用其他版本可能导致界面功能异常。

**解决方案**：

重新安装项目指定的依赖版本：

```bash
pip install -r requirements.txt --upgrade
```

如果问题持续，请检查是否有其他项目或环境安装了不同版本的 Gradio，建议使用虚拟环境隔离。

---

### 安装依赖时下载速度很慢

**解决方案**：使用国内镜像源加速下载：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 配置问题

### API KEY 配置后仍然报错

**现象描述**：已经在配置文件中填写了 API KEY，但运行时仍提示"缺少 api_key"或"Incorrect API key"。

**排查步骤**：

1. **检查配置文件优先级**

   GPT Academic 的配置读取优先级为：`环境变量 > config_private.py > config.py`。请确认您的 API KEY 配置在正确的文件中。推荐使用 `config_private.py`。

2. **检查 KEY 格式**

   确保 API KEY 的格式正确，没有多余的空格、换行符或引号嵌套：

   ```python
   # 正确
   API_KEY = "sk-xxxxxxxxxxxxxxxx"

   # 错误：有多余空格
   API_KEY = " sk-xxxxxxxxxxxxxxxx "

   # 错误：引号嵌套
   API_KEY = "'sk-xxxxxxxxxxxxxxxx'"
   ```

3. **检查 KEY 是否有效**

   部分 API KEY 有使用期限或额度限制。请登录相应平台确认 KEY 状态：

   - OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - 阿里云百炼: [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/)
   - DeepSeek: [platform.deepseek.com](https://platform.deepseek.com/)

4. **检查模型与 KEY 的匹配**

   不同的 API KEY 对应不同的模型。例如 `DASHSCOPE_API_KEY` 用于通义千问系列模型，`API_KEY` 用于 OpenAI 系列模型。请确保使用的模型与配置的 KEY 匹配。

---

### 代理配置不生效

**现象描述**：已经配置了代理，但访问 OpenAI API 时仍然连接超时。

**排查步骤**：

1. **确认 USE_PROXY 已开启**

   ```python
   USE_PROXY = True  # 必须设置为 True
   ```

2. **检查代理地址和端口**

   打开您的代理软件（如 Clash、V2Ray），确认本地监听端口。常见的端口配置：

   - Clash 默认：`http://127.0.0.1:7890`
   - V2Ray 默认：`socks5h://127.0.0.1:10808` 或 `http://127.0.0.1:10809`

3. **检查代理协议**

   不同代理软件使用不同协议，请根据实际情况配置：

   ```python
   proxies = {
       "http":  "http://127.0.0.1:7890",   # HTTP 代理
       "https": "http://127.0.0.1:7890",
   }

   # 或 SOCKS5 代理
   proxies = {
       "http":  "socks5h://127.0.0.1:10808",
       "https": "socks5h://127.0.0.1:10808",
   }
   ```

4. **测试代理是否正常工作**

   在终端中测试代理连通性：

   ```bash
   # 设置临时代理
   export https_proxy=http://127.0.0.1:7890

   # 测试访问
   curl -I https://api.openai.com
   ```

!!! tip "国内用户建议"
    如果您在国内且没有稳定的代理，强烈建议使用**通义千问**等国内模型，无需配置代理即可使用。

---

### 提示 "Model does not exist"

**现象描述**：调用模型时提示"Model xxx does not exist"。

**可能原因**：

1. **模型名称拼写错误**：OpenAI 的模型名称区分大小写，请使用小写，如 `gpt-3.5-turbo` 而非 `GPT-3.5-Turbo`。

2. **没有模型访问权限**：部分模型（如 GPT-4、O1）需要额外的访问权限。请登录 OpenAI 平台确认您的账户是否有权访问该模型。

3. **使用了错误的 API 端点**：如果您使用第三方中转服务，需要确认该服务支持您请求的模型。

---

## 网络问题

### 连接超时 / Connection Timeout

**现象描述**：请求发送后长时间无响应，最终提示超时。

**常见原因和解决方案**：

| 原因 | 解决方案 |
|------|---------|
| 未配置代理（访问 OpenAI） | 配置 `USE_PROXY = True` 和正确的代理地址 |
| 代理软件未启动 | 启动代理软件并确保正常运行 |
| 网络不稳定 | 检查网络连接，尝试切换网络环境 |
| 服务商限流 | 等待一分钟后重试 |

您可以适当调大超时时间：

```python
TIMEOUT_SECONDS = 60  # 默认为 30 秒
```

---

### Rate limit exceeded（请求频率超限）

**现象描述**：提示"Rate limit exceeded"或"Too many requests"。

**问题原因**：短时间内发送了过多请求，超出了 API 服务商的速率限制。

**解决方案**：

1. **等待后重试**：通常等待 1 分钟后即可恢复。

2. **减少并发数**：修改配置文件中的并发参数：

   ```python
   DEFAULT_WORKER_NUM = 3  # 降低并发线程数
   ```

3. **配置多 KEY 负载均衡**：

   ```python
   API_KEY = "sk-key1,sk-key2,sk-key3"  # 用英文逗号分隔
   ```

---

## 模型调用问题

### You exceeded your current quota（账户额度不足）

**现象描述**：提示"You exceeded your current quota"。

**问题原因**：API 账户余额不足或免费额度已用完。

**解决方案**：

1. 登录对应平台充值或绑定付费方式
2. 切换到其他有余额的 API KEY
3. 切换到免费额度更多的模型（如通义千问提供的免费额度）

---

### Your account is not active（账户未激活）

**现象描述**：提示账户未激活或已停用。

**问题原因**：API 账户状态异常，可能是未完成验证或被服务商停用。

**解决方案**：登录对应平台检查账户状态，按提示完成验证或联系客服。

---

### 输入内容过长 / Reduce the length

**现象描述**：提示需要减少输入长度，或"context length exceeded"。

**问题原因**：输入文本加上对话历史超过了模型的上下文长度限制。

**解决方案**：

1. **减少单次输入文本量**：将长文本分段处理。

2. **清除对话历史**：点击**重置**按钮清空历史记录。

3. **切换更大上下文的模型**：例如从 `gpt-3.5-turbo` 切换到 `gpt-3.5-turbo-16k`。

4. **启用自动上下文裁剪**：

   ```python
   AUTO_CONTEXT_CLIP_ENABLE = True
   ```

---

## 使用问题

### 翻译论文时卡住不动

**现象描述**：执行论文翻译时长时间没有进度更新。

**可能原因和解决方案**：

1. **论文过长**：长篇论文翻译耗时较长，请耐心等待。可以在对话区查看实时进度。

2. **网络不稳定**：检查网络连接，特别是代理是否正常工作。

3. **API 响应慢**：高峰期 API 响应可能变慢。可以尝试切换到响应更快的模型（如 gpt-3.5-turbo）。

4. **GROBID 服务不可用**：PDF 翻译依赖 GROBID 服务解析 PDF。检查配置的 GROBID 服务地址是否可访问：

   ```python
   GROBID_URLS = [
       "https://qingxu98-grobid.hf.space",
       # 可添加备用地址
   ]
   ```

---

### 界面显示异常 / 样式错乱

**解决方案**：

1. **清除浏览器缓存**：按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Delete</kbd> 清除缓存后刷新页面。

2. **使用推荐浏览器**：建议使用 Chrome、Edge 或 Firefox 的最新版本。

3. **检查浏览器扩展**：部分广告拦截插件可能影响页面渲染，尝试禁用后刷新。

---

### 文件上传后没有反应

**排查步骤**：

1. **检查文件格式**：确保上传的文件格式受支持（PDF、Word、代码文件等）。

2. **检查文件大小**：过大的文件可能需要较长上传时间，请耐心等待。

3. **查看对话区消息**：上传成功后，对话区会显示文件接收确认消息和路径。

4. **正确使用路径**：上传后需要点击**提交**按钮或选择相应插件，系统才会处理文件。

---

### 如何保存对话历史

点击函数插件区的**保存当前的对话**按钮，系统会将当前对话导出为 HTML 文件，保存在 `gpt_log` 目录下。您也可以在之后通过**载入对话历史存档**插件重新加载。

---

## 常见报错信息速查表

| 报错信息 | 含义 | 解决方案 |
|---------|------|---------|
| `Incorrect API key` | API KEY 无效 | 检查 KEY 是否正确，是否有多余空格 |
| `Rate limit exceeded` | 请求频率超限 | 等待 1 分钟或配置多 KEY |
| `You exceeded your current quota` | 账户额度不足 | 充值或切换 KEY |
| `Model does not exist` | 模型不存在 | 检查模型名称拼写，确认访问权限 |
| `Connection timeout` | 连接超时 | 检查网络和代理配置 |
| `context_length_exceeded` | 上下文过长 | 减少输入或清除历史 |
| `bad_request` | 请求格式错误 | 检查输入内容格式 |
| `authentication_error` | 认证失败 | 检查 API KEY 配置 |
| `system_busy` | 系统繁忙 | 等待后重试 |

---

## 获取更多帮助

如果上述内容未能解决您的问题，您可以：

1. **搜索 GitHub Issues**：[github.com/binary-husky/gpt_academic/issues](https://github.com/binary-husky/gpt_academic/issues)

   很可能其他用户已经遇到并解决了相同的问题。

2. **查看项目 Wiki**：[github.com/binary-husky/gpt_academic/wiki](https://github.com/binary-husky/gpt_academic/wiki)

   包含更多详细的配置说明和使用技巧。

3. **加入 QQ 交流群**：610599535

   与其他用户交流，获取实时帮助。

4. **提交 Issue**：如果确认是 Bug，欢迎在 GitHub 提交 Issue，请附上：
   - 操作系统和 Python 版本
   - 完整的报错信息
   - 复现步骤

---

## 相关文档

- **[安装指南](../get_started/installation.md)** — 详细的安装步骤
- **[配置详解](../get_started/configuration.md)** — 所有配置项说明
- **[中转渠道接入](../models/transit_api.md)** — 第三方 API 服务配置
