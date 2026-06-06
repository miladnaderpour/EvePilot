"""Console session interface for bootstrap automation."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from inspect import isawaitable
from typing import Any, Protocol

from telnetlib3 import open_connection as get_telnet_connection

from evepilot.bootstrap.errors import bootstrap_console_error
from evepilot.core.logging import get_logger

DEFAULT_READ_BYTES = 4096
DEFAULT_MIN_READ_ATTEMPTS = 3
DEFAULT_READ_DRAIN_TIMEOUT_SECONDS = 0.05
TelnetConnector = Callable[..., Awaitable[tuple[Any, Any]]]
RawTcpConnector = Callable[..., Awaitable[tuple[asyncio.StreamReader, asyncio.StreamWriter]]]
log = get_logger(__name__)


class AsyncConsoleSession(Protocol):
    """Console operations required by bootstrap flow execution."""

    async def connect(self) -> None:
        """Connect to the console transport."""
        ...

    async def read(self, timeout_seconds: float) -> str:
        """Read console output."""
        ...

    async def send(self, text: str) -> None:
        """Send text to the console."""
        ...

    async def close(self) -> None:
        """Close the console transport."""
        ...


class TelnetConsoleSession:
    """Async Telnet console session."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        connect_timeout_seconds: float = 10.0,
        read_bytes: int = DEFAULT_READ_BYTES,
        min_read_attempts: int = DEFAULT_MIN_READ_ATTEMPTS,
        read_drain_timeout_seconds: float = DEFAULT_READ_DRAIN_TIMEOUT_SECONDS,
        connector: TelnetConnector | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.connect_timeout_seconds = connect_timeout_seconds
        self.read_bytes = read_bytes
        self.min_read_attempts = min_read_attempts
        self.read_drain_timeout_seconds = read_drain_timeout_seconds
        self._connector = connector or get_telnet_connection
        self._reader: Any | None = None
        self._writer: Any | None = None

    async def __aenter__(self) -> TelnetConsoleSession:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        await self.close()

    async def connect(self) -> None:
        """Connect to a Telnet console endpoint."""

        log.info(
            "bootstrap_telnet_console_connect_started",
            extra={
                "host": self.host,
                "port": self.port,
                "timeout_seconds": self.connect_timeout_seconds,
            },
        )
        try:
            self._reader, self._writer = await asyncio.wait_for(
                self._connector(host=self.host, port=self.port),
                timeout=self.connect_timeout_seconds,
            )
        except TimeoutError as exc:
            log.error(
                "bootstrap_telnet_console_connect_timeout",
                extra={"host": self.host, "port": self.port},
            )
            raise bootstrap_console_error(
                reason="connect_timeout",
                details={"host": self.host, "port": self.port},
            ) from exc
        except Exception as exc:
            log.error(
                "bootstrap_telnet_console_connect_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="connect_failed",
                details={"host": self.host, "port": self.port},
            ) from exc
        log.info(
            "bootstrap_telnet_console_connected",
            extra={"host": self.host, "port": self.port},
        )

    async def read(self, timeout_seconds: float) -> str:
        """Read and buffer console output until the stream is briefly quiet."""

        reader = self._require_reader()
        chunks: list[str] = []
        attempt = 0

        while True:
            attempt += 1
            read_timeout = (
                timeout_seconds
                if attempt == 1
                else self.read_drain_timeout_seconds
            )
            text = await self._read_once(reader, read_timeout)
            if text:
                chunks.append(text)
            elif attempt >= self.min_read_attempts:
                break

        output = "".join(chunks)
        log.debug(
            "bootstrap_telnet_console_read_completed",
            extra={
                "host": self.host,
                "port": self.port,
                "output_length": len(output),
                "output": output,
                "attempts": attempt,
            },
        )
        return output

    async def _read_once(self, reader: Any, timeout_seconds: float) -> str:
        try:
            output = await asyncio.wait_for(
                reader.read(self.read_bytes),
                timeout=timeout_seconds,
            )
        except TimeoutError:
            log.debug(
                "bootstrap_telnet_console_read_timeout",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "timeout_seconds": timeout_seconds,
                },
            )
            return ""
        except Exception as exc:
            log.error(
                "bootstrap_telnet_console_read_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="read_failed",
                details={"host": self.host, "port": self.port},
            ) from exc

        return _decode_output(output)

    async def send(self, text: str) -> None:
        """Send exact text to the Telnet console."""

        writer = self._require_writer()
        try:
            writer.write(text)
            drain = getattr(writer, "drain", None)
            if drain is not None:
                maybe_awaitable = drain()
                if isawaitable(maybe_awaitable):
                    await maybe_awaitable
        except Exception as exc:
            log.error(
                "bootstrap_telnet_console_send_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="send_failed",
                details={"host": self.host, "port": self.port},
            ) from exc
        log.debug(
            "bootstrap_telnet_console_send_completed",
            extra={"host": self.host, "port": self.port, "text_length": len(text)},
        )

    async def close(self) -> None:
        """Close the Telnet console session."""

        writer = self._writer
        self._reader = None
        self._writer = None
        if writer is None:
            return

        close = getattr(writer, "close", None)
        if close is not None:
            maybe_awaitable = close()
            if isawaitable(maybe_awaitable):
                await maybe_awaitable

        wait_closed = getattr(writer, "wait_closed", None)
        if wait_closed is not None:
            maybe_awaitable = wait_closed()
            if isawaitable(maybe_awaitable):
                await maybe_awaitable

        log.info(
            "bootstrap_telnet_console_closed",
            extra={"host": self.host, "port": self.port},
        )

    def _require_reader(self) -> Any:
        if self._reader is None:
            raise bootstrap_console_error(
                reason="not_connected",
                details={"host": self.host, "port": self.port},
            )
        return self._reader

    def _require_writer(self) -> Any:
        if self._writer is None:
            raise bootstrap_console_error(
                reason="not_connected",
                details={"host": self.host, "port": self.port},
            )
        return self._writer


class RawTcpConsoleSession:
    """Async raw TCP console session with no Telnet negotiation."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        connect_timeout_seconds: float = 10.0,
        read_bytes: int = DEFAULT_READ_BYTES,
        min_read_attempts: int = DEFAULT_MIN_READ_ATTEMPTS,
        read_drain_timeout_seconds: float = DEFAULT_READ_DRAIN_TIMEOUT_SECONDS,
        connector: RawTcpConnector | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.connect_timeout_seconds = connect_timeout_seconds
        self.read_bytes = read_bytes
        self.min_read_attempts = min_read_attempts
        self.read_drain_timeout_seconds = read_drain_timeout_seconds
        self._connector = connector or asyncio.open_connection
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def __aenter__(self) -> RawTcpConsoleSession:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        await self.close()

    async def connect(self) -> None:
        """Connect to a raw TCP console endpoint."""

        log.info(
            "bootstrap_raw_tcp_console_connect_started",
            extra={
                "host": self.host,
                "port": self.port,
                "timeout_seconds": self.connect_timeout_seconds,
            },
        )
        try:
            self._reader, self._writer = await asyncio.wait_for(
                self._connector(host=self.host, port=self.port),
                timeout=self.connect_timeout_seconds,
            )
        except TimeoutError as exc:
            log.error(
                "bootstrap_raw_tcp_console_connect_timeout",
                extra={"host": self.host, "port": self.port},
            )
            raise bootstrap_console_error(
                reason="connect_timeout",
                details={"host": self.host, "port": self.port},
            ) from exc
        except Exception as exc:
            log.error(
                "bootstrap_raw_tcp_console_connect_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="connect_failed",
                details={"host": self.host, "port": self.port},
            ) from exc
        log.info(
            "bootstrap_raw_tcp_console_connected",
            extra={"host": self.host, "port": self.port},
        )

    async def read(self, timeout_seconds: float) -> str:
        """Read and buffer raw TCP output until the stream is briefly quiet."""

        reader = self._require_reader()
        chunks: list[str] = []
        attempt = 0

        while True:
            attempt += 1
            read_timeout = (
                timeout_seconds
                if attempt == 1
                else self.read_drain_timeout_seconds
            )
            text = await self._read_once(reader, read_timeout)
            if text:
                chunks.append(text)
            elif attempt >= self.min_read_attempts:
                break

        output = "".join(chunks)
        log.debug(
            "bootstrap_raw_tcp_console_read_completed",
            extra={
                "host": self.host,
                "port": self.port,
                "output_length": len(output),
                "output": output,
                "attempts": attempt,
            },
        )
        return output

    async def _read_once(
        self,
        reader: asyncio.StreamReader,
        timeout_seconds: float,
    ) -> str:
        try:
            output = await asyncio.wait_for(
                reader.read(self.read_bytes),
                timeout=timeout_seconds,
            )
        except TimeoutError:
            log.debug(
                "bootstrap_raw_tcp_console_read_timeout",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "timeout_seconds": timeout_seconds,
                },
            )
            return ""
        except Exception as exc:
            log.error(
                "bootstrap_raw_tcp_console_read_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="read_failed",
                details={"host": self.host, "port": self.port},
            ) from exc

        return _decode_output(output)

    async def send(self, text: str) -> None:
        """Send exact text to the raw TCP console."""

        writer = self._require_writer()
        try:
            writer.write(text.encode("utf-8"))
            await writer.drain()
        except Exception as exc:
            log.error(
                "bootstrap_raw_tcp_console_send_failed",
                extra={
                    "host": self.host,
                    "port": self.port,
                    "error_type": type(exc).__name__,
                },
            )
            raise bootstrap_console_error(
                reason="send_failed",
                details={"host": self.host, "port": self.port},
            ) from exc
        log.debug(
            "bootstrap_raw_tcp_console_send_completed",
            extra={"host": self.host, "port": self.port, "text_length": len(text)},
        )

    async def close(self) -> None:
        """Close the raw TCP console session."""

        writer = self._writer
        self._reader = None
        self._writer = None
        if writer is None:
            return

        writer.close()
        await writer.wait_closed()

        log.info(
            "bootstrap_raw_tcp_console_closed",
            extra={"host": self.host, "port": self.port},
        )

    def _require_reader(self) -> asyncio.StreamReader:
        if self._reader is None:
            raise bootstrap_console_error(
                reason="not_connected",
                details={"host": self.host, "port": self.port},
            )
        return self._reader

    def _require_writer(self) -> asyncio.StreamWriter:
        if self._writer is None:
            raise bootstrap_console_error(
                reason="not_connected",
                details={"host": self.host, "port": self.port},
            )
        return self._writer


def _decode_output(output: object) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)
