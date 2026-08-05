# 自定义模型开发

本文档面向希望将新的大语言模型接入 GPT Academic 的开发者。无论您是要接入一个尚未支持的在线 API 服务，还是部署自己训练的本地模型，本指南都将为您提供清晰的技术路径。在开始之前，建议您先熟悉 GPT Academic 的基本使用和配置，对 Python 和 HTTP API 调用有一定了解。

---

## 模型接入架构

GPT Academic 采用模块化的模型接入架构，所有模型调用都通过 `request_llms/bridge_all.py` 文件进行统一路由。这个设计使得添加新模型变得相对简单——您只需实现特定的接口函数，然后将模型注册到路由表中即可。

整个调用流程如下：用户在界面上选择模型并发送消息，系统根据模型名称在 `model_info` 字典中查找对应的处理函数，然后调用该函数与模型服务通信，最后将响应返回给用户界面。

每个模型需要实现两个核心函数：

| 函数 | 用途 | 特点 |
|-----|------|------|
| `predict` | 界面对话 | 流式输出，实时更新界面，支持用户交互 |
| `predict_no_ui_long_connection` | 插件调用 | 非界面模式，支持多线程，返回完整结果 |

理解这两个函数的区别是成功接入新模型的关键。`predict` 函数用于用户直接对话，需要支持流式输出以提供良好的体验；`predict_no_ui_long_connection` 则用于后台任务（如批量翻译），需要稳定且可并发调用。

---

## 快速接入方式

如果您要接入的模型服务兼容 OpenAI API 格式（这是目前大多数模型服务的选择），您可以使用 GPT Academic 提供的快捷前缀机制，完全无需编写代码。

### 使用 One-API 前缀

适用于自建的 One-API 服务或任何 OpenAI 兼容接口：

```python
# config_private.py

# 配置 API 密钥和重定向地址
API_KEY = "your-api-key"
API_URL_REDIRECT = {
    "https://api.openai.com/v1/chat/completions": "https://your-service.com/v1/chat/completions"
}

# 添加模型，格式：one-api-{模型名}(max_token={上下文长度})
AVAIL_LLM_MODELS = [
    "one-api-your-model-name(max_token=8000)",
]
```

系统会自动使用 OpenAI 兼容的方式调用您指定的服务。`max_token` 参数帮助系统在对话过长时正确裁剪历史记录。

### 使用 Ollama 前缀

适用于本地部署的 Ollama 服务：

```python
# config_private.py

# 如果 Ollama 不在默认地址，需要配置重定向
API_URL_REDIRECT = {
    "http://localhost:11434/api/chat": "http://your-ollama-host:11434/api/chat"
}

# 添加模型
AVAIL_LLM_MODELS = [
    "ollama-llama3(max_token=8000)",
    "ollama-qwen2(max_token=32000)",
]
```

### 使用 OpenRouter 前缀

OpenRouter 聚合了众多模型提供商，通过一个 API 即可访问上百种模型：

```python
# config_private.py

API_KEY = "sk-or-v1-your-openrouter-key"

# 模型名称格式：openrouter-{provider}/{model-id}
AVAIL_LLM_MODELS = [
    "openrouter-anthropic/claude-3.5-sonnet",
    "openrouter-google/gemini-pro-1.5",
    "openrouter-meta-llama/llama-3.1-70b-instruct",
]
```

### 使用火山引擎前缀

接入火山引擎托管的模型：

```python
# config_private.py

ARK_API_KEY = "your-ark-api-key"

AVAIL_LLM_MODELS = [
    "volcengine-deepseek-r1-250120",
    "volcengine-deepseek-v3-241226",
]
```

---

## 使用标准模板开发

如果您要接入的模型使用 OpenAI 兼容的 API 格式，但需要一些定制化处理（如特殊的认证方式或响应解析），可以使用 `oai_std_model_template.py` 提供的模板函数快速生成接口实现。

这个模板已经封装了 HTTP 请求、流式响应解析、错误处理等通用逻辑，您只需指定少量参数即可生成完整的模型接口。

### 模板使用示例

假设您要接入一个名为 "NewModel" 的服务，其 API 格式与 OpenAI 兼容：

```python
# 在 request_llms/bridge_all.py 中添加

# 导入模板函数
from .oai_std_model_template import get_predict_function

# 生成接口函数
newmodel_noui, newmodel_ui = get_predict_function(
    api_key_conf_name="NEWMODEL_API_KEY",  # config.py 中的 API 密钥配置项名称
    max_output_token=4096,                  # 单次请求的最大输出 token
    disable_proxy=False,                    # 是否禁用代理
)

# 注册到模型信息表
model_info.update({
    "newmodel-7b": {
        "fn_with_ui": newmodel_ui,
        "fn_without_ui": newmodel_noui,
        "endpoint": "https://api.newmodel.com/v1/chat/completions",
        "max_token": 32000,          # 模型的上下文窗口大小
        "tokenizer": tokenizer_gpt35,
        "token_cnt": get_token_num_gpt35,
    },
})
```

然后在 `config.py` 或 `config_private.py` 中添加密钥配置：

```python
NEWMODEL_API_KEY = "your-api-key-here"
```

### 模板参数说明

`get_predict_function` 函数接受以下参数：

| 参数 | 类型 | 说明 |
|-----|------|------|
| `api_key_conf_name` | `str` | config 中 API 密钥的配置项名称 |
| `max_output_token` | `int` | 单次请求的最大输出 token 数 |
| `disable_proxy` | `bool` | 是否禁用代理（国内服务建议设为 True） |
| `model_remove_prefix` | `list` | 需要从模型名移除的前缀列表 |

---

## 完整自定义开发

对于 API 格式不兼容 OpenAI 的模型（如使用 WebSocket、特殊认证或非标准响应格式的服务），您需要编写完整的模型接入模块。这种方式提供了最大的灵活性，但也需要更多的开发工作。

### 创建模型接口文件

在 `request_llms/` 目录下创建新文件，例如 `bridge_mymodel.py`：

```python
"""
MyModel 模型接入模块

该模块实现了 MyModel 大语言模型的接口封装，
提供界面对话和后台调用两种模式。
"""

import time
import requests
from toolbox import get_conf, update_ui, update_ui_latest_msg, trimmed_format_exc
from loguru import logger

# 读取配置
MYMODEL_API_KEY, TIMEOUT_SECONDS, MAX_RETRY, proxies = get_conf(
    "MYMODEL_API_KEY", "TIMEOUT_SECONDS", "MAX_RETRY", "proxies"
)

# 超时提示消息
TIMEOUT_MSG = "[Local Message] 请求超时，请检查网络连接或 API 服务状态。"


def predict_no_ui_long_connection(
    inputs: str,
    llm_kwargs: dict,
    history: list = [],
    sys_prompt: str = "",
    observe_window: list = None,
    console_silence: bool = False,
) -> str:
    """
    非界面模式的模型调用函数，用于插件和后台任务。

    Args:
        inputs: 用户本次输入的内容
        llm_kwargs: LLM 调用参数，包含 temperature、llm_model 等
        history: 对话历史列表，格式为 [user1, assistant1, user2, assistant2, ...]
        sys_prompt: 系统提示词
        observe_window: 观测窗口，用于跨线程传递输出 [当前输出, 看门狗时间戳, ...]
        console_silence: 是否静默控制台输出

    Returns:
        模型的完整响应文本
    """
    # 检查 API 密钥
    if not MYMODEL_API_KEY:
        raise RuntimeError("MYMODEL_API_KEY 未配置，请在 config_private.py 中设置")

    # 处理空输入
    if not inputs.strip():
        inputs = "你好"

    # 构建请求消息
    messages = [{"role": "system", "content": sys_prompt}]

    # 添加历史对话
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            messages.append({"role": "user", "content": history[i]})
            messages.append({"role": "assistant", "content": history[i + 1]})

    # 添加当前输入
    messages.append({"role": "user", "content": inputs})

    # 构建请求体（根据 API 格式调整）
    payload = {
        "model": llm_kwargs.get("llm_model", "mymodel-default"),
        "messages": messages,
        "temperature": llm_kwargs.get("temperature", 0.7),
        "stream": True,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MYMODEL_API_KEY}",
    }

    # 发送请求（带重试机制）
    endpoint = "https://api.mymodel.com/v1/chat/completions"
    retry_count = 0

    while True:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                stream=True,
                timeout=TIMEOUT_SECONDS,
                proxies=proxies,
            )
            break
        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count > MAX_RETRY:
                raise TimeoutError(TIMEOUT_MSG)
            logger.warning(f"请求失败，正在重试 ({retry_count}/{MAX_RETRY})...")
            time.sleep(1)

    # 解析流式响应
    result = ""
    watch_dog_patience = 5  # 看门狗超时时间

    for line in response.iter_lines():
        if not line:
            continue

        # 根据 API 返回格式解析（以 OpenAI 格式为例）
        line_text = line.decode("utf-8")
        if line_text.startswith("data: "):
            line_text = line_text[6:]

        if line_text == "[DONE]":
            break

        try:
            import json
            chunk = json.loads(line_text)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            result += content

            # 更新观测窗口（如果提供）
            if observe_window is not None:
                observe_window[0] = result
                # 检查看门狗（用户是否取消）
                if len(observe_window) >= 2:
                    if time.time() - observe_window[1] > watch_dog_patience:
                        raise RuntimeError("用户取消了请求")
        except json.JSONDecodeError:
            continue

    if not console_silence:
        logger.info(f"[MyModel Response] {result[:100]}...")

    return result


def predict(
    inputs: str,
    llm_kwargs: dict,
    plugin_kwargs: dict,
    chatbot: list,
    history: list = [],
    system_prompt: str = "",
    stream: bool = True,
    additional_fn: str = None,
):
    """
    界面对话模式的模型调用函数。

    这是一个生成器函数，通过 yield 实现流式输出。

    Args:
        inputs: 用户输入
        llm_kwargs: LLM 参数
        plugin_kwargs: 插件参数
        chatbot: 对话界面组件，格式为 [(user1, bot1), (user2, bot2), ...]
        history: 对话历史
        system_prompt: 系统提示词
        stream: 是否流式输出（已弃用，保持兼容）
        additional_fn: 基础功能区按钮的附加功能
    """
    # 检查 API 密钥
    if not MYMODEL_API_KEY:
        chatbot.append((inputs, "[错误] MYMODEL_API_KEY 未配置"))
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 处理基础功能区按钮
    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    # 添加用户输入到对话框
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="正在等待响应...")

    # 构建请求（与 predict_no_ui_long_connection 类似）
    messages = [{"role": "system", "content": system_prompt}]
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            messages.append({"role": "user", "content": history[i]})
            messages.append({"role": "assistant", "content": history[i + 1]})
    messages.append({"role": "user", "content": inputs})

    payload = {
        "model": llm_kwargs.get("llm_model", "mymodel-default"),
        "messages": messages,
        "temperature": llm_kwargs.get("temperature", 0.7),
        "stream": True,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MYMODEL_API_KEY}",
    }

    # 发送请求
    endpoint = "https://api.mymodel.com/v1/chat/completions"

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            stream=True,
            timeout=TIMEOUT_SECONDS,
            proxies=proxies,
        )
    except requests.exceptions.RequestException:
        chatbot[-1] = (inputs, TIMEOUT_MSG)
        yield from update_ui(chatbot=chatbot, history=history, msg="请求超时")
        return

    # 流式解析并更新界面
    gpt_reply = ""
    history.append(inputs)
    history.append("")

    for line in response.iter_lines():
        if not line:
            continue

        line_text = line.decode("utf-8")
        if line_text.startswith("data: "):
            line_text = line_text[6:]

        if line_text == "[DONE]":
            break

        try:
            import json
            chunk = json.loads(line_text)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            gpt_reply += content

            # 更新界面
            history[-1] = gpt_reply
            chatbot[-1] = (inputs, gpt_reply)
            yield from update_ui(chatbot=chatbot, history=history)
        except json.JSONDecodeError:
            continue

    logger.info(f"[MyModel] 对话完成")
```

### 注册模型

在 `request_llms/bridge_all.py` 中导入并注册您的模型：

```python
# 在文件适当位置添加导入
if "mymodel" in AVAIL_LLM_MODELS:
    try:
        from .bridge_mymodel import predict_no_ui_long_connection as mymodel_noui
        from .bridge_mymodel import predict as mymodel_ui
        model_info.update({
            "mymodel": {
                "fn_with_ui": mymodel_ui,
                "fn_without_ui": mymodel_noui,
                "endpoint": "https://api.mymodel.com/v1/chat/completions",
                "max_token": 32000,
                "tokenizer": tokenizer_gpt35,
                "token_cnt": get_token_num_gpt35,
            }
        })
    except Exception as e:
        logger.error(f"加载 MyModel 失败: {e}")
```

### 添加配置项

在 `config.py` 中添加配置项定义和说明：

```python
# MyModel 配置
MYMODEL_API_KEY = ""  # 您的 MyModel API 密钥
```

---

## 模型信息字段说明

在 `model_info` 中注册模型时，可以使用以下字段：

| 字段 | 类型 | 必填 | 说明 |
|-----|------|:---:|------|
| `fn_with_ui` | `function` | ✓ | 界面对话函数 |
| `fn_without_ui` | `function` | ✓ | 后台调用函数 |
| `endpoint` | `str` | ✓ | API 端点地址 |
| `max_token` | `int` | ✓ | 模型上下文窗口大小 |
| `tokenizer` | `object` | ✓ | 分词器（用于计算 token） |
| `token_cnt` | `function` | ✓ | token 计数函数 |
| `can_multi_thread` | `bool` | | 是否支持多线程调用 |
| `has_multimodal_capacity` | `bool` | | 是否支持多模态（图片输入） |
| `enable_reasoning` | `bool` | | 是否启用思维链展示 |
| `azure_api_key` | `str` | | Azure 专用密钥（Azure 模型使用） |

---

## 开发调试建议

在开发新模型接口时，建议按以下步骤进行：

**第一步**，先实现 `predict_no_ui_long_connection` 函数并进行单元测试，确保能够正确发送请求和解析响应。您可以创建一个简单的测试脚本：

```python
# test_mymodel.py
from request_llms.bridge_mymodel import predict_no_ui_long_connection

result = predict_no_ui_long_connection(
    inputs="你好，请介绍一下你自己",
    llm_kwargs={"llm_model": "mymodel", "temperature": 0.7},
    history=[],
    sys_prompt="你是一个有帮助的助手。",
)
print(result)
```

**第二步**，实现 `predict` 函数，注意正确使用 `yield from update_ui()` 来更新界面。

**第三步**，在 `bridge_all.py` 中注册模型，启动 GPT Academic 进行集成测试。测试时重点关注：流式输出是否正常、对话历史是否正确保留、错误处理是否友好。

**第四步**，测试插件调用场景，确保在多线程环境下模型接口稳定可靠。

<!-- IMAGE: model_02_custom_dev_arch.png -->
<!-- 描述: 模型接入架构图，展示从用户界面到模型调用的数据流向 -->
<!-- 标注: 标注关键组件：用户界面 → bridge_all.py（路由）→ bridge_xxx.py（模型接口）→ 模型API -->
<!-- 尺寸建议: 1000px -->
![模型接入架构](../images/model_02_custom_dev_arch.png)

---

## 相关文档

- [模型概览](overview.md) — 了解已支持的模型
- [中转渠道接入](transit_api.md) — 使用前缀方式快速接入
- [配置参考](../reference/config_reference.md) — 配置项完整说明
- [插件开发](../customization/plugin_development.md) — 了解如何开发功能插件
