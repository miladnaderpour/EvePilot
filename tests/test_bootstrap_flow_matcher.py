import logging

import pytest

from evepilot.bootstrap.errors import BootstrapFlowError
from evepilot.bootstrap.preparation.flow_matcher import detect_flow_state
from evepilot.bootstrap.preparation.models import FlowAction, FlowDefinition
from evepilot.bootstrap.preparation.models import FlowStateMarker, FlowStep


def test_detect_flow_state_with_plain_string_pattern() -> None:
    flow = _flow(
        states={
            "initial_config_dialog": FlowStateMarker(
                name="initial_config_dialog",
                patterns=[
                    "Would you like to enter the initial configuration dialog?"
                ],
            )
        }
    )

    match = detect_flow_state(
        "Would you like to enter the initial configuration dialog? [yes/no]:",
        flow,
    )

    assert match is not None
    assert match.state_name == "initial_config_dialog"
    assert match.is_regex is False


def test_detect_flow_state_with_regex_pattern() -> None:
    flow = _flow(
        states={
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            )
        }
    )

    match = detect_flow_state("Router#", flow)

    assert match is not None
    assert match.state_name == "privileged_exec_prompt"
    assert match.is_regex is True
    assert match.matched_text == "Router#"


def test_detect_flow_state_prompt_regex_can_require_line_boundary() -> None:
    flow = _flow(
        states={
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"(^|\r|\n)[A-Za-z0-9_.-]*>\s*$"],
            )
        }
    )

    assert detect_flow_state("Translating garbage>", flow) is None

    match = detect_flow_state("Translating garbage>\r\nRouter>", flow)

    assert match is not None
    assert match.state_name == "user_exec_prompt"


def test_detect_flow_state_returns_none_when_no_marker_matches() -> None:
    flow = _flow(
        states={
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+>\s*$"],
            )
        }
    )

    assert detect_flow_state("unrecognized output", flow) is None


def test_detect_flow_state_rejects_ambiguous_matches() -> None:
    flow = _flow(
        states={
            "state_one": FlowStateMarker(name="state_one", patterns=["Router"]),
            "state_two": FlowStateMarker(name="state_two", patterns=["Router"]),
        }
    )

    with pytest.raises(BootstrapFlowError) as exc_info:
        detect_flow_state("Router#", flow)

    assert exc_info.value.code == "bootstrap.flow_state_ambiguous"


def test_detect_flow_state_uses_latest_state_when_output_contains_history() -> None:
    flow = _flow(
        states={
            "autoinstall_running": FlowStateMarker(
                name="autoinstall_running",
                patterns=["No startup-config, starting autoinstall/pnp/ztp..."],
            ),
            "initial_config_dialog": FlowStateMarker(
                name="initial_config_dialog",
                patterns=[
                    "Would you like to enter the initial configuration dialog?"
                ],
            ),
        }
    )

    match = detect_flow_state(
        "No startup-config, starting autoinstall/pnp/ztp...\r\n"
        "Would you like to enter the initial configuration dialog? [yes/no]:",
        flow,
    )

    assert match is not None
    assert match.state_name == "initial_config_dialog"


def test_detect_flow_state_logs_selected_state(caplog: pytest.LogCaptureFixture) -> None:
    flow = _flow(
        states={
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            )
        }
    )

    with caplog.at_level(logging.DEBUG):
        detect_flow_state("Router#", flow)

    selected_records = [
        record
        for record in caplog.records
        if record.message == "bootstrap_flow_matcher_state_selected"
    ]
    assert selected_records[-1].flow_name == "example"
    assert selected_records[-1].state_name == "privileged_exec_prompt"


def test_detect_flow_state_logs_no_match(caplog: pytest.LogCaptureFixture) -> None:
    flow = _flow(
        states={
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            )
        }
    )

    with caplog.at_level(logging.DEBUG):
        detect_flow_state("booting", flow)

    no_match_records = [
        record
        for record in caplog.records
        if record.message == "bootstrap_flow_matcher_no_state_matched"
    ]
    assert no_match_records[-1].flow_name == "example"
    assert no_match_records[-1].sample == "booting"


def _flow(*, states: dict[str, FlowStateMarker]) -> FlowDefinition:
    first_state = next(iter(states))
    return FlowDefinition(
        name="example",
        version=1,
        states=states,
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state=first_state,
                mark_ready=True,
                next="stop",
            )
        ],
    )
