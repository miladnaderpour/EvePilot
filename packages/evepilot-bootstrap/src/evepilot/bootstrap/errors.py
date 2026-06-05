"""Bootstrap-specific errors and error factories."""

from evepilot.core.exceptions import EvePilotError


class BootstrapError(EvePilotError):
    """Base error for bootstrap failures."""


class BootstrapStateError(BootstrapError):
    """Bootstrap console state error."""


def bootstrap_unknown_state_error(*, sample: str = "") -> BootstrapStateError:
    """Build the error used when console state cannot be detected."""

    return BootstrapStateError(
        code="bootstrap.unknown_state",
        message="Console state could not be detected.",
        details={"sample": sample},
    )
