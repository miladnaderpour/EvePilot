"""CLI runtime helpers."""

from evepilot.core.config import Settings, get_settings
from evepilot.core.logging import setup_logging
from evepilot.eve_ng.client import EveNgClient


def load_runtime_settings() -> Settings:
    """Load settings and configure runtime services."""

    settings = get_settings()
    setup_logging(settings)
    return settings


def create_eve_ng_client(settings: Settings) -> EveNgClient:
    """Create an EVE-NG client from settings."""

    return EveNgClient.from_settings(settings)
