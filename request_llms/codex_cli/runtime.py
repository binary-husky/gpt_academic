"""Controlled Codex CLI process execution.

This module is intentionally independent of GPT Academic's UI and logging
layers.  It owns the process group, pipes, per-request empty directory, and
the fail-closed protocol boundary.
"""

import errno
import os
import queue
import select
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .config import CodexSettings, TERMINATION_GRACE_PERIOD
from .protocol import JsonlDecoder, ProtocolParser
from .types import CancelToken, CodexError, CodexRequest, CodexResult


@dataclass(frozen=True)
class CliCapabilities:
    supports_json: bool
    supports_ephemeral: bool
    supports_read_only_sandbox: bool
    supports_skip_git_repo_check: bool
    supports_ignore_user_config: bool
    supports_ignore_rules: bool
    supports_stdin: bool


PROBE_TIMEOUT = 10.0
PROBE_POLL_INTERVAL = 0.05
EVENT_QUEUE_CAPACITY = 64
EVENT_QUEUE_PUT_TIMEOUT = 0.05


def _unavailable(message: str = "Codex CLI 无法启动。") -> CodexError:
    return CodexError("cli_unavailable", message)


def _incompatible(message: str = "当前 Codex CLI 缺少后端所需的安全能力。") -> CodexError:
    return CodexError("cli_incompatible", message)


def _safe_environment() -> Dict[str, str]:
    environment = dict(os.environ)
    # Do not let a GPT Academic API credential accidentally select an API
    # route inside the child.  CODEX_HOME is deliberately retained because
    # the user's existing Codex login is owned by that CLI installation.
    for key in list(environment):
        if key == "API_KEY" or key.endswith("_API_KEY"):
            environment.pop(key, None)
    return environment


def probe_cli(
    settings: CodexSettings, cancel: Optional[CancelToken] = None
) -> CliCapabilities:
    """Inspect CLI help without sending a model prompt.

    Capability probing has its own fixed ten-second deadline.  It runs in an
    exact POSIX process group so cancellation can reap it before a formal
    request is considered.  The request timeout starts later, at formal
    ``Popen`` success in :func:`run_request`.
    """

    if os.name != "posix":
        raise _incompatible(
            "当前平台暂不支持可验证的 Codex CLI 进程组清理。"
        )
    if cancel is not None and cancel.is_cancelled():
        raise CodexError("cancelled", "Codex CLI 请求已取消。")
    argv = [
        settings.cli_path,
        "exec",
        "--help",
        "--ignore-user-config",
        "--ignore-rules",
    ]
    try:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_safe_environment(),
            shell=False,
            start_new_session=True,
        )
    except (OSError, ValueError):
        raise _unavailable()

    try:
        process_group_id = _verify_process_group(process)
    except CodexError:
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                if stream is not None:
                    stream.close()
            except (OSError, ValueError):
                pass
        raise

    communication = {}
    communication_done = threading.Event()

    def communicate():
        try:
            communication["output"] = process.communicate()
        except BaseException as error:
            communication["error"] = error
        finally:
            communication_done.set()

    communication_thread = threading.Thread(
        target=communicate,
        name="gpt-academic-codex-probe-reader",
        daemon=True,
    )
    communication_thread.start()

    probe_error = None
    cleanup_error = None
    deadline = time.monotonic() + PROBE_TIMEOUT
    while not communication_done.wait(PROBE_POLL_INTERVAL):
        if cancel is not None and cancel.is_cancelled():
            probe_error = CodexError("cancelled", "Codex CLI 请求已取消。")
            break
        if time.monotonic() >= deadline:
            probe_error = CodexError("probe_timeout", "Codex CLI 能力探测超时。")
            break

    if probe_error is not None:
        try:
            _terminate_process(
                process,
                TERMINATION_GRACE_PERIOD,
                process_group_id,
            )
        except CodexError as error:
            cleanup_error = error
    else:
        if cancel is not None and cancel.is_cancelled():
            probe_error = CodexError("cancelled", "Codex CLI 请求已取消。")
        elif not communication_done.is_set():
            probe_error = CodexError("probe_timeout", "Codex CLI 能力探测超时。")

    communication_thread.join(
        timeout=max(TERMINATION_GRACE_PERIOD, PROBE_POLL_INTERVAL)
    )
    if communication_thread.is_alive():
        cleanup_error = _cleanup_failure(
            "Codex CLI 能力探测读取线程未能退出，已暂停后续请求。"
        )

    if process.poll() is None or _process_group_exists(process_group_id):
        try:
            _terminate_process(process, TERMINATION_GRACE_PERIOD, process_group_id)
        except CodexError as error:
            cleanup_error = error

    for stream in (process.stdout, process.stderr):
        try:
            if stream is not None:
                stream.close()
        except (OSError, ValueError):
            pass

    if cleanup_error is not None:
        raise cleanup_error
    if probe_error is not None:
        raise probe_error
    if "error" in communication:
        raise _unavailable()

    stdout, stderr = communication.get("output", (b"", b""))

    if process.returncode != 0:
        raise _incompatible()
    try:
        help_text = (stdout + stderr).decode("utf-8")
    except UnicodeDecodeError:
        raise _incompatible()
    lower = help_text.lower()
    capabilities = CliCapabilities(
        supports_json="--json" in lower,
        supports_ephemeral="--ephemeral" in lower,
        supports_read_only_sandbox=("--sandbox" in lower and "read-only" in lower),
        supports_skip_git_repo_check="--skip-git-repo-check" in lower,
        supports_ignore_user_config="--ignore-user-config" in lower,
        supports_ignore_rules="--ignore-rules" in lower,
        supports_stdin=("stdin" in lower and "read" in lower and "-" in help_text),
    )
    if not all(capabilities.__dict__.values()):
        raise _incompatible()
    return capabilities


def build_argv(
    settings: CodexSettings, cwd: str, capabilities: CliCapabilities
) -> List[str]:
    """Build the fixed, non-shell command line used for one request."""

    if not isinstance(cwd, str) or not cwd:
        raise _incompatible("Codex CLI 工作目录无效。")
    if not all(capabilities.__dict__.values()):
        raise _incompatible()

    argv = [
        settings.cli_path,
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--color",
        "never",
    ]
    if settings.cli_model:
        argv.extend(["--model", settings.cli_model])
    argv.extend(["-C", cwd, "-"])
    return argv


def _cleanup_failure(
    message: str = "Codex CLI 进程清理失败，已暂停后续请求。"
) -> CodexError:
    return CodexError("cleanup_failed", message)


def _process_group_exists(process_group_id: Optional[int]) -> bool:
    """Return whether a POSIX process group is still observable."""

    if os.name != "posix" or process_group_id is None:
        return True
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except OSError as error:
        if getattr(error, "errno", None) == errno.ESRCH:
            return False
        # Permission and other errors are treated as "still present" so a
        # cleanup failure cannot be mistaken for a clean process tree.
        return True
    return True


def _kill_process_group(
    process: subprocess.Popen, sig: int, process_group_id: Optional[int] = None
) -> bool:
    """Signal an exact process group; never fall back to a parent-only kill."""

    del process  # kept in the signature for the existing internal contract
    if os.name != "posix" or process_group_id is None:
        return False
    try:
        os.killpg(process_group_id, sig)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    return True


def _reap_after_group_lookup_failure(
    process: subprocess.Popen, expected_process_group_id: int
) -> CodexError:
    """Best-effort exact cleanup after ``getpgid`` could not be verified.

    ``start_new_session=True`` makes the child PID the expected process-group
    ID.  The fallback is deliberately SIGKILL to that exact ID only; it never
    falls back to killing just the parent or to matching a process name.  A
    lookup failure remains a cleanup error even when the best-effort reap
    succeeds, because the process-group identity was not observable at the
    safety boundary.
    """

    cleanup_error = _cleanup_failure(
        "Codex CLI 进程组标识无法确认，已拒绝继续运行。"
    )
    if os.name != "posix" or not expected_process_group_id:
        return cleanup_error

    wait_period = max(float(TERMINATION_GRACE_PERIOD), 0.1)
    kill_succeeded = _kill_process_group(
        process, signal.SIGKILL, expected_process_group_id
    )
    try:
        process.wait(timeout=wait_period)
    except subprocess.TimeoutExpired:
        # Repeat the same exact group kill once if the first SIGKILL did not
        # result in a reaped parent within the bounded wait.
        if kill_succeeded:
            kill_succeeded = _kill_process_group(
                process, signal.SIGKILL, expected_process_group_id
            )
            try:
                process.wait(timeout=wait_period)
            except (subprocess.TimeoutExpired, OSError, ValueError):
                return cleanup_error
        else:
            return cleanup_error
    except (OSError, ValueError):
        return cleanup_error

    if not kill_succeeded:
        return cleanup_error
    if process.poll() is None or _process_group_exists(expected_process_group_id):
        return cleanup_error
    return cleanup_error


def _verify_process_group(process: subprocess.Popen) -> int:
    """Verify the ``start_new_session`` process-group invariant or reap."""

    expected_process_group_id = process.pid
    try:
        process_group_id = os.getpgid(process.pid)
    except OSError:
        raise _reap_after_group_lookup_failure(
            process, expected_process_group_id
        )
    if process_group_id != expected_process_group_id:
        raise _reap_after_group_lookup_failure(
            process, expected_process_group_id
        )
    return process_group_id


def _terminate_process(
    process: subprocess.Popen,
    grace_period: float,
    process_group_id: Optional[int] = None,
) -> None:
    """Terminate one independent process group, then force it, and wait."""

    if os.name != "posix":
        raise _cleanup_failure(
            "当前平台无法验证 Codex CLI 进程树，已拒绝继续运行。"
        )
    if process_group_id is None:
        raise _cleanup_failure()

    wait_period = max(float(grace_period), 0.1)

    def wait_for_group_exit(timeout: float) -> bool:
        deadline = time.monotonic() + max(float(timeout), 0.1)
        while _process_group_exists(process_group_id):
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)
        return True

    group_exists = _process_group_exists(process_group_id)
    if group_exists:
        if not _kill_process_group(process, signal.SIGTERM, process_group_id):
            raise _cleanup_failure()

    # Reap the parent before probing the group.  Otherwise a killed but
    # unreaped parent can remain as a zombie and make killpg(..., 0) report a
    # false-positive group that never disappears.
    try:
        process.wait(timeout=wait_period)
    except subprocess.TimeoutExpired:
        if not _kill_process_group(process, signal.SIGKILL, process_group_id):
            raise _cleanup_failure()
        try:
            process.wait(timeout=wait_period)
        except (subprocess.TimeoutExpired, OSError):
            raise _cleanup_failure()
    except OSError:
        raise _cleanup_failure()

    if not wait_for_group_exit(wait_period):
        if not _kill_process_group(process, signal.SIGKILL, process_group_id):
            raise _cleanup_failure()
        if not wait_for_group_exit(wait_period):
            raise _cleanup_failure()

    if process.poll() is None or _process_group_exists(process_group_id):
        raise _cleanup_failure()


def _cleanup_tempdir(path: Optional[str]) -> Optional[CodexError]:
    if not path:
        return None
    try:
        shutil.rmtree(path)
    except OSError:
        return CodexError(
            "cleanup_failed",
            "Codex CLI 临时资源清理失败，已暂停后续请求。",
        )
    return None


def run_request(
    request: CodexRequest,
    settings: CodexSettings,
    on_text: Callable[[str], None],
    on_process_start: Optional[Callable[[], None]] = None,
) -> CodexResult:
    """Run one request with fixed safety flags and no automatic retry."""

    if request.cancel.is_cancelled():
        raise CodexError("cancelled", "Codex CLI 请求已取消。")
    if os.name != "posix":
        raise _incompatible(
            "当前平台暂不支持可验证的 Codex CLI 进程组清理。"
        )
    try:
        prompt_bytes = request.prompt.encode("utf-8")
        input_bytes = len(prompt_bytes)
    except (AttributeError, UnicodeError):
        raise CodexError("input_limit", "Codex CLI 仅支持有效的 UTF-8 文本输入。")
    if input_bytes > settings.max_input_bytes:
        raise CodexError("input_limit", "Codex CLI 输入内容超过大小限制。")

    # Capability probing is deliberately lazy and happens only on a selected
    # Codex request, never when ordinary GPT Academic modules are imported.
    capabilities = probe_cli(settings, request.cancel)
    # A cancellation can race with the final help event.  Never cross the
    # capability boundary into a formal model request after cancellation.
    if request.cancel.is_cancelled():
        raise CodexError("cancelled", "Codex CLI 请求已取消。")
    tempdir = None
    process = None
    process_group_id = None
    reader_threads = []
    events = queue.Queue(maxsize=EVENT_QUEUE_CAPACITY)
    stop_event = threading.Event()
    stream_done = {"stdout": False, "stderr": False}
    stderr_tail = bytearray()
    parser = ProtocolParser()
    decoder = JsonlDecoder()
    stdout_bytes = 0
    request_error = None
    result = None
    started_at = None
    terminated = False
    writer_thread = None
    writer_done = threading.Event()
    writer_error = [None]

    def put_event(event):
        while not stop_event.is_set():
            try:
                events.put(event, timeout=EVENT_QUEUE_PUT_TIMEOUT)
                return True
            except queue.Full:
                continue
        return False

    def pump(name, stream):
        try:
            while True:
                # Buffered ``read(4096)`` may wait for the entire requested
                # size on a live pipe.  ``os.read`` returns the bytes already
                # available, so an action event can be rejected immediately
                # instead of waiting for the request timeout.
                chunk = os.read(stream.fileno(), 4096)
                if not chunk:
                    break
                if not put_event((name, chunk)):
                    return
        except OSError:
            pass
        finally:
            put_event((name, None))

    def stop_for(error):
        nonlocal request_error, terminated
        if request_error is None:
            request_error = error
        if process is not None and not terminated:
            terminated = True
            stop_event.set()
            try:
                _terminate_process(
                    process,
                    settings.TERMINATION_GRACE_PERIOD,
                    process_group_id,
                )
            except CodexError as cleanup_error:
                request_error = cleanup_error

    try:
        try:
            tempdir = tempfile.mkdtemp(prefix="gpt-academic-codex-")
        except OSError:
            raise _unavailable("Codex CLI 临时工作目录无法创建。")
        argv = build_argv(settings, tempdir, capabilities)
        try:
            popen_kwargs = {
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "cwd": tempdir,
                "env": _safe_environment(),
                "shell": False,
            }
            if os.name == "posix":
                popen_kwargs["start_new_session"] = True
            elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            if request.cancel.is_cancelled():
                raise CodexError("cancelled", "Codex CLI 请求已取消。")
            process = subprocess.Popen(argv, **popen_kwargs)
            if os.name == "posix":
                # Set the expected ID before verification so the finalizer
                # can still inspect/reap the exact group if verification
                # raises after Popen.
                process_group_id = process.pid
                process_group_id = _verify_process_group(process)
        except (OSError, ValueError):
            raise _unavailable()

        started_at = time.monotonic()
        if on_process_start is not None:
            try:
                on_process_start()
            except Exception:
                raise _cleanup_failure()
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            thread = threading.Thread(target=pump, args=(name, stream), daemon=True)
            thread.start()
            reader_threads.append(thread)

        def write_prompt():
            try:
                fd = process.stdin.fileno()
                try:
                    os.set_blocking(fd, False)
                except (AttributeError, OSError):
                    writer_error[0] = _cleanup_failure(
                        "Codex CLI 输入写入通道无法受控。"
                    )
                    return
                offset = 0
                while offset < len(prompt_bytes):
                    if request.cancel.is_cancelled():
                        writer_error[0] = CodexError(
                            "cancelled", "Codex CLI 请求已取消。"
                        )
                        return
                    try:
                        written = os.write(fd, prompt_bytes[offset:])
                        if written <= 0:
                            writer_error[0] = _unavailable(
                                "Codex CLI 无法接收请求内容。"
                            )
                            return
                        offset += written
                    except BlockingIOError:
                        try:
                            _, writable, _ = select.select([], [fd], [], 0.05)
                        except (OSError, ValueError):
                            if request.cancel.is_cancelled():
                                writer_error[0] = CodexError(
                                    "cancelled", "Codex CLI 请求已取消。"
                                )
                            else:
                                writer_error[0] = _unavailable(
                                    "Codex CLI 无法接收请求内容。"
                                )
                            return
                        if not writable:
                            continue
                    except BrokenPipeError:
                        writer_error[0] = (
                            CodexError("cancelled", "Codex CLI 请求已取消。")
                            if request.cancel.is_cancelled()
                            else _unavailable("Codex CLI 无法接收请求内容。")
                        )
                        return
                    except OSError:
                        writer_error[0] = (
                            CodexError("cancelled", "Codex CLI 请求已取消。")
                            if request.cancel.is_cancelled()
                            else _unavailable("Codex CLI 无法接收请求内容。")
                        )
                        return
                try:
                    process.stdin.close()
                except (OSError, ValueError):
                    if not request.cancel.is_cancelled():
                        writer_error[0] = _cleanup_failure()
            finally:
                writer_done.set()

        writer_thread = threading.Thread(
            target=write_prompt,
            name="gpt-academic-codex-stdin-writer",
            daemon=True,
        )
        writer_thread.start()

        while request_error is None:
            if request.cancel.is_cancelled():
                stop_for(CodexError("cancelled", "Codex CLI 请求已取消。"))
                break
            if started_at is not None and time.monotonic() - started_at >= settings.request_timeout:
                stop_for(CodexError("request_timeout", "Codex CLI 请求超时。"))
                break
            if writer_done.is_set() and writer_error[0] is not None:
                stop_for(writer_error[0])
                break

            try:
                name, chunk = events.get(timeout=0.05)
            except queue.Empty:
                if (
                    process.poll() is not None
                    and stream_done["stdout"]
                    and stream_done["stderr"]
                    and events.empty()
                    and writer_done.is_set()
                ):
                    break
                continue

            if chunk is None:
                stream_done[name] = True
                if (
                    process.poll() is not None
                    and stream_done["stdout"]
                    and stream_done["stderr"]
                    and events.empty()
                    and writer_done.is_set()
                ):
                    break
                continue

            if name == "stderr":
                stderr_tail.extend(chunk)
                if len(stderr_tail) > 8192:
                    del stderr_tail[:-8192]
                continue

            stdout_bytes += len(chunk)
            if stdout_bytes > settings.max_output_bytes:
                stop_for(CodexError("output_limit", "Codex CLI 输出内容超过大小限制。"))
                break
            try:
                decoded_events = decoder.feed(chunk)
                for event in decoded_events:
                    update = parser.accept(event)
                    if update.text is not None:
                        on_text(update.text)
            except CodexError as error:
                stop_for(error)
                break
            except Exception:
                stop_for(CodexError("process_failed", "Codex CLI 请求处理失败。"))
                break

        if request_error is None:
            try:
                for event in decoder.finish():
                    update = parser.accept(event)
                    if update.text is not None:
                        on_text(update.text)
                exit_code = process.wait(timeout=0.5)
                result = parser.finish(exit_code)
            except CodexError as error:
                request_error = error
            except (OSError, subprocess.TimeoutExpired):
                request_error = CodexError("process_failed", "Codex CLI 进程处理失败。")
    finally:
        stop_event.set()
        cleanup_error = None
        if process is not None:
            try:
                if (
                    process.poll() is None
                    or _process_group_exists(process_group_id)
                ):
                    _terminate_process(
                        process,
                        settings.TERMINATION_GRACE_PERIOD,
                        process_group_id,
                    )
                else:
                    process.wait(timeout=0.5)
            except CodexError as error:
                cleanup_error = error
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    if stream is not None:
                        stream.close()
                except (OSError, ValueError):
                    pass
        if writer_thread is not None:
            writer_thread.join(
                timeout=max(settings.TERMINATION_GRACE_PERIOD, 0.1)
            )
            if writer_thread.is_alive():
                cleanup_error = _cleanup_failure(
                    "Codex CLI 输入写入线程未能退出，已暂停后续请求。"
                )
        for thread in reader_threads:
            thread.join(timeout=max(settings.TERMINATION_GRACE_PERIOD, 0.1))
        if process is not None and _process_group_exists(process_group_id):
            cleanup_error = _cleanup_failure()
        tempdir_error = _cleanup_tempdir(tempdir)
        if tempdir_error is not None:
            cleanup_error = tempdir_error
        if cleanup_error is not None:
            request_error = cleanup_error

    if request_error is not None:
        raise request_error
    if result is None:
        raise CodexError("process_failed", "Codex CLI 请求处理失败。")
    return result
