"""Bootstrap domain models."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FlowAction(StrEnum):
    """Supported bootstrap flow actions for Milestone 0.2.0."""

    WAIT = "wait"
    SEND = "send"
    SEND_IF_NO_OUTPUT = "send_if_no_output"
    EXPECT = "expect"
    EXPECT_SEND = "expect_send"
    READY = "ready"


class FlowNext(StrEnum):
    """Built-in flow continuation rules."""

    DETECT = "detect"
    STOP = "stop"


@dataclass(frozen=True, slots=True)
class FlowStartup:
    """Startup behavior before flow state detection begins."""

    initial_read_seconds: float = 3.0
    send_enter_if_no_output: bool = True
    wake_enter: str = "\r\n"
    wake_attempts: int = 3
    read_after_wake_seconds: float = 2.0


@dataclass(frozen=True, slots=True)
class FlowStateMarker:
    """How to recognize a named flow state."""

    name: str
    patterns: list[str] = field(default_factory=list)
    regex: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class FlowStep:
    """Action to execute when a flow state is detected."""

    name: str
    action: FlowAction
    when_state: str | None = None
    send: str | None = None
    send_secret: str | None = None
    expect: str | None = None
    expect_regex: str | None = None
    timeout_seconds: int = 30
    optional: bool = False
    next: str | None = None
    mark_ready: bool = False


@dataclass(frozen=True, slots=True)
class FlowDefinition:
    """Bootstrap preparation flow definition."""

    name: str
    version: int
    states: dict[str, FlowStateMarker]
    steps: list[FlowStep]
    description: str | None = None
    startup: FlowStartup = field(default_factory=FlowStartup)
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FlowSummary:
    """Short description of an available bootstrap flow."""

    name: str
    source: str
    version: int
    description: str | None = None


@dataclass(frozen=True, slots=True)
class FlowStateMatch:
    """Matched flow-defined console state."""

    state_name: str
    matched_pattern: str
    matched_text: str
    is_regex: bool = False
    sample: str = ""


@dataclass(frozen=True, slots=True)
class FlowRunResult:
    """Result of running a bootstrap preparation flow."""

    flow_name: str
    final_state: str | None
    actions: list[str] = field(default_factory=list)
    output_sample: str = ""
    ready: bool = False
