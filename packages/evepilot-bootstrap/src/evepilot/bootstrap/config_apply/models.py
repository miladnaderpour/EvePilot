"""Config apply domain models."""

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True, slots=True)
class ConfigLine:
    """One command line from a rendered config file."""

    number: int
    text: str


@dataclass(frozen=True, slots=True)
class ConfigCommandResult:
    """Result for one config command sent to the console."""

    line_number: int
    command: str
    output_sample: str = ""


@dataclass(frozen=True, slots=True)
class ConfigApplyResult:
    """Result of applying rendered config lines to a console."""

    commands_total: int
    commands_sent: int
    command_results: list[ConfigCommandResult] = field(default_factory=list)
    ready: bool = False
    final_state: str | None = None
    apply_duration_seconds: float | None = None
