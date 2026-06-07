from typing import Any

from evepilot.eve_ng.client import EveNgClient


class FakeResponse:
    def __init__(self, *, status_code: int = 200, payload: object | None = None) -> None:
        self.status_code = status_code
        self.payload = payload or {}

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self) -> None:
        self.post_calls: list[dict[str, Any]] = []

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        self.post_calls.append({"url": url, **kwargs})
        return FakeResponse()


def test_login_sends_eve_ng_html5_payload() -> None:
    session = FakeSession()
    client = EveNgClient(
        base_url="http://10.1.2.3",
        username="admin",
        password="eve",
        session=session,
    )

    client.login()

    assert session.post_calls == [
        {
            "url": "http://10.1.2.3/api/auth/login",
            "json": {
                "username": "admin",
                "password": "eve",
                "html5": "-1",
            },
            "timeout": 10.0,
            "verify": False,
        }
    ]
