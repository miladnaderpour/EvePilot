"""CLI JSON output helpers."""

from __future__ import annotations

import json
from collections.abc import Callable
from enum import StrEnum
from time import monotonic
from typing import TypeVar

import typer

from evepilot.core.exceptions import EvePilotError
from evepilot.core.schemas import ServiceError, ServiceMeta, ServiceResult

JsonResult = TypeVar("JsonResult")


class OutputFormat(StrEnum):
    """Supported CLI output formats."""

    JSON = "json"
    TEXT = "text"


def _echo_json(payload: object, *, err: bool = False) -> None:
    """Print a JSON payload to stdout."""

    typer.echo(json.dumps(payload, indent=2), err=err)


def run_json_command(
    *,
    code: str,
    command: Callable[[], JsonResult],
    output_format: OutputFormat | str = OutputFormat.JSON,
) -> None:
    """Run a command and print a service result in the requested format."""

    started_at = monotonic()
    selected_format = OutputFormat(output_format)
    try:
        data = command()
        payload = _success_payload(code=code, data=data, started_at=started_at)
        _echo_result(payload, output_format=selected_format)
    except EvePilotError as exc:
        payload = _failure_payload(error=exc, started_at=started_at)
        _echo_result(payload, output_format=selected_format, err=True)
        raise typer.Exit(code=1) from exc


def _echo_result(
    payload: dict[str, object],
    *,
    output_format: OutputFormat,
    err: bool = False,
) -> None:
    if output_format == OutputFormat.JSON:
        _echo_json(payload, err=err)
        return

    typer.echo(_text_result(payload), err=err)


def _success_payload(
    *,
    code: str,
    data: JsonResult,
    started_at: float,
) -> dict[str, object]:
    result = ServiceResult[JsonResult](
        ok=True,
        code=code,
        data=data,
        meta=ServiceMeta(duration_seconds=_duration_seconds(started_at)),
    )
    return result.model_dump(mode="json")


def _failure_payload(
    *,
    error: EvePilotError,
    started_at: float,
) -> dict[str, object]:
    result = ServiceResult[object](
        ok=False,
        code=error.code,
        error=ServiceError(
            code=error.code,
            message=error.message,
            details=error.details,
            status_code=error.status_code,
        ),
        meta=ServiceMeta(duration_seconds=_duration_seconds(started_at)),
    )
    return result.model_dump(mode="json")


def _text_result(payload: dict[str, object]) -> str:
    ok = bool(payload.get("ok"))
    code = str(payload.get("code", ""))
    if not ok:
        error = payload.get("error")
        if isinstance(error, dict):
            message = str(error.get("message", ""))
            details = error.get("details")
            lines = [f"ERROR {code}", message]
            if details:
                lines.append(json.dumps(details, indent=2))
            return "\n".join(line for line in lines if line)
        return f"ERROR {code}"

    data = payload.get("data")
    if data is None:
        return f"OK {code}"
    return "\n".join([f"OK {code}", json.dumps(data, indent=2)])


def _duration_seconds(started_at: float) -> float:
    return round(monotonic() - started_at, 3)
