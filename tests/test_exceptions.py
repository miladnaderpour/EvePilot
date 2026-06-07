from evepilot.core.exceptions import EvePilotError


def test_error_shape_includes_code_message_details_and_status() -> None:
    error = EvePilotError(
        code="eve_ng.request_failed",
        message="Request failed.",
        details={"status_code": 500},
        status_code=500,
    )

    assert str(error) == "Request failed."
    assert error.to_dict() == {
        "code": "eve_ng.request_failed",
        "message": "Request failed.",
        "details": {"status_code": 500},
        "status_code": 500,
    }
