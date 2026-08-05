# GPT Academic

> 为 GPT/LLM 提供实用化交互界面，特别优化论文阅读/润色/写作体验

GPT Academic 是一款面向学术研究和技术开发的大模型交互工具。它将复杂的 AI 能力封装成简洁的功能按钮，让研究者无需编写代码就能完成论文翻译、文献润色、代码分析等专业任务。无论您是需要快速阅读英文论文的研究生，还是希望提升代码质量的开发者，GPT Academic 都能显著提升您的工作效率。

<!-- IMAGE: index_01_main_interface.png -->
<!-- 描述: GPT Academic 主界面全貌截图，展示左侧对话区和右侧功能面板 -->
<!-- 尺寸建议: 1200px -->
![GPT Academic 主界面](images/index_01_main_interface.png)

---

## 核心特性

<div class="grid cards" markdown>

-   :material-translate: **论文翻译**

    ---

    一键翻译 Arxiv/PDF 论文，保留原有排版格式，支持 LaTeX 公式渲染

-   :material-code-braces: **代码分析**

    ---

    支持 Python/Java/C++/Go/Rust 等多种语言项目解析，生成结构化分析报告

-   :material-robot: **多模型支持**

    ---

    OpenAI、通义千问、智谱GLM、DeepSeek 等 30+ 模型，可多模型同时对比

-   :material-lightning-bolt: **虚空终端**

    ---

    用自然语言调用所有功能插件，无需记忆按钮位置，说出需求即可执行

-   :material-palette: **界面定制**

    ---

    多种主题风格、暗色/亮色模式切换、字体自定义，打造个性化工作环境

-   :material-puzzle: **插件扩展**

    ---

    丰富的函数插件生态，支持热更新，开发者可轻松添加自定义功能

</div>

---

## 快速导航

根据您的需求，选择最适合的入口开始使用：

### 🚀 新手入门

刚接触 GPT Academic？建议按顺序阅读以下文档：

1. **[安装指南](get_started/installation.md)** — 三种方式安装项目，选择最适合您的方案
2. **[快速上手](get_started/quickstart.md)** — 5分钟完成首次配置和使用
3. **[配置详解](get_started/configuration.md)** — 深入理解配置文件结构

### 📚 我要翻译论文

学术论文翻译是 GPT Academic 的核心功能：

- **[Arxiv 论文翻译](features/academic/arxiv_translation.md)** — 输入论文 ID，一键下载并翻译为中文
- **[PDF 论文翻译](features/academic/pdf_translation.md)** — 上传本地 PDF 文件进行翻译

### 💻 我要分析代码

代码理解和分析功能帮助开发者快速掌握项目结构：

- **[源码分析](features/programming/code_analysis.md)** — 解析整个项目，生成代码结构报告
- **[代码注释生成](features/programming/code_comment.md)** — 为函数批量生成规范的文档字符串

### 🔧 我要部署服务

将 GPT Academic 部署为团队或个人服务：

- **[Docker 部署](deployment/docker.md)** — 容器化部署，一行命令启动
- **[云服务部署](deployment/cloud_deploy.md)** — 在 Sealos/HuggingFace 上免费托管

---

## 支持的模型

GPT Academic 支持广泛的大语言模型生态，您可以根据使用场景和预算灵活选择：

| 模型系列 | 代表模型 | 推荐场景 | 配置难度 |
|---------|---------|---------|:-------:|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | 通用场景、复杂推理 | ⭐⭐ |
| **通义千问** | qwen-max, qwen-turbo | 国内用户首选、无需代理 | ⭐ |
| **智谱 GLM** | GLM-4, GLM-3-turbo | 中文场景、性价比高 | ⭐ |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | 推理任务、代码生成 | ⭐ |
| **本地模型** | ChatGLM3/4, LLaMA | 离线使用、数据安全 | ⭐⭐⭐ |

!!! tip "国内用户推荐"
    如果您在国内，**通义千问**是最便捷的选择——注册阿里云账户后即可免费获取 API Key，无需配置代理，开箱即用。

---

## 基础功能一览

界面上的基础功能按钮提供常用的快捷操作：

| 功能按钮 | 作用 |
|---------|------|
| **学术润色** | 改进学术文本的语法、表达和可读性 |
| **中英互译** | 智能检测语言并翻译 |
| **查找语法错误** | 定位并修正语法问题 |
| **解释代码** | 解析代码逻辑和功能 |
| **总结绘制脑图** | 生成内容的 Mermaid 思维导图 |

了解更多功能细节，请阅读 **[基础功能详解](features/basic_functions.md)**。

---

## 获取帮助

遇到问题？以下资源可以帮助您：

- 📖 **[常见问题 FAQ](troubleshooting/faq.md)** — 汇总用户最常遇到的问题及解决方案
- 💬 **QQ 交流群**：610599535 — 与其他用户交流使用心得
- 🐛 **[GitHub Issues](https://github.com/binary-husky/gpt_academic/issues)** — 报告 Bug 或提出功能建议

---

## 项目信息

- **GitHub**: [binary-husky/gpt_academic](https://github.com/binary-husky/gpt_academic)
- **协议**: GPL-3.0
- **Star**: [![GitHub stars](https://img.shields.io/github/stars/binary-husky/gpt_academic?style=social)](https://github.com/binary-husky/gpt_academic)
