"""Bootstrap-specific errors and error factories."""

from evepilot.core.exceptions import EvePilotError


class BootstrapError(EvePilotError):
    """Base error for bootstrap failures."""


class BootstrapFlowError(BootstrapError):
    """Bootstrap flow definition or loading error."""


class BootstrapFlowRunError(BootstrapError):
    """Bootstrap flow execution error."""


class BootstrapConsoleError(BootstrapError):
    """Bootstrap console transport error."""


def bootstrap_flow_invalid_error(
    *,
    reason: str,
    details: dict[str, object] | None = None,
) -> BootstrapFlowError:
    """Build the error used when a bootstrap flow definition is invalid."""

    return BootstrapFlowError(
        code="bootstrap.flow_invalid",
        message="Bootstrap flow definition is invalid.",
        details={"reason": reason, **(details or {})},
    )


def bootstrap_flow_not_found_error(*, source: str) -> BootstrapFlowError:
    """Build the error used when a bootstrap flow cannot be found."""

    return BootstrapFlowError(
        code="bootstrap.flow_not_found",
        message="Bootstrap flow could not be found.",
        details={"source": source},
    )


def bootstrap_flow_ambiguous_state_error(
    *,
    state_names: list[str],
    sample: str,
) -> BootstrapFlowError:
    """Build the error used when multiple flow states match console output."""

    return BootstrapFlowError(
        code="bootstrap.flow_state_ambiguous",
        message="Multiple bootstrap flow states matched console output.",
        details={"state_names": state_names, "sample": sample},
    )


def bootstrap_flow_run_error(
    *,
    reason: str,
    details: dict[str, object] | None = None,
) -> BootstrapFlowRunError:
    """Build the error used when a bootstrap flow cannot continue."""

    return BootstrapFlowRunError(
        code="bootstrap.flow_run_failed",
        message="Bootstrap flow execution failed.",
        details={"reason": reason, **(details or {})},
    )


def bootstrap_console_error(
    *,
    reason: str,
    details: dict[str, object] | None = None,
) -> BootstrapConsoleError:
    """Build the error used when console transport fails."""

    return BootstrapConsoleError(
        code="bootstrap.console_failed",
        message="Bootstrap console transport failed.",
        details={"reason": reason, **(details or {})},
    )
