"""EVE-NG domain models."""

from dataclasses import asdict, dataclass
from typing import Any

from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.console import parse_console_url


@dataclass(frozen=True, slots=True)
class EveNgNode:
    """EVE-NG lab node with optional parsed console endpoint."""

    id: int
    name: str
    status: int | None = None
    type: str | None = None
    url: str | None = None
    console: ConsoleEndpoint | None = None

    @classmethod
    def from_api(
        cls,
        payload: dict[str, Any],
        *,
        fallback_id: int | None = None,
        fallback_host: str | None = None,
    ) -> "EveNgNode":
        """Build a node model from an EVE-NG API node payload."""

        node_id = int(payload.get("id", fallback_id if fallback_id is not None else 0))
        url = _optional_str(payload.get("url"))
        console_protocol = _optional_str(payload.get("console"))
        console = (
            parse_console_url(
                url,
                fallback_host=fallback_host,
                fallback_protocol=console_protocol,
            )
            if url
            else None
        )

        return cls(
            id=node_id,
            name=str(payload.get("name", "")),
            status=_optional_int(payload.get("status")),
            type=_optional_str(payload.get("type")),
            url=url,
            console=console,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)


def _optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
