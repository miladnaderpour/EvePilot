"""EvePilot command-line interface."""

import typer

from evepilot_cli.commands import bootstrap
from evepilot_cli.commands import nodes
from evepilot_cli.output import OutputFormat

app = typer.Typer(no_args_is_help=True)
app.add_typer(bootstrap.app, name="bootstrap")
app.add_typer(nodes.app, name="nodes")


@app.command("node-console", hidden=True)
def node_console(
    lab: str = typer.Option(..., "--lab", help="EVE-NG lab path."),
    node: str = typer.Option(..., "--node", help="EVE-NG node name."),
    output_format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        help="Output format: json or text.",
    ),
) -> None:
    """Return the console endpoint for one EVE-NG node."""

    nodes.node_console_payload(lab, node, output_format=output_format)
