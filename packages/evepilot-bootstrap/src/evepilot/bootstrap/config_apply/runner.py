"""Rendered config line application."""

from time import monotonic

from evepilot.bootstrap.config_apply.models import (
    ConfigApplyResult,
    ConfigCommandResult,
    ConfigLine,
)
from evepilot.bootstrap.transport.console import AsyncConsoleSession
from evepilot.core.logging import get_logger

DEFAULT_LINE_ENDING = "\r\n"
DEFAULT_READ_TIMEOUT_SECONDS = 3.0
DEFAULT_OUTPUT_SAMPLE_LIMIT = 500
log = get_logger(__name__)


async def apply_config_lines(
    *,
    lines: list[ConfigLine],
    console: AsyncConsoleSession,
    line_ending: str = DEFAULT_LINE_ENDING,
    read_timeout_seconds: float = DEFAULT_READ_TIMEOUT_SECONDS,
) -> ConfigApplyResult:
    """Apply rendered config lines to an already-prepared console session."""

    started_at = monotonic()
    command_results: list[ConfigCommandResult] = []
    log.info(
        "bootstrap_config_apply_started",
        extra={
            "commands_total": len(lines),
            "read_timeout_seconds": read_timeout_seconds,
        },
    )

    for line in lines:
        log.debug(
            "bootstrap_config_apply_command_started",
            extra={"line_number": line.number, "command_length": len(line.text)},
        )
        await console.send(f"{line.text}{line_ending}")
        output = await console.read(read_timeout_seconds)
        command_results.append(
            ConfigCommandResult(
                line_number=line.number,
                command=line.text,
                output_sample=_sample_output(output),
            )
        )
        log.debug(
            "bootstrap_config_apply_command_completed",
            extra={
                "line_number": line.number,
                "output_length": len(output),
            },
        )

    duration_seconds = monotonic() - started_at
    result = ConfigApplyResult(
        commands_total=len(lines),
        commands_sent=len(command_results),
        command_results=command_results,
        apply_duration_seconds=round(duration_seconds, 3),
    )
    log.info(
        "bootstrap_config_apply_completed",
        extra={
            "commands_total": result.commands_total,
            "commands_sent": result.commands_sent,
            "apply_duration_seconds": result.apply_duration_seconds,
        },
    )
    return result


def _sample_output(output: str) -> str:
    if len(output) <= DEFAULT_OUTPUT_SAMPLE_LIMIT:
        return output
    return output[-DEFAULT_OUTPUT_SAMPLE_LIMIT:]
