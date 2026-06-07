"""CLI runtime helpers."""

from collections.abc import Callable
from typing import TypeVar

from evepilot.core.config import Settings, get_settings
from evepilot.core.logging import setup_logging
from evepilot.eve_ng.client import EveNgClient

T = TypeVar("T")


def load_runtime_settings() -> Settings:
    """Load settings and configure runtime services."""

    settings = get_settings()
    setup_logging(settings)
    return settings


def create_eve_ng_client(settings: Settings) -> EveNgClient:
    """Create an EVE-NG client from settings."""

    return EveNgClient.from_settings(settings)


def run_with_eve_ng_client(command: Callable[[EveNgClient], T]) -> T:
    """Create an EVE-NG client, log in, and run a command."""

    settings = load_runtime_settings()
    client = create_eve_ng_client(settings)
    client.login()
    return command(client)
