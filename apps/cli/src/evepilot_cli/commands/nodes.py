"""Node discovery commands."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import typer

from evepilot.eve_ng.client import EveNgClient
from evepilot.eve_ng.errors import console_url_missing_error
from evepilot_cli.output import run_eve_ng_json_command

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
def all_nodes(lab: str = typer.Option(..., "--lab", help="EVE-NG lab path.")) -> None:
    """List nodes for an EVE-NG lab."""

    run_eve_ng_json_command(
        lambda client: [node.to_dict() for node in client.get_lab_nodes(lab)]
    )


@app.command("get")
def get_node(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
) -> None:
    """Return one EVE-NG node."""

    run_eve_ng_json_command(lambda client: client.get_node_by_name(lab, node).to_dict())


def node_console_payload(lab: str, node: str) -> None:
    """Return the console endpoint for one EVE-NG node."""

    def command(client: EveNgClient) -> dict[str, Any]:
        eve_ng_node = client.get_node_by_name(lab, node)
        if eve_ng_node.console is None:
            raise console_url_missing_error(lab_path=lab, node_name=node)
        return {
            "node": eve_ng_node.name,
            "console": asdict(eve_ng_node.console),
        }

    run_eve_ng_json_command(command)
