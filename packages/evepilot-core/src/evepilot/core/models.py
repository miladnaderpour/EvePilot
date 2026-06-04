"""Shared domain models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConsoleEndpoint:
    """Parsed device console endpoint."""

    protocol: str
    host: str
    port: int


@dataclass(frozen=True, slots=True)
class LogTarget:
    """Logging target configuration."""

    name: str
    output: str = "stdout"
    level: str = "INFO"
    format: str = "json"
    file_path: str | None = None
