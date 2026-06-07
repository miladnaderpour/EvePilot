from evepilot.core.schemas import ServiceError, ServiceMeta, ServiceResult
from evepilot.core.version import APP_NAME, APP_VERSION


def test_service_result_success_shape() -> None:
    result = ServiceResult[dict[str, str]](
        ok=True,
        code="nodes.get.completed",
        data={"node": "CSR-1"},
        meta=ServiceMeta(duration_seconds=1.25),
    )

    payload = result.model_dump(mode="json")

    assert payload["ok"] is True
    assert payload["code"] == "nodes.get.completed"
    assert payload["data"] == {"node": "CSR-1"}
    assert payload["error"] is None
    assert payload["meta"]["service"] == APP_NAME
    assert payload["meta"]["version"] == APP_VERSION
    assert payload["meta"]["duration_seconds"] == 1.25
    assert payload["meta"]["request_id"] is None
    assert isinstance(payload["meta"]["timestamp"], str)


def test_service_result_error_shape() -> None:
    result = ServiceResult[dict[str, object]](
        ok=False,
        code="bootstrap.config_apply_failed",
        error=ServiceError(
            code="bootstrap.config_apply_failed",
            message="Bootstrap config apply failed.",
            details={"reason": "config_file_not_found"},
            status_code=400,
        ),
        meta=ServiceMeta(duration_seconds=0.2, request_id="req-1"),
    )

    payload = result.model_dump(mode="json")

    assert payload["ok"] is False
    assert payload["data"] is None
    assert payload["error"] == {
        "code": "bootstrap.config_apply_failed",
        "message": "Bootstrap config apply failed.",
        "details": {"reason": "config_file_not_found"},
        "status_code": 400,
    }
    assert payload["meta"]["request_id"] == "req-1"
