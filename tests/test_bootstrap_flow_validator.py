import pytest

from evepilot.bootstrap.errors import BootstrapFlowError
from evepilot.bootstrap.preparation.flow_validator import validate_flow_definition
from evepilot.bootstrap.preparation.models import FlowAction, FlowDefinition
from evepilot.bootstrap.preparation.models import FlowStateMarker, FlowStep


def test_validate_flow_definition_accepts_valid_flow() -> None:
    validate_flow_definition(_valid_flow())


def test_validate_flow_definition_rejects_duplicate_step_names() -> None:
    flow = FlowDefinition(
        name="example",
        version=1,
        states=_states(),
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state=None,
            ),
        ],
    )

    with pytest.raises(BootstrapFlowError) as exc_info:
        validate_flow_definition(flow)

    assert exc_info.value.details["reason"] == "duplicate_step_name"


def test_validate_flow_definition_rejects_unknown_when_state() -> None:
    flow = FlowDefinition(
        name="example",
        version=1,
        states=_states(),
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="missing_state",
            )
        ],
    )

    with pytest.raises(BootstrapFlowError) as exc_info:
        validate_flow_definition(flow)

    assert exc_info.value.details["reason"] == "unknown_when_state"


def test_validate_flow_definition_rejects_unknown_next_step() -> None:
    flow = FlowDefinition(
        name="example",
        version=1,
        states=_states(),
        steps=[
            FlowStep(
                name="send-command",
                action=FlowAction.SEND,
                when_state="privileged_exec_prompt",
                send="show version\n",
                next="step:missing",
            )
        ],
    )

    with pytest.raises(BootstrapFlowError) as exc_info:
        validate_flow_definition(flow)

    assert exc_info.value.details["reason"] == "unknown_next_step"


def test_validate_flow_definition_rejects_ready_step_with_next() -> None:
    flow = FlowDefinition(
        name="example",
        version=1,
        states=_states(),
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
                next="stop",
            )
        ],
    )

    with pytest.raises(BootstrapFlowError) as exc_info:
        validate_flow_definition(flow)

    assert exc_info.value.details["reason"] == "ready_step_with_next"


def _valid_flow() -> FlowDefinition:
    return FlowDefinition(
        name="example",
        version=1,
        states=_states(),
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
            )
        ],
    )


def _states() -> dict[str, FlowStateMarker]:
    return {
        "privileged_exec_prompt": FlowStateMarker(
            name="privileged_exec_prompt",
            regex=[r"[A-Za-z0-9_.-]+#\s*$"],
        )
    }
