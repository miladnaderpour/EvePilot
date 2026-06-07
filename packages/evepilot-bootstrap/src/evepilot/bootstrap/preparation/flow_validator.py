"""Bootstrap flow validation."""

from __future__ import annotations

import re

from evepilot.bootstrap.errors import bootstrap_flow_invalid_error
from evepilot.bootstrap.preparation.models import FlowAction, FlowDefinition, FlowNext


def validate_flow_definition(flow: FlowDefinition) -> None:
    """Validate a bootstrap flow definition."""

    _validate_states(flow)
    _validate_steps(flow)


def _validate_states(flow: FlowDefinition) -> None:
    if not flow.states:
        raise bootstrap_flow_invalid_error(reason="missing_states")

    for state_name, marker in flow.states.items():
        if marker.name != state_name:
            raise bootstrap_flow_invalid_error(
                reason="state_name_mismatch",
                details={"state_name": state_name, "marker_name": marker.name},
            )
        if not marker.patterns and not marker.regex:
            raise bootstrap_flow_invalid_error(
                reason="state_marker_without_patterns",
                details={"state_name": state_name},
            )
        for regex_pattern in marker.regex:
            try:
                re.compile(regex_pattern)
            except re.error as exc:
                raise bootstrap_flow_invalid_error(
                    reason="invalid_state_regex",
                    details={"state_name": state_name, "regex": regex_pattern},
                ) from exc


def _validate_steps(flow: FlowDefinition) -> None:
    if not flow.steps:
        raise bootstrap_flow_invalid_error(reason="missing_steps")

    step_names: set[str] = set()
    when_states: set[str] = set()

    for step in flow.steps:
        if step.name in step_names:
            raise bootstrap_flow_invalid_error(
                reason="duplicate_step_name",
                details={"step_name": step.name},
            )
        step_names.add(step.name)

        if step.when_state is not None:
            if step.when_state not in flow.states:
                raise bootstrap_flow_invalid_error(
                    reason="unknown_when_state",
                    details={"step_name": step.name, "when_state": step.when_state},
                )
            if step.when_state in when_states:
                raise bootstrap_flow_invalid_error(
                    reason="duplicate_when_state",
                    details={"when_state": step.when_state},
                )
            when_states.add(step.when_state)

        _validate_next_rule(step.name, step.action, step.next)

    all_step_names = {step.name for step in flow.steps}
    for step in flow.steps:
        if step.next and step.next.startswith("step:"):
            target_step = step.next.split(":", maxsplit=1)[1]
            if target_step not in all_step_names:
                raise bootstrap_flow_invalid_error(
                    reason="unknown_next_step",
                    details={"step_name": step.name, "next": step.next},
                )


def _validate_next_rule(
    step_name: str,
    action: FlowAction,
    next_rule: str | None,
) -> None:
    if action == FlowAction.READY and next_rule is not None:
        raise bootstrap_flow_invalid_error(
            reason="ready_step_with_next",
            details={"step_name": step_name, "next": next_rule},
        )

    if next_rule is None:
        return
    if next_rule in {FlowNext.DETECT.value, FlowNext.STOP.value}:
        return
    if next_rule.startswith("step:") and next_rule != "step:":
        return
    raise bootstrap_flow_invalid_error(
        reason="invalid_next_rule",
        details={"step_name": step_name, "next": next_rule},
    )
