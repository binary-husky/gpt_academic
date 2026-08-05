# 安装指南

本指南将帮助您在本地环境中安装和运行 GPT Academic。无论您是 Python 新手还是有经验的开发者，都可以根据本文档顺利完成安装。

---

## 环境要求

在开始安装之前，请确保您的系统满足以下基本要求：

| 项目 | 要求 | 说明 |
|-----|------|------|
| 操作系统 | Windows / macOS / Linux | 均已测试支持 |
| Python | **3.9 - 3.11** | 推荐使用 3.10 版本 |
| Git | 任意版本 | 用于克隆代码仓库 |
| 网络 | 能访问 GitHub | 国内用户可能需要代理 |

!!! warning "Python 版本注意"
    本项目使用定制版 Gradio，**不兼容 Python 3.12 及以上版本**。如果您使用了较新的 Python 版本，可能会遇到依赖安装问题。

---

## 获取源代码

首先，打开终端（Windows 用户可使用 PowerShell 或 CMD），执行以下命令将项目克隆到本地：

```bash
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

这里使用了 `--depth=1` 参数进行浅克隆，可以显著加快下载速度。如果您需要完整的 Git 历史记录，可以去掉这个参数。

!!! tip "国内用户加速方案"
    如果克隆速度较慢，可以使用镜像地址：
    ```bash
    git clone --depth=1 https://gitee.com/binary-husky/gpt_academic.git
    ```

---

## 安装依赖

项目提供了完整的依赖清单，您可以根据自己的习惯选择以下任一方式安装。

=== "pip（推荐）"

    这是最简单直接的安装方式，适合大多数用户：

    ```bash
    pip install -r requirements.txt
    ```

    安装过程中会自动下载项目定制的 Gradio 版本及其他必要依赖。整个过程通常需要 2-5 分钟，具体取决于您的网络速度。

=== "conda"

    如果您使用 Anaconda 或 Miniconda 管理 Python 环境，建议先创建一个独立的虚拟环境：

    ```bash
    conda create -n gptac python=3.10
    conda activate gptac
    pip install -r requirements.txt
    ```

    使用虚拟环境可以避免与系统中其他 Python 项目产生依赖冲突。

=== "uv（高级）"

    [uv](https://github.com/astral-sh/uv) 是一个极速的 Python 包管理器，安装速度比 pip 快 10-100 倍：

    ```bash
    # 安装 uv（如果尚未安装）
    pip install uv

    # 创建虚拟环境并安装依赖
    uv venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    uv pip install -r requirements.txt
    ```

---

## 验证安装

安装完成后，您可以通过启动程序来验证安装是否成功：

```bash
python main.py
```

如果一切正常，您将在终端看到类似以下的输出：

```
INFO: 如果浏览器没有自动打开，请复制并转到以下URL：
INFO: 「暗色主题已启用（支持动态切换主题）」: http://localhost:xxxxx
```

此时浏览器应该会自动打开并显示 GPT Academic 的界面。如果浏览器没有自动打开，您可以手动复制终端中显示的 URL 并在浏览器中访问。

<!-- IMAGE: gs_01_startup_verify.png -->
<!-- 描述: 终端启动成功输出截图，显示URL地址；浏览器中打开的GPT Academic初始界面，两者可合并为一张图 -->
<!-- 标注: 用红框标注终端中的URL地址，用箭头指向浏览器界面 -->
<!-- 尺寸建议: 1000px -->
![启动验证](../images/gs_01_startup_verify.png)

!!! note "首次启动说明"
    首次启动时可能会下载一些额外的资源（如 tiktoken 编码器），这是正常现象。如果您尚未配置 API 密钥，界面可以正常显示，但无法进行对话。下一步请参阅 [快速上手](quickstart.md) 配置您的 API 密钥。

---

## 常见安装问题

### 依赖安装失败：externally-managed-environment

???+ question "在 Ubuntu 23.04+ 或 Debian 12+ 上安装时提示此错误"
    这是因为新版本的 Linux 发行版默认启用了 PEP 668 保护机制。解决方案是使用虚拟环境：

    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### Gradio 版本冲突

???+ question "提示 Gradio 版本不正确"
    本项目使用定制版 Gradio 3.32.15，如果您的环境中已安装其他版本，可能会产生冲突。请确保使用项目提供的 requirements.txt 进行安装，它会自动安装正确的版本。

    如果问题持续，尝试先卸载现有 Gradio：
    ```bash
    pip uninstall gradio gradio-client -y
    pip install -r requirements.txt
    ```

### 网络超时

???+ question "安装依赖时下载超时"
    国内用户可以配置 pip 镜像源加速下载：

    ```bash
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

---

## 下一步

恭喜您完成了安装！接下来请继续阅读 [快速上手](quickstart.md)，学习如何配置 API 密钥并开始您的第一次对话。
