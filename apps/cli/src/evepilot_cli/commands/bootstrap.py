"""Bootstrap preparation commands."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

from evepilot.bootstrap.service import apply_rendered_config
from evepilot.bootstrap.service import export_flow as export_flow_service
from evepilot.bootstrap.service import list_flows as list_flows_service
from evepilot.bootstrap.service import prepare_console
from evepilot.bootstrap.service import show_flow as show_flow_service
from evepilot.eve_ng.client import EveNgClient
from evepilot_cli.output import OutputFormat
from evepilot_cli.output import run_json_command
from evepilot_cli.runtime import run_with_eve_ng_client

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
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Prepare a node console using a bootstrap flow."""

    def command(client: EveNgClient) -> dict[str, object]:
        result = asyncio.run(
            prepare_console(
                eve_ng_client=client,
                lab_path=lab,
                node_name=node,
                flow_ref=flow,
                transport=transport,
                detect_console_timeout_seconds=detect_console_timeout,
            )
        )
        return result.model_dump(mode="json")

    run_json_command(
        code="bootstrap.prepare.completed",
        command=lambda: run_with_eve_ng_client(command),
        output_format=output_format,
    )


@app.command("apply")
def apply_config(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
    file: Path = typer.Option(..., "--file", help="Rendered config file path."),
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
    config_read_timeout: float = typer.Option(
        3.0,
        "--config-read-timeout",
        help="Seconds to read console output after each config line.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Prepare a node console and apply a rendered config file."""

    def command(client: EveNgClient) -> dict[str, object]:
        result = asyncio.run(
            apply_rendered_config(
                eve_ng_client=client,
                lab_path=lab,
                node_name=node,
                config_path=file,
                flow_ref=flow,
                transport=transport,
                detect_console_timeout_seconds=detect_console_timeout,
                config_read_timeout_seconds=config_read_timeout,
            )
        )
        return result.model_dump(mode="json")

    run_json_command(
        code="bootstrap.apply.completed",
        command=lambda: run_with_eve_ng_client(command),
        output_format=output_format,
    )


@flow_app.command("list")
def list_flows(
    source: str = typer.Option(
        FLOW_SOURCE_BUILT_IN,
        "--source",
        help="Flow source to list. Currently only built-in is supported.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """List available bootstrap flows."""

    run_json_command(
        code="bootstrap.flow.list.completed",
        command=lambda: list_flows_service(source=source).model_dump(mode="json"),
        output_format=output_format,
    )


@flow_app.command("show")
def show_flow(
    source: str = typer.Argument(..., help="Flow source to show."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Print a bootstrap flow YAML definition."""

    run_json_command(
        code="bootstrap.flow.show.completed",
        command=lambda: show_flow_service(source).model_dump(mode="json"),
        output_format=output_format,
    )


@flow_app.command("export")
def export_flow(
    source: str = typer.Argument(..., help="Flow source to export."),
    output: Path = typer.Option(..., "--output", "-o", help="Output YAML path."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing file."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Export a bootstrap flow YAML definition to a file."""

    run_json_command(
        code="bootstrap.flow.export.completed",
        command=lambda: export_flow_service(
            source=source,
            output=output,
            force=force,
        ).model_dump(mode="json"),
        output_format=output_format,
    )
