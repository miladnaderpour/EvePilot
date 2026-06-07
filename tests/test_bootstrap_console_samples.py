from pathlib import Path

from evepilot.bootstrap.preparation.flow_loader import load_builtin_flow
from evepilot.bootstrap.preparation.flow_matcher import detect_flow_state

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_builtin_cisco_flow_matches_csr1000_initial_dialog_sample() -> None:
    sample = (FIXTURES_DIR / "csr1000-full_console_sample.txt").read_text(
        encoding="utf-8"
    )
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state(sample, flow)

    assert match is not None
    assert match.state_name == "initial_config_dialog"


def test_builtin_cisco_flow_matches_bare_user_exec_prompt() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state(">", flow)

    assert match is not None
    assert match.state_name == "user_exec_prompt"


def test_builtin_cisco_flow_matches_yes_no_complaint_as_initial_dialog() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state("% Please answer 'yes' or 'no'.\r", flow)

    assert match is not None
    assert match.state_name == "initial_config_dialog"


def test_builtin_cisco_flow_matches_terminate_autoinstall_prompt() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state("Would you like to terminate autoinstall? [yes]: \r", flow)

    assert match is not None
    assert match.state_name == "terminate_autoinstall_prompt"


def test_builtin_cisco_flow_matches_autoinstall_running_output() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state(
        "\r\nNo startup-config, starting autoinstall/pnp/ztp...\r\n\r\n"
        "Autoinstall will terminate if any input is detected on console\r\n",
        flow,
    )

    assert match is not None
    assert match.state_name == "autoinstall_running"


def test_builtin_cisco_flow_matches_crashinfo_noise_output() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state(
        "no\r\r\n% Crashinfo may not be recovered at bootflash:crashinfo\r\n"
        "% This file system device reports an error",
        flow,
    )

    assert match is not None
    assert match.state_name == "console_noise_wait"


def test_builtin_cisco_flow_matches_dns_translation_noise_output() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    match = detect_flow_state(
        '\x07zz\b\b  \b\bXuTnEkRnMopnenable\r\n'
        'Translating "XuTnEkRnMopnenable"...domain server (255.255.255.255)',
        flow,
    )

    assert match is not None
    assert match.state_name == "console_noise_wait"
