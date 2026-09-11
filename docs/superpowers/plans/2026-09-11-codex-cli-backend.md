# Codex CLI 后端实施计划

日期：2026-09-11

## 目标

为 GPT Academic 增加可选的 codex-cli 模型后端。用户只需在未提交到
Git 的 config_private.py 中填写本机 Codex CLI 可执行文件路径，并把
LLM_MODEL 设为 codex-cli，即可复用当前系统账户已经登录的 Codex CLI。
原有 API 模型保持原认证和重试行为。

## 范围

### 纳入

1. 配置读取：路径、可选模型、队列、启动间隔、排队/请求超时及输入输出上限。
2. 后端桥接：UI 和无 UI 调用遵守 GPT Academic 现有接口。
3. 进程运行：固定参数数组、stdin、独立空临时目录、独立进程组和资源清理。
4. 协议边界：JSONL 分块解码、生命周期校验、文本快照去重和未知事件拒绝。
5. 调度边界：单进程单活跃槽位、FIFO 队列、取消传播、排队超时和清理失败
   后 fail-closed。
6. 文档和测试：配置示例、风险说明、fake CLI 测试夹具、回归测试。

### 不纳入

- 不读取、复制或解析 Codex 认证文件。
- 不让 GPT Academic 传入任意 CLI 参数、工作目录或 sandbox 配置。
- 不支持附件、多模态输入、Windows Job Object 或公网多租户部署。
- 不实现自动重试，不把真实 Codex 请求用于自动化测试。

## 关键设计决策

### 额度与并发

首选“同一 Python 进程只有一个活跃 Codex 进程”：默认队列容量 32，相邻
正式进程启动至少间隔 3 秒，Codex 后端不自动重试。这样论文翻译、源码剖析
等上层插件即使提交多个线程，也不会同时启动 10+ 个 Codex 进程；代价是
任务会排队，且串行化只能降低突发并发，不能消除订阅额度消耗。

### Agentic 行为

正式请求固定使用 --ephemeral、--sandbox read-only、
--skip-git-repo-check、--ignore-user-config、--ignore-rules 和
--color never，并在独立空临时目录中运行。提示词明确要求仅返回纯文本，
不读文件、不运行命令、不编辑文件、不使用 MCP 或浏览工具。

这些措施是最佳努力隔离，不是绝对的无工具保证。协议层一旦收到命令执行、
文件变更、MCP、联网或未知关键事件，就拒绝请求并终止进程；但 action 事件
到达前已经发生的副作用无法撤销，因此文档必须明确这一点。

### 进程安全

POSIX 平台使用 start_new_session=True 并验证子进程 PID 等于独立进程组 ID，
取消、超时、协议拒绝、输出超限和进程失败都按进程组终止。无法确认或回收
进程组时返回 cleanup_failed，阻塞后续 Codex 请求。Windows 首版直接返回
cli_incompatible，不伪称已经清理整个进程树。

## 实施步骤

1. 在 config.py 注册 Codex 配置和模型 ID，确认默认模型不变。
2. 增加 request_llms/codex_cli/ 内的类型、配置、JSONL 协议、运行时和调度器。
3. 增加 request_llms/bridge_codex_cli.py，串联 prompt、队列、UI 更新和错误边界。
4. 在 request_llms/bridge_all.py 注册路由，并在多模型路径中传播取消和清理逻辑。
5. 在 crazy_functions/crazy_utils.py 阻止 Codex 结构化失败进入旧 API 自动重试。
6. 在工具栏提供模型选择说明，在 docs/codex-cli.md 提供安装、配置和风险说明。
7. 用 fake CLI 覆盖成功、stdin 阻塞、stderr 洪泛、协议错误、工具事件、超时、
   输出上限、进程组回收、队列和多线程场景。
8. 执行定向测试、编译检查、差异检查、Gradio 兼容性检查和本机 CLI help 探测。

## 风险控制

| 风险 | 控制措施 | 剩余风险 |
| --- | --- | --- |
| 插件并发烧穿额度 | 单活跃进程、FIFO、启动间隔、无自动重试 | 不同 GPT Academic 进程仍可各自启动；每个串行请求仍消耗额度 |
| Codex 主动调用工具 | 固定 sandbox/工作目录/配置参数，协议见到 action 即终止 | 无法保证 action 之前没有读取、命令或网络副作用 |
| 子进程泄漏 | POSIX 进程组验证、双管道排空、fail-closed | Windows 尚未实现；清理失败时需人工处理 |
| 敏感信息泄露 | 不记录 prompt/stderr，子进程移除 API Key 环境变量 | Codex 自身登录态仍由用户本机账户管理 |
| CLI 升级破坏协议 | 严格能力探测和未知事件拒绝 | 未来版本需要重新验证 |

## 完成标准

- config_private.py 的路径配置能够在选择 codex-cli 时被正常读取。
- 不填写 GPT Academic API Key 时，Codex 路由仍可创建请求。
- 同一进程最多一个活跃 Codex 进程，队列、取消、超时和清理失败行为有测试。
- 纯文本请求成功，附件和工具/未知协议事件被拒绝。
- 原有默认模型、API Key 保留和 API 重试路径的回归测试通过。
- 定向 Codex 测试和实现相关编译检查通过；未覆盖的真实服务行为在执行报告中明确列出。
