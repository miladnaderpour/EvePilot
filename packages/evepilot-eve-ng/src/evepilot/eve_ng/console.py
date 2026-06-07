"""Console endpoint parsing."""

import base64

from urllib.parse import urlparse

from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.errors import console_url_invalid_error


def parse_console_url(
    url: str,
    *,
    fallback_host: str | None = None,
    fallback_protocol: str | None = None,
) -> ConsoleEndpoint:
    """Parse an EVE-NG console URL into protocol, host, and port."""

    parsed = urlparse(url)
    if not parsed.scheme:
        return _parse_html5_console_url(
            url,
            fallback_host=fallback_host,
            fallback_protocol=fallback_protocol,
        )
    if not parsed.hostname:
        raise console_url_invalid_error(url=url, reason="missing_host")
    try:
        port = parsed.port
    except ValueError as exc:
        raise console_url_invalid_error(url=url, reason="invalid_port") from exc

    if port is None:
        raise console_url_invalid_error(url=url, reason="missing_port")

    return ConsoleEndpoint(
        protocol=parsed.scheme,
        host=parsed.hostname,
        port=port,
    )


def _parse_html5_console_url(
    url: str,
    *,
    fallback_host: str | None,
    fallback_protocol: str | None,
) -> ConsoleEndpoint:
    if not fallback_host:
        raise console_url_invalid_error(url=url, reason="missing_host")

    encoded_client = _extract_html5_client_token(url)
    if not encoded_client:
        raise console_url_invalid_error(url=url, reason="missing_protocol")

    try:
        decoded = base64.b64decode(encoded_client).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise console_url_invalid_error(url=url, reason="invalid_html5_client") from exc

    parts = [part for part in decoded.split("\x00") if part]
    if not parts:
        raise console_url_invalid_error(url=url, reason="invalid_html5_client")

    try:
        port = int(parts[0])
    except ValueError as exc:
        raise console_url_invalid_error(url=url, reason="invalid_port") from exc

    return ConsoleEndpoint(
        protocol=fallback_protocol or "telnet",
        host=fallback_host,
        port=port,
    )


def _extract_html5_client_token(url: str) -> str | None:
    marker = "/client/"
    if marker not in url:
        return None

    encoded_client = url.split(marker, maxsplit=1)[1]
    encoded_client = encoded_client.split("?", maxsplit=1)[0]
    encoded_client = encoded_client.split("#", maxsplit=1)[0]
    return encoded_client or None
