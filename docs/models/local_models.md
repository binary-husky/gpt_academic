# 本地模型部署

在云端 API 之外，GPT Academic 还支持接入完全运行在本地的大语言模型。本地部署意味着您的所有数据都不会离开您的计算机——这对于处理敏感的学术论文、商业代码或私密对话来说尤为重要。此外，本地模型不受 API 配额限制，一旦部署完成便可无限制使用。

本文将引导您完成本地模型的部署和配置。根据您的硬件条件和使用场景，您可以选择最适合自己的部署方案。

---

## 选择合适的方案

在开始之前，请先评估您的硬件条件。本地模型对计算资源有一定要求，不同规模的模型所需的显存和内存差异很大。下表列出了常见的本地模型及其硬件需求：

| 模型名称 | 模型标识符 | 显存需求 | 推荐方案 | 特点说明 |
|---------|-----------|---------|---------|---------|
| ChatGLM4-9B | `chatglm4` | 16GB+ | 原生部署 | 智谱最新模型，中文能力出色 |
| ChatGLM3-6B | `chatglm3` | 13GB | 原生部署 | 经典选择，平衡性能与资源 |
| ChatGLM2-6B | `chatglm` | 13GB | 原生部署 | 稳定版本，兼容性好 |
| Qwen 系列 | `qwen-local` | 6-24GB | 原生/VLLM | 阿里通义千问本地版 |
| Llama 2/3 | `ollama-*` | 8-48GB | Ollama | Meta 开源模型，英文能力强 |
| 任意模型 | `ollama-*` | 视模型而定 | Ollama | 通过 Ollama 统一管理 |
| 自定义模型 | `vllm-*` | 视模型而定 | VLLM | 高性能推理，支持张量并行 |

基于这些信息，我们推荐以下选择路径：

- **显卡显存 ≥ 16GB，追求简单易用** → 使用 Ollama 部署（推荐）
- **显卡显存 ≥ 13GB，需要最佳中文体验** → 原生部署 ChatGLM3/4
- **显卡显存 ≥ 24GB，需要高性能推理** → 使用 VLLM 部署
- **仅有 CPU 或低显存显卡** → 使用 Ollama 运行量化模型

---

## 方案一：使用 Ollama 部署（推荐）

Ollama 是一个简洁高效的本地大模型运行工具，它将模型下载、量化和推理服务封装为简单的命令行操作。对于大多数用户而言，这是最省心的本地模型部署方式。

### 安装 Ollama

Ollama 的安装非常简单。访问 [ollama.com](https://ollama.com) 下载对应您操作系统的安装包，或使用以下命令直接安装：

=== "Linux / macOS"

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

=== "Windows"

    前往 [ollama.com/download](https://ollama.com/download) 下载 Windows 安装程序并运行。

安装完成后，Ollama 会自动作为后台服务运行，默认监听 `http://localhost:11434`。

### 下载并运行模型

Ollama 提供了丰富的预配置模型。以 Llama 3.2 为例，只需一条命令即可完成模型下载和启动：

```bash
ollama run llama3.2
```

首次运行时，Ollama 会自动下载模型文件（约 2-4GB），随后启动一个交互式对话界面。您可以在此测试模型是否正常工作，然后按 `Ctrl+D` 或输入 `/bye` 退出。

!!! tip "其他推荐模型"
    Ollama 支持数百种开源模型。对于中文场景，您可以尝试：

    - `ollama run qwen2.5:7b` — 通义千问 2.5，中文优秀
    - `ollama run deepseek-r1:7b` — DeepSeek R1，推理能力强

    完整模型列表请访问 [ollama.com/library](https://ollama.com/library)

### 配置 GPT Academic

模型准备就绪后，在 `config_private.py` 中添加以下配置：

```python
# Ollama 本地模型配置
LLM_MODEL = "ollama-llama3.2"  # 模型标识格式：ollama-{模型名}
OLLAMA_API_BASE = "http://localhost:11434"  # Ollama 服务地址

# 将模型添加到可用列表，以便在界面上切换
AVAIL_LLM_MODELS = [
    "ollama-llama3.2",
    "ollama-qwen2.5:7b",
    # ... 其他模型
]
```

模型标识符的格式为 `ollama-{模型名}`，其中模型名需与 `ollama run` 时使用的名称一致。如果您使用了带标签的模型（如 `qwen2.5:7b`），配置时也需要包含标签。

此外，您还可以通过括号语法指定模型参数。例如，`ollama-llama3.2(max_token=4096)` 会将最大 token 数设置为 4096。

---

## 方案二：原生部署 ChatGLM

如果您需要最佳的中文对话体验，并且拥有 NVIDIA GPU，可以选择原生部署 ChatGLM 系列模型。这种方式省去了 Ollama 中间层，能够充分发挥模型性能。

### 安装依赖

ChatGLM 模型需要额外的 Python 依赖。根据您选择的模型版本，安装对应的依赖包：

=== "ChatGLM4 (推荐)"

    ```bash
    pip install -r request_llms/requirements_chatglm4.txt
    pip install modelscope
    ```

=== "ChatGLM3"

    ```bash
    pip install -r request_llms/requirements_chatglm.txt
    ```

### 下载模型权重

模型权重可以从 ModelScope 或 Hugging Face 下载。以 ChatGLM4-9B 为例：

```bash
# 使用 ModelScope 下载（国内推荐）
modelscope download --model ZhipuAI/glm-4-9b-chat --local_dir ./THUDM/glm-4-9b-chat
```

下载完成后，模型文件将保存在 `./THUDM/glm-4-9b-chat` 目录下。您也可以选择其他路径，只需在后续配置中正确指定即可。

!!! note "关于模型大小"
    ChatGLM4-9B 完整模型约 18GB，下载时间取决于您的网络速度。如果显存不足，可以考虑使用量化版本或选择参数更少的 ChatGLM3-6B。

### 配置 GPT Academic

在 `config_private.py` 中添加以下配置：

```python
# ChatGLM 本地模型配置
LLM_MODEL = "chatglm4"  # 或 "chatglm3", "chatglm"
CHATGLM_LOCAL_MODEL_PATH = "./THUDM/glm-4-9b-chat"  # 模型存放路径

# 运行设备配置
LOCAL_MODEL_DEVICE = "cuda"  # 使用 GPU；如只有 CPU，改为 "cpu"
LOCAL_MODEL_QUANT = "FP16"   # 精度选项：FP16, INT8, INT4

# 添加到可用模型列表
AVAIL_LLM_MODELS = ["chatglm4", "chatglm3", "gpt-3.5-turbo"]
```

配置中的关键参数说明如下：

`LOCAL_MODEL_DEVICE` 决定模型运行在 GPU 还是 CPU 上。GPU 模式推理速度快但需要足够显存；CPU 模式则会非常缓慢，仅建议在测试时使用。

`LOCAL_MODEL_QUANT` 控制模型精度。`FP16` 是默认的半精度模式，提供最佳性能；`INT8` 和 `INT4` 是量化模式，可以显著减少显存占用，但会略微影响输出质量。如果您的显存不足以运行 FP16，可以尝试量化模式。

---

## 方案三：使用 VLLM 部署

VLLM 是一个高性能的 LLM 推理引擎，支持 PagedAttention、连续批处理等先进技术，特别适合需要高吞吐量或多用户并发的场景。如果您拥有多张 GPU 并希望充分利用硬件性能，VLLM 是理想的选择。

### 启动 VLLM 服务

首先，安装并启动 VLLM 服务。以下示例使用 Qwen 1.5 32B 模型，您可以根据需要替换为其他模型：

```bash
# 安装 VLLM
pip install vllm

# 启动服务（单 GPU）
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --dtype=half

# 多 GPU 张量并行（以 2 卡为例）
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --tensor-parallel-size 2 \
    --dtype=half
```

服务启动后，默认监听 `http://localhost:8000`。您可以使用 curl 命令测试服务是否正常：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/path/to/your/model",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 配置 GPT Academic

VLLM 服务提供了与 OpenAI 兼容的 API 接口，因此配置方式比较特殊。在 `config_private.py` 中添加：

```python
# VLLM 模型配置
# 格式：vllm-{模型路径}(max_token={数值})
LLM_MODEL = "vllm-/path/to/your/model(max_token=4096)"

# API 密钥（VLLM 本地服务不需要真实密钥，但格式必须正确）
API_KEY = "sk-placeholder"

# 将 OpenAI API 请求重定向到 VLLM 服务
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "http://localhost:8000/v1/chat/completions"
}
```

模型标识符的格式为 `vllm-{模型路径}(max_token={数值})`，其中模型路径需与启动 VLLM 时 `--model` 参数保持一致。`max_token` 用于指定单次请求的最大 token 数。

---

## 验证配置

完成配置后，启动 GPT Academic 验证本地模型是否正常工作：

```bash
python main.py
```

在浏览器中打开界面后，从右上角的模型下拉菜单中选择您配置的本地模型，然后发送一条测试消息。如果收到正常回复，说明配置成功。

<!-- IMAGE: model_local_01_verify.png -->
<!-- 描述: GPT Academic 界面截图，展示模型下拉菜单选择本地模型（如 ollama-llama3.2），以及一次成功的对话 -->
<!-- 标注: 用红框标注模型下拉菜单位置 -->
<!-- 尺寸建议: 1000px -->
![本地模型验证](../images/model_local_01_verify.png)

!!! warning "首次加载说明"
    原生部署的 ChatGLM 等模型首次使用时需要加载模型权重到显存，这个过程可能需要 1-3 分钟。在模型加载期间，界面会显示"正在加载模型"等提示信息，请耐心等待。

---

## 常见问题

### 显存不足（CUDA out of memory）

???+ question "运行时提示 CUDA out of memory"
    这通常意味着您的显卡显存不足以加载完整模型。您可以尝试以下解决方案：

    **方案一：使用量化模型**

    在配置中启用 INT8 或 INT4 量化：
    ```python
    LOCAL_MODEL_QUANT = "INT4"  # 显存占用约为 FP16 的 1/4
    ```

    **方案二：选择更小的模型**

    如果使用 ChatGLM4-9B 显存不足，可以尝试 ChatGLM3-6B 或通过 Ollama 使用更小的量化模型。

    **方案三：使用 CPU 模式（仅供测试）**

    将 `LOCAL_MODEL_DEVICE` 设为 `"cpu"` 可以完全避免显存问题，但推理速度会非常缓慢。

### Ollama 连接失败

???+ question "提示无法连接到 Ollama 服务"
    首先确认 Ollama 服务正在运行：

    ```bash
    # 检查 Ollama 状态
    ollama list

    # 如果服务未启动，手动启动
    ollama serve
    ```

    如果您修改了 Ollama 的监听地址，请确保 `OLLAMA_API_BASE` 配置正确。

### 模型响应异常

???+ question "模型返回空回复或乱码"
    这可能是由于模型加载不完整或配置错误导致的。请检查：

    1. 模型文件是否完整下载
    2. `CHATGLM_LOCAL_MODEL_PATH` 路径是否正确
    3. 终端是否有错误日志输出

    如果问题持续，尝试重新下载模型或切换到其他模型进行测试。

---

## 下一步

本地模型部署完成后，您可以：

- 在 [配置详解](../get_started/configuration.md) 中了解更多高级配置选项
- 学习 [多模型询问](../features/conversation/multi_model_query.md) 功能，对比本地模型与云端模型的表现
- 探索 [插件开发](../customization/plugin_development.md)，为本地模型定制专属功能
