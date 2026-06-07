"""Public schemas for EVE-NG node discovery."""

from pydantic import BaseModel

from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.models import EveNgNode


class EveNgConsoleEndpoint(BaseModel):
    """Public console endpoint schema."""

    protocol: str
    host: str
    port: int

    @classmethod
    def from_domain(cls, console: ConsoleEndpoint) -> "EveNgConsoleEndpoint":
        """Build a schema from a core console endpoint."""

        return cls(protocol=console.protocol, host=console.host, port=console.port)


class EveNgNodeResult(BaseModel):
    """Public EVE-NG node schema."""

    id: int
    name: str
    status: int | None = None
    type: str | None = None
    url: str | None = None
    console: EveNgConsoleEndpoint | None = None

    @classmethod
    def from_domain(cls, node: EveNgNode) -> "EveNgNodeResult":
        """Build a schema from an internal EVE-NG node."""

        return cls(
            id=node.id,
            name=node.name,
            status=node.status,
            type=node.type,
            url=node.url,
            console=(
                EveNgConsoleEndpoint.from_domain(node.console)
                if node.console is not None
                else None
            ),
        )


class EveNgNodesResult(BaseModel):
    """Public result for listing EVE-NG nodes."""

    nodes: list[EveNgNodeResult]


class EveNgNodeConsoleResult(BaseModel):
    """Public result for one EVE-NG node console endpoint."""

    node: str
    console: EveNgConsoleEndpoint
