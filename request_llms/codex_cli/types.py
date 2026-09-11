"""Small shared types for the Codex CLI backend."""

from concurrent.futures import Future
from dataclasses import dataclass
from threading import Event, Lock
from typing import Callable, List


class CodexError(RuntimeError):
    """A safe, structured error exposed by the Codex backend.

    ``public_message`` is deliberately the only text intended for the UI.  In
    particular, command lines, prompts, authentication data, and raw stderr
    are never attached to this exception.
    """

    def __init__(self, code: str, public_message: str, retryable: bool = False):
        self.code = code
        self.public_message = public_message
        self.retryable = bool(retryable)
        super().__init__(public_message)


class CancelToken:
    """Thread-safe cancellation signal shared by a queued request and runner."""

    def __init__(self):
        self._event = Event()
        self._lock = Lock()
        self._callbacks: List[Callable[[], None]] = []

    def cancel(self) -> None:
        with self._lock:
            if self._event.is_set():
                return
            self._event.set()
            callbacks = list(self._callbacks)
            self._callbacks.clear()
        for callback in callbacks:
            try:
                callback()
            except Exception:
                # Cancellation must not be made unreliable by an observer.
                pass

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def add_callback(self, callback: Callable[[], None]) -> None:
        """Register an internal observer, invoking it if already cancelled."""

        with self._lock:
            if self._event.is_set():
                invoke_now = True
            else:
                self._callbacks.append(callback)
                invoke_now = False
        if invoke_now:
            callback()


@dataclass
class CodexRequest:
    request_id: str
    prompt: str
    cancel: CancelToken


@dataclass
class CodexResult:
    text: str


@dataclass
class Submission:
    future: Future
    cancel: CancelToken
