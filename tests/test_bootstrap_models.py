from evepilot.bootstrap.models import ConsolePrepareResult, ConsoleState
from evepilot.bootstrap.models import ConsoleStateDetection


def test_console_state_detection_shape() -> None:
    detection = ConsoleStateDetection(
        state=ConsoleState.PRIVILEGED_EXEC_PROMPT,
        matched_pattern="# at line end",
        sample="Router#",
    )

    assert detection.state == ConsoleState.PRIVILEGED_EXEC_PROMPT
    assert detection.matched_pattern == "# at line end"
    assert detection.sample == "Router#"


def test_console_prepare_result_shape() -> None:
    result = ConsolePrepareResult(
        initial_state=ConsoleState.INITIAL_CONFIG_DIALOG,
        final_state=ConsoleState.USER_EXEC_PROMPT,
        actions=["answered_initial_config_dialog_no"],
        output_sample="Router>",
        ready_for_bootstrap=False,
    )

    assert result.initial_state == ConsoleState.INITIAL_CONFIG_DIALOG
    assert result.final_state == ConsoleState.USER_EXEC_PROMPT
    assert result.actions == ["answered_initial_config_dialog_no"]
    assert result.output_sample == "Router>"
    assert result.ready_for_bootstrap is False
