"""Node discovery commands."""

from __future__ import annotations

import typer

from evepilot.eve_ng.service import get_node as get_eve_ng_node
from evepilot.eve_ng.service import get_node_console
from evepilot.eve_ng.service import list_nodes
from evepilot_cli.output import OutputFormat
from evepilot_cli.output import run_json_command
from evepilot_cli.runtime import run_with_eve_ng_client

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def nodes_group(
    ctx: typer.Context,
    lab: str | None = typer.Option(None, "--lab", help="EVE-NG lab path."),
) -> None:
    """Work with lab nodes."""

    if ctx.invoked_subcommand is not None:
        return

    if lab is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    all_nodes(lab)


@app.command("all")
def all_nodes(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """List nodes for an EVE-NG lab."""

    run_json_command(
        code="nodes.all.completed",
        command=lambda: run_with_eve_ng_client(
            lambda client: list_nodes(
                eve_ng_client=client,
                lab_path=lab,
            ).model_dump(mode="json")
        ),
        output_format=output_format,
    )


@app.command("get")
def get_node(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Return one EVE-NG node."""

    run_json_command(
        code="nodes.get.completed",
        command=lambda: run_with_eve_ng_client(
            lambda client: get_eve_ng_node(
                eve_ng_client=client,
                lab_path=lab,
                node_name=node,
            ).model_dump(mode="json")
        ),
        output_format=output_format,
    )


def node_console_payload(
    lab: str,
    node: str,
    output_format: OutputFormat = OutputFormat.JSON,
) -> None:
    """Return the console endpoint for one EVE-NG node."""

    run_json_command(
        code="nodes.console.completed",
        command=lambda: run_with_eve_ng_client(
            lambda client: get_node_console(
                eve_ng_client=client,
                lab_path=lab,
                node_name=node,
            ).model_dump(mode="json")
        ),
        output_format=output_format,
    )
