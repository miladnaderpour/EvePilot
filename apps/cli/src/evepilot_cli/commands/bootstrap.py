"""Bootstrap preparation commands."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path

import typer

from evepilot.bootstrap.preparation.flow_loader import list_builtin_flows, load_flow
from evepilot.bootstrap.preparation.flow_loader import read_builtin_flow_text
from evepilot.bootstrap.preparation.flow_runner import run_flow
from evepilot.bootstrap.preparation.models import FlowDefinition, FlowRunResult
from evepilot.bootstrap.preparation.variables import resolve_flow_variables
from evepilot.bootstrap.transport.console import (
    RawTcpConsoleSession,
    TelnetConsoleSession,
)
from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.client import EveNgClient
from evepilot.eve_ng.errors import console_url_missing_error
from evepilot.eve_ng.models import EveNgNode
from evepilot_cli.output import run_eve_ng_json_command
from evepilot_cli.output import echo_json

DEFAULT_FLOW = "built-in:cisco-router-first-boot"
TRANSPORT_AUTO = "auto"
TRANSPORT_TELNET = "telnet"
TRANSPORT_RAW_TCP = "raw-tcp"
FLOW_SOURCE_BUILT_IN = "built-in"

app = typer.Typer(no_args_is_help=True, help="Bootstrap preparation commands.")
flow_app = typer.Typer(no_args_is_help=True, help="Bootstrap flow commands.")
app.add_typer(flow_app, name="flow")


@app.command("prepare")
def prepare(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
    flow: str = typer.Option(DEFAULT_FLOW, "--flow", help="Bootstrap flow source."),
    transport: str = typer.Option(
        TRANSPORT_AUTO,
        "--transport",
        help="Console transport: auto, telnet, or raw-tcp.",
    ),
    detect_console_timeout: float = typer.Option(
        120.0,
        "--detect-console-timeout",
        "--timeout",
        help="Seconds to wait for a flow-defined console state.",
    ),
) -> None:
    """Prepare a node console using a bootstrap flow."""

    def command(client: EveNgClient) -> dict[str, object]:
        eve_ng_node = client.get_node_by_name(lab, node)
        if eve_ng_node.console is None:
            raise console_url_missing_error(lab_path=lab, node_name=node)

        flow_definition = load_flow(flow)
        variables = resolve_flow_variables(flow_definition)
        selected_transport = select_console_transport(eve_ng_node, transport)
        result = asyncio.run(
            _run_prepare_flow(
                console=eve_ng_node.console,
                flow_definition=flow_definition,
                variables=variables,
                transport=selected_transport,
                detect_console_timeout=detect_console_timeout,
            )
        )
        return {
            "node": eve_ng_node.name,
            "console": asdict(eve_ng_node.console),
            "flow": flow,
            "transport": selected_transport,
            "result": asdict(result),
        }

    run_eve_ng_json_command(command)


@flow_app.command("list")
def list_flows(
    source: str = typer.Option(
        FLOW_SOURCE_BUILT_IN,
        "--source",
        help="Flow source to list. Currently only built-in is supported.",
    ),
) -> None:
    """List available bootstrap flows."""

    if source != FLOW_SOURCE_BUILT_IN:
        raise typer.BadParameter("Only built-in flow listing is supported.")

    echo_json([asdict(flow) for flow in list_builtin_flows()])


@flow_app.command("show")
def show_flow(source: str = typer.Argument(..., help="Flow source to show.")) -> None:
    """Print a bootstrap flow YAML definition."""

    typer.echo(_read_flow_text(source))


@flow_app.command("export")
def export_flow(
    source: str = typer.Argument(..., help="Flow source to export."),
    output: Path = typer.Option(..., "--output", "-o", help="Output YAML path."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing file."),
) -> None:
    """Export a bootstrap flow YAML definition to a file."""

    text = _read_flow_text(source)
    if output.exists() and not force:
        raise typer.BadParameter(f"Output file already exists: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    echo_json({"source": source, "output": str(output)})


async def _run_prepare_flow(
    *,
    console: ConsoleEndpoint,
    flow_definition: FlowDefinition,
    variables: dict[str, str],
    transport: str,
    detect_console_timeout: float,
) -> FlowRunResult:
    async with _console_session(console=console, transport=transport) as session:
        return await run_flow(
            flow_definition,
            session,
            variables=variables,
            detection_timeout_seconds=detect_console_timeout,
        )


def select_console_transport(node: EveNgNode, requested_transport: str) -> str:
    """Select the console transport for a node."""

    normalized_transport = requested_transport.lower()
    if normalized_transport not in {
        TRANSPORT_AUTO,
        TRANSPORT_TELNET,
        TRANSPORT_RAW_TCP,
    }:
        raise typer.BadParameter("Transport must be auto, telnet, or raw-tcp.")

    if normalized_transport != TRANSPORT_AUTO:
        return normalized_transport

    if (node.type or "").lower() == "dynamips":
        return TRANSPORT_RAW_TCP

    return TRANSPORT_TELNET


def _read_flow_text(source: str) -> str:
    if not source.startswith("built-in:"):
        raise typer.BadParameter("Only built-in flow sources are supported.")
    flow_name = source.removeprefix("built-in:")
    return read_builtin_flow_text(flow_name)


def _console_session(
    *,
    console: ConsoleEndpoint,
    transport: str,
) -> RawTcpConsoleSession | TelnetConsoleSession:
    if transport == TRANSPORT_RAW_TCP:
        return RawTcpConsoleSession(host=console.host, port=console.port)
    return TelnetConsoleSession(host=console.host, port=console.port)
