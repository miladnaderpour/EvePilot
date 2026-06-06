"""EvePilot command-line interface."""

import typer

from evepilot_cli.commands import bootstrap
from evepilot_cli.commands import nodes

app = typer.Typer(no_args_is_help=True)
app.add_typer(bootstrap.app, name="bootstrap")
app.add_typer(nodes.app, name="nodes")


@app.command("node-console", hidden=True)
def node_console(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
) -> None:
    """Return the console endpoint for one EVE-NG node."""

    nodes.node_console_payload(lab, node)
