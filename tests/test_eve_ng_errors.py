from evepilot.eve_ng.errors import (
    EveNgAuthError,
    EveNgConsoleError,
    EveNgNotFoundError,
    auth_failed_error,
    console_url_missing_error,
    lab_not_found_error,
    node_not_found_error,
)


def test_auth_failed_error_shape() -> None:
    error = auth_failed_error(status_code=401)

    assert isinstance(error, EveNgAuthError)
    assert error.code == "eve_ng.auth_failed"
    assert error.message == "Failed to authenticate to EVE-NG."
    assert error.details == {"status_code": 401}
    assert error.status_code == 401


def test_lab_not_found_error_shape() -> None:
    error = lab_not_found_error(lab_path="EIGRP/Basics.unl")

    assert isinstance(error, EveNgNotFoundError)
    assert error.code == "eve_ng.lab_not_found"
    assert error.message == "EVE-NG lab was not found."
    assert error.details == {"lab_path": "EIGRP/Basics.unl"}
    assert error.status_code == 404


def test_node_not_found_error_shape() -> None:
    error = node_not_found_error(
        lab_path="EIGRP/Basics.unl",
        node_name="CSR-1",
    )

    assert isinstance(error, EveNgNotFoundError)
    assert error.code == "eve_ng.node_not_found"
    assert error.details == {
        "lab_path": "EIGRP/Basics.unl",
        "node_name": "CSR-1",
    }


def test_console_url_missing_error_shape() -> None:
    error = console_url_missing_error(
        lab_path="EIGRP/Basics.unl",
        node_name="CSR-1",
    )

    assert isinstance(error, EveNgConsoleError)
    assert error.code == "eve_ng.console_url_missing"
    assert error.message == "EVE-NG node does not have a console URL."
