"""Public schemas for rendered config apply workflows."""

from pydantic import BaseModel

from evepilot.bootstrap.config_apply.models import ConfigApplyResult
from evepilot.bootstrap.preparation.models import FlowRunResult
from evepilot.core.models import ConsoleEndpoint


class BootstrapConsoleEndpoint(BaseModel):
    """Console endpoint used for bootstrap operations."""

    protocol: str
    host: str
    port: int

    @classmethod
    def from_domain(cls, console: ConsoleEndpoint) -> "BootstrapConsoleEndpoint":
        """Build a schema from a core console endpoint."""

        return cls(protocol=console.protocol, host=console.host, port=console.port)


class BootstrapPreparationResult(BaseModel):
    """Public preparation result schema."""

    flow_name: str
    final_state: str | None
    actions: list[str]
    output_sample: str
    ready: bool

    @classmethod
    def from_domain(cls, result: FlowRunResult) -> "BootstrapPreparationResult":
        """Build a schema from an internal flow result."""

        return cls(
            flow_name=result.flow_name,
            final_state=result.final_state,
            actions=result.actions,
            output_sample=result.output_sample,
            ready=result.ready,
        )


class BootstrapConfigApplySummary(BaseModel):
    """Public summary of the config apply phase."""

    commands_total: int
    commands_sent: int
    ready: bool
    final_state: str | None
    apply_duration_seconds: float | None

    @classmethod
    def from_domain(cls, result: ConfigApplyResult) -> "BootstrapConfigApplySummary":
        """Build a schema from an internal config apply result."""

        return cls(
            commands_total=result.commands_total,
            commands_sent=result.commands_sent,
            ready=result.ready,
            final_state=result.final_state,
            apply_duration_seconds=result.apply_duration_seconds,
        )


class BootstrapConfigApplyResult(BaseModel):
    """Public service result for applying a rendered config file."""

    node: str
    console: BootstrapConsoleEndpoint
    flow: str
    transport: str
    config_path: str
    prepared: bool
    preparation: BootstrapPreparationResult
    config_apply: BootstrapConfigApplySummary
    duration_seconds: float


class BootstrapConsolePrepareResult(BaseModel):
    """Public service result for preparing a console with a bootstrap flow."""

    node: str
    console: BootstrapConsoleEndpoint
    flow: str
    transport: str
    result: BootstrapPreparationResult
    duration_seconds: float
