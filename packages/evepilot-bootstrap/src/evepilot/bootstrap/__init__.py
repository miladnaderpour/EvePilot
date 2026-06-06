"""Console bootstrap primitives for EvePilot."""

from evepilot.bootstrap.preparation.flow_loader import load_flow
from evepilot.bootstrap.preparation.flow_matcher import detect_flow_state
from evepilot.bootstrap.preparation.flow_runner import run_flow
from evepilot.bootstrap.preparation.models import (
    FlowAction,
    FlowDefinition,
    FlowNext,
    FlowRunResult,
    FlowStartup,
    FlowStateMatch,
    FlowStateMarker,
    FlowStep,
)
from evepilot.bootstrap.preparation.variables import (
    resolve_flow_variables,
    variable_env_name,
)
from evepilot.bootstrap.transport.console import (
    AsyncConsoleSession,
    RawTcpConsoleSession,
    TelnetConsoleSession,
)

__all__ = [
    "AsyncConsoleSession",
    "RawTcpConsoleSession",
    "TelnetConsoleSession",
    "FlowAction",
    "FlowDefinition",
    "FlowNext",
    "FlowRunResult",
    "FlowStartup",
    "FlowStateMatch",
    "FlowStateMarker",
    "FlowStep",
    "detect_flow_state",
    "load_flow",
    "resolve_flow_variables",
    "run_flow",
    "variable_env_name",
]
