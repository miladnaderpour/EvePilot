"""EvePilot command-line interface."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

import typer

from evepilot.core.config import get_settings
from evepilot.core.exceptions import EvePilotError
from evepilot.core.logging import setup_logging
from evepilot.eve_ng.client import EveNgClient
from evepilot.eve_ng.errors import console_url_missing_error

app = typer.Typer(no_args_is_help=True)


@app.command("nodes")
def nodes(lab: str = typer.Option(..., "--lab", help="EVE-NG lab path.")) -> None:
    """List nodes for an EVE-NG lab."""

    _run_json_command(lambda client: [node.to_dict() for node in client.get_lab_nodes(lab)])


@app.command("node-console")
def node_console(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
) -> None:
    """Return the console endpoint for one EVE-NG node."""

    def command(client: EveNgClient) -> dict[str, Any]:
        eve_ng_node = client.get_node_by_name(lab, node)
        if eve_ng_node.console is None:
            raise console_url_missing_error(lab_path=lab, node_name=node)
        return {
            "node": eve_ng_node.name,
            "console": asdict(eve_ng_node.console),
        }

    _run_json_command(command)


def _run_json_command(command: Any) -> None:
    settings = get_settings()
    setup_logging(settings)
    client = EveNgClient.from_settings(settings)
    try:
        client.login()
        typer.echo(json.dumps(command(client), indent=2))
    except EvePilotError as exc:
        typer.echo(json.dumps({"error": exc.to_dict()}, indent=2), err=True)
        raise typer.Exit(code=1) from exc
