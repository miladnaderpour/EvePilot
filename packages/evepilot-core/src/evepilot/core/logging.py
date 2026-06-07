"""Logging helpers for EvePilot."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evepilot.core.config import Settings
from evepilot.core.exceptions import EvePilotConfigError
from evepilot.core.models import LogTarget

SENSITIVE_KEYS = {"password", "token", "cookie", "authorization"}
SUPPORTED_OUTPUTS = {"stdout", "file"}
SUPPORTED_FORMATS = {"json", "text"}


class JsonLogFormatter(logging.Formatter):
    """Small JSON formatter with sensitive field redaction."""

    def __init__(self) -> None:
        super().__init__()
        self.timezone = UTC

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(self.timezone).isoformat(),
            "service": "EvePilot",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key.startswith("_") or key in _standard_record_keys():
                continue
            payload[key] = _redact(key, value)

        return json.dumps(payload, sort_keys=True)


class TextLogFormatter(logging.Formatter):
    """Text formatter with UTC timestamps."""

    def __init__(self) -> None:
        super().__init__()
        self.timezone = UTC

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(self.timezone).isoformat()
        base_message = f"{timestamp} {record.levelname} {record.name} {record.getMessage()}"
        extras = {
            key: _redact(key, value)
            for key, value in record.__dict__.items()
            if not key.startswith("_") and key not in _standard_record_keys()
        }
        if not extras:
            return base_message
        return f"{base_message} {json.dumps(extras, sort_keys=True)}"


def setup_logging(settings: Settings | None = None) -> None:
    """Configure root logging for EvePilot."""

    targets = _build_log_targets(settings)
    handlers = [_build_handler(target) for target in targets]
    root_level = min(handler.level for handler in handlers)

    root = logging.getLogger()
    root.handlers.clear()
    for handler in handlers:
        root.addHandler(handler)
    root.setLevel(root_level)


def parse_log_targets(log_targets_json: str) -> list[LogTarget]:
    """Parse JSON logging target configuration."""

    try:
        raw_targets = json.loads(log_targets_json)
    except json.JSONDecodeError as exc:
        raise EvePilotConfigError(
            code="config.invalid_log_targets",
            message="EVEPILOT_LOG_TARGETS_JSON must be valid JSON.",
        ) from exc

    if not isinstance(raw_targets, list):
        raise EvePilotConfigError(
            code="config.invalid_log_targets",
            message="EVEPILOT_LOG_TARGETS_JSON must contain a list of targets.",
        )

    targets: list[LogTarget] = []
    for raw_target in raw_targets:
        if not isinstance(raw_target, dict):
            raise EvePilotConfigError(
                code="config.invalid_log_targets",
                message="Each logging target must be an object.",
            )
        targets.append(LogTarget(**raw_target))

    return targets


def _build_log_targets(settings: Settings | None) -> list[LogTarget]:
    if settings is None:
        return [LogTarget(name="default")]

    if settings.log_targets_json:
        return parse_log_targets(settings.log_targets_json)

    return [
        LogTarget(
            name="default",
            output=settings.log_output,
            level=settings.log_level,
            format=settings.log_format,
            file_path=settings.log_file_path,
        )
    ]


def _build_handler(target: LogTarget) -> logging.Handler:
    output = target.output.lower()
    log_format = target.format.lower()

    if output not in SUPPORTED_OUTPUTS:
        raise EvePilotConfigError(
            code="config.unsupported_log_output",
            message="Logging target output is not supported.",
            details={"name": target.name, "output": target.output},
        )

    if log_format == "json":
        formatter: logging.Formatter = JsonLogFormatter()
    elif log_format == "text":
        formatter = TextLogFormatter()
    else:
        raise EvePilotConfigError(
            code="config.unsupported_log_format",
            message="Logging target format is not supported.",
            details={"name": target.name, "format": target.format},
        )

    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    else:
        if not target.file_path:
            raise EvePilotConfigError(
                code="config.missing_value",
                message="File logging target requires file_path.",
                details={"name": target.name},
            )
        file_path = Path(target.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(file_path, encoding="utf-8")

    handler.setLevel(target.level.upper())
    handler.setFormatter(formatter)
    return handler


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger under the EvePilot namespace."""

    return logging.getLogger(name or "evepilot")


def _redact(key: str, value: object) -> object:
    if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
        return "***REDACTED***"
    return value


def _standard_record_keys() -> set[str]:
    return {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "taskName",
        "processName",
        "process",
        "message",
    }
