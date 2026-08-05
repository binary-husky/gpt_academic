# 5 分钟快速上手

本教程将引导您完成首次配置和使用 GPT Academic。在接下来的几分钟内，您将学会配置 API 密钥、启动应用、熟悉界面布局，并完成第一次智能对话。

---

## 本教程将带您完成

通过本教程，您将实现以下目标：

- ✅ 理解配置文件的工作机制
- ✅ 成功配置 API 密钥
- ✅ 启动应用并访问界面
- ✅ 熟悉界面各功能区域
- ✅ 完成第一次对话和功能体验

---

## 配置 API 密钥

GPT Academic 需要大语言模型的 API 支持才能正常工作。在开始之前，您需要获取至少一个可用的 API 密钥。

### 配置文件优先级

项目采用三层配置机制，读取优先级从高到低依次为：

```
环境变量  >  config_private.py  >  config.py
```

!!! tip "最佳实践"
    **强烈建议创建 `config_private.py` 文件存放您的私密配置**。该文件已被添加到 `.gitignore`，不会被 Git 追踪，避免您的密钥意外泄露，也不会在更新代码时被覆盖。

### 创建私密配置文件

在项目根目录下创建 `config_private.py` 文件，并根据您的 API 来源添加相应配置。

=== "OpenAI 官方 API"

    如果您有 OpenAI 官方账户，可在 [OpenAI Platform](https://platform.openai.com/api-keys) 获取 API Key：

    ```python
    API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```

    由于 OpenAI API 在国内无法直接访问，您还需要配置代理：

    ```python
    USE_PROXY = True
    proxies = {
        "http":  "http://127.0.0.1:7890",  # 改为您的代理地址和端口
        "https": "http://127.0.0.1:7890",
    }
    ```

=== "通义千问（国内推荐）"

    对于国内用户，阿里云通义千问是最便捷的选择，无需代理即可使用。前往 [阿里云百炼平台](https://dashscope.console.aliyun.com/) 注册并获取 API Key：

    ```python
    DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
    LLM_MODEL = "qwen-max"  # 设置默认使用通义千问
    ```

=== "DeepSeek"

    DeepSeek 提供高性价比的推理模型，在 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API Key：

    ```python
    DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
    LLM_MODEL = "deepseek-chat"  # 或使用 deepseek-reasoner 获得更强推理能力
    ```

=== "中转 API（进阶）"

    如果您使用第三方中转服务，请参阅 [中转渠道接入指南](../models/transit_api.md)。

### 多密钥配置

如果您同时拥有多个 API 密钥，可以用英文逗号分隔，系统会自动进行负载均衡：

```python
API_KEY = "sk-key1,sk-key2,sk-key3"
```

---

## 启动应用

配置完成后，在项目根目录执行以下命令启动应用：

```bash
python main.py
```

启动成功后，终端会显示访问地址。默认情况下，浏览器会自动打开。如果没有自动打开，请手动访问终端中显示的 URL（通常是 `http://localhost:端口号`）。

!!! info "端口说明"
    默认情况下系统会随机选择一个可用端口。如果您希望固定端口，可以在配置文件中设置：
    ```python
    WEB_PORT = 7860  # 指定固定端口
    ```

---

## 认识界面

GPT Academic 的界面设计注重实用性，主要分为以下几个功能区域：

<!-- IMAGE: gs_02_ui_overview.png -->
<!-- 描述: GPT Academic 主界面截图，使用标注说明各区域功能 -->
<!-- 标注:
  ① 对话显示区 - 左侧大区域
  ② 输入区 - 右上方的文本输入框和提交按钮
  ③ 基础功能区 - 包含"学术润色"等预设按钮
  ④ 函数插件区 - 包含插件分类下拉和各种插件按钮
  ⑤ 模型选择 - 左上角工具栏中的模型下拉菜单
-->
<!-- 尺寸建议: 1200px -->
![界面概览](../images/gs_02_ui_overview.png)

| 区域 | 功能说明 |
|-----|---------|
| **对话显示区** | 展示您与 AI 的对话历史，支持 Markdown 渲染和代码高亮 |
| **输入区** | 输入问题或文本，按 <kbd>Enter</kbd> 提交，<kbd>Shift</kbd>+<kbd>Enter</kbd> 换行 |
| **基础功能区** | 预设的快捷功能按钮，如学术润色、中英翻译等，点击即可对输入文本执行相应操作 |
| **函数插件区** | 更丰富的功能插件，包括论文翻译、代码分析等，通过分类标签筛选 |
| **模型选择** | 在左上角下拉菜单中切换不同的大语言模型 |

---

## 第一次对话

现在让我们开始第一次对话，验证配置是否成功。

在输入框中输入一个简单的问题，例如：

```
请用一句话解释什么是机器学习
```

点击 **提交** 按钮或按下 <kbd>Enter</kbd> 键。如果配置正确，您将在对话区看到 AI 的回复。

!!! success "配置成功"
    如果您能看到 AI 的回复，说明 API 配置已经成功！您现在可以开始探索更多功能了。

???+ failure "常见错误排查"
    **如果提示"缺少 api_key"**：请检查 `config_private.py` 中的 API 密钥是否正确配置。

    **如果提示"连接超时"**：

    - 使用 OpenAI 官方 API 时，请检查代理配置是否正确
    - 使用国内模型时，请检查网络连接是否正常

    **如果提示"API KEY 无效"**：请确认密钥是否正确复制，注意不要有多余的空格或换行符。

---

## 体验学术润色功能

GPT Academic 的核心特色之一是针对学术场景优化的功能。让我们体验一下**学术润色**功能。

在输入框中粘贴一段需要润色的学术文本，例如：

```
This paper propose a new method for image classification.
The method is based on deep learning and achieve good results on ImageNet dataset.
```

然后点击基础功能区的 **学术润色** 按钮。AI 将对文本进行语法修正、表达优化，并使其更符合学术写作规范。

---

## 下一步探索

恭喜您完成了快速上手！根据您的需求，可以继续探索以下内容：

| 我想要... | 推荐阅读 |
|----------|---------|
| 翻译 Arxiv 论文 | [Arxiv 论文翻译](../features/academic/arxiv_translation.md) |
| 翻译本地 PDF | [PDF 论文翻译](../features/academic/pdf_translation.md) |
| 分析代码项目 | [源码分析](../features/programming/code_analysis.md) |
| 使用第三方中转 API | [中转渠道接入](../models/transit_api.md) |
| 了解所有配置项 | [配置详解](configuration.md) |
