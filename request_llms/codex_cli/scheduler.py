"""One-slot FIFO scheduling for all Codex CLI requests in one process."""

import inspect
import threading
import time
from collections import deque
from concurrent.futures import Future, InvalidStateError
from dataclasses import dataclass
from typing import Callable, Deque, List, Optional, Tuple

from .config import CodexSettings, load_settings
from .runtime import run_request
from .types import CancelToken, CodexError, CodexRequest, CodexResult, Submission


def _supports_process_start_callback(runner: Callable) -> bool:
    """Detect the optional fourth runner argument without retrying calls."""

    try:
        parameters = inspect.signature(runner).parameters.values()
    except (TypeError, ValueError):
        return False
    positional = [
        parameter
        for parameter in parameters
        if parameter.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    return any(
        parameter.kind == inspect.Parameter.VAR_POSITIONAL
        for parameter in parameters
    ) or len(positional) >= 4


@dataclass
class _QueueEntry:
    request: CodexRequest
    on_text: Callable[[str], None]
    future: Future
    submitted_at: float
    timeout_timer: Optional[threading.Timer] = None


class CodexScheduler:
    """A single worker that owns the only active Codex execution slot."""

    def __init__(
        self,
        settings: CodexSettings,
        runner: Callable[[CodexRequest, CodexSettings, Callable[[str], None]], CodexResult],
        monotonic: Callable[[], float] = time.monotonic,
    ):
        self.settings = settings
        self.runner = runner
        self._runner_supports_process_start = _supports_process_start_callback(runner)
        self._monotonic = monotonic
        self._condition = threading.Condition()
        self._queue: Deque[_QueueEntry] = deque()
        self._running = False
        self._active: Optional[_QueueEntry] = None
        self._last_start: Optional[float] = None
        self._closed = False
        self._cleanup_blocked = False
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="gpt-academic-codex-scheduler",
            daemon=True,
        )
        self._worker.start()

    @staticmethod
    def _cancel_error() -> CodexError:
        return CodexError("cancelled", "Codex CLI 请求已取消。")

    @staticmethod
    def _closed_error() -> CodexError:
        return CodexError("service_closed", "Codex CLI 后端已关闭。")

    @staticmethod
    def _queue_full_error() -> CodexError:
        return CodexError("queue_full", "Codex CLI 等待队列已满。")

    @staticmethod
    def _queue_timeout_error() -> CodexError:
        return CodexError("queue_timeout", "Codex CLI 排队等待超时。")

    @staticmethod
    def _cleanup_error() -> CodexError:
        return CodexError("cleanup_failed", "Codex CLI 资源清理失败，已暂停后续请求。")

    @staticmethod
    def _resolve(entry: _QueueEntry, result=None, error: Optional[BaseException] = None):
        if entry.timeout_timer is not None:
            entry.timeout_timer.cancel()
        try:
            if error is not None:
                entry.future.set_exception(error)
            else:
                entry.future.set_result(result)
        except InvalidStateError:
            # Queue timeout, cancellation, close, and worker completion may
            # race.  The Future is the single terminal-state authority.
            pass

    def _expire_waiters_locked(self, now: float) -> List[Tuple[_QueueEntry, CodexError]]:
        expired = []
        retained = deque()
        while self._queue:
            entry = self._queue.popleft()
            if entry.request.cancel.is_cancelled():
                expired.append((entry, self._cancel_error()))
            elif now - entry.submitted_at >= self.settings.queue_timeout:
                expired.append((entry, self._queue_timeout_error()))
            else:
                retained.append(entry)
        self._queue = retained
        return expired

    def submit(
        self, request: CodexRequest, on_text: Callable[[str], None]
    ) -> Submission:
        if not isinstance(request, CodexRequest):
            raise TypeError("request must be a CodexRequest")
        if not callable(on_text):
            raise TypeError("on_text must be callable")
        future = Future()
        expired = []
        rejected = None
        with self._condition:
            expired = self._expire_waiters_locked(self._monotonic())
            if self._closed:
                rejected = self._closed_error()
            elif self._cleanup_blocked:
                rejected = self._cleanup_error()
            elif len(self._queue) >= self.settings.queue_capacity:
                rejected = self._queue_full_error()
            if rejected is not None:
                entry = None
            else:
                entry = _QueueEntry(
                    request=request,
                    on_text=on_text,
                    future=future,
                    submitted_at=self._monotonic(),
                )
                self._queue.append(entry)
                self._condition.notify_all()
        for expired_entry, error in expired:
            self._resolve(expired_entry, error=error)
        if rejected is not None:
            raise rejected
        assert entry is not None
        # Register outside the scheduler lock.  If the caller cancelled just
        # before registration, CancelToken invokes this callback immediately.
        request.cancel.add_callback(lambda: self._cancel_queued(entry))
        entry.timeout_timer = threading.Timer(
            self.settings.queue_timeout, self._timeout_queued, args=(entry,)
        )
        entry.timeout_timer.daemon = True
        entry.timeout_timer.start()
        return Submission(future=future, cancel=request.cancel)

    def _cancel_queued(self, entry: _QueueEntry) -> None:
        removed = False
        with self._condition:
            for queued_entry in list(self._queue):
                if queued_entry is entry:
                    self._queue.remove(queued_entry)
                    removed = True
                    break
            if removed:
                self._condition.notify_all()
        if removed:
            self._resolve(entry, error=self._cancel_error())

    def _timeout_queued(self, entry: _QueueEntry) -> None:
        removed = False
        with self._condition:
            for queued_entry in list(self._queue):
                if queued_entry is entry:
                    self._queue.remove(queued_entry)
                    removed = True
                    break
            if removed:
                self._condition.notify_all()
        if removed:
            self._resolve(entry, error=self._queue_timeout_error())

    def _worker_loop(self):
        while True:
            completions: List[Tuple[_QueueEntry, object, Optional[BaseException]]] = []
            entry = None
            with self._condition:
                now = self._monotonic()
                for expired_entry, error in self._expire_waiters_locked(now):
                    completions.append((expired_entry, None, error))

                if self._cleanup_blocked:
                    while self._queue:
                        blocked_entry = self._queue.popleft()
                        completions.append((blocked_entry, None, self._cleanup_error()))
                    should_exit = self._closed
                    wait_for = None
                elif self._closed and not self._running and not self._queue:
                    should_exit = True
                    wait_for = None
                elif self._running or not self._queue:
                    should_exit = False
                    wait_for = None
                else:
                    candidate = self._queue[0]
                    wait_for = None
                    if self._last_start is not None:
                        interval_wait = (
                            self._last_start + self.settings.min_start_interval - now
                        )
                        if interval_wait > 0:
                            wait_for = interval_wait
                    if wait_for is not None and wait_for > 0:
                        should_exit = False
                    else:
                        entry = self._queue.popleft()
                        self._running = True
                        self._active = entry
                        should_exit = False

                if entry is None and not should_exit:
                    # A bounded wait also lets an injected clock or a late
                    # cancellation be noticed when no new submission arrives.
                    self._condition.wait(timeout=wait_for if wait_for and wait_for > 0 else 0.05)

            for completed_entry, result, error in completions:
                self._resolve(completed_entry, result=result, error=error)
            if should_exit:
                return
            if entry is None:
                continue

            # Close/cancel can race with the hand-off from the queue to the
            # runner.  Check under the scheduler lock, but never wait there.
            with self._condition:
                now = self._monotonic()
                timed_out = now - entry.submitted_at >= self.settings.queue_timeout
                if self._closed or entry.request.cancel.is_cancelled():
                    self._running = False
                    self._active = None
                    handoff_error = self._cancel_error()
                elif timed_out:
                    self._running = False
                    self._active = None
                    handoff_error = self._queue_timeout_error()
                else:
                    handoff_error = None
            if handoff_error is not None:
                self._resolve(entry, error=handoff_error)
                continue

            result = None
            error = None

            def on_process_start():
                # The runner invokes this only after its real Popen succeeds.
                # A slow capability probe therefore cannot consume the
                # scheduler's start interval early.
                with self._condition:
                    self._last_start = self._monotonic()

            try:
                if self._runner_supports_process_start:
                    result = self.runner(
                        entry.request,
                        self.settings,
                        entry.on_text,
                        on_process_start,
                    )
                else:
                    # Keep injected legacy test runners and third-party local
                    # adapters callable while production run_request uses the
                    # callback-aware signature.
                    result = self.runner(entry.request, self.settings, entry.on_text)
                if not isinstance(result, CodexResult):
                    error = CodexError("process_failed", "Codex CLI 返回了无效结果。")
            except CodexError as caught:
                error = caught
            except BaseException:
                # Do not expose arbitrary runner tracebacks, which may contain
                # prompt or stderr data.
                error = CodexError("process_failed", "Codex CLI 请求处理失败。")

            with self._condition:
                self._running = False
                self._active = None
                if isinstance(error, CodexError) and error.code == "cleanup_failed":
                    self._cleanup_blocked = True
                if self._cleanup_blocked:
                    while self._queue:
                        blocked_entry = self._queue.popleft()
                        # Apply after leaving the lock below.
                        completions.append((blocked_entry, None, self._cleanup_error()))
                self._condition.notify_all()
            self._resolve(entry, result=result, error=error)
            for completed_entry, completed_result, completed_error in completions:
                self._resolve(
                    completed_entry,
                    result=completed_result,
                    error=completed_error,
                )

    def close(self) -> None:
        completions = []
        active = None
        with self._condition:
            if self._closed:
                return
            self._closed = True
            while self._queue:
                entry = self._queue.popleft()
                completions.append((entry, self._cancel_error()))
            active = self._active
            self._condition.notify_all()
        for entry, error in completions:
            self._resolve(entry, error=error)
        if active is not None:
            # Cancel callbacks acquire the scheduler condition, so invoke the
            # token outside that condition to avoid lock inversion.
            active.request.cancel.cancel()
        if threading.current_thread() is not self._worker:
            self._worker.join(timeout=min(max(self.settings.TERMINATION_GRACE_PERIOD + 1.0, 1.0), 5.0))


_scheduler_lock = threading.Lock()
_scheduler: Optional[CodexScheduler] = None


def get_scheduler() -> CodexScheduler:
    """Return the process-wide scheduler, constructing it lazily."""

    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            settings = load_settings()
            _scheduler = CodexScheduler(settings, run_request, time.monotonic)
        return _scheduler


def reset_scheduler_for_tests() -> None:
    """Close and forget the singleton; intended for isolated test processes."""

    global _scheduler
    with _scheduler_lock:
        scheduler = _scheduler
        _scheduler = None
    if scheduler is not None:
        scheduler.close()
