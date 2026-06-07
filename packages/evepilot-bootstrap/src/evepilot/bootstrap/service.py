"""Public bootstrap service use cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Protocol

from evepilot.bootstrap.config_apply.config_file import load_config_lines
from evepilot.bootstrap.config_apply.models import ConfigApplyResult, ConfigLine
from evepilot.bootstrap.config_apply.runner import DEFAULT_LINE_ENDING
from evepilot.bootstrap.config_apply.runner import apply_config_lines
from evepilot.bootstrap.errors import bootstrap_config_apply_error
from evepilot.bootstrap.errors import bootstrap_flow_service_error
from evepilot.bootstrap.preparation.flow_loader import load_flow
from evepilot.bootstrap.preparation.flow_loader import list_builtin_flows
from evepilot.bootstrap.preparation.flow_loader import read_builtin_flow_text
from evepilot.bootstrap.preparation.flow_runner import run_flow
from evepilot.bootstrap.preparation.models import FlowDefinition, FlowRunResult
from evepilot.bootstrap.preparation.variables import resolve_flow_variables
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
from evepilot.bootstrap.transport.console import (
    AsyncConsoleSession,
    RawTcpConsoleSession,
    TelnetConsoleSession,
)
from evepilot.core.logging import get_logger
from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.client import EveNgClient
from evepilot.eve_ng.errors import console_url_missing_error
from evepilot.eve_ng.models import EveNgNode

DEFAULT_FLOW_REF = "built-in:cisco-router-first-boot"
TRANSPORT_AUTO = "auto"
TRANSPORT_TELNET = "telnet"
TRANSPORT_RAW_TCP = "raw-tcp"
DEFAULT_DETECT_CONSOLE_TIMEOUT_SECONDS = 120.0
DEFAULT_CONFIG_READ_TIMEOUT_SECONDS = 3.0
FLOW_SOURCE_BUILT_IN = "built-in"
log = get_logger(__name__)


class ConsoleSessionFactory(Protocol):
    """Create a console session for a resolved console endpoint."""

    def __call__(
        self,
        *,
        console: ConsoleEndpoint,
        transport: str,
    ) -> AsyncConsoleSession:
        """Return an unconnected console session."""
        ...


@dataclass(frozen=True, slots=True)
class _ConfigApplyContext:
    node: EveNgNode
    console: ConsoleEndpoint
    transport: str
    flow: FlowDefinition
    flow_ref: str
    variables: dict[str, str]
    lines: list[ConfigLine]
    session: AsyncConsoleSession


@dataclass(frozen=True, slots=True)
class _PrepareContext:
    node: EveNgNode
    console: ConsoleEndpoint
    transport: str
    flow: FlowDefinition
    flow_ref: str
    variables: dict[str, str]
    session: AsyncConsoleSession


def list_flows(*, source: str = FLOW_SOURCE_BUILT_IN) -> BootstrapFlowListResult:
    """List available bootstrap flows."""

    _assert_supported_flow_source(source)
    return BootstrapFlowListResult(
        source=source,
        flows=[BootstrapFlowSummary.from_domain(flow) for flow in list_builtin_flows()],
    )


def show_flow(source: str) -> BootstrapFlowShowResult:
    """Return a bootstrap flow definition as text."""

    return BootstrapFlowShowResult(source=source, text=_read_flow_text(source))


def export_flow(
    *,
    source: str,
    output: Path,
    force: bool = False,
) -> BootstrapFlowExportResult:
    """Export a bootstrap flow definition to a file."""

    text = _read_flow_text(source)
    if output.exists() and not force:
        raise bootstrap_flow_service_error(
            reason="flow_export_output_exists",
            details={"output": str(output)},
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return BootstrapFlowExportResult(source=source, output=str(output))


async def prepare_console(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
    flow_ref: str = DEFAULT_FLOW_REF,
    transport: str = TRANSPORT_AUTO,
    variables: dict[str, str] | None = None,
    detect_console_timeout_seconds: float = DEFAULT_DETECT_CONSOLE_TIMEOUT_SECONDS,
    console_session_factory: ConsoleSessionFactory | None = None,
) -> BootstrapConsolePrepareResult:
    """Prepare a node console using a bootstrap preparation flow."""

    started_at = monotonic()
    _log_prepare_started(
        lab_path=lab_path,
        node_name=node_name,
        flow_ref=flow_ref,
        transport=transport,
    )
    context = _build_prepare_context(
        eve_ng_client=eve_ng_client,
        lab_path=lab_path,
        node_name=node_name,
        flow_ref=flow_ref,
        transport=transport,
        variables=variables,
        console_session_factory=console_session_factory,
    )
    preparation = await _run_prepare_context(
        context=context,
        detect_console_timeout_seconds=detect_console_timeout_seconds,
    )
    result = _build_prepare_result(
        context=context,
        preparation=preparation,
        duration_seconds=round(monotonic() - started_at, 3),
    )
    _log_prepare_completed(lab_path=lab_path, node_name=node_name, result=result)
    return result


def _assert_supported_flow_source(source: str) -> None:
    if source == FLOW_SOURCE_BUILT_IN:
        return

    raise bootstrap_flow_service_error(
        reason="unsupported_flow_source",
        details={"source": source},
    )


def _read_flow_text(source: str) -> str:
    if not source.startswith("built-in:"):
        raise bootstrap_flow_service_error(
            reason="unsupported_flow_reference",
            details={"source": source},
        )
    flow_name = source.removeprefix("built-in:")
    return read_builtin_flow_text(flow_name)


async def apply_rendered_config(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
    config_path: Path,
    flow_ref: str = DEFAULT_FLOW_REF,
    transport: str = TRANSPORT_AUTO,
    variables: dict[str, str] | None = None,
    detect_console_timeout_seconds: float = DEFAULT_DETECT_CONSOLE_TIMEOUT_SECONDS,
    config_read_timeout_seconds: float = DEFAULT_CONFIG_READ_TIMEOUT_SECONDS,
    line_ending: str = DEFAULT_LINE_ENDING,
    console_session_factory: ConsoleSessionFactory | None = None,
) -> BootstrapConfigApplyResult:
    """Prepare a node console and apply an already-rendered config file."""

    started_at = monotonic()
    _log_apply_started(
        lab_path=lab_path,
        node_name=node_name,
        config_path=config_path,
        flow_ref=flow_ref,
        transport=transport,
    )
    context = _build_config_apply_context(
        eve_ng_client=eve_ng_client,
        lab_path=lab_path,
        node_name=node_name,
        config_path=config_path,
        flow_ref=flow_ref,
        transport=transport,
        variables=variables,
        console_session_factory=console_session_factory,
    )
    preparation, config_apply = await _run_config_apply_context(
        context=context,
        detect_console_timeout_seconds=detect_console_timeout_seconds,
        config_read_timeout_seconds=config_read_timeout_seconds,
        line_ending=line_ending,
    )
    result = _build_config_apply_result(
        context=context,
        preparation=preparation,
        config_apply=config_apply,
        config_path=config_path,
        duration_seconds=round(monotonic() - started_at, 3),
    )
    _log_apply_completed(lab_path=lab_path, node_name=node_name, result=result)
    return result


def _log_prepare_started(
    *,
    lab_path: str,
    node_name: str,
    flow_ref: str,
    transport: str,
) -> None:
    log.info(
        "bootstrap_prepare_console_started",
        extra={
            "lab_path": lab_path,
            "node_name": node_name,
            "flow_ref": flow_ref,
            "transport": transport,
        },
    )


def _build_prepare_context(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
    flow_ref: str,
    transport: str,
    variables: dict[str, str] | None,
    console_session_factory: ConsoleSessionFactory | None,
) -> _PrepareContext:
    node = eve_ng_client.get_node_by_name(lab_path, node_name)
    if node.console is None:
        raise console_url_missing_error(lab_path=lab_path, node_name=node_name)

    selected_transport = select_console_transport(node, transport)
    flow = load_flow(flow_ref)
    flow_variables = variables if variables is not None else resolve_flow_variables(flow)
    session_factory = console_session_factory or create_console_session
    session = session_factory(console=node.console, transport=selected_transport)

    return _PrepareContext(
        node=node,
        console=node.console,
        transport=selected_transport,
        flow=flow,
        flow_ref=flow_ref,
        variables=flow_variables,
        session=session,
    )


async def _run_prepare_context(
    *,
    context: _PrepareContext,
    detect_console_timeout_seconds: float,
) -> FlowRunResult:
    await context.session.connect()
    try:
        return await run_flow(
            context.flow,
            context.session,
            variables=context.variables,
            detection_timeout_seconds=detect_console_timeout_seconds,
        )
    finally:
        await context.session.close()


def _build_prepare_result(
    *,
    context: _PrepareContext,
    preparation: FlowRunResult,
    duration_seconds: float,
) -> BootstrapConsolePrepareResult:
    return BootstrapConsolePrepareResult(
        node=context.node.name,
        console=BootstrapConsoleEndpoint.from_domain(context.console),
        flow=context.flow_ref,
        transport=context.transport,
        result=BootstrapPreparationResult.from_domain(preparation),
        duration_seconds=duration_seconds,
    )


def _log_prepare_completed(
    *,
    lab_path: str,
    node_name: str,
    result: BootstrapConsolePrepareResult,
) -> None:
    log.info(
        "bootstrap_prepare_console_completed",
        extra={
            "lab_path": lab_path,
            "node_name": node_name,
            "ready": result.result.ready,
            "duration_seconds": result.duration_seconds,
        },
    )


def _log_apply_started(
    *,
    lab_path: str,
    node_name: str,
    config_path: Path,
    flow_ref: str,
    transport: str,
) -> None:
    log.info(
        "bootstrap_apply_rendered_config_started",
        extra={
            "lab_path": lab_path,
            "node_name": node_name,
            "config_path": str(config_path),
            "flow_ref": flow_ref,
            "transport": transport,
        },
    )


def _build_config_apply_context(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
    config_path: Path,
    flow_ref: str,
    transport: str,
    variables: dict[str, str] | None,
    console_session_factory: ConsoleSessionFactory | None,
) -> _ConfigApplyContext:
    node = eve_ng_client.get_node_by_name(lab_path, node_name)
    if node.console is None:
        raise console_url_missing_error(lab_path=lab_path, node_name=node_name)

    selected_transport = select_console_transport(node, transport)
    flow = load_flow(flow_ref)
    flow_variables = variables if variables is not None else resolve_flow_variables(flow)
    lines = load_config_lines(config_path)
    session_factory = console_session_factory or create_console_session
    session = session_factory(console=node.console, transport=selected_transport)

    return _ConfigApplyContext(
        node=node,
        console=node.console,
        transport=selected_transport,
        flow=flow,
        flow_ref=flow_ref,
        variables=flow_variables,
        lines=lines,
        session=session,
    )


async def _run_config_apply_context(
    *,
    context: _ConfigApplyContext,
    detect_console_timeout_seconds: float,
    config_read_timeout_seconds: float,
    line_ending: str,
) -> tuple[FlowRunResult, ConfigApplyResult]:
    await context.session.connect()
    try:
        preparation = await _run_preparation(
            context=context,
            detect_console_timeout_seconds=detect_console_timeout_seconds,
        )
        _assert_ready_for_config_apply(preparation)
        config_apply = await _apply_config(
            context=context,
            line_ending=line_ending,
            read_timeout_seconds=config_read_timeout_seconds,
        )
        return preparation, config_apply
    finally:
        await context.session.close()


async def _run_preparation(
    *,
    context: _ConfigApplyContext,
    detect_console_timeout_seconds: float,
) -> FlowRunResult:
    return await run_flow(
        context.flow,
        context.session,
        variables=context.variables,
        detection_timeout_seconds=detect_console_timeout_seconds,
    )


def _assert_ready_for_config_apply(preparation: FlowRunResult) -> None:
    if preparation.ready:
        return

    raise bootstrap_config_apply_error(
        reason="console_not_ready",
        details={
            "flow_name": preparation.flow_name,
            "final_state": preparation.final_state,
        },
    )


async def _apply_config(
    *,
    context: _ConfigApplyContext,
    line_ending: str,
    read_timeout_seconds: float,
) -> ConfigApplyResult:
    return await apply_config_lines(
        lines=context.lines,
        console=context.session,
        line_ending=line_ending,
        read_timeout_seconds=read_timeout_seconds,
    )


def _build_config_apply_result(
    *,
    context: _ConfigApplyContext,
    preparation: FlowRunResult,
    config_apply: ConfigApplyResult,
    config_path: Path,
    duration_seconds: float,
) -> BootstrapConfigApplyResult:
    return BootstrapConfigApplyResult(
        node=context.node.name,
        console=BootstrapConsoleEndpoint.from_domain(context.console),
        flow=context.flow_ref,
        transport=context.transport,
        config_path=str(config_path),
        prepared=preparation.ready,
        preparation=BootstrapPreparationResult.from_domain(preparation),
        config_apply=BootstrapConfigApplySummary.from_domain(config_apply),
        duration_seconds=duration_seconds,
    )


def _log_apply_completed(
    *,
    lab_path: str,
    node_name: str,
    result: BootstrapConfigApplyResult,
) -> None:
    log.info(
        "bootstrap_apply_rendered_config_completed",
        extra={
            "lab_path": lab_path,
            "node_name": node_name,
            "commands_sent": result.config_apply.commands_sent,
            "duration_seconds": result.duration_seconds,
        },
    )


def select_console_transport(node: EveNgNode, requested_transport: str) -> str:
    """Select the console transport for a node."""

    normalized_transport = requested_transport.lower()
    if normalized_transport not in {
        TRANSPORT_AUTO,
        TRANSPORT_TELNET,
        TRANSPORT_RAW_TCP,
    }:
        raise bootstrap_config_apply_error(
            reason="unsupported_transport",
            details={"transport": requested_transport},
        )

    if normalized_transport != TRANSPORT_AUTO:
        return normalized_transport

    if (node.type or "").lower() == "dynamips":
        return TRANSPORT_RAW_TCP

    return TRANSPORT_TELNET


def create_console_session(
    *,
    console: ConsoleEndpoint,
    transport: str,
) -> AsyncConsoleSession:
    """Create the default console session for a selected transport."""

    if transport == TRANSPORT_RAW_TCP:
        return RawTcpConsoleSession(host=console.host, port=console.port)
    return TelnetConsoleSession(host=console.host, port=console.port)
