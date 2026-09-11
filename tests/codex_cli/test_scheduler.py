import os
import signal
import threading
import time

import pytest

from request_llms.codex_cli.config import CodexSettings
from request_llms.codex_cli.runtime import run_request
from request_llms.codex_cli.scheduler import CodexScheduler
from request_llms.codex_cli.types import CodexError, CodexRequest, CodexResult

from .conftest import make_request, pid_exists, wait_for_json


class FakeClock:
    def __init__(self):
        self.value = 0.0
        self.lock = threading.Lock()

    def __call__(self):
        with self.lock:
            return self.value

    def advance(self, amount):
        with self.lock:
            self.value += amount


def _settings(**changes):
    values = {
        "cli_path": "/tmp/fake-codex",
        "cli_model": "",
        "queue_capacity": 32,
        "min_start_interval": 0.0,
        "queue_timeout": 10.0,
        "request_timeout": 10.0,
        "max_input_bytes": 1000,
        "max_output_bytes": 1000,
    }
    values.update(changes)
    return CodexSettings(**values)


def _wait_until(predicate, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    assert predicate()


def _submit_many(scheduler, count):
    submissions = []
    for index in range(count):
        submissions.append(scheduler.submit(make_request(str(index)), lambda text: None))
    return submissions


def test_twelve_submissions_peak_at_one():
    active = 0
    peak = 0
    lock = threading.Lock()
    started = []

    def runner(request, settings, on_text):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
            started.append(request.prompt)
        time.sleep(0.01)
        on_text(request.prompt)
        with lock:
            active -= 1
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    try:
        submissions = _submit_many(scheduler, 12)
        assert [submission.future.result(timeout=3).text for submission in submissions] == [str(i) for i in range(12)]
        assert peak == 1
        assert started == [str(i) for i in range(12)]
    finally:
        scheduler.close()


def test_fifo_order():
    started = []

    def runner(request, settings, on_text):
        started.append(request.prompt)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    try:
        submissions = _submit_many(scheduler, 5)
        for submission in submissions:
            submission.future.result(timeout=2)
        assert started == ["0", "1", "2", "3", "4"]
    finally:
        scheduler.close()


def test_capacity_excludes_running_request():
    entered = threading.Event()
    release = threading.Event()
    started = []

    def runner(request, settings, on_text):
        started.append(request.prompt)
        entered.set()
        release.wait(2)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(queue_capacity=2), runner, time.monotonic)
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert entered.wait(1)
        second = scheduler.submit(make_request("second"), lambda text: None)
        third = scheduler.submit(make_request("third"), lambda text: None)
        with pytest.raises(CodexError) as caught:
            scheduler.submit(make_request("fourth"), lambda text: None)
        assert caught.value.code == "queue_full"
        release.set()
        assert first.future.result(timeout=2).text == "first"
        assert second.future.result(timeout=2).text == "second"
        assert third.future.result(timeout=2).text == "third"
    finally:
        release.set()
        scheduler.close()


def test_queue_full_starts_no_process():
    entered = threading.Event()
    release = threading.Event()
    calls = []

    def runner(request, settings, on_text):
        calls.append(request.prompt)
        entered.set()
        release.wait(2)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(queue_capacity=1), runner, time.monotonic)
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert entered.wait(1)
        second = scheduler.submit(make_request("second"), lambda text: None)
        with pytest.raises(CodexError) as caught:
            scheduler.submit(make_request("third"), lambda text: None)
        assert caught.value.code == "queue_full"
        time.sleep(0.05)
        assert calls == ["first"]
        release.set()
        first.future.result(timeout=2)
        second.future.result(timeout=2)
    finally:
        release.set()
        scheduler.close()


def test_cancel_queued_request_frees_capacity():
    entered = threading.Event()
    release = threading.Event()
    calls = []

    def runner(request, settings, on_text):
        calls.append(request.prompt)
        entered.set()
        while not release.is_set():
            if request.cancel.is_cancelled():
                raise CodexError("cancelled", "cancelled")
            time.sleep(0.01)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(queue_capacity=1), runner, time.monotonic)
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert entered.wait(1)
        queued = scheduler.submit(make_request("queued"), lambda text: None)
        with pytest.raises(CodexError):
            scheduler.submit(make_request("rejected"), lambda text: None)
        queued.cancel.cancel()
        with pytest.raises(CodexError) as caught:
            queued.future.result(timeout=2)
        assert caught.value.code == "cancelled"
        replacement = scheduler.submit(make_request("replacement"), lambda text: None)
        release.set()
        assert first.future.result(timeout=2).text == "first"
        assert replacement.future.result(timeout=2).text == "replacement"
        assert calls == ["first", "replacement"]
    finally:
        release.set()
        scheduler.close()


def test_queue_timeout_starts_no_process():
    clock = FakeClock()
    entered = threading.Event()
    release = threading.Event()
    calls = []

    def runner(request, settings, on_text):
        calls.append(request.prompt)
        entered.set()
        release.wait(2)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(
        _settings(queue_capacity=2, queue_timeout=5.0), runner, clock
    )
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert entered.wait(1)
        queued = scheduler.submit(make_request("queued"), lambda text: None)
        clock.advance(6.0)
        # A new submission wakes the worker so the injected clock can be
        # observed without sleeping for the configured timeout.
        replacement = scheduler.submit(make_request("replacement"), lambda text: None)
        with pytest.raises(CodexError) as caught:
            queued.future.result(timeout=2)
        assert caught.value.code == "queue_timeout"
        release.set()
        assert first.future.result(timeout=2).text == "first"
        assert replacement.future.result(timeout=2).text == "replacement"
        assert calls == ["first", "replacement"]
    finally:
        release.set()
        scheduler.close()


def test_start_interval_uses_actual_start_time():
    clock = FakeClock()
    started = []

    def runner(request, settings, on_text):
        started.append((request.prompt, clock()))
        if request.prompt == "first":
            clock.advance(100.0)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(
        _settings(min_start_interval=3.0, queue_timeout=1000.0), runner, clock
    )
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        second = scheduler.submit(make_request("second"), lambda text: None)
        first.future.result(timeout=2)
        assert second.future.result(timeout=2).text == "second"
        assert started == [("first", 0.0), ("second", 100.0)]
    finally:
        scheduler.close()


def test_start_interval_uses_real_process_start_callback():
    starts = []

    def runner(request, settings, on_text, on_process_start):
        if request.prompt == "first":
            # Simulate a slow capability probe before the real Popen.
            time.sleep(0.08)
        on_process_start()
        starts.append(time.monotonic())
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(
        _settings(min_start_interval=0.04), runner, time.monotonic
    )
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        second = scheduler.submit(make_request("second"), lambda text: None)
        assert first.future.result(timeout=2).text == "first"
        assert second.future.result(timeout=2).text == "second"
        assert len(starts) == 2
        assert starts[1] - starts[0] >= 0.035
    finally:
        scheduler.close()


def test_nonreading_cli_cancellation_releases_scheduler_slot(
    fake_settings, tmp_path, monkeypatch
):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "no_stdin")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    values = fake_settings.__dict__.copy()
    values.update(
        {
            "min_start_interval": 0.0,
            "max_input_bytes": 2 * 1024 * 1024,
            "request_timeout": 10.0,
        }
    )
    settings = CodexSettings(**values)
    scheduler = CodexScheduler(settings, run_request, time.monotonic)
    first = scheduler.submit(
        make_request("x" * (2 * 1024 * 1024)), lambda text: None
    )
    metadata = wait_for_json(metadata_path)
    try:
        first.cancel.cancel()
        with pytest.raises(CodexError) as caught:
            first.future.result(timeout=3)
        assert caught.value.code == "cancelled"

        monkeypatch.setenv("FAKE_CODEX_SCENARIO", "success")
        second = scheduler.submit(make_request("second"), lambda text: None)
        assert second.future.result(timeout=3).text == "fake response"
    finally:
        if pid_exists(metadata["pid"]):
            os.kill(metadata["pid"], signal.SIGKILL)
        scheduler.close()


def test_failure_is_not_retried():
    calls = []

    def runner(request, settings, on_text):
        calls.append(request.prompt)
        raise CodexError("process_failed", "failed")

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    try:
        submission = scheduler.submit(make_request(), lambda text: None)
        with pytest.raises(CodexError) as caught:
            submission.future.result(timeout=2)
        assert caught.value.code == "process_failed"
        assert calls == ["hello"]
    finally:
        scheduler.close()


def test_cancel_completion_race_finishes_once():
    entered = threading.Event()
    release = threading.Event()

    def runner(request, settings, on_text):
        entered.set()
        release.wait(2)
        return CodexResult("completed")

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    try:
        submission = scheduler.submit(make_request(), lambda text: None)
        assert entered.wait(1)
        submission.cancel.cancel()
        release.set()
        try:
            value = submission.future.result(timeout=2)
            assert value.text == "completed"
        except CodexError as error:
            assert error.code == "cancelled"
        assert submission.future.done()
        assert submission.future.cancelled() is False
    finally:
        release.set()
        scheduler.close()


def test_close_rejects_and_cancels():
    started = threading.Event()
    release = threading.Event()

    def runner(request, settings, on_text):
        started.set()
        while not release.is_set():
            if request.cancel.is_cancelled():
                raise CodexError("cancelled", "cancelled")
            time.sleep(0.01)
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    first = scheduler.submit(make_request("first"), lambda text: None)
    assert started.wait(1)
    queued = scheduler.submit(make_request("queued"), lambda text: None)
    scheduler.close()
    with pytest.raises(CodexError) as caught:
        scheduler.submit(make_request("new"), lambda text: None)
    assert caught.value.code == "service_closed"
    with pytest.raises(CodexError) as caught:
        queued.future.result(timeout=2)
    assert caught.value.code == "cancelled"
    release.set()
    with pytest.raises(CodexError) as caught:
        first.future.result(timeout=2)
    assert caught.value.code == "cancelled"


def test_cleanup_failure_blocks_next_start():
    calls = []
    started = threading.Event()
    release = threading.Event()

    def runner(request, settings, on_text):
        calls.append(request.prompt)
        started.set()
        release.wait(2)
        if request.prompt == "first":
            raise CodexError("cleanup_failed", "cleanup failed")
        return CodexResult(request.prompt)

    scheduler = CodexScheduler(_settings(), runner, time.monotonic)
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert started.wait(1)
        second = scheduler.submit(make_request("second"), lambda text: None)
        release.set()
        with pytest.raises(CodexError) as caught:
            first.future.result(timeout=2)
        assert caught.value.code == "cleanup_failed"
        with pytest.raises(CodexError) as caught:
            second.future.result(timeout=2)
        assert caught.value.code == "cleanup_failed"
        assert calls == ["first"]
    finally:
        release.set()
        scheduler.close()
