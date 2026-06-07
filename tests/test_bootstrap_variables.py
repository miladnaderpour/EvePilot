import pytest

from evepilot.bootstrap.errors import BootstrapFlowRunError
from evepilot.bootstrap.preparation.models import FlowAction
from evepilot.bootstrap.preparation.models import FlowDefinition
from evepilot.bootstrap.preparation.models import FlowStateMarker
from evepilot.bootstrap.preparation.models import FlowStep
from evepilot.bootstrap.preparation.variables import resolve_flow_variables
from evepilot.bootstrap.preparation.variables import variable_env_name


def test_variable_env_name_normalizes_variable_name() -> None:
    assert variable_env_name("enable_secret") == "EVEPILOT_BOOTSTRAP_ENABLE_SECRET"
    assert variable_env_name("enable-secret") == "EVEPILOT_BOOTSTRAP_ENABLE_SECRET"


def test_resolve_flow_variables_reads_environment_values() -> None:
    flow = _flow({"enable_secret": {"required": True, "secret": True}})

    resolved = resolve_flow_variables(
        flow,
        environ={"EVEPILOT_BOOTSTRAP_ENABLE_SECRET": "EvePilotLab123"},
    )

    assert resolved == {"enable_secret": "EvePilotLab123"}


def test_resolve_flow_variables_skips_missing_optional_values() -> None:
    flow = _flow({"enable_secret": {"required": False, "secret": True}})

    assert resolve_flow_variables(flow, environ={}) == {}


def test_resolve_flow_variables_raises_for_missing_required_values() -> None:
    flow = _flow({"enable_secret": {"required": True, "secret": True}})

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        resolve_flow_variables(flow, environ={})

    assert exc_info.value.details["reason"] == "missing_variable"
    assert exc_info.value.details["variable"] == "enable_secret"
    assert exc_info.value.details["env_name"] == "EVEPILOT_BOOTSTRAP_ENABLE_SECRET"


def test_resolve_flow_variables_raises_for_invalid_variable_definition() -> None:
    flow = _flow({"enable_secret": "required"})

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        resolve_flow_variables(flow, environ={})

    assert exc_info.value.details["reason"] == "invalid_variable_definition"
    assert exc_info.value.details["variable"] == "enable_secret"


def test_resolve_flow_variables_raises_for_invalid_boolean_field() -> None:
    flow = _flow({"enable_secret": {"required": "true", "secret": True}})

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        resolve_flow_variables(flow, environ={})

    assert exc_info.value.details["reason"] == "invalid_variable_definition"
    assert exc_info.value.details["variable"] == "enable_secret"
    assert exc_info.value.details["field"] == "required"


def _flow(variables: dict[str, object]) -> FlowDefinition:
    return FlowDefinition(
        name="test-flow",
        version=1,
        states={
            "ready": FlowStateMarker(
                name="ready",
                regex=[r"[A-Za-z0-9_.-]+#"],
            )
        },
        steps=[
            FlowStep(
                name="ready",
                when_state="ready",
                action=FlowAction.READY,
            )
        ],
        variables=variables,
    )
