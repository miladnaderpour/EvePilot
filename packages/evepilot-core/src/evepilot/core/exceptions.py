"""Project-wide base exception types."""

from typing import Any


class EvePilotError(Exception):
    """Base error for EvePilot failures."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, object] | None = None,
        status_code: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for CLI/API output."""

        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
        if self.status_code is not None:
            payload["status_code"] = self.status_code
        return payload


class EvePilotConfigError(EvePilotError):
    """Core configuration error."""


class EvePilotInvariantError(EvePilotError):
    """Core invariant error."""
