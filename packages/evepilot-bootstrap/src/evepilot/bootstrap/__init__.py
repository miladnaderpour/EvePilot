"""Console bootstrap primitives for EvePilot."""

from evepilot.bootstrap.config_apply.config_file import load_config_lines
from evepilot.bootstrap.config_apply.models import (
    ConfigApplyResult,
    ConfigCommandResult,
    ConfigLine,
)
from evepilot.bootstrap.config_apply.runner import apply_config_lines
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
from evepilot.bootstrap.schemas import (
    BootstrapConfigApplyResult,
    BootstrapConfigApplySummary,
    BootstrapConsoleEndpoint,
    BootstrapConsolePrepareResult,
    BootstrapFlowExportResult,
    BootstrapFlowListResult,
    BootstrapFlowShowResult,
    BootstrapFlowSummary,
    BootstrapPreparationResult,
)
from evepilot.bootstrap.service import (
    apply_rendered_config,
    export_flow,
    list_flows,
    prepare_console,
    show_flow,
)
from evepilot.bootstrap.transport.console import (
    AsyncConsoleSession,
    RawTcpConsoleSession,
    TelnetConsoleSession,
)

__all__ = [
    "AsyncConsoleSession",
    "BootstrapConfigApplyResult",
    "BootstrapConfigApplySummary",
    "BootstrapConsoleEndpoint",
    "BootstrapConsolePrepareResult",
    "BootstrapFlowExportResult",
    "BootstrapFlowListResult",
    "BootstrapFlowShowResult",
    "BootstrapFlowSummary",
    "BootstrapPreparationResult",
    "ConfigApplyResult",
    "ConfigCommandResult",
    "ConfigLine",
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
    "apply_rendered_config",
    "export_flow",
    "list_flows",
    "prepare_console",
    "show_flow",
    "apply_config_lines",
    "detect_flow_state",
    "load_config_lines",
    "load_flow",
    "resolve_flow_variables",
    "run_flow",
    "variable_env_name",
]
