# Codex CLI JSONL contract evidence

This fixture records the wire shapes used by the first Codex CLI backend. It is
evidence for the parser tests, not a claim that a fake CLI proves the behavior
of a real Codex run.

## Version and sources

- Local executable checked without a model prompt on 2026-09-11:
  `codex-cli 0.153.4`.
- Local `codex exec --help` checked the stdin form (`-` or no positional
  prompt), `--json`, `--ephemeral`, `--sandbox read-only`,
  `--skip-git-repo-check`, `--ignore-user-config`, `--ignore-rules`, `-C`,
  `-m`, and `--color never`. The help text does not itself promise that
  read-only prevents all agent actions.
- Exact-version upstream source reviewed at
  `https://github.com/openai/codex/tree/rust-v0.153.4`, specifically
  `codex-rs/exec/src/exec_events.rs` and
  `codex-rs/exec/src/event_processor_with_jsonl_output.rs`.

The upstream source is the authoritative source for the event names and field
shapes below. It is not an end-to-end execution of a real model request.

## Confirmed top-level event vocabulary

The JSONL stream uses an object per line with a discriminator in `type`:

- `thread.started`: `{ "thread_id": string }`
- `turn.started`: no required payload fields
- `turn.completed`: `{ "usage": { ... token counters ... } }`
- `turn.failed`: `{ "error": { "message": string } }`
- `item.started`, `item.updated`, `item.completed`: `{ "item": { ... } }`
- `error`: `{ "message": string }`

The parser accepts lifecycle events only when their required shape and order
are present: `thread.started` must precede `turn.started`, item events must
belong to that started turn, and `turn.completed` must follow both. It treats
the stream as successful only after at least one `agent_message` item has
supplied assistant text and every observed `agent_message` item has received
its own `item.completed` event. A missing lifecycle event or item completion,
a non-zero process exit, a top-level error, or a failed turn is not successful.

## Confirmed item shapes

The `item` object has an `id` and a type-specific `type`:

- `agent_message`: `{ "id": string, "type": "agent_message", "text": string }`
- `reasoning`: `{ "id": string, "type": "reasoning", "text": string }`
- `command_execution`: includes `command`, `aggregated_output`, `exit_code`,
  and `status`.
- `file_change`: includes `changes` and `status`.
- `mcp_tool_call`: includes `server`, `tool`, `arguments`, `result`, `error`,
  and `status`.
- `collab_tool_call`, `web_search`, `todo_list`, and `error` are also present
  in the exact-version source.

Only `agent_message` is user-facing answer text. The backend rejects all
action-bearing item types (`command_execution`, `file_change`, `mcp_tool_call`,
`collab_tool_call`, `web_search`) and rejects unknown item types. Reasoning,
todo, and non-fatal item errors are not answer text; an item error is still
treated as a failed/unsafe run rather than displayed as a model answer.

## Text aggregation and lifecycle

The upstream JSONL adapter emits completed `agent_message` items with a full
`text` snapshot. The local parser stores the latest snapshot per item id and
publishes the cumulative answer snapshot to its callback. It never appends a
snapshot to an earlier snapshot, so an update such as `"hel"` followed by
`"hello"` yields `"hello"`, not `"helhello"`.

The exact upstream stream behavior can change in future releases. The
implementation therefore fails closed on unknown top-level or item events and
does not claim an absolute no-tools guarantee from the prompt or sandbox
flags.

## Runtime safety timing evidence

Capability probing is a separate local safety step: it runs only `exec --help`
with no model prompt and has a fixed ten-second deadline. Its internal
`probe_timeout` error is non-retryable, prevents the formal request from
starting, and is distinct from `request_timeout`, which starts only after the
formal request `Popen` succeeds. A process-group identity lookup failure is
also treated as `cleanup_failed`; the runtime makes one exact expected-PGID
SIGKILL/wait attempt and continues to fail closed if group exit cannot be
confirmed.

## GPT Academic integration evidence

- The baseline no-UI bridge signature is
  `predict_no_ui_long_connection(inputs, llm_kwargs, history, sys_prompt,
  observe_window, console_silence)`. The baseline UI bridge signature is
  `predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt,
  stream, additional_fn)`. The Codex bridge preserves both call shapes.
- `bridge_all.model_info` supplies `fn_with_ui`, `fn_without_ui`, `endpoint`,
  `max_token`, `tokenizer`, and `token_cnt`, plus `requires_api_key=False` for
  `codex-cli`; the default `LLM_MODEL` remains unchanged.
- The existing API bridge keeps its `is_any_api_key` gate and `MAX_RETRY`
  loop. Codex errors are typed and are intercepted before the shared plugin
  retry loops, so a Codex submission is not resubmitted automatically.
- Existing plugin thread pools remain in place. Their Codex calls enter the
  process-wide one-slot scheduler, which is the only production path that can
  start the CLI.

## Explicitly not verified here

- No real model request was made.
- No real Codex JSONL stream was sampled from the installed binary.
- Authentication, subscription quota, answer quality, actual tool dispatch,
  and behavior of future CLI versions remain unverified.
- The fake CLI used by tests is deterministic test infrastructure only.
