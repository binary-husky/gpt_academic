# GPT Academic 文档撰写规划

> **文档版本**: v1.0
> **创建日期**: 2025-01-09
> **首要目标**: 教导用户如何配置和使用 GPT Academic

---

## 一、文档设计原则

### 1.1 用户导向原则

- **任务驱动**: 每篇文档围绕"用户想要完成什么"来组织内容
- **渐进式学习**: 从简单到复杂，从常用到进阶
- **可操作性**: 每个步骤都应该是可执行的，避免空泛描述
- **快速验证**: 用户应能在最短时间内验证配置是否成功

### 1.2 内容编写规范

- 每篇文档开头说明**前置条件**和**预期结果**
- 关键操作步骤必须配图说明
- 代码块必须可直接复制使用
- 配置项说明需包含：参数名、类型、默认值、示例值、说明

### 1.3 图片使用规范

#### 图片命名标准

```
{章节缩写}_{序号}_{描述}.png

示例:
- gs_01_clone_repo.png          # get_started 章节第1张图：克隆仓库
- gs_02_config_apikey.png       # get_started 章节第2张图：配置API KEY
- model_01_openai_apikey.png    # models 章节第1张图：OpenAI API KEY
- feat_arxiv_01_input.png       # features/arxiv 章节第1张图：输入界面
```

#### 章节缩写对照表

| 章节路径 | 缩写 |
|---------|------|
| get_started/ | gs |
| models/ | model |
| features/basic | feat_basic |
| features/academic/arxiv | feat_arxiv |
| features/academic/pdf | feat_pdf |
| features/academic/latex | feat_latex |
| features/programming | feat_prog |
| features/conversation | feat_conv |
| features/agents | feat_agent |
| customization/ | custom |
| deployment/ | deploy |
| troubleshooting/ | trouble |

#### 图片占位符格式

在文档中使用以下格式标记需要添加的图片：

```markdown
<!-- IMAGE: {图片文件名} -->
<!-- 描述: {图片应展示的内容} -->
<!-- 尺寸建议: {宽度}px -->
![{alt文本}](images/{图片文件名})
```

---

## 二、文档目录结构

```
docs/
├── index.md                              # 首页
├── images/                               # 所有图片存放目录
│   ├── gs_*.png                          # 快速开始相关图片
│   ├── model_*.png                       # 模型接入相关图片
│   ├── feat_*.png                        # 功能指南相关图片
│   ├── custom_*.png                      # 自定义扩展相关图片
│   ├── deploy_*.png                      # 部署相关图片
│   └── trouble_*.png                     # 问题排查相关图片
│
├── get_started/                          # 快速开始
│   ├── installation.md                   # 安装指南
│   ├── quickstart.md                     # 5分钟快速上手
│   └── configuration.md                  # 配置文件详解
│
├── models/                               # 模型接入
│   ├── overview.md                       # 模型支持概览
│   ├── openai.md                         # OpenAI 接入
│   ├── azure.md                          # Azure OpenAI 接入
│   ├── chinese_models.md                 # 国产模型接入
│   ├── local_models.md                   # 本地模型部署
│   └── custom_models.md                  # 自定义模型开发
│
├── features/                             # 功能指南
│   ├── basic_functions.md                # 基础功能
│   ├── academic/                         # 学术功能
│   │   ├── arxiv_translation.md          # Arxiv论文翻译
│   │   ├── pdf_translation.md            # PDF论文翻译
│   │   ├── latex_polish.md               # Latex项目处理
│   │   ├── paper_reading.md              # 论文阅读助手
│   │   ├── pdf_summary.md                # 批量总结PDF文档 [新增]
│   │   ├── word_summary.md               # 批量总结Word文档 [新增]
│   │   ├── pdf_qa.md                     # PDF问答(ChatPDF) [新增]
│   │   ├── tex_abstract.md               # 读Tex论文写摘要 [新增]
│   │   ├── google_scholar.md             # 谷歌学术检索助手 [新增]
│   │   ├── arxiv_download.md             # Arxiv论文下载与摘要翻译 [新增]
│   │   ├── latex_proofread.md            # Latex英文纠错+高亮对比 [新增]
│   │   ├── pdf_nougat.md                 # PDF精准翻译(NOUGAT) [新增]
│   │   └── batch_file_query.md           # 批量文件询问 [新增]
│   ├── programming/                      # 编程功能
│   │   ├── code_analysis.md              # 源码分析
│   │   ├── code_comment.md               # 代码注释生成
│   │   ├── markdown_translate.md         # Markdown翻译
│   │   ├── jupyter_analysis.md           # Jupyter Notebook分析 [新增]
│   │   ├── custom_code_analysis.md       # 自定义源码分析 [新增]
│   │   └── batch_comment_gen.md          # 批量函数注释生成 [新增]
│   ├── conversation/                     # 对话功能
│   │   ├── internet_search.md            # 联网搜索
│   │   ├── multi_model_query.md          # 多模型询问
│   │   ├── image_generation.md           # 图片生成
│   │   ├── voice_assistant.md            # 语音助手
│   │   ├── conversation_save.md          # 对话保存与载入 [新增]
│   │   └── mermaid_gen.md                # Mermaid图表生成 [新增]
│   └── agents/                           # 智能体
│       ├── void_terminal.md
│       └── code_interpreter.md
│
├── customization/                        # 自定义与扩展
│   ├── custom_buttons.md
│   ├── plugin_development.md
│   └── theme_customization.md
│
├── deployment/                           # 部署指南
│   ├── docker.md
│   ├── cloud_deploy.md
│   └── reverse_proxy.md
│
├── troubleshooting/                      # 问题排查
│   ├── faq.md
│   ├── network_issues.md
│   └── model_errors.md
│
└── reference/                            # 参考资料
    ├── config_reference.md
    └── changelog.md
```

---

## 三、各文档详细规划

### 3.1 首页 (index.md)

**目标**: 让用户在30秒内了解项目价值，并找到自己需要的内容

**内容结构**:

```markdown
# GPT Academic

[一句话介绍]

## 核心特性
- 特性卡片 x 4-6 个（带图标）

## 快速导航
- 新手用户 → 快速开始
- 我要翻译论文 → Arxiv/PDF翻译
- 我要分析代码 → 源码分析
- 我要部署服务 → 部署指南

## 界面预览
[主界面截图]
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `index_01_main_interface.png` | 主界面全貌截图 | 1200px |
| `index_02_feature_demo.gif` | 核心功能演示动图 | 800px |

---

### 3.2 快速开始 - 安装指南 (get_started/installation.md)

**目标**: 用户能够成功安装并运行项目

**内容结构**:

```markdown
# 安装指南

## 前置条件
- Python 版本要求
- 系统要求

## 安装方式一：直接运行（推荐新手）

### 步骤1：克隆项目
[代码块]
[截图：克隆成功的终端输出]

### 步骤2：安装依赖
[代码块 - pip/conda/uv 三种方式]

### 步骤3：验证安装
[代码块]
[截图：验证成功的输出]

## 安装方式二：Docker 部署

### 步骤1：安装 Docker
[链接到官方文档]

### 步骤2：启动容器
[代码块]
[截图：容器启动成功]

## 安装方式三：一键安装脚本（Windows）
[下载链接]
[截图：脚本运行界面]

## 常见安装问题
- 问题1及解决方案
- 问题2及解决方案
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `gs_01_clone_success.png` | git clone 成功的终端输出 | 800px |
| `gs_02_pip_install.png` | pip install 过程截图 | 800px |
| `gs_03_verify_success.png` | 验证安装成功的输出 | 600px |
| `gs_04_docker_run.png` | Docker 容器启动成功 | 800px |
| `gs_05_windows_script.png` | Windows一键脚本界面 | 800px |

---

### 3.3 快速开始 - 快速上手 (get_started/quickstart.md)

**目标**: 用户在5分钟内完成首次使用

**内容结构**:

```markdown
# 5分钟快速上手

## 本教程将带你完成
- ✅ 配置第一个 API KEY
- ✅ 启动应用
- ✅ 进行第一次对话
- ✅ 使用第一个插件功能

## 步骤1：配置 API KEY

### 方式A：使用 OpenAI API
[截图：config.py 中 API_KEY 位置]
[代码块：配置示例]

### 方式B：使用通义千问（国内推荐）
[截图：config.py 中 DASHSCOPE_API_KEY 位置]
[代码块：配置示例]

## 步骤2：启动应用
[代码块]
[截图：启动成功，显示访问地址]

## 步骤3：访问界面
[截图：浏览器中打开的主界面，标注主要区域]
- 输入区
- 功能按钮区
- 插件下拉菜单
- 对话显示区

## 步骤4：第一次对话
[截图：输入问题]
[截图：获得回复]

## 步骤5：使用"学术润色"功能
[截图：点击学术润色按钮]
[截图：润色结果]

## 下一步
- 想翻译论文？→ [Arxiv论文翻译](../features/academic/arxiv_translation.md)
- 想分析代码？→ [源码分析](../features/programming/code_analysis.md)
- 想了解更多配置？→ [配置详解](configuration.md)
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `gs_06_config_apikey_location.png` | config.py 中 API_KEY 的位置（高亮标注） | 800px |
| `gs_07_config_dashscope.png` | config.py 中通义千问配置位置 | 800px |
| `gs_08_startup_success.png` | 启动成功的终端输出（显示URL） | 600px |
| `gs_09_main_ui_annotated.png` | 主界面各区域标注图 | 1200px |
| `gs_10_first_chat_input.png` | 输入第一个问题 | 1000px |
| `gs_11_first_chat_response.png` | 收到回复 | 1000px |
| `gs_12_polish_button.png` | 点击学术润色按钮 | 1000px |
| `gs_13_polish_result.png` | 润色结果展示 | 1000px |

---

### 3.4 快速开始 - 配置详解 (get_started/configuration.md)

**目标**: 用户理解配置文件结构，能够根据需求修改配置

**内容结构**:

```markdown
# 配置文件详解

## 配置文件说明

### 配置优先级
环境变量 > config_private.py > config.py

### 推荐做法
创建 config_private.py 存放个人配置（不会被git覆盖）

[截图：config_private.py 文件示例]

## 核心配置项

### API 配置
| 配置项 | 说明 | 示例值 |
|-------|------|-------|
| API_KEY | OpenAI API密钥 | sk-xxx |
| DASHSCOPE_API_KEY | 通义千问密钥 | sk-xxx |
| ... | ... | ... |

### 代理配置
[代码块：代理配置示例]
[截图：代理软件中查看端口]

### 模型配置
[代码块：LLM_MODEL 和 AVAIL_LLM_MODELS 配置]

### 界面配置
[截图：不同 LAYOUT 的效果对比]
[截图：不同 THEME 的效果对比]

## 配置关系图
[mermaid 图或截图：展示配置项之间的关系]

## 环境变量配置
适用于 Docker 部署场景
[代码块：docker-compose.yml 示例]
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `gs_14_config_private_example.png` | config_private.py 文件内容示例 | 800px |
| `gs_15_proxy_port.png` | 代理软件中查看端口位置 | 600px |
| `gs_16_layout_leftright.png` | 左右布局效果 | 1000px |
| `gs_17_layout_topdown.png` | 上下布局效果 | 1000px |
| `gs_18_theme_default.png` | Default 主题效果 | 800px |
| `gs_19_theme_chuanhu.png` | Chuanhu 主题效果 | 800px |

---

### 3.5 模型接入 - 概览 (models/overview.md)

**目标**: 用户了解支持哪些模型，如何选择适合自己的模型

**内容结构**:

```markdown
# 模型支持概览

## 支持的模型一览

### 在线模型

| 模型系列 | 具体模型 | 配置难度 | 推荐场景 |
|---------|---------|---------|---------|
| OpenAI | gpt-4o, gpt-4, gpt-3.5-turbo | ⭐⭐ | 通用场景 |
| 通义千问 | qwen-max, qwen-turbo | ⭐ | 国内用户首选 |
| 智谱GLM | glm-4, glm-3-turbo | ⭐ | 中文场景 |
| DeepSeek | deepseek-chat, deepseek-reasoner | ⭐ | 推理任务 |
| ... | ... | ... | ... |

### 本地模型

| 模型 | 显存要求 | 配置难度 |
|-----|---------|---------|
| ChatGLM3-6B | 13GB | ⭐⭐⭐ |
| ChatGLM4-9B | 24GB | ⭐⭐⭐ |
| ... | ... | ... |

## 模型选择建议

### 场景1：国内用户，快速上手
推荐：通义千问 qwen-max
[配置链接]

### 场景2：需要最强能力
推荐：GPT-4o 或 DeepSeek-R1
[配置链接]

### 场景3：离线使用/数据安全
推荐：本地部署 ChatGLM
[配置链接]

## 多模型配置
[截图：AVAIL_LLM_MODELS 配置]
[截图：界面上的模型下拉菜单]
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `model_01_avail_models_config.png` | AVAIL_LLM_MODELS 配置示例 | 800px |
| `model_02_model_dropdown.png` | 界面上的模型选择下拉菜单 | 400px |

---

### 3.6 模型接入 - OpenAI (models/openai.md)

**目标**: 用户能成功接入 OpenAI API

**内容结构**:

```markdown
# OpenAI / GPT 系列接入

## 前置条件
- OpenAI 账号
- 有效的 API KEY

## 步骤1：获取 API KEY

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 登录账号
3. 进入 API Keys 页面
   [截图：API Keys 页面位置]
4. 创建新的 API KEY
   [截图：创建 API KEY]
5. 复制保存 KEY（只显示一次！）
   [截图：复制 KEY]

## 步骤2：配置 API KEY

在 `config_private.py` 中添加：

```python
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

### 多 KEY 负载均衡

```python
API_KEY = "sk-key1,sk-key2,sk-key3"
```

## 步骤3：配置代理（国内用户必需）

[截图：USE_PROXY 配置位置]

```python
USE_PROXY = True
proxies = {
    "http":  "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
```

## 步骤4：验证配置

启动应用，选择 gpt-3.5-turbo 模型，发送测试消息。

[截图：验证成功的对话]

## 高级配置

### API URL 重定向
适用于使用第三方代理服务的场景

```python
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-proxy.com/v1/chat/completions"
}
```

### 组织 ID 配置
极少数情况下需要

```python
API_ORG = "org-xxxxxxxx"
```

## 常见问题

### Q: 提示 "API KEY 无效"
A: 检查 KEY 是否正确复制，是否有多余空格

### Q: 提示 "连接超时"
A: 检查代理配置是否正确
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `model_03_openai_apikeys_page.png` | OpenAI API Keys 页面 | 1000px |
| `model_04_openai_create_key.png` | 创建 API KEY 按钮 | 600px |
| `model_05_openai_copy_key.png` | 复制 API KEY | 600px |
| `model_06_proxy_config.png` | 代理配置代码位置 | 800px |
| `model_07_openai_verify.png` | 验证配置成功的对话 | 1000px |

---

### 3.7 模型接入 - 国产模型 (models/chinese_models.md)

**目标**: 国内用户能快速接入国产大模型

**内容结构**:

```markdown
# 国产模型接入

## 通义千问（推荐）

### 获取 API KEY
1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
   [截图：百炼平台首页]
2. 创建 API KEY
   [截图：创建 KEY 的位置]

### 配置

```python
DASHSCOPE_API_KEY = "sk-xxxxxxxx"
LLM_MODEL = "qwen-max"
```

### 支持的模型
- qwen-max（推荐）
- qwen-turbo
- dashscope-qwen3-14b
- dashscope-deepseek-r1

---

## 智谱 GLM

### 获取 API KEY
[截图及步骤]

### 配置

```python
ZHIPUAI_API_KEY = "xxxxxxxx"
LLM_MODEL = "glm-4"
```

---

## DeepSeek

### 获取 API KEY
[截图及步骤]

### 配置

```python
DEEPSEEK_API_KEY = "sk-xxxxxxxx"
LLM_MODEL = "deepseek-chat"  # 或 deepseek-reasoner
```

---

## 百度千帆

### 获取凭证
[截图及步骤]

### 配置

```python
BAIDU_CLOUD_API_KEY = 'xxxxx'
BAIDU_CLOUD_SECRET_KEY = 'xxxxx'
BAIDU_CLOUD_QIANFAN_MODEL = 'ERNIE-Bot-4'
LLM_MODEL = "qianfan"
```

---

## 讯飞星火

### 获取凭证
[截图及步骤]

### 配置

```python
XFYUN_APPID = "xxxxxxxx"
XFYUN_API_SECRET = "xxxxxxxx"
XFYUN_API_KEY = "xxxxxxxx"
LLM_MODEL = "sparkv4"
```
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `model_08_dashscope_home.png` | 阿里云百炼平台首页 | 1000px |
| `model_09_dashscope_apikey.png` | 百炼平台创建 API KEY | 800px |
| `model_10_zhipu_apikey.png` | 智谱开放平台 API KEY 页面 | 800px |
| `model_11_deepseek_apikey.png` | DeepSeek API KEY 页面 | 800px |
| `model_12_qianfan_console.png` | 百度千帆控制台 | 800px |
| `model_13_xfyun_console.png` | 讯飞开放平台控制台 | 800px |

---

### 3.8 功能指南 - Arxiv论文翻译 (features/academic/arxiv_translation.md)

**目标**: 用户能成功翻译一篇 Arxiv 论文

**内容结构**:

```markdown
# Arxiv 论文翻译

## 功能说明
一键将 Arxiv 论文精细翻译为中文，保留原有排版格式。

## 前置条件
- 已配置可用的大模型 API
- （可选）安装 LaTeX 环境以生成 PDF

## 使用方法

### 步骤1：获取论文 ID
从 Arxiv 论文 URL 中提取 ID

示例：`https://arxiv.org/abs/2301.00234` → ID 为 `2301.00234`

[截图：Arxiv 页面，标注 ID 位置]

### 步骤2：输入论文 ID
在输入框中输入论文 ID

[截图：输入框中输入 ID]

### 步骤3：选择翻译插件
从下拉菜单中选择 "Arxiv论文翻译" 或 "📚Arxiv论文精细翻译"

[截图：下拉菜单选择插件]

### 步骤4：点击执行
[截图：点击提交按钮]

### 步骤5：等待翻译完成
翻译过程会显示进度

[截图：翻译进度显示]

### 步骤6：获取结果
翻译完成后，可下载翻译后的 PDF

[截图：下载结果]

## 高级用法

### 自定义翻译指令
在高级参数区输入特定翻译要求

```
If the term "agent" is used, translate it to "智能体".
If the term "transformer" is used, keep it as "Transformer".
```

[截图：高级参数输入区]

## 常见问题

### Q: 翻译速度很慢
A: 论文越长翻译时间越长，可尝试使用更快的模型如 gpt-3.5-turbo

### Q: 部分公式显示异常
A: 确保安装了完整的 LaTeX 环境
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `feat_arxiv_01_paper_id.png` | Arxiv 页面标注 ID 位置 | 1000px |
| `feat_arxiv_02_input_id.png` | 输入框中输入论文 ID | 800px |
| `feat_arxiv_03_select_plugin.png` | 下拉菜单选择翻译插件 | 600px |
| `feat_arxiv_04_progress.png` | 翻译进度显示 | 1000px |
| `feat_arxiv_05_result.png` | 翻译结果和下载链接 | 1000px |
| `feat_arxiv_06_advanced_args.png` | 高级参数输入区 | 800px |
| `feat_arxiv_07_pdf_compare.png` | 翻译前后 PDF 对比 | 1200px |

---

### 3.9 功能指南 - PDF论文翻译 (features/academic/pdf_translation.md)

**目标**: 用户能成功翻译本地 PDF 论文

**内容结构**:

```markdown
# PDF 论文翻译

## 功能说明
上传 PDF 论文文件，翻译为中文。

## 使用方法

### 步骤1：上传 PDF 文件
点击上传区域，选择 PDF 文件

[截图：上传区域]
[截图：选择文件]

### 步骤2：选择翻译插件
从下拉菜单选择 "PDF论文翻译"

[截图：选择插件]

### 步骤3：执行翻译
[截图：翻译过程]

### 步骤4：下载结果
[截图：下载翻译结果]

## 翻译方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|-----|------|------|---------|
| 默认（GROBID） | 速度快 | 复杂排版可能丢失 | 常规论文 |
| Doc2x | 排版保留好 | 需要额外 API | 复杂排版论文 |
| Nougat | 公式识别好 | 速度较慢 | 数学公式多的论文 |

## Doc2x 配置
[配置说明]

## 常见问题
[FAQ]
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `feat_pdf_01_upload_area.png` | PDF 上传区域 | 800px |
| `feat_pdf_02_select_file.png` | 选择 PDF 文件 | 600px |
| `feat_pdf_03_select_plugin.png` | 选择翻译插件 | 600px |
| `feat_pdf_04_translating.png` | 翻译过程 | 1000px |
| `feat_pdf_05_download.png` | 下载结果 | 800px |

---

### 3.10 功能指南 - 虚空终端 (features/agents/void_terminal.md)

**目标**: 用户学会用自然语言调用各种插件

**内容结构**:

```markdown
# 虚空终端

## 功能说明
使用自然语言描述你的需求，自动调用合适的插件完成任务。

## 使用示例

### 示例1：翻译论文
输入：`请帮我翻译这篇论文 https://arxiv.org/abs/2301.00234`

[截图：输入自然语言指令]
[截图：自动识别并调用翻译插件]

### 示例2：分析代码
输入：`分析一下 /path/to/project 这个Python项目`

[截图：输入和结果]

### 示例3：联网搜索
输入：`搜索一下最新的 GPT-5 消息`

[截图：输入和结果]

## 支持的任务类型
- 论文翻译
- 代码分析
- 联网搜索
- 图片生成
- ...

## 使用技巧
1. 描述尽量具体
2. 可以指定使用的模型
3. 可以提供文件路径或URL
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `feat_agent_01_void_input.png` | 虚空终端输入示例 | 1000px |
| `feat_agent_02_void_recognize.png` | 自动识别任务类型 | 1000px |
| `feat_agent_03_void_result.png` | 执行结果 | 1000px |

---

### 3.11 自定义扩展 - 自定义按钮 (customization/custom_buttons.md)

**目标**: 用户能添加自己的快捷功能按钮

**内容结构**:

```markdown
# 自定义快捷按钮

## 方法一：通过界面添加（推荐）

### 步骤1：打开自定义菜单
点击 "界面外观" → "自定义菜单"

[截图：菜单位置]

### 步骤2：添加新按钮
[截图：添加按钮的界面]

### 步骤3：配置按钮参数
- 按钮名称
- 前缀提示词（Prefix）
- 后缀提示词（Suffix）

[截图：配置参数]

### 步骤4：保存并使用
[截图：新按钮出现在界面上]

---

## 方法二：通过代码添加

编辑 `core_functional.py` 文件：

```python
"我的翻译按钮": {
    "Prefix": "请将以下内容翻译成专业的学术中文：\n\n",
    "Suffix": "",
    "Color": "secondary",
    "Visible": True,
},
```

## 参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| Prefix | 添加在用户输入前的文本 | "请翻译：" |
| Suffix | 添加在用户输入后的文本 | "\n请保持格式" |
| Color | 按钮颜色 | "primary", "secondary", "stop" |
| Visible | 是否显示 | True / False |
| AutoClearHistory | 是否清除历史 | True / False |
| PreProcess | 预处理函数 | clear_line_break |

## 实用示例

### 示例1：论文润色按钮
[代码示例]

### 示例2：代码Review按钮
[代码示例]

### 示例3：会议纪要生成按钮
[代码示例]
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `custom_01_menu_location.png` | 自定义菜单位置 | 600px |
| `custom_02_add_button.png` | 添加按钮界面 | 800px |
| `custom_03_config_params.png` | 配置参数界面 | 800px |
| `custom_04_new_button.png` | 新按钮在界面上的位置 | 600px |

---

### 3.12 问题排查 - 常见问题 (troubleshooting/faq.md)

**目标**: 用户能快速找到常见问题的解决方案

**内容结构**:

```markdown
# 常见问题 FAQ

## 安装问题

### Q: pip install 报错 "externally-managed-environment"
**解决方案**：
使用虚拟环境或添加 `--break-system-packages` 参数
[代码示例]

### Q: 提示缺少某个依赖
**解决方案**：
[解决步骤]

---

## 配置问题

### Q: API KEY 配置后仍然报错
**排查步骤**：
1. 检查 KEY 是否正确复制
2. 检查是否有多余空格或换行
3. 检查配置文件优先级
[截图：正确的配置格式]

### Q: 代理配置不生效
**排查步骤**：
[排查步骤和截图]

---

## 使用问题

### Q: 翻译论文时卡住不动
**可能原因及解决方案**：
[解决方案]

### Q: 界面显示异常
**解决方案**：
清除浏览器缓存，使用 Chrome/Edge 浏览器

---

## 报错信息对照表

| 报错信息 | 原因 | 解决方案 |
|---------|------|---------|
| "Rate limit exceeded" | API 调用频率超限 | 等待或使用多 KEY |
| "Invalid API key" | API KEY 无效 | 检查 KEY 配置 |
| ... | ... | ... |
```

**需要的图片**:

| 图片文件名 | 描述 | 尺寸建议 |
|-----------|------|---------|
| `trouble_01_correct_config.png` | 正确的 API KEY 配置格式 | 800px |
| `trouble_02_proxy_check.png` | 代理检查方法 | 600px |

---

## 四、分阶段撰写计划

> **原则**：每阶段撰写 3 篇文档，按功能重要程度和用户关心程度排序

---

### 📋 阶段总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         文档撰写阶段规划                                  │
├─────────┬───────────────────────────────────────────────────────────────┤
│ 阶段 1  │ 安装指南 → 快速上手 → 国产模型接入                              │
│         │ 【目标：用户能跑起来】                                          │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 2  │ Arxiv论文翻译 → PDF论文翻译 → 配置详解                          │
│         │ 【目标：用户能用核心功能】                                       │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 3  │ 首页 → 基础功能 → 常见问题FAQ                                   │
│         │ 【目标：完善入口和帮助】                                         │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 4  │ OpenAI接入 → 虚空终端 → 源码分析                                │
│         │ 【目标：覆盖常用场景】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 5  │ 自定义按钮 → Docker部署 → 联网搜索                              │
│         │ 【目标：扩展和部署】                                             │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 6  │ Latex处理 → 模型概览 → 多模型询问                               │
│         │ 【目标：学术进阶功能】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 7  │ 本地模型 → 插件开发 → Azure接入                                 │
│         │ 【目标：高级用户需求】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 8  │ 代码注释 → 图片生成 → 论文阅读助手                              │
│         │ 【目标：补充功能文档】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 9  │ 云服务部署 → 网络问题排查 → 主题定制                            │
│         │ 【目标：部署和定制】                                             │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 10 │ Markdown翻译 → 语音助手 → 代码解释器                            │
│         │ 【目标：特色功能】                                               │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 11 │ 配置参考 → 反向代理 → 自定义模型                                │
│         │ 【目标：参考文档】                                               │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 12 │ 模型错误排查 → 更新日志                                         │
│         │ 【目标：收尾】                                                   │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 13 │ PDF总结 → Word总结 → PDF问答(ChatPDF)                           │
│         │ 【目标：学术文档总结】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 14 │ Tex摘要生成 → 谷歌学术助手 → Arxiv下载与摘要翻译                 │
│         │ 【目标：学术辅助功能】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 15 │ Latex纠错高亮 → PDF翻译(NOUGAT) → 批量文件询问                   │
│         │ 【目标：学术高级功能】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 16 │ Jupyter分析 → 自定义源码分析 → 批量函数注释                      │
│         │ 【目标：编程功能补充】                                           │
├─────────┼───────────────────────────────────────────────────────────────┤
│ 阶段 17 │ 对话保存载入 → Mermaid图表生成                                   │
│         │ 【目标：对话功能补充】                                           │
└─────────┴───────────────────────────────────────────────────────────────┘
```

---

### 🚀 阶段 1：让用户跑起来（最高优先级）

**目标**：新用户能在30分钟内成功安装、配置并运行项目

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 1 | `get_started/installation.md` | 安装指南 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3小时 | 5 |
| 2 | `get_started/quickstart.md` | 快速上手 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3小时 | 8 |
| 3 | `models/chinese_models.md` | 国产模型接入 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3小时 | 6 |

**选择理由**：
- 安装是第一道门槛，必须先解决
- 快速上手让用户立即获得成就感
- 国内用户占主流，国产模型（通义千问）是最便捷的选择

**阶段产出检验**：
- [ ] 用户按文档能成功 `git clone` 并安装依赖
- [ ] 用户能配置通义千问 API 并成功对话
- [ ] 用户能看到完整的界面并进行基本交互

---

### 📚 阶段 2：核心功能上手

**目标**：用户掌握基础操作并能使用核心的论文翻译功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 4 | `features/basic_operations.md` | 基础操作 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2小时 | 1 |
| 5 | `features/academic/arxiv_translation.md` | Arxiv论文翻译 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2小时 | 1 |
| 6 | `features/academic/pdf_translation.md` | PDF论文翻译 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2小时 | 1 |
| 7 | `get_started/configuration.md` | 配置详解（补充） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 1小时 | 0 |

**选择理由**：
- 基础操作是所有功能的前提，涵盖对话、文件上传、图片上传、网页提取
- 论文翻译是项目最核心、最有特色的功能
- Arxiv翻译使用频率极高
- PDF翻译覆盖本地论文场景
- 配置详解帮助用户理解和调整参数

**阶段产出检验**：
- [x] 用户能进行基础对话并理解界面布局
- [x] 用户能上传文件并配合插件使用
- [x] 用户能输入 Arxiv ID 成功翻译论文
- [x] 用户能上传 PDF 并获得翻译结果
- [x] 用户理解 config.py 的配置结构和优先级

---

### 🏠 阶段 3：完善入口与帮助

**目标**：完善文档首页，提供问题排查支持

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 7 | `index.md` | 首页 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 2 |
| 8 | `features/basic_functions.md` | 基础功能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 4 |
| 9 | `troubleshooting/faq.md` | 常见问题FAQ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3小时 | 2 |

**选择理由**：
- 首页是文档门面，需要引导用户
- 基础功能（润色、翻译按钮）使用频率高
- FAQ 可以减少重复问题咨询

**阶段产出检验**：
- [x] 首页能清晰引导不同需求的用户
- [x] 用户了解界面上各个基础按钮的用途
- [x] 常见问题有清晰的解答

---

### 🔧 阶段 4：覆盖常用场景

**目标**：覆盖 OpenAI 用户、自然语言交互、代码分析场景

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 10 | `models/openai.md` | OpenAI接入 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 5 |
| 11 | `features/agents/void_terminal.md` | 虚空终端 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 3 |
| 12 | `features/programming/code_analysis.md` | 源码分析 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 4 |

**选择理由**：
- OpenAI 仍是主流选择，海外用户必需
- 虚空终端是项目特色功能
- 代码分析是程序员高频使用功能

**阶段产出检验**：
- [ ] 用户能成功配置 OpenAI API（含代理）
- [ ] 用户能用自然语言调用各种插件
- [ ] 用户能分析一个完整的代码项目

---

### 🚀 阶段 5：扩展与部署

**目标**：支持自定义和 Docker 部署

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 13 | `customization/custom_buttons.md` | 自定义按钮 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 4 |
| 14 | `deployment/docker.md` | Docker部署 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 3 |
| 15 | `features/conversation/internet_search.md` | 联网搜索 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 3 |

**选择理由**：
- 自定义按钮让用户创建个性化工作流
- Docker 是生产部署的主流方式
- 联网搜索解决信息时效性问题

**阶段产出检验**：
- [ ] 用户能添加自己的快捷按钮
- [ ] 用户能用 Docker 部署项目
- [ ] 用户能使用联网搜索获取实时信息

---

### 📖 阶段 6：学术进阶功能

**目标**：完善学术相关功能文档

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 16 | `features/academic/latex_polish.md` | Latex项目处理 | ⭐⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 4 |
| 17 | `models/overview.md` | 模型概览 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 2 |
| 18 | `features/conversation/multi_model_query.md` | 多模型询问 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 2 |

**选择理由**：
- Latex 处理是学术用户刚需
- 模型概览帮助用户选择合适的模型
- 多模型询问是特色对比功能

**阶段产出检验**：
- [ ] 用户能润色/纠错 Latex 项目
- [ ] 用户了解各模型的特点和选择建议
- [ ] 用户能同时询问多个模型对比结果

---

### ⚙️ 阶段 7：高级用户需求

**目标**：满足开发者和高级用户的需求

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 19 | `models/local_models.md` | 本地模型部署 | ⭐⭐⭐ | ⭐⭐⭐ | 3小时 | 5 |
| 20 | `customization/plugin_development.md` | 插件开发指南 | ⭐⭐⭐ | ⭐⭐⭐ | 4小时 | 6 |
| 21 | `models/azure.md` | Azure OpenAI接入 | ⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 4 |

**选择理由**：
- 本地模型满足离线/数据安全需求
- 插件开发让开发者能扩展功能
- Azure 是企业用户的常见选择

**阶段产出检验**：
- [ ] 用户能部署 ChatGLM 本地模型
- [ ] 开发者能按模板开发新插件
- [ ] 企业用户能接入 Azure OpenAI

---

### 📝 阶段 8：补充功能文档

**目标**：补充其他实用功能的文档

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 22 | `features/programming/code_comment.md` | 代码注释生成 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 23 | `features/conversation/image_generation.md` | 图片生成 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 24 | `features/academic/paper_reading.md` | 论文阅读助手 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |

**选择理由**：
- 代码注释是程序员实用功能
- 图片生成有一定使用场景
- 论文阅读补充学术功能闭环

**阶段产出检验**：
- [ ] 用户能为代码批量生成注释
- [ ] 用户能使用 DALLE 生成图片
- [ ] 用户能快速阅读和理解论文

---

### 🌐 阶段 9：部署与定制

**目标**：完善部署方案和界面定制

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 25 | `deployment/cloud_deploy.md` | 云服务部署 | ⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 4 |
| 26 | `troubleshooting/network_issues.md` | 网络问题排查 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 2 |
| 27 | `customization/theme_customization.md` | 主题定制 | ⭐⭐ | ⭐⭐⭐ | 1.5小时 | 4 |

**选择理由**：
- 云服务部署满足服务器部署需求
- 网络问题是常见痛点
- 主题定制提升个性化体验

**阶段产出检验**：
- [ ] 用户能在 Sealos/HuggingFace 上部署
- [ ] 用户能排查代理和网络问题
- [ ] 用户能切换主题和自定义字体

---

### 🎯 阶段 10：特色功能

**目标**：补充项目特色功能文档

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 28 | `features/programming/markdown_translate.md` | Markdown翻译 | ⭐⭐ | ⭐⭐⭐ | 1.5小时 | 2 |
| 29 | `features/conversation/voice_assistant.md` | 语音助手 | ⭐⭐ | ⭐⭐⭐ | 2小时 | 3 |
| 30 | `features/agents/code_interpreter.md` | 代码解释器 | ⭐⭐ | ⭐⭐⭐ | 2小时 | 3 |

**选择理由**：
- Markdown 翻译用于 README 等文档
- 语音助手是交互创新
- 代码解释器是智能体功能

**阶段产出检验**：
- [ ] 用户能翻译 README 文件
- [ ] 用户能配置并使用语音对话
- [ ] 用户能使用动态代码解释器

---

### 📚 阶段 11：参考文档

**目标**：提供完整的参考资料

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 31 | `reference/config_reference.md` | 配置参考 | ⭐⭐⭐ | ⭐⭐⭐ | 3小时 | 0 |
| 32 | `deployment/reverse_proxy.md` | 反向代理 | ⭐⭐ | ⭐⭐ | 2小时 | 2 |
| 33 | `models/custom_models.md` | 自定义模型开发 | ⭐⭐ | ⭐⭐ | 2.5小时 | 2 |

**选择理由**：
- 配置参考是查阅型文档
- 反向代理是生产部署常见需求
- 自定义模型面向开发者

**阶段产出检验**：
- [x] 用户能查阅所有配置项说明
- [x] 用户能配置 Nginx 反向代理
- [x] 开发者能接入新的大模型

---

### 🏁 阶段 12：收尾

**目标**：完成剩余文档

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 34 | `troubleshooting/model_errors.md` | 模型错误排查 | ⭐⭐ | ⭐⭐⭐ | 2小时 | 1 |
| 35 | `reference/changelog.md` | 更新日志 | ⭐⭐ | ⭐⭐ | 1小时 | 0 |

**选择理由**：
- 模型错误排查帮助解决调用问题
- 更新日志记录版本变化

**阶段产出检验**：
- [x] 用户能根据错误信息排查问题
- [x] 用户能了解版本更新内容

---

### 📄 阶段 13：学术文档总结

**目标**：补充文档总结类功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 36 | `features/academic/pdf_summary.md` | 批量总结PDF文档 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 1.5小时 | 3 |
| 37 | `features/academic/word_summary.md` | 批量总结Word文档 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 38 | `features/academic/pdf_qa.md` | PDF问答(ChatPDF) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 4 |

**选择理由**：
- PDF/Word 总结是日常文档处理高频需求
- PDF问答模仿 ChatPDF，用户接受度高
- 这些功能相互关联，便于一起学习

**阶段产出检验**：
- [ ] 用户能批量总结 PDF 文档内容
- [ ] 用户能批量总结 Word 文档内容
- [ ] 用户能与 PDF 文档进行问答交互

---

### 📚 阶段 14：学术辅助功能

**目标**：补充论文搜索和下载相关功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 39 | `features/academic/tex_abstract.md` | 读Tex论文写摘要 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 40 | `features/academic/google_scholar.md` | 谷歌学术检索助手 | ⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 4 |
| 41 | `features/academic/arxiv_download.md` | Arxiv论文下载与摘要翻译 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 1.5小时 | 3 |

**选择理由**：
- 自动生成摘要减轻论文写作负担
- 谷歌学术助手帮助快速检索文献
- Arxiv下载功能方便获取最新论文

**阶段产出检验**：
- [x] 用户能从 Tex 项目自动生成论文摘要
- [x] 用户能使用谷歌学术助手检索论文
- [x] 用户能一键下载 Arxiv 论文并翻译摘要

---

### 🔬 阶段 15：学术高级功能

**目标**：补充高级学术处理功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 42 | `features/academic/latex_proofread.md` | Latex英文纠错+高亮对比 | ⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 4 |
| 43 | `features/academic/pdf_nougat.md` | PDF精准翻译(NOUGAT) | ⭐⭐⭐ | ⭐⭐⭐ | 2小时 | 3 |
| 44 | `features/academic/batch_file_query.md` | 批量文件询问 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 4 |

**选择理由**：
- Latex纠错+高亮是论文修改的刚需
- NOUGAT 提供更精准的 PDF 翻译（特别是公式）
- 批量文件询问支持多种文件格式的统一处理

**阶段产出检验**：
- [ ] 用户能对 Latex 项目进行纠错并查看高亮对比
- [ ] 用户能使用 NOUGAT 翻译含公式的 PDF
- [ ] 用户能批量询问多种格式的文件

---

### 💻 阶段 16：编程功能补充

**目标**：补充遗漏的编程相关功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 45 | `features/programming/jupyter_analysis.md` | Jupyter Notebook分析 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 46 | `features/programming/custom_code_analysis.md` | 自定义源码分析 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |
| 47 | `features/programming/batch_comment_gen.md` | 批量函数注释生成 | ⭐⭐⭐ | ⭐⭐⭐ | 1.5小时 | 3 |

**选择理由**：
- Jupyter Notebook 是数据科学常用格式
- 自定义源码分析支持灵活指定文件类型
- 批量函数注释提升代码可读性

**阶段产出检验**：
- [ ] 用户能分析 Jupyter Notebook 文件
- [ ] 用户能手动指定文件类型进行源码分析
- [ ] 用户能批量为函数生成注释

---

### 💬 阶段 17：对话功能补充

**目标**：补充对话管理和图表生成功能

| 序号 | 文档路径 | 文档名称 | 重要性 | 用户关心度 | 预计工时 | 图片数 |
|:---:|---------|---------|:-----:|:--------:|:-------:|:-----:|
| 48 | `features/conversation/conversation_save.md` | 对话保存与载入 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 1.5小时 | 4 |
| 49 | `features/conversation/mermaid_gen.md` | Mermaid图表生成 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 2小时 | 5 |

**选择理由**：
- 对话保存/载入是日常使用的基础功能
- Mermaid 图表生成可视化信息，提升理解效率

**阶段产出检验**：
- [ ] 用户能保存当前对话并在以后载入
- [ ] 用户能从对话或文档生成 Mermaid 图表

---

### 📊 阶段进度追踪表

| 阶段 | 文档数 | 总工时 | 总图片数 | 状态 | 完成日期 |
|:---:|:-----:|:-----:|:-------:|:----:|:-------:|
| 阶段 1 | 3 | 9h | 19 | ✅ 已完成 | 2025-01-09 |
| 阶段 2 | 4 | 8h | 3 | ✅ 已完成 | 2025-01-09 |
| 阶段 3 | 3 | 7h | 8 | ✅ 已完成 | 2026-01-09 |
| 阶段 4 | 3 | 6h | 2 | ✅ 已完成 | 2025-01-09 |
| 阶段 5 | 3 | 6h | 3 | ✅ 已完成 | 2026-01-09 |
| 阶段 6 | 3 | 5.5h | 0 | ✅ 已完成 | 2026-01-09 |
| 阶段 7 | 3 | 9h | 15 | ✅ 已完成 | 2025-01-09 |
| 阶段 8 | 3 | 4.5h | 3 | ✅ 已完成 | 2026-01-09 |
| 阶段 9 | 3 | 5.5h | 1 | ✅ 已完成 | 2026-01-09 |
| 阶段 10 | 3 | 5.5h | 8 | ✅ 已完成 | 2025-01-09 |
| 阶段 11 | 3 | 7.5h | 4 | ✅ 已完成 | 2026-01-09 |
| 阶段 12 | 2 | 3h | 1 | ✅ 已完成 | 2026-01-09 |
| 阶段 13 | 3 | 5h | 10 | ⬜ 未开始 | - |
| 阶段 14 | 3 | 5h | 3 | ✅ 已完成 | 2026-01-09 |
| 阶段 15 | 3 | 6h | 11 | ⬜ 未开始 | - |
| 阶段 16 | 3 | 4.5h | 9 | ⬜ 未开始 | - |
| 阶段 17 | 2 | 3.5h | 2 | ✅ 已完成 | 2026-01-09 |
| **总计** | **49** | **~100h** | **~171** | - | - |

**状态图例**：
- ⬜ 未开始
- 🔄 进行中
- ✅ 已完成
- ⏸️ 暂停

---

### 💡 撰写建议

#### 每阶段工作流程

```
1. 阅读规划 → 了解本阶段3篇文档的目标
      ↓
2. 准备素材 → 截图、录制GIF、收集代码示例
      ↓
3. 撰写文档 → 按模板填充内容
      ↓
4. 本地预览 → mkdocs serve 检查效果
      ↓
5. 自检清单 → 对照检查清单逐项确认
      ↓
6. 更新进度 → 标记完成状态和日期
```

#### 建议时间安排

- **每周完成 1 个阶段**（3 篇文档）
- **每篇文档 2-3 小时**（含截图制作）
- **预计总周期**：17 周（约 4 个月）

#### 优先级调整原则

如需调整优先级，请遵循：
1. **用户反馈优先**：用户频繁询问的内容优先补充
2. **依赖关系优先**：被其他文档引用的内容优先完成
3. **核心功能优先**：使用频率高的功能优先覆盖

---

## 五、图片清单汇总

共需准备约 **120-150 张** 图片，按类型分类：

| 类型 | 数量 | 说明 |
|------|------|------|
| 界面截图 | ~70 | 主界面、配置界面、功能界面 |
| 终端输出 | ~20 | 安装、启动、运行输出 |
| 外部平台 | ~25 | OpenAI、阿里云、智谱等平台截图 |
| 流程图/对比图 | ~15 | 配置关系图、效果对比图 |
| 动图GIF | ~10 | 核心功能演示 |

### 图片制作建议

1. **统一风格**：使用相同的浏览器、相同的主题截图
2. **标注清晰**：使用红色箭头或方框标注关键位置
3. **尺寸统一**：宽度统一为 800px 或 1000px
4. **格式选择**：静态图用 PNG，动态演示用 GIF
5. **压缩优化**：使用 TinyPNG 等工具压缩图片

---

## 六、mkdocs.yml 配置

```yaml
site_name: GPT Academic
site_url: https://github.com/binary-husky/gpt_academic
site_description: "GPT Academic - 为GPT/LLM提供实用化交互界面，特别优化论文阅读/润色/写作体验"
site_author: "GPT Academic Team"
repo_url: https://github.com/binary-husky/gpt_academic
repo_name: binary-husky/gpt_academic
copyright: "Copyright &copy; 2025 GPT Academic Team"

theme:
  name: shadcn
  show_stargazers: true
  git_enabled: false
  nav_sort: false
  features:
    - content.code.copy
    - content.code.annotate

nav:
  - 首页: index.md

  - 快速开始:
      - 安装指南: get_started/installation.md
      - 快速上手: get_started/quickstart.md
      - 配置详解: get_started/configuration.md

  - 模型接入:
      - 模型概览: models/overview.md
      - OpenAI / GPT: models/openai.md
      - Azure OpenAI: models/azure.md
      - 国产模型: models/chinese_models.md
      - 本地模型: models/local_models.md
      - 自定义模型: models/custom_models.md

  - 功能指南:
      - 基础功能: features/basic_functions.md
      - 学术功能:
          - Arxiv论文翻译: features/academic/arxiv_translation.md
          - PDF论文翻译: features/academic/pdf_translation.md
          - Latex项目处理: features/academic/latex_polish.md
          - 论文阅读助手: features/academic/paper_reading.md
          - 批量总结PDF: features/academic/pdf_summary.md
          - 批量总结Word: features/academic/word_summary.md
          - PDF问答(ChatPDF): features/academic/pdf_qa.md
          - Tex论文摘要生成: features/academic/tex_abstract.md
          - 谷歌学术助手: features/academic/google_scholar.md
          - Arxiv下载与摘要翻译: features/academic/arxiv_download.md
          - Latex纠错+高亮对比: features/academic/latex_proofread.md
          - PDF精准翻译(NOUGAT): features/academic/pdf_nougat.md
          - 批量文件询问: features/academic/batch_file_query.md
      - 编程功能:
          - 源码分析: features/programming/code_analysis.md
          - 代码注释生成: features/programming/code_comment.md
          - Markdown翻译: features/programming/markdown_translate.md
          - Jupyter Notebook分析: features/programming/jupyter_analysis.md
          - 自定义源码分析: features/programming/custom_code_analysis.md
          - 批量函数注释生成: features/programming/batch_comment_gen.md
      - 对话功能:
          - 联网搜索: features/conversation/internet_search.md
          - 多模型询问: features/conversation/multi_model_query.md
          - 图片生成: features/conversation/image_generation.md
          - 语音助手: features/conversation/voice_assistant.md
          - 对话保存与载入: features/conversation/conversation_save.md
          - Mermaid图表生成: features/conversation/mermaid_gen.md
      - 智能体:
          - 虚空终端: features/agents/void_terminal.md
          - 代码解释器: features/agents/code_interpreter.md

  - 自定义扩展:
      - 自定义按钮: customization/custom_buttons.md
      - 插件开发: customization/plugin_development.md
      - 主题定制: customization/theme_customization.md

  - 部署指南:
      - Docker部署: deployment/docker.md
      - 云服务部署: deployment/cloud_deploy.md
      - 反向代理: deployment/reverse_proxy.md

  - 问题排查:
      - 常见问题: troubleshooting/faq.md
      - 网络问题: troubleshooting/network_issues.md
      - 模型错误: troubleshooting/model_errors.md

  - 参考:
      - 配置参考: reference/config_reference.md
      - 更新日志: reference/changelog.md

plugins:
  - search:
      lang:
        - en
        - zh
      separator: '[\s\-\.\(\)\/]+'
      min_search_length: 2
      prebuild_index: true
      indexing: 'full'
  - mkdocstrings:
      handlers:
        python:
          paths: [.]
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true
            show_root_full_path: false
            members_order: source
            show_submodules: true

markdown_extensions:
  - admonition
  - footnotes
  - tables
  - extra
  - attr_list
  - md_in_html
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.progressbar
  - pymdownx.snippets
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - shadcn.extensions.iconify

extra_css:
  - https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap
  - stylesheets/feature-cards.css
  - stylesheets/tabbed-code.css
  - stylesheets/readability-enhancements.css
  - stylesheets/code-enhancements.css
  - stylesheets/syntax-highlight.css
  - stylesheets/table-enhancements.css
  - stylesheets/jupyter-simple.css
  - stylesheets/nav-scroll-fix.css
  - stylesheets/workflow.css
  - stylesheets/animations.css
  - stylesheets/mermaid.css
  - stylesheets/mkdocstrings.css
  - stylesheets/responsive.css

extra_javascript:
  - javascripts/tabbed-code.js
  - javascripts/code-copy.js
  - javascripts/search-fix.js
  - javascripts/code-zoom.js
  - javascripts/nav-scroll-fix.js
  - javascripts/animations.js
  - javascripts/responsive.js
```

---

## 七、文档模板

### 功能文档模板

```markdown
# {功能名称}

## 功能说明
{一句话描述这个功能能做什么}

## 前置条件
- {条件1}
- {条件2}

## 使用方法

### 步骤1：{步骤名称}
{步骤说明}

<!-- IMAGE: {图片文件名} -->
<!-- 描述: {图片应展示的内容} -->
<!-- 尺寸建议: {宽度}px -->
![{alt文本}](../images/{图片文件名})

### 步骤2：{步骤名称}
{步骤说明}

<!-- IMAGE: {图片文件名} -->
![{alt文本}](../images/{图片文件名})

## 高级用法
{可选的高级配置或用法}

## 常见问题

### Q: {问题1}
**A**: {答案1}

### Q: {问题2}
**A**: {答案2}

## 相关文档
- [{相关文档1}]({链接})
- [{相关文档2}]({链接})
```

---

## 八、检查清单

每篇文档完成后，使用此清单检查：

- [ ] 标题层级正确（h1 只有一个）
- [ ] 前置条件已说明
- [ ] 步骤可操作、可验证
- [ ] 关键步骤配有截图
- [ ] 代码块可直接复制
- [ ] 常见问题已覆盖
- [ ] 图片命名符合规范
- [ ] 内部链接正确
- [ ] 无错别字和语法错误
- [ ] 在 mkdocs serve 中预览正常
