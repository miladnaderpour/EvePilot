"""Public schemas for bootstrap flow management."""

from pydantic import BaseModel

from evepilot.bootstrap.preparation.models import FlowSummary


class BootstrapFlowSummary(BaseModel):
    """Public summary of an available bootstrap flow."""

    name: str
    source: str
    version: int
    description: str | None = None

    @classmethod
    def from_domain(cls, flow: FlowSummary) -> "BootstrapFlowSummary":
        """Build a schema from an internal flow summary."""

        return cls(
            name=flow.name,
            source=flow.source,
            version=flow.version,
            description=flow.description,
        )


class BootstrapFlowListResult(BaseModel):
    """Public result for listing bootstrap flows."""

    source: str
    flows: list[BootstrapFlowSummary]


class BootstrapFlowShowResult(BaseModel):
    """Public result for reading a bootstrap flow definition."""

    source: str
    text: str


class BootstrapFlowExportResult(BaseModel):
    """Public result for exporting a bootstrap flow definition."""

    source: str
    output: str
