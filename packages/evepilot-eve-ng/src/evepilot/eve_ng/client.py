"""Small EVE-NG API client."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote, urlparse

import requests
from pydantic import SecretStr

from evepilot.core.config import Settings
from evepilot.core.logging import get_logger
from evepilot.eve_ng.errors import (
    auth_failed_error,
    invalid_response_error,
    lab_not_found_error,
    node_not_found_error,
    request_failed_error,
)
from evepilot.eve_ng.models import EveNgNode

log = get_logger(__name__)


class EveNgClient:
    """Client for the EVE-NG API operations needed by the first milestone."""

    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: SecretStr | str,
        verify_ssl: bool = False,
        timeout_seconds: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    @classmethod
    def from_settings(cls, settings: Settings) -> "EveNgClient":
        """Create a client from EvePilot settings."""

        return cls(
            base_url=settings.eve_ng_url,
            username=settings.eve_ng_username,
            password=settings.eve_ng_password,
            verify_ssl=settings.eve_ng_verify_ssl,
            timeout_seconds=settings.eve_ng_timeout_seconds,
        )

    def login(self) -> None:
        """Authenticate with EVE-NG."""

        log.debug("eve_ng_login_started", extra={"base_url": self.base_url})
        response = self.session.post(
            self._url("/api/auth/login"),
            json={
                "username": self.username,
                "password": self._password_value(),
                "html5": "-1",
            },
            timeout=self.timeout_seconds,
            verify=self.verify_ssl,
        )
        if response.status_code >= 400:
            raise auth_failed_error(status_code=response.status_code)

    def get_lab_nodes(self, lab_path: str) -> list[EveNgNode]:
        """Fetch nodes from an EVE-NG lab."""

        encoded_lab_path = quote(lab_path.strip("/"), safe="/")
        response = self.session.get(
            self._url(f"/api/labs/{encoded_lab_path}/nodes"),
            timeout=self.timeout_seconds,
            verify=self.verify_ssl,
        )
        if response.status_code == 404:
            raise lab_not_found_error(lab_path=lab_path)
        if response.status_code >= 400:
            raise request_failed_error(
                lab_path=lab_path,
                status_code=response.status_code,
            )

        return parse_nodes_response(response.json(), fallback_host=self._host())

    def get_node_by_name(self, lab_path: str, node_name: str) -> EveNgNode:
        """Fetch a single node by name from an EVE-NG lab."""

        for node in self.get_lab_nodes(lab_path):
            if node.name == node_name:
                return node

        raise node_not_found_error(lab_path=lab_path, node_name=node_name)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _password_value(self) -> str:
        if isinstance(self.password, SecretStr):
            return self.password.get_secret_value()
        return self.password

    def _host(self) -> str | None:
        return urlparse(self.base_url).hostname


def parse_nodes_response(
    payload: Any,
    *,
    fallback_host: str | None = None,
) -> list[EveNgNode]:
    """Parse the nodes portion of an EVE-NG API response."""

    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(data, dict) and "nodes" in data:
        data = data["nodes"]

    if isinstance(data, dict):
        nodes = [
            EveNgNode.from_api(
                node,
                fallback_id=_parse_int_or_none(node_id),
                fallback_host=fallback_host,
            )
            for node_id, node in data.items()
            if isinstance(node, dict)
        ]
    elif isinstance(data, list):
        nodes = [
            EveNgNode.from_api(node, fallback_host=fallback_host)
            for node in data
            if isinstance(node, dict)
        ]
    else:
        raise invalid_response_error()

    return nodes


def _parse_int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
