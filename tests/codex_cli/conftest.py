import json
import os
import time
from pathlib import Path

import pytest

from request_llms.codex_cli.config import CodexSettings
from request_llms.codex_cli.types import CancelToken, CodexRequest


@pytest.fixture
def fake_cli_path():
    path = Path(__file__).with_name("fake_codex_cli.py")
    return path


@pytest.fixture
def fake_settings(fake_cli_path):
    return CodexSettings(
        cli_path=str(fake_cli_path),
        cli_model="fake-model",
        queue_capacity=32,
        min_start_interval=3.0,
        queue_timeout=2.0,
        request_timeout=2.0,
        max_input_bytes=262144,
        max_output_bytes=8388608,
    )


def make_request(prompt="hello"):
    return CodexRequest(request_id="test-request", prompt=prompt, cancel=CancelToken())


def wait_for_json(path, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if Path(path).exists():
            try:
                return json.loads(Path(path).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
        time.sleep(0.01)
    raise AssertionError("timed out waiting for fake CLI metadata")


def pid_exists(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, TypeError, ValueError):
        return False
    return True
