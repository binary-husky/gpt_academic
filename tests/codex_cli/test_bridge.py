import importlib
import threading
import time
from concurrent.futures import Future
from pathlib import Path

import pytest

from request_llms.codex_cli.types import CodexError, CodexResult, Submission

import request_llms.bridge_codex_cli as bridge


class ImmediateScheduler:
    def __init__(self, text="fake response"):
        self.text = text
        self.submissions = []

    def submit(self, request, on_text):
        future = Future()
        self.submissions.append(request)
        on_text(self.text)
        future.set_result(CodexResult(self.text))
        return Submission(future=future, cancel=request.cancel)


class DelayedScheduler:
    def __init__(self, delay=0.3):
        self.delay = delay
        self.submissions = []

    def submit(self, request, on_text):
        future = Future()
        self.submissions.append(request)

        def finish():
            time.sleep(self.delay)
            if request.cancel.is_cancelled():
                future.set_exception(CodexError("cancelled", "cancelled"))
            else:
                on_text("delayed response")
                future.set_result(CodexResult("delayed response"))

        threading.Thread(target=finish, daemon=True).start()
        return Submission(future=future, cancel=request.cancel)


def _patch_scheduler(monkeypatch, scheduler):
    monkeypatch.setattr(bridge, "get_scheduler", lambda: scheduler)


def test_prompt_preserves_role_and_history_boundaries():
    prompt = bridge.build_prompt(
        "current input",
        ["old question", "old answer"],
        "system instructions",
    )
    assert "[SYSTEM]" in prompt
    assert "system instructions" in prompt
    assert "[CONVERSATION HISTORY]" in prompt
    assert "USER (history 1):\nold question" in prompt
    assert "ASSISTANT (history 1):\nold answer" in prompt
    assert "[CURRENT USER INPUT]\ncurrent input" in prompt
    assert prompt.index("[SYSTEM]") < prompt.index("[CONVERSATION HISTORY]")
    assert prompt.index("[CONVERSATION HISTORY]") < prompt.index("[CURRENT USER INPUT]")


def test_codex_without_api_key_reaches_fake_cli(monkeypatch):
    scheduler = ImmediateScheduler()
    _patch_scheduler(monkeypatch, scheduler)
    observe = ["", time.time()]
    result = bridge.predict_no_ui_long_connection(
        "hello",
        {"llm_model": "codex-cli", "api_key": ""},
        [],
        "system",
        observe,
        True,
    )
    assert result == "fake response"
    assert len(scheduler.submissions) == 1
    assert scheduler.submissions[0].prompt.startswith("[SYSTEM]")
    assert "api_key" not in scheduler.submissions[0].prompt


def test_ui_and_no_ui_share_scheduler(monkeypatch):
    scheduler = ImmediateScheduler()
    _patch_scheduler(monkeypatch, scheduler)
    monkeypatch.setattr(bridge, "_ui_update", lambda chatbot, history, msg="正常": iter([msg]))
    llm_kwargs = {"llm_model": "codex-cli", "api_key": ""}
    observe = ["", time.time()]
    assert bridge.predict_no_ui_long_connection("one", llm_kwargs, [], "", observe, True) == "fake response"
    chatbot = []
    history = []
    list(bridge.predict("two", llm_kwargs, {}, chatbot, history, "", True, None))
    assert len(scheduler.submissions) == 2
    assert all(request.prompt.startswith("[SYSTEM]") for request in scheduler.submissions)


def test_text_snapshot_updates_without_duplication(monkeypatch):
    class SnapshotScheduler:
        def submit(self, request, on_text):
            future = Future()
            on_text("hel")
            on_text("hello")
            future.set_result(CodexResult("hello"))
            return Submission(future=future, cancel=request.cancel)

    scheduler = SnapshotScheduler()
    _patch_scheduler(monkeypatch, scheduler)
    observe = ["", time.time()]
    result = bridge.predict_no_ui_long_connection("x", {"llm_model": "codex-cli"}, [], "", observe, True)
    assert result == "hello"
    assert observe[0] == "hello"
    assert "helhello" not in observe[0]


def test_existing_cancel_signal_cancels_submission(monkeypatch):
    scheduler = DelayedScheduler(delay=0.5)
    _patch_scheduler(monkeypatch, scheduler)
    observe = ["", time.time() - 10]
    with pytest.raises(CodexError) as caught:
        bridge.predict_no_ui_long_connection("x", {"llm_model": "codex-cli"}, [], "", observe, True)
    assert caught.value.code == "cancelled"
    assert scheduler.submissions[0].cancel.is_cancelled()


def test_no_ui_backend_does_not_feed_observer_watchdog(monkeypatch):
    scheduler = DelayedScheduler(delay=0.25)
    _patch_scheduler(monkeypatch, scheduler)
    original = time.time()
    observe = ["", original]
    result = {}

    def call():
        try:
            result["value"] = bridge.predict_no_ui_long_connection(
                "x", {"llm_model": "codex-cli"}, [], "", observe, True
            )
        except BaseException as error:
            result["error"] = error

    thread = threading.Thread(target=call)
    thread.start()
    time.sleep(0.12)
    assert observe[1] == original
    thread.join(2)
    assert not thread.is_alive()
    assert result["value"] == "delayed response"


def test_stopped_observer_cancels_submission(monkeypatch):
    scheduler = DelayedScheduler(delay=0.2)
    _patch_scheduler(monkeypatch, scheduler)
    monkeypatch.setattr(bridge, "_WATCHDOG_PATIENCE", 0.05)
    original = time.time()
    observe = ["", original]
    result = {}

    def call():
        try:
            result["value"] = bridge.predict_no_ui_long_connection(
                "x", {"llm_model": "codex-cli"}, [], "", observe, True
            )
        except BaseException as error:
            result["error"] = error

    thread = threading.Thread(target=call)
    thread.start()
    thread.join(2)
    assert not thread.is_alive()
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "cancelled"
    assert scheduler.submissions[0].cancel.is_cancelled()
    assert observe[1] == original


def test_unsupported_attachment_is_explicit_error(monkeypatch):
    scheduler = ImmediateScheduler()
    _patch_scheduler(monkeypatch, scheduler)
    with pytest.raises(CodexError) as caught:
        bridge.predict_no_ui_long_connection(
            "x",
            {"llm_model": "codex-cli", "attachments": ["file.pdf"]},
            [],
            "",
            ["", time.time()],
            True,
        )
    assert caught.value.code == "unsupported_input"
    assert scheduler.submissions == []


def test_non_codex_import_does_not_probe_cli(monkeypatch):
    calls = []

    def fail_probe(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("probe must be lazy")

    import request_llms.codex_cli.runtime as runtime
    monkeypatch.setattr(runtime, "probe_cli", fail_probe)
    importlib.reload(bridge)
    assert calls == []


def test_default_model_unchanged():
    config_source = Path(__file__).parents[2] / "config.py"
    source = config_source.read_text(encoding="utf-8")
    assert 'LLM_MODEL = "gpt-3.5-turbo-16k"' in source
