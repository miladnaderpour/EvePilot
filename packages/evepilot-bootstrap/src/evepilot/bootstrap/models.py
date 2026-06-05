"""Bootstrap domain models."""

from dataclasses import dataclass, field
from enum import StrEnum


class ConsoleState(StrEnum):
    """Known console states for network devices."""

    BOOTING = "booting"
    INITIAL_CONFIG_DIALOG = "initial_config_dialog"
    PRESS_RETURN = "press_return"
    LOGIN_PROMPT = "login_prompt"
    PASSWORD_PROMPT = "password_prompt"
    USER_EXEC_PROMPT = "user_exec_prompt"
    PRIVILEGED_EXEC_PROMPT = "privileged_exec_prompt"
    CONFIG_PROMPT = "config_prompt"
    ROMMON = "rommon"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ConsoleStateDetection:
    """Detected console state and the output sample used for detection."""

    state: ConsoleState
    matched_pattern: str | None = None
    sample: str = ""


@dataclass(frozen=True, slots=True)
class ConsolePrepareResult:
    """Result of preparing a console for future bootstrap actions."""

    initial_state: ConsoleState
    final_state: ConsoleState
    actions: list[str] = field(default_factory=list)
    output_sample: str = ""
    ready_for_bootstrap: bool = False
