# 插件开发指南

GPT Academic 的核心能力来源于其丰富的插件生态。从论文翻译到代码分析，从联网搜索到图片生成，每一个功能都以插件的形式实现。这种设计不仅保持了系统的模块化和可维护性，更为开发者提供了无限的扩展可能。

本文将带您从零开始，掌握 GPT Academic 插件的开发方法。无论您想创建一个简单的文本处理工具，还是构建带有复杂交互界面的高级功能，都能在这里找到答案。

---

## 插件系统概览

在开始编写代码之前，我们先了解 GPT Academic 插件系统的基本架构。

所有插件都位于 `crazy_functions/` 目录下。当用户点击界面上的功能按钮或从下拉菜单选择插件时，系统会调用相应的插件函数或类来处理请求。插件可以访问用户的输入文本、对话历史、文件上传等信息，并通过大模型生成响应。

GPT Academic 支持两种插件形式：

| 类型 | 适用场景 | 特点 |
|-----|---------|------|
| **函数式插件** | 简单功能，无需用户额外输入 | 开发快速，代码简洁 |
| **类式插件** | 复杂功能，需要二级选项菜单 | 支持参数配置，交互更灵活 |

对于大多数场景，函数式插件已经足够。当您需要在执行前让用户选择参数（如翻译语言、输出格式等）时，再考虑使用类式插件。

---

## 开发环境准备

插件开发无需特殊的环境配置，只需确保您已经成功运行了 GPT Academic。在开发过程中，建议开启热重载功能，这样修改插件代码后无需重启程序即可生效。

项目默认已启用热重载。当您保存插件文件后，下次调用该插件时会自动加载最新代码。这极大地提升了开发效率。

---

## 函数式插件开发

我们从最简单的函数式插件开始。下面这个示例会查询"历史上的今天"发生的事件：

```python
from toolbox import CatchException, update_ui
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime

@CatchException
def 历史上的今天(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    插件入口函数

    参数说明:
        txt           - 用户在输入框中输入的文本
        llm_kwargs    - 大模型参数（温度、top_p 等）
        plugin_kwargs - 插件参数（来自二级菜单，函数式插件通常为空）
        chatbot       - 对话显示组件，用于更新界面
        history       - 对话历史记录
        system_prompt - 系统提示词
        user_request  - 用户请求信息（包含 IP 等）
    """
    # 清空历史，避免上下文过长
    history = []

    # 获取当前日期
    today = datetime.date.today()

    # 在界面上显示处理状态
    chatbot.append(("正在查询历史上的今天...", "请稍候..."))
    yield from update_ui(chatbot=chatbot, history=history)

    # 构造提问
    query = f"请列举历史上 {today.month} 月 {today.day} 日发生的 3 个重要事件，简要说明每个事件的背景和影响。"

    # 调用大模型并流式输出
    response = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=query,
        inputs_show_user=query,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=history,
        sys_prompt="你是一位历史学专家，擅长介绍历史事件。"
    )

    # 更新对话历史
    history.extend([query, response])
    yield from update_ui(chatbot=chatbot, history=history)
```

这个示例虽然简单，但包含了插件开发的所有核心要素。让我们逐一解析：

**装饰器 `@CatchException`** 是一个错误处理包装器，确保插件运行时的异常不会导致整个程序崩溃。在开发阶段，它会将错误信息显示在对话界面中，方便调试。

**函数签名**定义了插件接收的参数。这七个参数是所有插件的标准接口，您可以根据需要使用其中的部分或全部。

**`yield from update_ui()`** 是更新界面的关键。由于插件函数是一个生成器，使用 `yield from` 可以实时将处理进度反馈给用户，而不是等待所有处理完成后才显示结果。

**`request_gpt_model_in_new_thread_with_ui_alive()`** 是调用大模型的核心函数。它在独立线程中发起请求，同时保持界面响应。函数返回的 `response` 是模型的完整回复文本。

---

## 注册插件

插件编写完成后，需要在 `crazy_functional.py` 中注册才能在界面上使用。打开该文件，在 `function_plugins` 字典中添加您的插件：

```python
function_plugins = {
    # ... 其他插件 ...

    "历史上的今天": {
        "Group": "对话",           # 所属分组，用于插件分类
        "Color": "secondary",      # 按钮颜色：primary/secondary/stop
        "AsButton": False,         # True 显示为按钮，False 放入下拉菜单
        "Info": "查询历史上今天发生的重要事件",  # 插件说明
        "Function": HotReload(历史上的今天),    # 关联函数，HotReload 启用热重载
    },

    # ... 其他插件 ...
}
```

注册时需要指定的属性含义如下：

`Group` 决定插件在界面上的分类位置。可选值包括"对话"、"编程"、"学术"、"智能体"，也可以用 `|` 分隔同时归属多个分组，如 `"对话|学术"`。

`AsButton` 控制插件的显示形式。设为 `True` 时，插件会以按钮形式显示在主界面；设为 `False` 时，插件会出现在下拉菜单中。常用功能建议设为按钮，以便快速访问。

`Function` 必须用 `HotReload()` 包装，这样修改插件代码后无需重启程序。

保存文件后，刷新浏览器页面，您的新插件就会出现在界面上。

---

## 类式插件开发

当插件需要用户在执行前配置参数时，类式插件是更好的选择。它允许您定义一个二级选项菜单，用户可以在其中输入文本、选择下拉选项等。

下面是一个支持自定义天数的"历史上的今天"插件：

```python
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty
from toolbox import update_ui
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime

class HistoryToday_Wrap(GptAcademicPluginTemplate):
    """
    类式插件必须继承 GptAcademicPluginTemplate
    """

    def __init__(self):
        """
        初始化函数。注意：execute 方法可能在不同线程中运行，
        避免在此存储会被多线程访问的状态。
        """
        pass

    def define_arg_selection_menu(self):
        """
        定义二级选项菜单

        返回一个字典，每个键值对对应一个参数。
        支持的参数类型：
          - type="string": 文本输入框
          - type="dropdown": 下拉选择菜单
        """
        gui_definition = {
            "main_input": ArgProperty(
                title="查询日期",
                description="留空则查询今天，或输入指定日期如 3-15",
                default_value="",
                type="string"
            ).model_dump_json(),

            "event_count": ArgProperty(
                title="事件数量",
                description="选择要列举的历史事件数量",
                options=["3个事件", "5个事件", "10个事件"],
                default_value="3个事件",
                type="dropdown"
            ).model_dump_json(),

            "advanced_arg": ArgProperty(
                title="额外要求",
                description="如有特殊要求可在此输入，如：只列举中国历史事件",
                default_value="",
                type="string"
            ).model_dump_json(),
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件主逻辑

        用户在二级菜单中的选择会通过 plugin_kwargs 字典传入。
        字典的键与 define_arg_selection_menu 中定义的参数名对应。
        """
        # 从 plugin_kwargs 获取用户选择
        main_input = plugin_kwargs.get("main_input", "")
        event_count = plugin_kwargs.get("event_count", "3个事件")
        advanced_arg = plugin_kwargs.get("advanced_arg", "")

        # 解析日期
        if main_input:
            try:
                month, day = map(int, main_input.split("-"))
            except:
                month, day = datetime.date.today().month, datetime.date.today().day
        else:
            month, day = datetime.date.today().month, datetime.date.today().day

        # 解析事件数量
        count = int(event_count.replace("个事件", ""))

        # 构造提问
        query = f"请列举历史上 {month} 月 {day} 日发生的 {count} 个重要事件。"
        if advanced_arg:
            query += f" 额外要求：{advanced_arg}"

        # 清空历史并显示状态
        history = []
        chatbot.append((f"查询 {month}月{day}日 的历史事件", "正在查询..."))
        yield from update_ui(chatbot=chatbot, history=history)

        # 调用大模型
        response = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=query,
            inputs_show_user=query,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history=history,
            sys_prompt="你是一位历史学专家。"
        )

        history.extend([query, response])
        yield from update_ui(chatbot=chatbot, history=history)
```

类式插件的核心在于 `define_arg_selection_menu()` 方法。它返回的字典定义了二级菜单的结构，每个参数都由 `ArgProperty` 对象描述。

有两个特殊的参数名需要注意：

- `main_input` 会与界面主输入框自动同步，用户在输入框中的内容会预填到这个参数
- `advanced_arg` 会与界面的高级参数输入区自动同步

除此之外，您可以自由定义其他参数名。整个菜单最多支持 8 个参数。

注册类式插件时，需要同时指定 `Function` 和 `Class`：

```python
"历史上的今天（高级版）": {
    "Group": "对话",
    "Color": "stop",
    "AsButton": False,
    "Info": "可自定义日期和事件数量的历史查询插件",
    "Function": HotReload(历史上的今天),  # 兼容虚空终端调用
    "Class": HistoryToday_Wrap,           # 类式插件的类名
},
```

当插件同时注册了 `Function` 和 `Class` 时，界面按钮会触发类式插件（显示二级菜单），而虚空终端等自然语言调用场景会使用函数式入口。

---

## 实用开发技巧

### 处理文件上传

许多插件需要处理用户上传的文件。用户上传的文件路径会通过 `txt` 参数传入，您可以使用以下模式解析：

```python
import os, glob

@CatchException
def 处理上传文件(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    # txt 可能是单个文件路径，也可能是目录路径
    if os.path.isfile(txt):
        file_list = [txt]
    elif os.path.isdir(txt):
        # 获取目录下所有 PDF 文件
        file_list = glob.glob(os.path.join(txt, "*.pdf"))
    else:
        chatbot.append(("错误", "请先上传文件或输入有效路径"))
        yield from update_ui(chatbot=chatbot, history=history)
        return

    for file_path in file_list:
        # 处理每个文件...
        pass
```

### 多线程批量处理

当需要处理大量文件或执行耗时操作时，可以使用多线程提升效率：

```python
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_target

def 批量处理(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    # 准备多个任务
    inputs_array = ["任务1", "任务2", "任务3"]
    inputs_show_user_array = inputs_array.copy()

    # 并行执行
    results = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_target(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[] for _ in inputs_array],
        sys_prompt_array=["" for _ in inputs_array],
    )

    # results 是所有任务结果的列表
```

### 生成下载文件

插件可以生成文件供用户下载。使用 `on_report_generated()` 函数将文件注册到下载区：

```python
from toolbox import on_report_generated

def 生成报告(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    # ... 生成报告内容 ...

    # 保存文件
    report_path = "path/to/report.pdf"
    with open(report_path, "wb") as f:
        f.write(report_content)

    # 注册到下载区
    cookies = user_request.get("cookies", {})
    cookies, report_files, chatbot = on_report_generated(
        cookies=cookies,
        files=[report_path],
        chatbot=chatbot
    )

    yield from update_ui(chatbot=chatbot, history=history)
```

---

## 调试与测试

开发过程中，您可以使用以下方法进行调试：

**查看日志输出**：在插件代码中使用 `logger` 输出调试信息：

```python
from loguru import logger

logger.info(f"处理文件: {file_path}")
logger.warning("参数可能不正确")
logger.error("发生错误")
```

日志会输出到终端，帮助您追踪插件的执行流程。

**使用虚空终端测试**：虚空终端支持通过自然语言调用插件，是快速测试插件功能的好方法。只需在虚空终端中描述您想执行的任务，系统会自动匹配并调用相应插件。

**渐进式开发**：建议先实现最基本的功能，验证可行后再逐步添加复杂特性。利用热重载特性，您可以在不重启程序的情况下快速迭代。

---

## 下一步

恭喜您掌握了 GPT Academic 插件开发的基础知识！接下来您可以：

- 阅读 `crazy_functions/` 目录下的现有插件源码，学习更多实现技巧
- 在 [GitHub Issues](https://github.com/binary-husky/gpt_academic/issues) 中寻找灵感或提交您的插件
- 探索 [自定义按钮](custom_buttons.md) 功能，创建更轻量的快捷功能
- 查阅 [主题定制](theme_customization.md)，为您的插件界面增添个性
