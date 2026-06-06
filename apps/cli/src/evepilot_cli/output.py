"""CLI JSON output helpers."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypeVar

import typer

from evepilot.core.exceptions import EvePilotError
from evepilot.eve_ng.client import EveNgClient
from evepilot_cli.runtime import create_eve_ng_client, load_runtime_settings

JsonResult = TypeVar("JsonResult")


def echo_json(payload: object) -> None:
    """Print a JSON payload to stdout."""

    typer.echo(json.dumps(payload, indent=2))


def echo_error(error: EvePilotError) -> None:
    """Print a JSON error payload to stderr."""

    typer.echo(json.dumps({"error": error.to_dict()}, indent=2), err=True)


def run_eve_ng_json_command(command: Callable[[EveNgClient], JsonResult]) -> None:
    """Run an EVE-NG command and print JSON output."""

    settings = load_runtime_settings()
    client = create_eve_ng_client(settings)
    try:
        client.login()
        echo_json(command(client))
    except EvePilotError as exc:
        echo_error(exc)
        raise typer.Exit(code=1) from exc
