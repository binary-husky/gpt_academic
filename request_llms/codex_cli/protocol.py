"""Fail-closed JSONL decoding for ``codex exec --json``."""

import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from .types import CodexError, CodexResult


MAX_JSONL_LINE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class ProtocolUpdate:
    text: Optional[str]
    completed: bool


def _protocol_error(message: str = "Codex CLI 返回了无法识别的协议数据。") -> CodexError:
    return CodexError("protocol_error", message)


def _tool_activity_error() -> CodexError:
    return CodexError(
        "tool_activity_blocked",
        "Codex CLI 请求包含未允许的工具或操作，已终止。",
    )


class JsonlDecoder:
    """Decode arbitrarily chunked UTF-8 JSONL without replacement characters."""

    def __init__(self, max_line_bytes: int = MAX_JSONL_LINE_BYTES):
        if not isinstance(max_line_bytes, int) or max_line_bytes <= 0:
            raise ValueError("max_line_bytes must be a positive integer")
        self._max_line_bytes = max_line_bytes
        self._buffer = bytearray()

    def _decode_line(self, line: bytes):
        if not line.strip():
            return None
        try:
            decoded = line.decode("utf-8")
        except UnicodeDecodeError:
            raise _protocol_error("Codex CLI 返回了无效的 UTF-8 数据。")
        try:
            event = json.loads(decoded)
        except (TypeError, ValueError, json.JSONDecodeError):
            raise _protocol_error("Codex CLI 返回了损坏的 JSON 数据。")
        if not isinstance(event, dict):
            raise _protocol_error("Codex CLI JSONL 事件必须是对象。")
        return event

    def feed(self, chunk: bytes) -> Sequence[Mapping[str, object]]:
        if not isinstance(chunk, (bytes, bytearray)):
            raise TypeError("JSONL chunks must be bytes")
        self._buffer.extend(chunk)
        events = []
        while True:
            try:
                newline_at = self._buffer.index(10)
            except ValueError:
                break
            line = bytes(self._buffer[:newline_at])
            del self._buffer[: newline_at + 1]
            if len(line) > self._max_line_bytes:
                raise _protocol_error("Codex CLI 返回的单行数据超过大小限制。")
            event = self._decode_line(line)
            if event is not None:
                events.append(event)
        if len(self._buffer) > self._max_line_bytes:
            raise _protocol_error("Codex CLI 返回的单行数据超过大小限制。")
        return events

    def finish(self) -> Sequence[Mapping[str, object]]:
        if not self._buffer:
            return []
        line = bytes(self._buffer)
        self._buffer.clear()
        if len(line) > self._max_line_bytes:
            raise _protocol_error("Codex CLI 返回的单行数据超过大小限制。")
        event = self._decode_line(line)
        return [] if event is None else [event]


class ProtocolParser:
    """Parse the exact-version event vocabulary and reject agent actions."""

    _TOP_LEVEL_EVENTS = {
        "thread.started",
        "turn.started",
        "turn.completed",
        "turn.failed",
        "item.started",
        "item.updated",
        "item.completed",
        "error",
    }
    _ACTION_ITEM_TYPES = {
        "command_execution",
        "file_change",
        "mcp_tool_call",
        "collab_tool_call",
        "web_search",
    }
    _NON_TEXT_ITEM_TYPES = {"reasoning", "todo_list"}

    def __init__(self):
        self._thread_started = False
        self._turn_started = False
        self._turn_completed = False
        self._agent_items = OrderedDict()
        self._item_types = {}
        self._completed_agent_items = set()
        self._completed_items = {}
        self._last_emitted_text = object()

    def _require_mapping(self, value: object) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise _protocol_error()
        return value

    def _parse_item(
        self, event: Mapping[str, object], event_type: str
    ) -> ProtocolUpdate:
        item = self._require_mapping(event.get("item"))
        item_id = item.get("id")
        item_type = item.get("type")
        if not isinstance(item_id, str) or not item_id:
            raise _protocol_error()
        if not isinstance(item_type, str):
            raise _protocol_error()
        if item_type in self._ACTION_ITEM_TYPES:
            raise _tool_activity_error()
        if not self._thread_started or not self._turn_started or self._turn_completed:
            raise _protocol_error("Codex CLI 输出缺少有效的线程或回合生命周期事件。")
        previous_type = self._item_types.get(item_id)
        if previous_type is not None and previous_type != item_type:
            raise _protocol_error()
        item_snapshot = dict(item)
        completed_snapshot = self._completed_items.get(item_id)
        if completed_snapshot is not None:
            if event_type != "item.completed" or item_snapshot != completed_snapshot:
                raise _protocol_error()
            # A repeated completion with the exact same item snapshot is
            # harmless, but must not re-emit or mutate accumulated state.
            return ProtocolUpdate(text=None, completed=False)
        self._item_types[item_id] = item_type
        if item_type == "agent_message":
            text = item.get("text")
            if not isinstance(text, str):
                raise _protocol_error()
            self._agent_items[item_id] = text
            if event_type == "item.completed":
                self._completed_agent_items.add(item_id)
                self._completed_items[item_id] = item_snapshot
            answer = "".join(self._agent_items.values())
            if answer == self._last_emitted_text:
                return ProtocolUpdate(text=None, completed=False)
            self._last_emitted_text = answer
            return ProtocolUpdate(text=answer, completed=False)
        if item_type in self._NON_TEXT_ITEM_TYPES:
            if event_type == "item.completed":
                self._completed_items[item_id] = item_snapshot
            return ProtocolUpdate(text=None, completed=False)
        # Error items are not safe to expose as assistant text.  They are a
        # known item type, but still make this request unsuccessful.
        if item_type == "error":
            raise CodexError("process_failed", "Codex CLI 在处理请求时报告了错误。")
        raise _protocol_error()

    def accept(self, event: Mapping[str, object]) -> ProtocolUpdate:
        if not isinstance(event, Mapping):
            raise _protocol_error()
        event_type = event.get("type")
        if event_type not in self._TOP_LEVEL_EVENTS:
            raise _protocol_error()

        if event_type == "thread.started":
            if self._thread_started or not isinstance(event.get("thread_id"), str):
                raise _protocol_error()
            self._thread_started = True
            return ProtocolUpdate(text=None, completed=False)

        if event_type == "turn.started":
            if not self._thread_started or self._turn_started or self._turn_completed:
                raise _protocol_error("Codex CLI 输出缺少有效的线程生命周期事件。")
            self._turn_started = True
            return ProtocolUpdate(text=None, completed=False)

        if event_type in {"item.started", "item.updated", "item.completed"}:
            return self._parse_item(event, event_type)

        if event_type == "turn.completed":
            if not self._thread_started or not self._turn_started or self._turn_completed:
                raise _protocol_error("Codex CLI 输出缺少有效的回合生命周期事件。")
            usage = event.get("usage")
            if not isinstance(usage, Mapping):
                raise _protocol_error()
            self._turn_completed = True
            answer = "".join(self._agent_items.values()) if self._agent_items else None
            if answer == self._last_emitted_text:
                answer = None
            elif answer is not None:
                self._last_emitted_text = answer
            return ProtocolUpdate(
                text=answer,
                completed=True,
            )

        if event_type == "turn.failed":
            error = self._require_mapping(event.get("error"))
            if not isinstance(error.get("message"), str):
                raise _protocol_error()
            raise CodexError("process_failed", "Codex CLI 未能完成请求。")

        if event_type == "error":
            if not isinstance(event.get("message"), str):
                raise _protocol_error()
            raise CodexError("process_failed", "Codex CLI 返回了不可恢复的错误。")

        raise _protocol_error()

    def finish(self, exit_code: int) -> CodexResult:
        if not isinstance(exit_code, int):
            raise _protocol_error()
        if exit_code != 0:
            raise CodexError("process_failed", "Codex CLI 进程未成功退出。")
        if not self._thread_started:
            raise _protocol_error("Codex CLI 输出缺少线程开始事件。")
        if not self._turn_started:
            raise _protocol_error("Codex CLI 输出缺少回合开始事件。")
        if not self._turn_completed:
            raise _protocol_error("Codex CLI 输出缺少完成事件。")
        if not self._agent_items:
            raise _protocol_error("Codex CLI 输出缺少助手文本。")
        if set(self._agent_items) - self._completed_agent_items:
            raise _protocol_error("Codex CLI 输出缺少助手消息完成事件。")
        return CodexResult(text="".join(self._agent_items.values()))
