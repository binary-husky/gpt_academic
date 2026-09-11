"""Configuration loading and validation for the Codex CLI backend."""

import math
import os
from dataclasses import dataclass
from typing import ClassVar, Mapping

from shared_utils.config_loader import get_conf

ACTIVE_PROCESS_LIMIT = 1
AUTO_RETRY_COUNT = 0
TERMINATION_GRACE_PERIOD = 2.0

DEFAULTS = {
    "CODEX_CLI_MODEL": "",
    "CODEX_CLI_QUEUE_CAPACITY": 32,
    "CODEX_CLI_MIN_START_INTERVAL": 3.0,
    "CODEX_CLI_QUEUE_TIMEOUT": 600.0,
    "CODEX_CLI_REQUEST_TIMEOUT": 600.0,
    "CODEX_CLI_MAX_INPUT_BYTES": 262144,
    "CODEX_CLI_MAX_OUTPUT_BYTES": 8388608,
}


@dataclass(frozen=True)
class CodexSettings:
    cli_path: str
    cli_model: str
    queue_capacity: int
    min_start_interval: float
    queue_timeout: float
    request_timeout: float
    max_input_bytes: int
    max_output_bytes: int

    ACTIVE_PROCESS_LIMIT: ClassVar[int] = ACTIVE_PROCESS_LIMIT
    AUTO_RETRY_COUNT: ClassVar[int] = AUTO_RETRY_COUNT
    TERMINATION_GRACE_PERIOD: ClassVar[float] = TERMINATION_GRACE_PERIOD

    @property
    def active_process_limit(self) -> int:
        return self.ACTIVE_PROCESS_LIMIT

    @property
    def auto_retry_count(self) -> int:
        return self.AUTO_RETRY_COUNT

    @property
    def termination_grace_period(self) -> float:
        return self.TERMINATION_GRACE_PERIOD


def _config_error(message: str) -> "CodexError":
    from .types import CodexError

    return CodexError("config_invalid", message)


def _value(values: Mapping[str, object], upper_name: str, field_name: str):
    if upper_name in values:
        return values[upper_name]
    if field_name in values:
        return values[field_name]
    if upper_name == "CODEX_CLI_PATH":
        return ""
    return DEFAULTS[upper_name]


def _require_string(value: object, field: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise _config_error("Codex 配置项类型错误。")
    result = value.strip()
    if not result and not allow_empty:
        raise _config_error("选择 Codex CLI 时必须配置可执行文件路径。")
    return result


def _require_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _config_error("Codex 数值配置项类型错误。")
    return value


def _require_finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _config_error("Codex 数值配置项类型错误。")
    result = float(value)
    if not math.isfinite(result):
        raise _config_error("Codex 数值配置项必须是有限数值。")
    return result


def validate_settings(values: Mapping[str, object]) -> CodexSettings:
    """Validate a full Codex configuration and return normalized settings."""

    if not isinstance(values, Mapping):
        raise _config_error("Codex 配置必须是映射。")

    cli_path_value = _require_string(
        _value(values, "CODEX_CLI_PATH", "cli_path"), "CODEX_CLI_PATH"
    )
    cli_path = os.path.abspath(os.path.expanduser(cli_path_value))
    if not os.path.isfile(cli_path) or not os.access(cli_path, os.X_OK):
        raise _config_error("配置的 Codex CLI 路径不可执行。")

    cli_model = _require_string(
        _value(values, "CODEX_CLI_MODEL", "cli_model"), "CODEX_CLI_MODEL", allow_empty=True
    )

    queue_capacity = _require_int(
        _value(values, "CODEX_CLI_QUEUE_CAPACITY", "queue_capacity")
    )
    if queue_capacity < 1 or queue_capacity > 256:
        raise _config_error("Codex 等待队列容量必须在 1 到 256 之间。")

    min_start_interval = _require_finite_float(
        _value(values, "CODEX_CLI_MIN_START_INTERVAL", "min_start_interval")
    )
    if min_start_interval < 3.0:
        raise _config_error("Codex 启动间隔不能小于 3 秒。")

    queue_timeout = _require_finite_float(
        _value(values, "CODEX_CLI_QUEUE_TIMEOUT", "queue_timeout")
    )
    request_timeout = _require_finite_float(
        _value(values, "CODEX_CLI_REQUEST_TIMEOUT", "request_timeout")
    )
    if queue_timeout <= 0 or request_timeout <= 0:
        raise _config_error("Codex 超时时间必须为正数。")

    max_input_bytes = _require_int(
        _value(values, "CODEX_CLI_MAX_INPUT_BYTES", "max_input_bytes")
    )
    max_output_bytes = _require_int(
        _value(values, "CODEX_CLI_MAX_OUTPUT_BYTES", "max_output_bytes")
    )
    if max_input_bytes <= 0 or max_output_bytes <= 0:
        raise _config_error("Codex 输入输出上限必须为正整数。")

    return CodexSettings(
        cli_path=cli_path,
        cli_model=cli_model,
        queue_capacity=queue_capacity,
        min_start_interval=min_start_interval,
        queue_timeout=queue_timeout,
        request_timeout=request_timeout,
        max_input_bytes=max_input_bytes,
        max_output_bytes=max_output_bytes,
    )


def load_settings() -> CodexSettings:
    """Load Codex settings through GPT Academic's normal config precedence."""

    names = (
        "CODEX_CLI_PATH",
        "CODEX_CLI_MODEL",
        "CODEX_CLI_QUEUE_CAPACITY",
        "CODEX_CLI_MIN_START_INTERVAL",
        "CODEX_CLI_QUEUE_TIMEOUT",
        "CODEX_CLI_REQUEST_TIMEOUT",
        "CODEX_CLI_MAX_INPUT_BYTES",
        "CODEX_CLI_MAX_OUTPUT_BYTES",
    )
    raw_values = get_conf(*names)
    return validate_settings(dict(zip(names, raw_values)))
