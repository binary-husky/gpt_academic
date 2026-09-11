# 本机 Codex CLI 后端

GPT Academic 可以把 `codex-cli` 作为一个可选的纯文本模型后端，复用
同一台机器、同一系统账户中已经登录的 Codex CLI。它不读取或复制
Codex 的认证文件，也不会把 GPT Academic 的 API Key 放进提示词。

## 配置

先在运行 GPT Academic 的机器上安装并登录 Codex CLI，然后在不会提交到
Git 的 `config_private.py` 中填写可执行文件路径。例如路径包含空格时也
直接写成 Python 字符串：

```python
LLM_MODEL = "codex-cli"
CODEX_CLI_PATH = "/Applications/ChatGPT.app/Contents/Resources/codex"
CODEX_CLI_MODEL = ""
```

`CODEX_CLI_PATH` 必须是 GPT Academic 进程所在机器和系统账户可执行的
Codex CLI 路径。可选的队列、超时和大小限制仍使用 `config_private.py`
中的对应 `CODEX_CLI_*` 配置；首版不提供任意 CLI 参数、工作目录或
sandbox 配置入口。

选择 `codex-cli` 时不需要填写 GPT Academic 的 `API_KEY`。选择 OpenAI
等原有 API 模型时，原有 API Key 认证和重试行为保持不变。

## 调度和提示

同一个 Python 进程内默认只有一个活跃 Codex CLI 进程，等待队列容量为
32，相邻启动至少间隔 3 秒。Codex 后端不自动重试；队列满、排队超时、
取消、请求超时或进程失败都会以明确的本地错误结束。串行调度只限制
并发进程，不代表不会消耗 Codex 订阅额度。

能力探测只执行不带模型提示词的 `exec --help`，有独立固定的 10 秒上限。
探测超时返回内部安全错误 `probe_timeout`，不会启动正式请求，也不会自动
重试；正式请求的 `request_timeout` 从正式进程 `Popen` 成功后开始计时。

Codex 请求使用 stdin、独立的空临时工作目录、ephemeral 模式、read-only
sandbox、跳过 Git 仓库检查，并忽略用户配置和规则。提示词会要求只返回
纯文本，不读取文件、不运行命令、不编辑文件、不使用 MCP 或浏览工具。
当前实现是最佳努力隔离：这些组合只能降低风险，不能保证绝对“无工具”，
也不能保证 action 事件到达前没有已经发生的读取、命令或网络副作用。只要
收到工具、命令、文件、MCP、联网或未知关键事件，后端就会拒绝该请求并终止
进程，但终止不等于撤销事件到达前可能产生的副作用。

首版只支持可信的本机单进程部署，不适用于把不可信用户直接接入同一个
Codex 登录态的公网多租户服务。输入附件和上传文件不在首版支持范围内。

## 平台边界

当前实现只在 POSIX 平台（macOS、Linux）启用可验证的独立进程组回收。
Windows Job Object 尚未实现；在 Windows 上后端会在启动前报告
`cli_incompatible`，不会只终止父进程后声称子进程树已经清理完成。运行中
若无法确认进程组已退出，则报告 `cleanup_failed` 并暂停后续 Codex 请求，
以避免把不确定的残留进程放行到下一次启动。

## 验证边界

仓库测试使用确定性的 fake CLI 验证参数数组、stdin、JSONL 解析、双管道
排空、队列、取消、超时、进程组回收和临时目录清理。fake CLI 不是实际
Codex 服务的协议或安全保证。真实 Codex 登录状态、订阅额度、回答质量、
真实 JSONL 流、工具行为和未来 CLI 版本兼容性仍需在部署环境中另行验证。
