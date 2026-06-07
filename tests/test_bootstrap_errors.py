from evepilot.bootstrap.errors import BootstrapConfigApplyError, BootstrapError
from evepilot.bootstrap.errors import BootstrapFlowError
from evepilot.bootstrap.errors import BootstrapFlowServiceError
from evepilot.bootstrap.errors import bootstrap_config_apply_error
from evepilot.bootstrap.errors import bootstrap_flow_invalid_error
from evepilot.bootstrap.errors import bootstrap_flow_service_error
from evepilot.core.exceptions import EvePilotError


def test_bootstrap_errors_inherit_from_evepilot_error() -> None:
    assert issubclass(BootstrapError, EvePilotError)
    assert issubclass(BootstrapFlowError, EvePilotError)
    assert issubclass(BootstrapConfigApplyError, EvePilotError)
    assert issubclass(BootstrapFlowServiceError, EvePilotError)


def test_bootstrap_flow_invalid_error_shape() -> None:
    error = bootstrap_flow_invalid_error(
        reason="missing_steps",
        details={"flow_name": "example"},
    )

    assert isinstance(error, BootstrapFlowError)
    assert error.code == "bootstrap.flow_invalid"
    assert error.message == "Bootstrap flow definition is invalid."
    assert error.details == {"reason": "missing_steps", "flow_name": "example"}


def test_bootstrap_config_apply_error_shape() -> None:
    error = bootstrap_config_apply_error(
        reason="config_file_not_found",
        details={"path": "missing.txt"},
    )

    assert isinstance(error, BootstrapConfigApplyError)
    assert error.code == "bootstrap.config_apply_failed"
    assert error.message == "Bootstrap config apply failed."
    assert error.details == {
        "reason": "config_file_not_found",
        "path": "missing.txt",
    }


def test_bootstrap_flow_service_error_shape() -> None:
    error = bootstrap_flow_service_error(
        reason="unsupported_flow_source",
        details={"source": "custom"},
    )

    assert isinstance(error, BootstrapFlowServiceError)
    assert error.code == "bootstrap.flow_service_failed"
    assert error.message == "Bootstrap flow service action failed."
    assert error.details == {
        "reason": "unsupported_flow_source",
        "source": "custom",
    }
