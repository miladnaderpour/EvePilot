import pytest

from evepilot.eve_ng.console import parse_console_url
from evepilot.eve_ng.errors import EveNgConsoleError


def test_parse_console_url() -> None:
    endpoint = parse_console_url("telnet://10.1.2.3:32769")

    assert endpoint.protocol == "telnet"
    assert endpoint.host == "10.1.2.3"
    assert endpoint.port == 32769


def test_parse_html5_console_url() -> None:
    endpoint = parse_console_url(
        "/html5/#/client/MzI3NjkAYwBteXNxbA==?token=example",
        fallback_host="10.1.2.3",
        fallback_protocol="telnet",
    )

    assert endpoint.protocol == "telnet"
    assert endpoint.host == "10.1.2.3"
    assert endpoint.port == 32769


def test_parse_console_url_rejects_missing_port() -> None:
    with pytest.raises(EveNgConsoleError) as exc_info:
        parse_console_url("telnet://10.1.2.3")

    assert exc_info.value.code == "eve_ng.console_url_invalid"
    assert exc_info.value.details["reason"] == "missing_port"
