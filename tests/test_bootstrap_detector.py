from evepilot.bootstrap.detector import detect_console_state
from evepilot.bootstrap.models import ConsoleState


def test_detect_initial_config_dialog() -> None:
    detection = detect_console_state(
        "Would you like to enter the initial configuration dialog? [yes/no]:"
    )

    assert detection.state == ConsoleState.INITIAL_CONFIG_DIALOG
    assert detection.matched_pattern == "initial configuration dialog"


def test_detect_press_return_prompt() -> None:
    detection = detect_console_state("Press RETURN to get started!")

    assert detection.state == ConsoleState.PRESS_RETURN
    assert detection.matched_pattern == "Press RETURN to get started"


def test_detect_login_prompt() -> None:
    detection = detect_console_state("\nUsername:")

    assert detection.state == ConsoleState.LOGIN_PROMPT


def test_detect_password_prompt() -> None:
    detection = detect_console_state("\nPassword:")

    assert detection.state == ConsoleState.PASSWORD_PROMPT


def test_detect_user_exec_prompt() -> None:
    detection = detect_console_state("\nRouter>")

    assert detection.state == ConsoleState.USER_EXEC_PROMPT


def test_detect_privileged_exec_prompt() -> None:
    detection = detect_console_state("\nRouter#")

    assert detection.state == ConsoleState.PRIVILEGED_EXEC_PROMPT


def test_detect_config_prompt_before_privileged_prompt() -> None:
    detection = detect_console_state("\nRouter(config)#")

    assert detection.state == ConsoleState.CONFIG_PROMPT


def test_detect_rommon() -> None:
    detection = detect_console_state("\nrommon 1 >")

    assert detection.state == ConsoleState.ROMMON


def test_detect_booting_output() -> None:
    detection = detect_console_state(
        "System Bootstrap, Version 17.3\nSelf decompressing the image"
    )

    assert detection.state == ConsoleState.BOOTING


def test_detect_unknown_state() -> None:
    detection = detect_console_state("some unrecognized console output")

    assert detection.state == ConsoleState.UNKNOWN
    assert detection.matched_pattern is None
    assert detection.sample == "some unrecognized console output"


def test_detection_sample_is_truncated_from_end() -> None:
    detection = detect_console_state("a" * 2100)

    assert detection.state == ConsoleState.UNKNOWN
    assert len(detection.sample) == 2000
