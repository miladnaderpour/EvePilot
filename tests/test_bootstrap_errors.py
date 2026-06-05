from evepilot.bootstrap.errors import BootstrapError, BootstrapStateError
from evepilot.bootstrap.errors import bootstrap_unknown_state_error
from evepilot.core.exceptions import EvePilotError


def test_bootstrap_errors_inherit_from_evepilot_error() -> None:
    assert issubclass(BootstrapError, EvePilotError)
    assert issubclass(BootstrapStateError, EvePilotError)


def test_bootstrap_unknown_state_error_shape() -> None:
    error = bootstrap_unknown_state_error(sample="unrecognized")

    assert isinstance(error, BootstrapStateError)
    assert error.code == "bootstrap.unknown_state"
    assert error.message == "Console state could not be detected."
    assert error.details == {"sample": "unrecognized"}
