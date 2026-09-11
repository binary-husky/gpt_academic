import math
import os

import pytest

from request_llms.codex_cli.config import load_settings, validate_settings
from request_llms.codex_cli.types import CodexError


def _make_cli(tmp_path, name="codex cli"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / name
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def _values(path, **overrides):
    values = {
        "CODEX_CLI_PATH": str(path),
        "CODEX_CLI_MODEL": "",
        "CODEX_CLI_QUEUE_CAPACITY": 32,
        "CODEX_CLI_MIN_START_INTERVAL": 3.0,
        "CODEX_CLI_QUEUE_TIMEOUT": 600.0,
        "CODEX_CLI_REQUEST_TIMEOUT": 600.0,
        "CODEX_CLI_MAX_INPUT_BYTES": 262144,
        "CODEX_CLI_MAX_OUTPUT_BYTES": 8388608,
    }
    values.update(overrides)
    return values


def test_defaults_match_design(tmp_path):
    settings = validate_settings(_values(_make_cli(tmp_path)))

    assert settings.queue_capacity == 32
    assert settings.min_start_interval == 3.0
    assert settings.queue_timeout == 600.0
    assert settings.request_timeout == 600.0
    assert settings.max_input_bytes == 262144
    assert settings.max_output_bytes == 8388608
    assert settings.ACTIVE_PROCESS_LIMIT == 1
    assert settings.AUTO_RETRY_COUNT == 0
    assert settings.TERMINATION_GRACE_PERIOD == 2.0


def test_path_with_spaces_is_accepted(tmp_path):
    path = _make_cli(tmp_path / "directory with spaces")
    settings = validate_settings(_values(path))
    assert settings.cli_path == os.path.abspath(str(path))


def test_relative_path_is_accepted_when_executable(tmp_path, monkeypatch):
    path = _make_cli(tmp_path, "relative-codex")
    monkeypatch.chdir(tmp_path)
    settings = validate_settings(_values("relative-codex"))
    assert settings.cli_path == os.path.abspath("relative-codex")


def test_missing_path_is_reported_when_codex_is_selected(tmp_path):
    with pytest.raises(CodexError) as caught:
        validate_settings(_values(tmp_path / "missing", CODEX_CLI_PATH=""))
    assert caught.value.code == "config_invalid"
    assert caught.value.retryable is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("CODEX_CLI_QUEUE_CAPACITY", 0),
        ("CODEX_CLI_QUEUE_CAPACITY", -1),
        ("CODEX_CLI_QUEUE_CAPACITY", 257),
        ("CODEX_CLI_MIN_START_INTERVAL", 0),
        ("CODEX_CLI_MIN_START_INTERVAL", -1),
        ("CODEX_CLI_MIN_START_INTERVAL", 2.99),
        ("CODEX_CLI_MIN_START_INTERVAL", math.nan),
        ("CODEX_CLI_MIN_START_INTERVAL", math.inf),
        ("CODEX_CLI_QUEUE_TIMEOUT", 0),
        ("CODEX_CLI_QUEUE_TIMEOUT", -1),
        ("CODEX_CLI_QUEUE_TIMEOUT", math.nan),
        ("CODEX_CLI_QUEUE_TIMEOUT", math.inf),
        ("CODEX_CLI_REQUEST_TIMEOUT", 0),
        ("CODEX_CLI_REQUEST_TIMEOUT", -1),
        ("CODEX_CLI_REQUEST_TIMEOUT", math.nan),
        ("CODEX_CLI_REQUEST_TIMEOUT", math.inf),
        ("CODEX_CLI_MAX_INPUT_BYTES", 0),
        ("CODEX_CLI_MAX_INPUT_BYTES", -1),
        ("CODEX_CLI_MAX_OUTPUT_BYTES", 0),
        ("CODEX_CLI_MAX_OUTPUT_BYTES", -1),
    ],
)
def test_invalid_numbers_rejected(tmp_path, field, value):
    with pytest.raises(CodexError) as caught:
        validate_settings(_values(_make_cli(tmp_path), **{field: value}))
    assert caught.value.code == "config_invalid"


@pytest.mark.parametrize(
    "field,value",
    [
        ("CODEX_CLI_QUEUE_CAPACITY", True),
        ("CODEX_CLI_QUEUE_TIMEOUT", "600"),
        ("CODEX_CLI_MAX_OUTPUT_BYTES", 1.5),
        ("CODEX_CLI_MODEL", None),
    ],
)
def test_invalid_types_rejected(tmp_path, field, value):
    with pytest.raises(CodexError) as caught:
        validate_settings(_values(_make_cli(tmp_path), **{field: value}))
    assert caught.value.code == "config_invalid"


@pytest.mark.parametrize("path_kind", ["directory", "not_found", "not_executable"])
def test_invalid_cli_path_rejected(tmp_path, path_kind):
    if path_kind == "directory":
        path = tmp_path / "a-directory"
        path.mkdir()
    elif path_kind == "not_found":
        path = tmp_path / "missing"
    else:
        path = tmp_path / "not-executable"
        path.write_text("#!/bin/sh\n", encoding="utf-8")
        path.chmod(0o644)

    with pytest.raises(CodexError) as caught:
        validate_settings(_values(path))
    assert caught.value.code == "config_invalid"


def test_environment_override_uses_existing_loader(tmp_path, monkeypatch):
    path = _make_cli(tmp_path)
    monkeypatch.setenv("GPT_ACADEMIC_CODEX_CLI_PATH", str(path))
    monkeypatch.setenv("GPT_ACADEMIC_CODEX_CLI_QUEUE_CAPACITY", "7")

    from shared_utils.config_loader import get_conf, read_single_conf_with_lru_cache

    get_conf.cache_clear()
    read_single_conf_with_lru_cache.cache_clear()
    try:
        settings = load_settings()
    finally:
        get_conf.cache_clear()
        read_single_conf_with_lru_cache.cache_clear()

    assert settings.cli_path == os.path.abspath(str(path))
    assert settings.queue_capacity == 7


def test_codex_error_is_non_retryable():
    error = CodexError("protocol_error", "协议错误")
    assert error.code == "protocol_error"
    assert error.public_message == "协议错误"
    assert error.retryable is False
