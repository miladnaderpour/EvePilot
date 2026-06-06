from evepilot.bootstrap.errors import BootstrapError, BootstrapFlowError
from evepilot.bootstrap.errors import bootstrap_flow_invalid_error
from evepilot.core.exceptions import EvePilotError


def test_bootstrap_errors_inherit_from_evepilot_error() -> None:
    assert issubclass(BootstrapError, EvePilotError)
    assert issubclass(BootstrapFlowError, EvePilotError)


def test_bootstrap_flow_invalid_error_shape() -> None:
    error = bootstrap_flow_invalid_error(
        reason="missing_steps",
        details={"flow_name": "example"},
    )

    assert isinstance(error, BootstrapFlowError)
    assert error.code == "bootstrap.flow_invalid"
    assert error.message == "Bootstrap flow definition is invalid."
    assert error.details == {"reason": "missing_steps", "flow_name": "example"}
