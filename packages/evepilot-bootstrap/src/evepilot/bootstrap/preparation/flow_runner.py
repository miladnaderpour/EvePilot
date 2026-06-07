"""Bootstrap flow runner."""

from __future__ import annotations

import re
from time import monotonic

from evepilot.bootstrap.errors import bootstrap_flow_run_error
from evepilot.bootstrap.preparation.console_buffer import ConsoleBuffer
from evepilot.bootstrap.preparation.flow_matcher import detect_flow_state
from evepilot.bootstrap.preparation.models import (
    FlowAction,
    FlowDefinition,
    FlowNext,
    FlowRunResult,
    FlowStateMatch,
    FlowStep,
)
from evepilot.bootstrap.preparation.variables import resolve_flow_variables
from evepilot.bootstrap.transport.console import AsyncConsoleSession
from evepilot.core.logging import get_logger

DEFAULT_MAX_STEPS = 50
DEFAULT_READ_INTERVAL_SECONDS = 2.0
DEFAULT_STATE_DETECTION_TIMEOUT_SECONDS = 120.0
DEFAULT_NO_MATCH_WAKE_ATTEMPTS = 3
log = get_logger(__name__)


async def run_flow(
    flow: FlowDefinition,
    console: AsyncConsoleSession,
    *,
    variables: dict[str, str] | None = None,
    max_steps: int = DEFAULT_MAX_STEPS,
    detection_timeout_seconds: float = DEFAULT_STATE_DETECTION_TIMEOUT_SECONDS,
) -> FlowRunResult:
    """Run a bootstrap preparation flow against a console."""

    variable_values = variables if variables is not None else resolve_flow_variables(flow)
    actions: list[str] = []
    log.info(
        "bootstrap_flow_run_started",
        extra={
            "flow_name": flow.name,
            "version": flow.version,
            "max_steps": max_steps,
            "detection_timeout_seconds": detection_timeout_seconds,
            "state_count": len(flow.states),
            "step_count": len(flow.steps),
        },
    )
    buffer = await _wake_console(flow, console, actions)

    current_step: FlowStep | None = None
    current_match: FlowStateMatch | None = None

    for _ in range(max_steps):
        current_step, current_match, output = await _execute_current_step(
            flow=flow,
            console=console,
            step=current_step,
            match=current_match,
            buffer=buffer,
            variables=variable_values,
            actions=actions,
            detection_timeout_seconds=detection_timeout_seconds,
        )

        terminal_result = _terminal_result(
            flow=flow,
            step=current_step,
            match=current_match,
            actions=actions,
            output=buffer.recent_text(),
        )
        if terminal_result is not None:
            return terminal_result

        current_step = _next_step(flow, current_step)
        if current_step is None:
            current_match = None

    log.error(
        "bootstrap_flow_run_failed",
        extra={
            "flow_name": flow.name,
            "reason": "max_steps_exceeded",
            "max_steps": max_steps,
            "action_count": len(actions),
        },
    )
    raise bootstrap_flow_run_error(
        reason="max_steps_exceeded",
        details={"flow_name": flow.name, "max_steps": max_steps},
    )


async def _execute_current_step(
    *,
    flow: FlowDefinition,
    console: AsyncConsoleSession,
    step: FlowStep | None,
    match: FlowStateMatch | None,
    buffer: ConsoleBuffer,
    variables: dict[str, str],
    actions: list[str],
    detection_timeout_seconds: float,
) -> tuple[FlowStep, FlowStateMatch | None, str]:
    if step is None:
        match, output = await _wait_for_detectable_state(
            flow=flow,
            console=console,
            buffer=buffer,
            timeout_seconds=detection_timeout_seconds,
            actions=actions,
        )
        step = _step_for_state(flow, match.state_name)
    else:
        output = buffer.recent_text()

    log.debug(
        "bootstrap_flow_step_started",
        extra={
            "flow_name": flow.name,
            "step_name": step.name,
            "action": step.action.value,
            "state_name": match.state_name if match else None,
        },
    )
    chunk = await _execute_step(step, console, output, variables)
    if _should_clear_buffer_after_step(step):
        buffer.clear()
    buffer.append(chunk)
    output = buffer.recent_text()
    actions.append(step.name)
    log.debug(
        "bootstrap_flow_step_completed",
        extra={
            "flow_name": flow.name,
            "step_name": step.name,
            "next": step.next or "detect",
            "output_length": len(output),
        },
    )
    return step, match, output


def _terminal_result(
    *,
    flow: FlowDefinition,
    step: FlowStep,
    match: FlowStateMatch | None,
    actions: list[str],
    output: str,
) -> FlowRunResult | None:
    if _is_ready_step(step):
        return _ready_result(flow=flow, match=match, actions=actions, output=output)

    if _is_stop_step(step):
        return _stopped_result(flow=flow, match=match, actions=actions, output=output)

    return None


def _is_ready_step(step: FlowStep) -> bool:
    return step.action == FlowAction.READY or step.mark_ready


def _is_stop_step(step: FlowStep) -> bool:
    return step.next == FlowNext.STOP.value


def _should_clear_buffer_after_step(step: FlowStep) -> bool:
    return not _is_ready_step(step) and not _is_stop_step(step)


def _ready_result(
    *,
    flow: FlowDefinition,
    match: FlowStateMatch | None,
    actions: list[str],
    output: str,
) -> FlowRunResult:
    result = FlowRunResult(
        flow_name=flow.name,
        final_state=match.state_name if match else None,
        actions=actions,
        output_sample=_ready_output_sample(match, output),
        ready=True,
    )
    log.info(
        "bootstrap_flow_run_ready",
        extra={
            "flow_name": flow.name,
            "final_state": result.final_state,
            "action_count": len(actions),
        },
    )
    return result


def _ready_output_sample(match: FlowStateMatch | None, output: str) -> str:
    if match is not None:
        return match.matched_text.strip()
    return output.strip()


def _stopped_result(
    *,
    flow: FlowDefinition,
    match: FlowStateMatch | None,
    actions: list[str],
    output: str,
) -> FlowRunResult:
    result = FlowRunResult(
        flow_name=flow.name,
        final_state=match.state_name if match else None,
        actions=actions,
        output_sample=output,
        ready=False,
    )
    log.info(
        "bootstrap_flow_run_stopped",
        extra={
            "flow_name": flow.name,
            "final_state": result.final_state,
            "action_count": len(actions),
        },
    )
    return result


async def _wake_console(
    flow: FlowDefinition,
    console: AsyncConsoleSession,
    actions: list[str],
) -> ConsoleBuffer:
    buffer = ConsoleBuffer()
    output = await console.read(flow.startup.initial_read_seconds)
    buffer.append(output)
    log.debug(
        "bootstrap_flow_startup_read_completed",
        extra={
            "flow_name": flow.name,
            "timeout_seconds": flow.startup.initial_read_seconds,
            "output_length": len(output),
        },
    )

    if _has_detectable_state(buffer.recent_text(), flow) or not flow.startup.send_enter_if_no_output:
        return buffer
    if output:
        return buffer

    for attempt in range(1, flow.startup.wake_attempts + 1):
        log.info(
            "bootstrap_flow_console_wake_sent",
            extra={
                "flow_name": flow.name,
                "attempt": attempt,
                "max_attempts": flow.startup.wake_attempts,
            },
        )
        await console.send(flow.startup.wake_enter)
        actions.append(f"startup:wake_console:{attempt}")
        chunk = await console.read(flow.startup.read_after_wake_seconds)
        buffer.append(chunk)
        output = buffer.recent_text()
        log.debug(
            "bootstrap_flow_startup_wake_read_completed",
            extra={
                "flow_name": flow.name,
                "attempt": attempt,
                "timeout_seconds": flow.startup.read_after_wake_seconds,
                "output_length": len(output),
            },
        )
        if _has_detectable_state(output, flow):
            return buffer
        if chunk:
            return buffer

    if buffer.text():
        return buffer

    log.error(
        "bootstrap_flow_console_wake_failed",
        extra={
            "flow_name": flow.name,
            "reason": "no_output_after_wake_attempts",
            "attempts": flow.startup.wake_attempts,
        },
    )
    raise bootstrap_flow_run_error(
        reason="console_wake_failed",
        details={"flow_name": flow.name, "attempts": flow.startup.wake_attempts},
    )


def _has_detectable_state(output: str, flow: FlowDefinition) -> bool:
    return detect_flow_state(output, flow) is not None


async def _wait_for_detectable_state(
    *,
    flow: FlowDefinition,
    console: AsyncConsoleSession,
    buffer: ConsoleBuffer,
    timeout_seconds: float,
    actions: list[str],
    read_interval_seconds: float = DEFAULT_READ_INTERVAL_SECONDS,
    no_match_wake_attempts: int = DEFAULT_NO_MATCH_WAKE_ATTEMPTS,
) -> tuple[FlowStateMatch, str]:
    deadline = monotonic() + timeout_seconds
    no_output_attempts = 0

    while True:
        output = buffer.recent_text()
        match = detect_flow_state(output, flow)
        if match is not None:
            log.debug(
                "bootstrap_flow_state_detected",
                extra={
                    "flow_name": flow.name,
                    "state_name": match.state_name,
                    "is_regex": match.is_regex,
                    "matched_pattern": match.matched_pattern,
                    "output_length": len(output),
                },
            )
            return match, output

        remaining_seconds = deadline - monotonic()
        if remaining_seconds <= 0:
            sample = buffer.recent_text()
            log.warning(
                "bootstrap_flow_state_detection_timeout",
                extra={
                    "flow_name": flow.name,
                    "timeout_seconds": timeout_seconds,
                    "sample_length": len(sample),
                },
            )
            raise bootstrap_flow_run_error(
                reason="state_detection_timeout",
                details={
                    "flow_name": flow.name,
                    "timeout_seconds": timeout_seconds,
                    "sample": sample,
                },
            )

        chunk = await console.read(min(read_interval_seconds, remaining_seconds))
        buffer.append(chunk)
        if chunk:
            no_output_attempts = 0
            log.debug(
                "bootstrap_flow_detection_read_completed",
                extra={
                    "flow_name": flow.name,
                    "chunk_length": len(chunk),
                    "buffer_length": len(buffer.recent_text()),
                },
            )
            continue

        no_output_attempts += 1
        if no_output_attempts <= no_match_wake_attempts:
            log.info(
                "bootstrap_flow_detection_wake_sent",
                extra={
                    "flow_name": flow.name,
                    "attempt": no_output_attempts,
                    "max_attempts": no_match_wake_attempts,
                },
            )
            await console.send(flow.startup.wake_enter)
            actions.append(f"detect:wake_console:{no_output_attempts}")


def _step_for_state(flow: FlowDefinition, state_name: str) -> FlowStep:
    for step in flow.steps:
        if step.when_state == state_name:
            return step
    log.error(
        "bootstrap_flow_step_not_found_for_state",
        extra={"flow_name": flow.name, "state_name": state_name},
    )
    raise bootstrap_flow_run_error(
        reason="step_not_found_for_state",
        details={"flow_name": flow.name, "state_name": state_name},
    )


async def _execute_step(
    step: FlowStep,
    console: AsyncConsoleSession,
    output: str,
    variables: dict[str, str],
) -> str:
    if step.action == FlowAction.WAIT:
        return await _execute_wait_step(step, console)

    if step.action == FlowAction.SEND:
        return await _execute_send_step(step, console, variables)

    if step.action == FlowAction.SEND_IF_NO_OUTPUT:
        return await _execute_send_if_no_output_step(step, console, output, variables)

    if step.action == FlowAction.EXPECT:
        return _execute_expect_step(step, output)

    if step.action == FlowAction.EXPECT_SEND:
        return await _execute_expect_send_step(step, console, output, variables)

    if step.action == FlowAction.READY:
        return _execute_ready_step(step, output)

    log.error(
        "bootstrap_flow_step_unsupported_action",
        extra={"step_name": step.name, "action": step.action.value},
    )
    raise bootstrap_flow_run_error(
        reason="unsupported_action",
        details={"step_name": step.name, "action": step.action.value},
    )


async def _execute_wait_step(step: FlowStep, console: AsyncConsoleSession) -> str:
    log.debug(
        "bootstrap_flow_step_wait",
        extra={"step_name": step.name, "timeout_seconds": step.timeout_seconds},
    )
    return await console.read(step.timeout_seconds)


async def _execute_send_step(
    step: FlowStep,
    console: AsyncConsoleSession,
    variables: dict[str, str],
) -> str:
    log.debug(
        "bootstrap_flow_step_send",
        extra={
            "step_name": step.name,
            "send_secret": step.send_secret is not None,
            "timeout_seconds": step.timeout_seconds,
        },
    )
    await console.send(_step_send_text(step, variables))
    return await console.read(step.timeout_seconds)


async def _execute_send_if_no_output_step(
    step: FlowStep,
    console: AsyncConsoleSession,
    output: str,
    variables: dict[str, str],
) -> str:
    if output.strip():
        log.debug(
            "bootstrap_flow_step_send_if_no_output_skipped",
            extra={"step_name": step.name, "output_length": len(output)},
        )
        return ""

    log.debug(
        "bootstrap_flow_step_send_if_no_output_sent",
        extra={
            "step_name": step.name,
            "send_secret": step.send_secret is not None,
            "timeout_seconds": step.timeout_seconds,
        },
    )
    await console.send(_step_send_text(step, variables))
    return await console.read(step.timeout_seconds)


def _execute_expect_step(step: FlowStep, output: str) -> str:
    _assert_step_expectation(step, output)
    log.debug(
        "bootstrap_flow_step_expect_matched",
        extra={"step_name": step.name},
    )
    return ""


async def _execute_expect_send_step(
    step: FlowStep,
    console: AsyncConsoleSession,
    output: str,
    variables: dict[str, str],
) -> str:
    _assert_step_expectation(step, output)
    log.debug(
        "bootstrap_flow_step_expect_send",
        extra={
            "step_name": step.name,
            "send_secret": step.send_secret is not None,
            "timeout_seconds": step.timeout_seconds,
        },
    )
    await console.send(_step_send_text(step, variables))
    return await console.read(step.timeout_seconds)


def _execute_ready_step(step: FlowStep, output: str) -> str:
    log.debug("bootstrap_flow_step_ready", extra={"step_name": step.name})
    return ""


def _step_send_text(step: FlowStep, variables: dict[str, str]) -> str:
    if step.send_secret:
        try:
            return _secret_send_text(variables[step.send_secret])
        except KeyError as exc:
            log.error(
                "bootstrap_flow_missing_variable",
                extra={"step_name": step.name, "variable": step.send_secret},
            )
            raise bootstrap_flow_run_error(
                reason="missing_variable",
                details={"step_name": step.name, "variable": step.send_secret},
            ) from exc

    if step.send is None:
        log.error(
            "bootstrap_flow_missing_send_text",
            extra={"step_name": step.name},
        )
        raise bootstrap_flow_run_error(
            reason="missing_send_text",
            details={"step_name": step.name},
        )
    return step.send


def _secret_send_text(value: str) -> str:
    if value.endswith(("\r", "\n")):
        return value
    return f"{value}\r\n"


def _assert_step_expectation(step: FlowStep, output: str) -> None:
    if step.expect is not None and step.expect in output:
        log.debug(
            "bootstrap_flow_expect_plain_matched",
            extra={"step_name": step.name},
        )
        return

    if step.expect_regex is not None and re.search(step.expect_regex, output, re.MULTILINE):
        log.debug(
            "bootstrap_flow_expect_regex_matched",
            extra={"step_name": step.name},
        )
        return

    log.warning(
        "bootstrap_flow_expectation_not_met",
        extra={"step_name": step.name, "output_length": len(output)},
    )
    raise bootstrap_flow_run_error(
        reason="expectation_not_met",
        details={"step_name": step.name},
    )


def _next_step(flow: FlowDefinition, step: FlowStep) -> FlowStep | None:
    if step.next is None or step.next == FlowNext.DETECT.value:
        log.debug(
            "bootstrap_flow_next_detect",
            extra={"step_name": step.name, "explicit": step.next is not None},
        )
        return None

    if step.next.startswith("step:"):
        target_name = step.next.split(":", maxsplit=1)[1]
        for candidate in flow.steps:
            if candidate.name == target_name:
                log.debug(
                    "bootstrap_flow_next_step_jump",
                    extra={"step_name": step.name, "next_step_name": candidate.name},
                )
                return candidate

    log.error(
        "bootstrap_flow_invalid_next_rule",
        extra={"step_name": step.name, "next": step.next},
    )
    raise bootstrap_flow_run_error(
        reason="invalid_next_rule",
        details={"step_name": step.name, "next": step.next},
    )
