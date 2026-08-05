# 自定义快捷按钮

在日常使用中，您可能会发现某些特定的提示词组合使用频率很高——比如将文本翻译成特定的学术风格、按照固定格式生成代码注释、或者用专业术语润色技术文档。GPT Academic 提供了自定义按钮功能，让您可以把这些常用的提示词模板固化为界面上的快捷按钮，一键触发专属的 AI 工作流。

本文将介绍两种创建自定义按钮的方式：通过界面配置和通过代码修改。界面方式适合快速创建个人专属按钮，配置会保存在浏览器本地；代码方式则适合团队共享或需要更高级功能的场景。

---

## 通过界面添加按钮

这是最便捷的方式，无需修改任何代码，配置会自动保存在浏览器的本地存储中。

### 打开自定义菜单

在 GPT Academic 主界面的左下角，找到 **界面外观** 下拉菜单并点击展开。在弹出的浮动面板中选择 **自定义菜单** 选项，这会打开按钮配置界面。

<!-- IMAGE: custom_01_open_menu.png -->
<!-- 描述: 点击界面外观后展开的菜单，高亮显示"自定义菜单"选项的位置 -->
<!-- 标注: ① 界面外观按钮位置 ② 自定义菜单选项 -->
<!-- 尺寸建议: 600px -->
![打开自定义菜单](../images/custom_01_open_menu.png)

### 配置按钮参数

自定义菜单面板包含四个核心配置项。首先，在最上方的下拉框中选择要配置的按钮槽位——系统预留了 4 个自定义按钮槽位（自定义按钮1~4），您也可以选择覆盖现有的基础功能按钮如"学术润色"等。

接下来填写三个文本框：

- **按钮名称**：显示在界面上的按钮文字，建议简短明了，如"论文翻译"、"代码审查"
- **提示前缀**：添加在用户输入内容**之前**的提示词，用于描述任务要求
- **提示后缀**：添加在用户输入内容**之后**的补充说明

当您点击自定义按钮时，系统会将这三部分按"前缀 + 用户输入 + 后缀"的顺序拼接，然后发送给 AI。

<!-- IMAGE: custom_02_config_panel.png -->
<!-- 描述: 自定义菜单的配置面板，展示各个输入框的位置和作用 -->
<!-- 标注: ① 按钮槽位选择下拉框 ② 按钮名称输入框 ③ 提示前缀输入框 ④ 提示后缀输入框 ⑤ 确认保存按钮 -->
<!-- 尺寸建议: 800px -->
![配置面板](../images/custom_02_config_panel.png)

### 保存并使用

配置完成后点击 **确认并保存** 按钮，新创建的按钮会立即出现在基础功能区。此时在输入框中输入需要处理的文本，点击您的自定义按钮，AI 就会按照预设的提示词模板进行处理。

如果需要恢复默认设置，点击 **恢复默认** 按钮可以清除所有自定义配置。

!!! tip "配置持久化"
    通过界面创建的自定义按钮配置保存在浏览器的 localStorage 中。这意味着在同一浏览器中再次访问时，配置会自动恢复。但如果您更换浏览器或清除浏览器数据，配置将丢失。对于需要长期保存或跨设备使用的配置，建议采用代码方式。

---

## 通过代码添加按钮

代码方式提供了更强大的功能控制，包括按钮颜色、自动清除历史、文本预处理等高级选项。所有预设的基础功能按钮都在 `core_functional.py` 文件中定义。

### 配置文件结构

打开项目根目录下的 `core_functional.py` 文件，您会看到 `get_core_functions()` 函数返回一个字典，每个键值对定义了一个按钮。以"学术语料润色"按钮为例：

```python
"学术语料润色": {
    "Prefix":   "作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性...",
    "Suffix":   "",
    "Color":    "secondary",
    "Visible":  True,
    "AutoClearHistory": False,
    "PreProcess": None,
},
```

### 添加新按钮

要添加自己的按钮，在 `get_core_functions()` 函数的返回字典中增加新的条目即可。下面是一个完整的示例，创建一个将文本翻译为学术英文的按钮：

```python
"学术英译": {
    "Prefix":   "Please translate the following Chinese text into formal academic English. "
                "Maintain the original meaning while using appropriate academic vocabulary and sentence structures. "
                "The text to translate is:\n\n",
    "Suffix":   "\n\nPlease provide only the translation without explanations.",
    "Color":    "primary",
    "Visible":  True,
},
```

修改完成后保存文件，重新启动应用即可看到新按钮。由于 GPT Academic 支持热重载，如果在 `config.py` 中启用了 `PLUGIN_HOT_RELOAD = True`，部分修改无需重启即可生效。

### 参数详解

每个按钮支持以下配置参数：

| 参数 | 类型 | 必填 | 说明 |
|-----|------|:----:|------|
| `Prefix` | str | 是 | 添加在用户输入前的提示词 |
| `Suffix` | str | 是 | 添加在用户输入后的提示词 |
| `Color` | str | 否 | 按钮颜色：`primary`（强调色）、`secondary`（次要色）、`stop`（警示色） |
| `Visible` | bool | 否 | 是否在界面显示，默认 `True` |
| `AutoClearHistory` | bool | 否 | 点击时是否清除对话历史，默认 `False` |
| `PreProcess` | callable | 否 | 输入预处理函数，如 `clear_line_break` 可移除换行符 |
| `ModelOverride` | str | 否 | 强制使用指定模型，覆盖全局选择 |

!!! info "颜色主题"
    按钮颜色与 `themes/theme.py` 中的主题配置关联：`primary` 对应 `primary_hue`，`secondary` 对应 `neutral_hue`，`stop` 对应 `color_er`（通常是红色系）。

---

## 实用示例

以下是几个经过验证的实用按钮配置，您可以根据需要直接复制使用或稍作修改。

### 示例一：代码审查按钮

适合快速审查一段代码，获取改进建议：

```python
"代码审查": {
    "Prefix":   "请以资深软件工程师的角度审查以下代码。分析代码的：\n"
                "1. 潜在的 bug 或逻辑错误\n"
                "2. 性能优化空间\n"
                "3. 代码风格和可读性问题\n"
                "4. 安全隐患\n\n"
                "代码如下：\n```\n",
    "Suffix":   "\n```\n\n请逐项给出分析和改进建议。",
    "Color":    "secondary",
},
```

### 示例二：会议纪要生成

将会议录音转写文本整理成结构化的会议纪要：

```python
"会议纪要": {
    "Prefix":   "请将以下会议记录整理成正式的会议纪要，包含以下部分：\n"
                "- 会议要点摘要\n"
                "- 主要讨论事项\n"
                "- 决议与行动项（Action Items）\n"
                "- 待跟进问题\n\n"
                "会议记录原文：\n",
    "Suffix":   "",
    "Color":    "primary",
    "AutoClearHistory": True,
},
```

### 示例三：专业术语翻译

保留专业术语原文的翻译按钮：

```python
"术语翻译": {
    "Prefix":   "翻译以下技术文档为中文。对于专业术语，请采用"中文翻译（English Original）"的格式。"
                "常见缩写如 API、SDK、HTTP 等保留原样不翻译。\n\n",
    "Suffix":   "",
    "Color":    "secondary",
},
```

---

## 进阶技巧

**利用 PreProcess 预处理输入**：某些场景下，您可能希望在发送前对用户输入进行处理。例如，`clear_line_break` 函数可以将多行文本合并为单行，适合处理从 PDF 复制的带有不规则换行的文本：

```python
from toolbox import clear_line_break

"论文润色": {
    "Prefix":   "请润色以下学术段落：",
    "Suffix":   "",
    "PreProcess": clear_line_break,
},
```

**使用 ModelOverride 指定模型**：对于特定任务，您可能希望始终使用某个模型。例如，代码相关任务使用更快的 GPT-3.5：

```python
"快速解释代码": {
    "Prefix":   "用简洁的语言解释这段代码的功能：\n",
    "Suffix":   "",
    "ModelOverride": "gpt-3.5-turbo",
},
```

**按钮数量限制**：通过界面创建的自定义按钮数量由 `config.py` 中的 `NUM_CUSTOM_BASIC_BTN` 控制，默认为 4 个。如果需要更多按钮，可以修改此值或直接通过代码方式添加。

---

## 相关文档

- [配置详解](../get_started/configuration.md) — 了解更多配置选项
- [插件开发指南](plugin_development.md) — 开发更复杂的功能插件
- [基础操作](../features/basic_operations.md) — 掌握基础功能按钮的使用方式
