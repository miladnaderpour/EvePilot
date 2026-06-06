import asyncio

import pytest

from evepilot.bootstrap.errors import BootstrapFlowRunError
from evepilot.bootstrap.preparation.flow_runner import run_flow
from evepilot.bootstrap.preparation.models import FlowAction, FlowDefinition
from evepilot.bootstrap.preparation.models import FlowStartup, FlowStateMarker, FlowStep
from evepilot.bootstrap.transport.console import AsyncConsoleSession


class InMemoryConsoleSession(AsyncConsoleSession):
    def __init__(self, reads: list[str]) -> None:
        self.reads = reads
        self.sent: list[str] = []

    async def connect(self) -> None:
        return None

    async def read(self, timeout_seconds: float) -> str:
        if not self.reads:
            return ""
        return self.reads.pop(0)

    async def send(self, text: str) -> None:
        self.sent.append(text)

    async def close(self) -> None:
        return None


def test_run_flow_returns_ready_when_ready_state_detected() -> None:
    result = asyncio.run(run_flow(_ready_flow(), InMemoryConsoleSession(["Router#"])))

    assert result.ready is True
    assert result.final_state == "privileged_exec_prompt"
    assert result.actions == ["ready"]


def test_run_flow_sends_step_and_detects_next_state() -> None:
    console = InMemoryConsoleSession(["Router>", "Router#"])

    result = asyncio.run(run_flow(_enable_flow(), console))

    assert console.sent == ["enable\n"]
    assert result.ready is True
    assert result.actions == ["enter-enable-mode", "ready"]


def test_run_flow_buffers_split_prompt_before_detecting_state() -> None:
    console = InMemoryConsoleSession(["Router", ">", "Router#"])

    result = asyncio.run(run_flow(_enable_flow(), console))

    assert console.sent == ["enable\n"]
    assert result.ready is True
    assert result.actions == ["enter-enable-mode", "ready"]


def test_run_flow_ready_result_uses_clean_matched_prompt_sample() -> None:
    result = asyncio.run(
        run_flow(
            _ready_flow(),
            InMemoryConsoleSession(["r>enable\r\nRouter#\r\nRouter#"]),
        )
    )

    assert result.ready is True
    assert result.output_sample == "Router#"


def test_run_flow_sends_enter_when_startup_output_is_empty() -> None:
    console = InMemoryConsoleSession(["", "Router#"])

    result = asyncio.run(run_flow(_ready_flow(), console))

    assert console.sent == ["\r\n"]
    assert result.ready is True
    assert result.actions == ["startup:wake_console:1", "ready"]


def test_run_flow_sends_enter_when_startup_output_has_no_detectable_state() -> None:
    console = InMemoryConsoleSession(["\x1b]0;", "Router#"])

    result = asyncio.run(run_flow(_ready_flow(), console))

    assert console.sent == []
    assert result.ready is True
    assert result.actions == ["ready"]


def test_run_flow_wakes_when_detection_gets_quiet_output() -> None:
    console = InMemoryConsoleSession(["\x1b]0;", "", "Router#"])

    result = asyncio.run(run_flow(_ready_flow(), console))

    assert console.sent == ["\r\n"]
    assert result.ready is True
    assert result.actions == ["detect:wake_console:1", "ready"]


def test_run_flow_uses_flow_startup_wake_enter() -> None:
    console = InMemoryConsoleSession(["", "Router#"])

    result = asyncio.run(
        run_flow(_ready_flow(startup=FlowStartup(wake_enter="\n")), console)
    )

    assert console.sent == ["\n"]
    assert result.ready is True


def test_run_flow_retries_console_wake_until_output_arrives() -> None:
    console = InMemoryConsoleSession(["", "", "", "Router#"])

    result = asyncio.run(run_flow(_ready_flow(), console))

    assert console.sent == ["\r\n", "\r\n", "\r\n"]
    assert result.ready is True
    assert result.actions == [
        "startup:wake_console:1",
        "startup:wake_console:2",
        "startup:wake_console:3",
        "ready",
    ]


def test_run_flow_settles_partial_startup_output_before_detecting_state() -> None:
    console = InMemoryConsoleSession(
        [
            "\x1b]0;CSR-9\x07",
            "\r\r\n% Please answer 'yes' or 'no'.\r\nWould you like t",
            "o enter the initial configuration dialog? [yes/no]:",
            ">",
        ]
    )

    result = asyncio.run(run_flow(_initial_dialog_flow(), console))

    assert console.sent == ["no\n"]
    assert result.ready is True
    assert result.actions == [
        "decline-initial-config-dialog",
        "ready",
    ]


def test_run_flow_waits_and_wakes_after_autoinstall_running_state() -> None:
    console = InMemoryConsoleSession(
        [
            "No startup-config, starting autoinstall/pnp/ztp...\r\n",
            "",
            "Press RETURN to get started!",
            ">",
        ]
    )

    result = asyncio.run(run_flow(_autoinstall_flow(), console))

    assert console.sent == ["\r\n", "\r\n"]
    assert result.ready is True
    assert result.actions == [
        "wait-for-autoinstall-to-settle",
        "wake-after-autoinstall",
        "press-return",
        "ready",
    ]


def test_run_flow_times_out_when_state_is_not_detected() -> None:
    console = InMemoryConsoleSession(["Router booting", "", "", ""])

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        asyncio.run(
            run_flow(
                _ready_flow(),
                console,
                detection_timeout_seconds=0.01,
            )
        )

    assert exc_info.value.details["reason"] == "state_detection_timeout"
    assert exc_info.value.details["flow_name"] == "ready-flow"
    assert "Router booting" in exc_info.value.details["sample"]


def test_run_flow_fails_when_console_wake_receives_no_output() -> None:
    console = InMemoryConsoleSession(["", "", "", ""])

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        asyncio.run(run_flow(_ready_flow(), console))

    assert console.sent == ["\r\n", "\r\n", "\r\n"]
    assert exc_info.value.details["reason"] == "console_wake_failed"
    assert exc_info.value.details["attempts"] == 3


def test_run_flow_uses_variables_for_send_secret() -> None:
    console = InMemoryConsoleSession(["Enter enable secret:", "Router#"])

    result = asyncio.run(
        run_flow(
            _secret_flow(),
            console,
            variables={"enable_secret": "EvePilotLab123\n"},
        )
    )

    assert console.sent == ["EvePilotLab123\n"]
    assert result.ready is True


def test_run_flow_uses_enable_secret_for_password_prompt() -> None:
    console = InMemoryConsoleSession(["Router>", "Password:", "Router#"])

    result = asyncio.run(
        run_flow(
            _enable_password_flow(),
            console,
            variables={"enable_secret": "EvePilotLab123\r\n"},
        )
    )

    assert console.sent == ["enable\n", "EvePilotLab123\r\n"]
    assert result.ready is True
    assert result.actions == [
        "enter-enable-mode",
        "enter-enable-password",
        "ready",
    ]


def test_run_flow_resolves_flow_variables_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EVEPILOT_BOOTSTRAP_ENABLE_SECRET", "EvePilotLab123\n")
    console = InMemoryConsoleSession(["Enter enable secret:", "Router#"])

    result = asyncio.run(run_flow(_secret_flow_with_variable(), console))

    assert console.sent == ["EvePilotLab123\n"]
    assert result.ready is True


def test_run_flow_rejects_missing_secret_variable() -> None:
    console = InMemoryConsoleSession(["Enter enable secret:"])

    with pytest.raises(BootstrapFlowRunError) as exc_info:
        asyncio.run(run_flow(_secret_flow(), console))

    assert exc_info.value.details["reason"] == "missing_variable"
    assert exc_info.value.details["variable"] == "enable_secret"


def _ready_flow(startup: FlowStartup | None = None) -> FlowDefinition:
    return FlowDefinition(
        name="ready-flow",
        version=1,
        states={
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            )
        },
        steps=[
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
            )
        ],
        startup=startup or FlowStartup(),
    )


def _enable_flow() -> FlowDefinition:
    return FlowDefinition(
        name="enable-flow",
        version=1,
        states={
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+>\s*$"],
            ),
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            ),
        },
        steps=[
            FlowStep(
                name="enter-enable-mode",
                action=FlowAction.SEND,
                when_state="user_exec_prompt",
                send="enable\n",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
            ),
        ],
    )


def _initial_dialog_flow() -> FlowDefinition:
    return FlowDefinition(
        name="initial-dialog-flow",
        version=1,
        states={
            "initial_config_dialog": FlowStateMarker(
                name="initial_config_dialog",
                patterns=["% Please answer 'yes' or 'no'."],
            ),
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]*>\s*$"],
            ),
        },
        steps=[
            FlowStep(
                name="decline-initial-config-dialog",
                action=FlowAction.SEND,
                when_state="initial_config_dialog",
                send="no\n",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="user_exec_prompt",
                mark_ready=True,
            ),
        ],
    )


def _autoinstall_flow() -> FlowDefinition:
    return FlowDefinition(
        name="autoinstall-flow",
        version=1,
        states={
            "autoinstall_running": FlowStateMarker(
                name="autoinstall_running",
                patterns=["No startup-config, starting autoinstall/pnp/ztp..."],
            ),
            "press_return": FlowStateMarker(
                name="press_return",
                patterns=["Press RETURN to get started"],
            ),
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]*>\s*$"],
            ),
        },
        steps=[
            FlowStep(
                name="wait-for-autoinstall-to-settle",
                action=FlowAction.WAIT,
                when_state="autoinstall_running",
                timeout_seconds=10,
                next="step:wake-after-autoinstall",
            ),
            FlowStep(
                name="wake-after-autoinstall",
                action=FlowAction.SEND,
                send="\r\n",
            ),
            FlowStep(
                name="press-return",
                action=FlowAction.SEND,
                when_state="press_return",
                send="\r\n",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="user_exec_prompt",
                mark_ready=True,
            ),
        ],
    )


def _secret_flow() -> FlowDefinition:
    return FlowDefinition(
        name="secret-flow",
        version=1,
        states={
            "enable_secret_prompt": FlowStateMarker(
                name="enable_secret_prompt",
                patterns=["Enter enable secret:"],
            ),
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            ),
        },
        steps=[
            FlowStep(
                name="enter-enable-secret",
                action=FlowAction.SEND,
                when_state="enable_secret_prompt",
                send_secret="enable_secret",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
            ),
        ],
    )


def _secret_flow_with_variable() -> FlowDefinition:
    flow = _secret_flow()
    return FlowDefinition(
        name=flow.name,
        version=flow.version,
        states=flow.states,
        steps=flow.steps,
        startup=flow.startup,
        variables={"enable_secret": {"required": True, "secret": True}},
    )


def _enable_password_flow() -> FlowDefinition:
    return FlowDefinition(
        name="enable-password-flow",
        version=1,
        states={
            "user_exec_prompt": FlowStateMarker(
                name="user_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+>\s*$"],
            ),
            "password_prompt": FlowStateMarker(
                name="password_prompt",
                patterns=["Password:"],
            ),
            "privileged_exec_prompt": FlowStateMarker(
                name="privileged_exec_prompt",
                regex=[r"[A-Za-z0-9_.-]+#\s*$"],
            ),
        },
        steps=[
            FlowStep(
                name="enter-enable-mode",
                action=FlowAction.SEND,
                when_state="user_exec_prompt",
                send="enable\n",
            ),
            FlowStep(
                name="enter-enable-password",
                action=FlowAction.SEND,
                when_state="password_prompt",
                send_secret="enable_secret",
            ),
            FlowStep(
                name="ready",
                action=FlowAction.READY,
                when_state="privileged_exec_prompt",
                mark_ready=True,
            ),
        ],
    )
