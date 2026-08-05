# LaTeX 英文纠错与高亮对比

在学术论文写作过程中，英文语法和拼写错误往往是投稿前需要反复核查的重点。传统的人工校对不仅耗时耗力，还容易遗漏细节问题。GPT Academic 提供的 **LaTeX 英文纠错+高亮修正位置** 功能，能够自动检测并修正整个 LaTeX 项目中的语法问题，同时生成直观的 PDF 对比文档，让您一目了然地看到每一处修改。

---

## 功能概述

与普通的文本纠错不同，这个功能专门针对 LaTeX 学术论文设计。它会智能识别并保护 LaTeX 命令（如 `\section`、`\cite`、`\ref`、数学环境等），确保纠错过程不会破坏论文的编译结构。更重要的是，系统会利用 `latexdiff` 工具生成修改前后的对比 PDF，所有修正之处都会以醒目的颜色标注出来。

这项功能特别适合以下场景：论文投稿前的最终语言审查、收到审稿意见后的语言修订、以及多人协作论文的语言统一。相比雇用专业校对服务，使用 AI 纠错不仅成本更低，而且可以反复迭代直到满意为止。

---

## 前置条件

由于功能需要编译 LaTeX 源码并生成 PDF，您的运行环境必须满足以下条件：

### LaTeX 环境

系统需要能够调用 `pdflatex` 命令。如果您尚未安装 LaTeX 环境，请根据操作系统选择合适的发行版：

| 操作系统 | 推荐安装 | 安装方式 |
|---------|---------|---------|
| Windows | TeX Live | 从 [tug.org/texlive](https://tug.org/texlive/) 下载完整版安装程序 |
| macOS | MacTeX | 从 [tug.org/mactex](https://tug.org/mactex/) 下载安装 |
| Linux | TeX Live | `sudo apt-get install texlive-full`（Ubuntu/Debian） |
| Docker | 官方镜像 | GPT Academic 官方 Docker 镜像已内置完整 LaTeX 环境 |

安装完成后，在终端运行 `pdflatex -version` 确认命令可用。如果提示找不到命令，可能需要将 LaTeX 的 bin 目录添加到系统 PATH 环境变量中。

### latexdiff 工具

`latexdiff` 是生成高亮对比 PDF 的关键工具，它通常随 TeX Live 或 MacTeX 一起安装。您可以运行 `latexdiff --version` 检查是否可用。如果缺失，可以通过 TeX Live Manager（`tlmgr install latexdiff`）单独安装。

---

## 使用方法

### 准备 LaTeX 项目

首先，将您的 LaTeX 项目整理好。项目应包含完整的源文件结构，主 `.tex` 文件应位于项目根目录或一级子目录中。您可以将整个项目文件夹打包成 ZIP 压缩文件，或者如果项目位于本地，也可以直接使用文件夹路径。

如果项目使用了 BibTeX 参考文献，请确保 `.bib` 文件和已编译的 `.bbl` 文件都包含在项目中，这有助于生成完整的 PDF 输出。

### 上传并执行

将压缩包上传到 GPT Academic 界面，文件路径会自动填入输入框。然后在函数插件下拉菜单中找到 **学术** 分类，选择 **Latex英文纠错+高亮修正位置 [需Latex]** 插件并点击执行。

系统会首先验证 LaTeX 环境是否可用——如果检测到 `pdflatex` 命令不存在，会提示安装说明并终止处理。环境检查通过后，系统将开始分析您的 LaTeX 项目。

<!-- IMAGE: feat_latex_proofread_01_workflow.png -->
<!-- 描述: LaTeX 纠错功能的操作流程界面 -->
<!-- 标注: ① 上传区显示已上传的 ZIP 项目 ② 函数插件区展开的"学术"分类 ③ "Latex英文纠错+高亮修正位置"插件（带 [需Latex] 标记） ④ 对话区显示的处理进度信息 -->
<!-- 尺寸建议: 1000px -->
![LaTeX 纠错操作流程](../../images/feat_latex_proofread_01_workflow.png)

### 处理流程

执行过程会依次经历以下阶段，每个阶段的进度都会实时显示在对话区：

**项目解析**：系统扫描项目中所有 `.tex` 文件，自动识别主文件（通常是包含 `\documentclass` 的文件）。如果存在多个可能的主文件，系统会提示您确认。

**内容融合**：为了便于处理和对比，系统会将多文件项目中通过 `\input` 或 `\include` 引用的内容合并为单一的 `merge.tex` 文件。原始项目结构保持不变。

**智能纠错**：合并后的内容会被切分成多个片段，并行发送给 AI 模型进行语法纠错。系统使用专门的 prompt 指导模型只修改语言问题，不改动 LaTeX 命令和数学公式。

**编译输出**：纠错完成后，系统调用 `pdflatex` 分别编译原始版本和纠错版本，然后使用 `latexdiff` 生成对比文档，最后将对比文档也编译为 PDF。

---

## 高级参数

如果您对纠错有特殊要求，可以在调用插件前展开高级参数输入区，输入自定义指令。这些指令会追加到默认的纠错 prompt 中，指导 AI 模型按照您的要求处理。

以下是一些常见的自定义指令示例：

```text
# 保留特定术语不变
If the term "LLM" appears, keep it as is without expanding.

# 保持特定缩写
Do not expand abbreviations like "CNN", "RNN", "LSTM".

# 指定语言风格
Use American English spelling conventions.

# 避免修改某些表达
Keep all instances of "state-of-the-art" unchanged.
```

请注意，自定义指令应使用英文编写，因为底层的纠错 prompt 是英文的。指令内容会直接影响 AI 模型的处理行为，清晰具体的指令能获得更好的效果。

---

## 输出结果

处理完成后，所有结果会被打包成 ZIP 压缩文件，出现在界面右侧的文件下载区。压缩包中包含以下内容：

| 文件 | 说明 |
|-----|------|
| `merge.pdf` | 原始论文编译的 PDF，作为对比基准 |
| `merge_proofread_en.pdf` | 纠错后的论文 PDF |
| `merge_diff.pdf` | **高亮对比 PDF**，修改处以红色删除线（原文）和蓝色文字（修正）标注 |
| `merge.tex` | 融合后的原始 LaTeX 源文件 |
| `merge_proofread_en.tex` | 纠错后的 LaTeX 源文件 |
| 其他项目文件 | 原始项目中的图片、样式文件等 |

其中 `merge_diff.pdf` 是最具价值的输出——它以 `latexdiff` 的标准格式清晰展示了所有修改：被删除的文字以红色删除线标注，新增或修改的文字以蓝色显示。您可以快速浏览这份文档，审核 AI 的每一处修改是否恰当。

如果您认同所有修改，可以直接使用 `merge_proofread_en.tex` 作为最终版本；如果有不满意的修正，可以参照对比结果手动调整。

---

## 技术原理

理解功能的技术实现有助于更好地使用它并排查可能的问题。

### LaTeX 命令保护

系统在发送文本给 AI 模型前，会明确指示模型不要修改任何 LaTeX 命令。prompt 中包含类似这样的指令：

> Do not modify any latex command such as \section, \cite, \begin, \item and equations.

这种设计确保了即使 AI 模型有时会"创意发挥"，LaTeX 结构也能保持完整。如果您发现某些命令被意外修改，可以在高级参数中添加更具体的保护指令。

### latexdiff 对比

`latexdiff` 是 LaTeX 社区广泛使用的文档对比工具，它能够智能比较两个 `.tex` 文件的差异，并生成一个新的 `.tex` 文件，其中用特殊的 LaTeX 命令标记出所有修改。编译这个对比文件后，差异就会以视觉化的方式呈现。

系统执行的核心命令类似于：

```bash
latexdiff --encoding=utf8 merge.tex merge_proofread_en.tex --flatten > merge_diff.tex
```

`--flatten` 参数确保即使原始项目包含多个文件，对比也能正确进行。

---

## 常见问题

???+ question "PDF 编译失败，但纠错已完成"
    这种情况下，结果压缩包中仍然包含纠错后的 `.tex` 源文件，您可以下载后在本地环境中手动编译。编译失败通常是因为：

    - 项目依赖特定的 LaTeX 宏包，而运行环境未安装
    - 原始项目本身存在编译警告或错误
    - 字体缺失（尤其在 Linux 环境下处理含中文的项目时）

    检查对话区的错误信息，通常能找到具体原因。

???+ question "对比 PDF 中某些修改看起来不合理"
    AI 纠错不是完美的，有时会出现以下情况：

    - 将正确的表达改成了另一种正确但不同的表达
    - 对专业术语进行了不恰当的"修正"
    - 理解偏差导致的语义改变

    这正是我们提供对比 PDF 的原因——您可以审核每一处修改，保留合理的、撤销不当的。使用更高性能的模型（如 GPT-4o）可以显著减少此类问题。

???+ question "处理速度较慢如何优化"
    处理速度取决于项目大小和 API 响应时间。以下方法可以加快处理：

    1. 在配置文件中增大 `DEFAULT_WORKER_NUM` 的值，提高并行处理数
    2. 使用响应更快的模型（如 `gpt-3.5-turbo`），但可能牺牲一定的纠错质量
    3. 如果项目非常大，考虑分章节处理

???+ question "如何处理中文 LaTeX 论文"
    本功能专门针对英文论文设计。如果您需要润色中文 LaTeX 论文，请使用 **中文 Latex 项目全文润色** 插件，但该插件不提供高亮对比功能。对于中英混合的论文，可以先用本功能处理英文部分，手动保留中文内容不变。

---

## 相关文档

- [LaTeX 项目处理](latex_polish.md) — 基础润色功能的详细说明
- [Arxiv 论文翻译](arxiv_translation.md) — 翻译 Arxiv 论文为中文
- [配置详解](../../get_started/configuration.md) — 了解 DEFAULT_WORKER_NUM 等配置项
