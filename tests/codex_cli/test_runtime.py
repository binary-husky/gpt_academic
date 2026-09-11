import json
import os
import signal
import tempfile
import threading
import time

import pytest

from request_llms.codex_cli.config import CodexSettings
import request_llms.codex_cli.runtime as runtime
from request_llms.codex_cli.runtime import CliCapabilities, build_argv, run_request
from request_llms.codex_cli.types import CancelToken, CodexError, CodexRequest

from .conftest import make_request, pid_exists, wait_for_json


ALL_CAPABILITIES = CliCapabilities(
    supports_json=True,
    supports_ephemeral=True,
    supports_read_only_sandbox=True,
    supports_skip_git_repo_check=True,
    supports_ignore_user_config=True,
    supports_ignore_rules=True,
    supports_stdin=True,
)


def _settings(base, **changes):
    values = base.__dict__.copy()
    values.update(changes)
    return CodexSettings(**values)


def _run_in_thread(request, settings, updates=None):
    result = {}

    def target():
        try:
            result["value"] = run_request(request, settings, (updates or []).append)
        except BaseException as error:
            result["error"] = error

    thread = threading.Thread(target=target)
    thread.start()
    return thread, result


def _wait_dead(thread, timeout=4.0):
    thread.join(timeout)
    assert not thread.is_alive()


def test_argv_uses_argument_list_and_stdin(fake_settings):
    argv = build_argv(fake_settings, "/tmp/empty codex cwd", ALL_CAPABILITIES)
    assert argv[0] == fake_settings.cli_path
    assert argv[1:3] == ["exec", "--json"]
    assert "-" in argv
    assert "--sandbox" in argv and "read-only" in argv
    assert "--ephemeral" in argv
    assert "--skip-git-repo-check" in argv
    assert "--ignore-user-config" in argv
    assert "--ignore-rules" in argv
    assert "--model" in argv and "fake-model" in argv
    assert all(isinstance(value, str) for value in argv)


def test_non_posix_is_rejected_before_spawn(fake_settings, monkeypatch):
    monkeypatch.setattr(runtime.os, "name", "nt")
    with pytest.raises(CodexError) as caught:
        runtime.run_request(make_request(), fake_settings, lambda text: None)
    assert caught.value.code == "cli_incompatible"


def test_cancel_during_probe_never_starts_formal_cli(fake_settings, tmp_path, monkeypatch):
    probe_metadata_path = tmp_path / "probe.json"
    formal_count_path = tmp_path / "formal-start-count"
    monkeypatch.setenv("FAKE_CODEX_PROBE_METADATA_PATH", str(probe_metadata_path))
    monkeypatch.setenv("FAKE_CODEX_PROBE_DELAY", "60")
    monkeypatch.setenv("FAKE_CODEX_FORMAL_START_COUNT_PATH", str(formal_count_path))
    request = make_request()
    thread, result = _run_in_thread(request, fake_settings)
    probe_metadata = wait_for_json(probe_metadata_path)
    try:
        request.cancel.cancel()
        _wait_dead(thread, timeout=3.0)
    finally:
        if thread.is_alive() and pid_exists(probe_metadata["pid"]):
            os.kill(probe_metadata["pid"], signal.SIGKILL)
        thread.join(2.0)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "cancelled"
    assert not pid_exists(probe_metadata["pid"])
    assert not formal_count_path.exists()


def test_probe_timeout_reaps_without_starting_formal_cli(fake_settings, tmp_path, monkeypatch):
    probe_metadata_path = tmp_path / "probe.json"
    formal_count_path = tmp_path / "formal-start-count"
    monkeypatch.setattr(runtime, "PROBE_TIMEOUT", 0.1)
    monkeypatch.setenv("FAKE_CODEX_PROBE_METADATA_PATH", str(probe_metadata_path))
    monkeypatch.setenv("FAKE_CODEX_PROBE_DELAY", "60")
    monkeypatch.setenv("FAKE_CODEX_FORMAL_START_COUNT_PATH", str(formal_count_path))
    with pytest.raises(CodexError) as caught:
        run_request(make_request(), fake_settings, lambda text: None)
    assert caught.value.code == "probe_timeout"
    probe_metadata = wait_for_json(probe_metadata_path)
    assert not pid_exists(probe_metadata["pid"])
    assert not formal_count_path.exists()


def test_probe_getpgid_failure_reaps_started_help_process(
    fake_settings, tmp_path, monkeypatch
):
    probe_metadata_path = tmp_path / "probe-getpgid.json"
    monkeypatch.setenv("FAKE_CODEX_PROBE_METADATA_PATH", str(probe_metadata_path))
    monkeypatch.setenv("FAKE_CODEX_PROBE_DELAY", "60")

    def fail_getpgid(pid):
        # Wait until the real help process has recorded its PID so the test
        # exercises cleanup after Popen rather than interpreter startup.
        wait_for_json(probe_metadata_path)
        raise OSError("simulated getpgid failure")

    monkeypatch.setattr(runtime.os, "getpgid", fail_getpgid)
    try:
        with pytest.raises(CodexError) as caught:
            runtime.probe_cli(fake_settings)
        assert caught.value.code == "cleanup_failed"
        metadata = wait_for_json(probe_metadata_path)
        assert not pid_exists(metadata["pid"])
    finally:
        # The assertion above is intentionally before this fallback: it keeps
        # the regression test red if the started probe process is leaked.
        if probe_metadata_path.exists():
            metadata = json.loads(probe_metadata_path.read_text(encoding="utf-8"))
            if pid_exists(metadata["pid"]):
                os.kill(metadata["pid"], signal.SIGKILL)


def test_formal_getpgid_failure_reaps_started_request_process(
    fake_settings, tmp_path, monkeypatch
):
    metadata_path = tmp_path / "formal-getpgid.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "no_stdin")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    monkeypatch.setenv("FAKE_CODEX_DELAY", "60")
    real_getpgid = runtime.os.getpgid
    calls = []

    def fail_formal_getpgid(pid):
        calls.append(pid)
        if len(calls) == 2:
            # Hold the simulated lookup failure until the formal fake has
            # recorded its real PID.  This removes the interpreter-startup
            # race while still exercising the post-Popen exception path.
            wait_for_json(metadata_path)
            raise OSError("simulated formal getpgid failure")
        return real_getpgid(pid)

    monkeypatch.setattr(runtime.os, "getpgid", fail_formal_getpgid)
    try:
        with pytest.raises(CodexError) as caught:
            run_request(make_request("formal prompt"), fake_settings, lambda text: None)
        assert caught.value.code == "cleanup_failed"
        metadata = wait_for_json(metadata_path)
        assert len(calls) >= 2
        assert not pid_exists(metadata["pid"])
    finally:
        # See the probe test above: this only prevents a deliberately failing
        # red test from leaking the fake process into later test cases.
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if pid_exists(metadata["pid"]):
                os.kill(metadata["pid"], signal.SIGKILL)


def test_workdir_is_empty_and_auth_source_is_not_copied(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    auth_source = tmp_path / "codex-auth"
    auth_source.mkdir()
    (auth_source / "auth.json").write_text("do not copy", encoding="utf-8")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    monkeypatch.setenv("CODEX_HOME", str(auth_source))

    result = run_request(make_request("stdin payload"), fake_settings, lambda text: None)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert result.text == "fake response"
    assert metadata["prompt"] == "stdin payload"
    assert metadata["cwd_entries"] == []
    assert not os.path.exists(os.path.join(metadata["cwd"], "auth.json"))
    assert auth_source.joinpath("auth.json").read_text(encoding="utf-8") == "do not copy"
    assert not os.path.exists(metadata["cwd"])


def test_api_key_is_not_inherited(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    monkeypatch.setenv("OPENAI_API_KEY", "do-not-leak")
    monkeypatch.setenv("API_KEY", "also-do-not-leak")
    monkeypatch.setenv("OTHER_API_KEY", "also-do-not-leak")

    run_request(make_request(), fake_settings, lambda text: None)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["openai_api_key"] is None
    assert metadata["api_key"] is None
    assert metadata["other_api_key"] is None


def test_stdout_and_stderr_are_drained(fake_settings, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "stderr_flood")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(tmp_path / "metadata.json"))
    result = run_request(make_request(), fake_settings, lambda text: None)
    assert result.text == "fake response"


def test_cancel_reaps_process_tree(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "ignore_terminate")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    request = make_request()
    thread, result = _run_in_thread(request, fake_settings)
    metadata = wait_for_json(metadata_path)
    child_pid = metadata.get("child_pid")
    request.cancel.cancel()
    _wait_dead(thread)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "cancelled"
    assert not pid_exists(metadata["pid"])
    if child_pid:
        assert not pid_exists(child_pid)
    assert not os.path.exists(metadata["cwd"])


def test_cancel_when_cli_does_not_read_stdin(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "no_stdin")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    settings = _settings(
        fake_settings,
        max_input_bytes=2 * 1024 * 1024,
        request_timeout=10.0,
    )
    request = make_request("x" * (2 * 1024 * 1024))
    thread, result = _run_in_thread(request, settings)
    metadata = wait_for_json(metadata_path)
    try:
        request.cancel.cancel()
        _wait_dead(thread, timeout=3.0)
    finally:
        # Keep the red test from leaking the deliberately sleeping fake
        # process if the old synchronous writer is still blocked.
        if thread.is_alive() and pid_exists(metadata["pid"]):
            os.kill(metadata["pid"], signal.SIGKILL)
        thread.join(2.0)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "cancelled"
    assert not pid_exists(metadata["pid"])
    assert not os.path.exists(metadata["cwd"])


def test_timeout_escalates_and_reaps(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "ignore_terminate")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    settings = _settings(fake_settings, request_timeout=0.2)
    thread, result = _run_in_thread(make_request(), settings)
    metadata = wait_for_json(metadata_path)
    _wait_dead(thread)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "request_timeout"
    assert not pid_exists(metadata["pid"])
    assert not os.path.exists(metadata["cwd"])


def test_action_event_terminates_process(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "action")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    thread, result = _run_in_thread(make_request(), fake_settings)
    metadata = wait_for_json(metadata_path)
    _wait_dead(thread)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "tool_activity_blocked"
    assert not pid_exists(metadata["pid"])
    assert not os.path.exists(metadata["cwd"])


def test_output_limit_terminates_process(fake_settings, tmp_path, monkeypatch):
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "output_limit")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(metadata_path))
    settings = _settings(fake_settings, max_output_bytes=512)
    thread, result = _run_in_thread(make_request(), settings)
    metadata = wait_for_json(metadata_path)
    _wait_dead(thread)
    assert isinstance(result.get("error"), CodexError)
    assert result["error"].code == "output_limit"
    assert not pid_exists(metadata["pid"])
    assert not os.path.exists(metadata["cwd"])


def test_event_queue_is_bounded(fake_settings, tmp_path, monkeypatch):
    queues = []
    real_queue = runtime.queue.Queue

    def make_queue(*args, **kwargs):
        created = real_queue(*args, **kwargs)
        queues.append(created)
        return created

    monkeypatch.setattr(runtime.queue, "Queue", make_queue)
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "output_limit")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(tmp_path / "metadata.json"))
    settings = _settings(fake_settings, max_output_bytes=512)
    with pytest.raises(CodexError) as caught:
        run_request(make_request(), settings, lambda text: None)
    assert caught.value.code == "output_limit"
    assert queues and queues[0].maxsize > 0


def test_tempdir_removed_on_spawn_failure(fake_settings, tmp_path, monkeypatch):
    settings = _settings(fake_settings, cli_path=str(tmp_path / "does-not-exist"))
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    with pytest.raises(CodexError) as caught:
        run_request(make_request(), settings, lambda text: None)
    assert caught.value.code == "cli_unavailable"
    assert list(tmp_path.glob("gpt-academic-codex-*")) == []


def test_sensitive_output_not_logged(fake_settings, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("FAKE_CODEX_SCENARIO", "sensitive")
    monkeypatch.setenv("FAKE_SECRET", "sensitive-stderr-value")
    monkeypatch.setenv("FAKE_CODEX_METADATA_PATH", str(tmp_path / "metadata.json"))
    result = run_request(make_request("sensitive-prompt"), fake_settings, lambda text: None)
    captured = capsys.readouterr()
    assert result.text == "safe response"
    assert "sensitive-stderr-value" not in captured.out
    assert "sensitive-stderr-value" not in captured.err
