import json

import pytest

from request_llms.codex_cli.protocol import JsonlDecoder, ProtocolParser
from request_llms.codex_cli.types import CodexError


def _success_events(text="hello"):
    return [
        {"type": "thread.started", "thread_id": "thread-1"},
        {"type": "turn.started"},
        {
            "type": "item.completed",
            "item": {"id": "item-1", "type": "agent_message", "text": text},
        },
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 1,
                "cached_input_tokens": 0,
                "output_tokens": 1,
                "reasoning_output_tokens": 0,
            },
        },
    ]


def _feed_events(parser, events):
    for event in events:
        parser.accept(event)


def test_chunk_boundaries_and_utf8():
    event = {"type": "item.completed", "item": {"id": "1", "type": "agent_message", "text": "你好"}}
    encoded = (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")
    decoder = JsonlDecoder()
    split_at = encoded.index("好".encode("utf-8")) + 1

    assert decoder.feed(encoded[:split_at]) == []
    assert decoder.feed(encoded[split_at:]) == [event]
    assert decoder.finish() == []


def test_text_snapshots_do_not_duplicate():
    parser = ProtocolParser()
    updates = []
    for event in [
        {"type": "thread.started", "thread_id": "thread-1"},
        {"type": "turn.started"},
        {
            "type": "item.started",
            "item": {"id": "item-1", "type": "agent_message", "text": "hel"},
        },
        {
            "type": "item.updated",
            "item": {"id": "item-1", "type": "agent_message", "text": "hello"},
        },
        {
            "type": "item.completed",
            "item": {"id": "item-1", "type": "agent_message", "text": "hello"},
        },
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 1,
                "cached_input_tokens": 0,
                "output_tokens": 1,
                "reasoning_output_tokens": 0,
            },
        },
    ]:
        update = parser.accept(event)
        if update.text is not None:
            updates.append(update.text)

    result = parser.finish(0)
    assert updates == ["hel", "hello"]
    assert result.text == "hello"
    assert "helhello" not in result.text


@pytest.mark.parametrize(
    "item_type,item",
    [
        (
            "command_execution",
            {
                "command": "echo unsafe",
                "aggregated_output": "",
                "exit_code": None,
                "status": "in_progress",
            },
        ),
        (
            "file_change",
            {"changes": [], "status": "completed"},
        ),
        (
            "mcp_tool_call",
            {
                "server": "unsafe",
                "tool": "do_thing",
                "arguments": {},
                "result": None,
                "error": None,
                "status": "completed",
            },
        ),
        (
            "collab_tool_call",
            {
                "tool": "spawn_agent",
                "sender_thread_id": "thread-1",
                "receiver_thread_ids": [],
                "prompt": None,
                "agents_states": {},
                "status": "completed",
            },
        ),
        (
            "web_search",
            {"id": "search-1", "query": "unsafe", "action": {"type": "search"}},
        ),
    ],
)
def test_action_event_is_rejected(item_type, item):
    parser = ProtocolParser()
    with pytest.raises(CodexError) as caught:
        parser.accept(
            {
                "type": "item.started",
                "item": {"id": "action-1", "type": item_type, **item},
            }
        )
    assert caught.value.code == "tool_activity_blocked"
    assert caught.value.retryable is False


def test_unknown_event_is_rejected():
    with pytest.raises(CodexError) as caught:
        ProtocolParser().accept({"type": "future.event", "payload": {}})
    assert caught.value.code == "protocol_error"


def test_unknown_item_is_rejected():
    with pytest.raises(CodexError) as caught:
        ProtocolParser().accept(
            {
                "type": "item.completed",
                "item": {"id": "1", "type": "future_item", "value": "x"},
            }
        )
    assert caught.value.code == "protocol_error"


def test_malformed_json_is_rejected():
    with pytest.raises(CodexError) as caught:
        JsonlDecoder().feed(b'{"type":"broken"\n')
    assert caught.value.code == "protocol_error"


def test_oversized_line_is_rejected():
    decoder = JsonlDecoder()
    with pytest.raises(CodexError) as caught:
        decoder.feed(b"x" * (1024 * 1024 + 1) + b"\n")
    assert caught.value.code == "protocol_error"


def test_nonzero_exit_cannot_succeed():
    parser = ProtocolParser()
    _feed_events(parser, _success_events())
    with pytest.raises(CodexError) as caught:
        parser.finish(1)
    assert caught.value.code == "process_failed"


def test_missing_completion_cannot_succeed():
    parser = ProtocolParser()
    _feed_events(parser, _success_events()[:-1])
    with pytest.raises(CodexError) as caught:
        parser.finish(0)
    assert caught.value.code == "protocol_error"


def test_missing_thread_started_cannot_succeed():
    parser = ProtocolParser()
    with pytest.raises(CodexError) as caught:
        parser.accept({"type": "turn.started"})
    assert caught.value.code == "protocol_error"


def test_missing_turn_started_cannot_succeed():
    parser = ProtocolParser()
    parser.accept({"type": "thread.started", "thread_id": "thread-1"})
    with pytest.raises(CodexError) as caught:
        parser.accept(
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            }
        )
    assert caught.value.code == "protocol_error"


def test_agent_message_without_item_completed_cannot_succeed():
    parser = ProtocolParser()
    _feed_events(
        parser,
        [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "turn.started"},
            {
                "type": "item.updated",
                "item": {"id": "item-1", "type": "agent_message", "text": "partial"},
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        ],
    )
    with pytest.raises(CodexError) as caught:
        parser.finish(0)
    assert caught.value.code == "protocol_error"


def test_duplicate_agent_completion_same_snapshot_is_idempotent():
    parser = ProtocolParser()
    parser.accept({"type": "thread.started", "thread_id": "thread-1"})
    parser.accept({"type": "turn.started"})
    event = {
        "type": "item.completed",
        "item": {"id": "item-1", "type": "agent_message", "text": "hello"},
    }
    assert parser.accept(event).text == "hello"
    assert parser.accept(event).text is None
    parser.accept(
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }
    )
    assert parser.finish(0).text == "hello"


def test_duplicate_agent_completion_with_changed_snapshot_is_rejected():
    parser = ProtocolParser()
    parser.accept({"type": "thread.started", "thread_id": "thread-1"})
    parser.accept({"type": "turn.started"})
    parser.accept(
        {
            "type": "item.completed",
            "item": {"id": "item-1", "type": "agent_message", "text": "hello"},
        }
    )
    with pytest.raises(CodexError) as caught:
        parser.accept(
            {
                "type": "item.completed",
                "item": {"id": "item-1", "type": "agent_message", "text": "changed"},
            }
        )
    assert caught.value.code == "protocol_error"


def test_completed_non_agent_item_cannot_roll_back_to_update():
    parser = ProtocolParser()
    parser.accept({"type": "thread.started", "thread_id": "thread-1"})
    parser.accept({"type": "turn.started"})
    parser.accept(
        {
            "type": "item.completed",
            "item": {"id": "reasoning-1", "type": "reasoning", "text": "thought"},
        }
    )
    with pytest.raises(CodexError) as caught:
        parser.accept(
            {
                "type": "item.updated",
                "item": {"id": "reasoning-1", "type": "reasoning", "text": "stale"},
            }
        )
    assert caught.value.code == "protocol_error"


def test_missing_agent_message_cannot_succeed():
    parser = ProtocolParser()
    _feed_events(parser, [
        {"type": "thread.started", "thread_id": "thread-1"},
        {"type": "turn.started"},
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 1,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "reasoning_output_tokens": 0,
            },
        },
    ])
    with pytest.raises(CodexError) as caught:
        parser.finish(0)
    assert caught.value.code == "protocol_error"


def test_final_line_without_newline():
    event = {"type": "turn.started"}
    decoder = JsonlDecoder()
    assert decoder.feed(json.dumps(event).encode("utf-8")) == []
    assert decoder.finish() == [event]


def test_lifecycle_events_do_not_enter_final_text():
    parser = ProtocolParser()
    update = parser.accept({"type": "thread.started", "thread_id": "thread-1"})
    assert update.text is None
    update = parser.accept({"type": "turn.started"})
    assert update.text is None
