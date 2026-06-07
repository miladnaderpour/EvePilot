"""Shared public result schemas for EvePilot interfaces."""

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from evepilot.core.version import APP_NAME, APP_VERSION

T = TypeVar("T")


class ServiceError(BaseModel):
    """Structured error payload for CLI/API result wrappers."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    status_code: int | None = None


class ServiceMeta(BaseModel):
    """Metadata shared by first-layer CLI/API results."""

    service: str = APP_NAME
    version: str = APP_VERSION
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_seconds: float
    request_id: str | None = None


class ServiceResult(BaseModel, Generic[T]):
    """Consistent top-level result wrapper for EvePilot interfaces."""

    ok: bool
    code: str
    data: T | None = None
    error: ServiceError | None = None
    meta: ServiceMeta
