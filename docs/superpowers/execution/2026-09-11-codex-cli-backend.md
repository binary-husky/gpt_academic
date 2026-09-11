# Codex CLI 后端执行报告

日期：2026-09-11
功能分支：`codex-cli-backend`
基线提交：`d6bde0fa54373309bd05823a49bda8da019d2c77`

## 目标

为 GPT Academic 增加一个可选的 `codex-cli` 模型后端。用户在未提交到 Git
的 `config_private.py` 中填写本机 Codex CLI 可执行文件路径后，GPT Academic
可以复用该 CLI 已有的登录状态，不再要求为这一后端填写 GPT Academic 的
LLM API Key。

## 实际完成的范围

- 增加 `config_private.py` 可覆盖的 `CODEX_CLI_*` 配置，并注册
  `codex-cli` 模型；原有模型的默认值、API Key 路由和重试逻辑保持不变。
- 增加固定参数的 CLI 运行时：`shell=False`、stdin 输入、独立空临时目录、
  `--ephemeral`、`--sandbox read-only`、`--ignore-user-config`、
  `--ignore-rules` 和 `--skip-git-repo-check`。
- 增加 JSONL 协议边界，只接受预期的生命周期和文本事件；命令、文件变更、
  MCP、联网及未知关键事件会拒绝当前请求。
- 增加单进程 FIFO 调度器：默认一个活跃进程、32 个排队槽位、相邻启动至少
  间隔 3 秒、无自动重试；排队、取消、超时和清理失败都有明确错误。
- 增加 POSIX 进程组清理、双管道排空、输入/输出上限、取消传播及
  `cleanup_failed` fail-closed 保护。Windows 首版会报告不兼容，不声称已
  实现 Job Object 进程树回收。
- UI 和无 UI 调用共用同一个调度器；附件输入在边界处拒绝，并保持原有模型
  的多模型调用路径可用。
- 增加中文配置与风险说明：这是最佳努力隔离，不是绝对的无工具保证；
  action 事件到达前可能已经发生副作用，且串行化只降低并发消耗，不会消除
  Codex 订阅额度消耗。

## 规划与执行记录

本功能先由独立规划阶段确定范围、风险、接口和验证标准，再由独立执行阶段
实现，随后进行两轮独立审查和主流程复核。实施范围和验收标准记录在仓库内的
[实施计划](../plans/2026-09-11-codex-cli-backend.md)中。

## 已执行的验证

在当前功能分支上实际执行：

| 验证 | 结果 |
| --- | --- |
| `python3 -m pytest tests/codex_cli -q` | 109 passed，17 warnings，8.36s |
| `python3 -m compileall -q ...`（实现相关 Python 文件） | 通过 |
| `git diff --check` | 通过 |
| Gradio 3.32.15 下模型下拉框构造 | 通过，选项保持为字符串且可选中 `codex-cli` |
| 本机 Codex CLI `--version` / `exec --help` | 已验证版本 `codex-cli 0.153.4` 及所需参数存在 |
| `PYTHONPATH=tests python3 -m pytest tests/test_key_pattern_manager.py tests/test_utils.py -q` | 3 passed，17 warnings，1.07s |

`exec --help` 和能力探测没有发送模型提示词；本次没有消耗真实 Codex
请求额度，也没有把真实回答作为集成测试结果。

## 未通过或未覆盖的验证

仓库完整 `python3 -m pytest -q` 在收集阶段被基线环境问题阻断，共 12 个
收集错误，主要包括缺少既有测试依赖/模块（`init_test`、`llama_index`、
`edge_tts`）、既有测试对象接口不匹配，以及本机未运行的 SearxNG 服务。
这些错误未指向本次新增的 Codex 测试，但因此不能声明整个仓库测试套件全绿。

仍需部署者在自己的环境中验证：真实 Codex 登录态、真实 JSONL 回答、实际
订阅额度行为、不同 Codex CLI 版本、真实工具行为，以及 Windows 支持。

## 交付判断

本次功能代码和针对性测试已完成，满足首版的本地单用户、POSIX、纯文本输入
范围。由于完整仓库测试受既有环境阻断，且真实 Codex 模型请求未执行，交付
结论是“针对性验证通过，完整仓库与真实服务集成仍需部署环境复核”。
