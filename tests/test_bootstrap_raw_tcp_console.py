import asyncio
import logging

import pytest

from evepilot.bootstrap.errors import BootstrapConsoleError
from evepilot.bootstrap.transport.console import RawTcpConsoleSession


class FakeRawTcpReader:
    def __init__(self, outputs: list[object]) -> None:
        self.outputs = outputs
        self.read_count = 0

    async def read(self, read_bytes: int) -> object:
        self.read_count += 1
        if not self.outputs:
            await asyncio.sleep(1)
            return b""
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output


class FakeRawTcpWriter:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.closed = False
        self.drained = False
        self.waited_closed = False

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    async def drain(self) -> None:
        self.drained = True

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        self.waited_closed = True


def test_raw_tcp_console_session_connect_read_send_close() -> None:
    reader = FakeRawTcpReader([b"Router#"])
    writer = FakeRawTcpWriter()

    async def connector(
        **kwargs: object,
    ) -> tuple[FakeRawTcpReader, FakeRawTcpWriter]:
        assert kwargs == {"host": "10.1.2.3", "port": 32769}
        return reader, writer

    async def run() -> None:
        session = RawTcpConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )

        await session.connect()
        output = await session.read(1)
        await session.send("enable\r\n")
        await session.close()

        assert output == "Router#"
        assert reader.read_count == 3
        assert writer.writes == [b"enable\r\n"]
        assert writer.drained is True
        assert writer.closed is True
        assert writer.waited_closed is True

    asyncio.run(run())


def test_raw_tcp_console_session_buffers_chunked_output_until_quiet() -> None:
    reader = FakeRawTcpReader([b"Would you like t", b"o enter setup?", b""])
    writer = FakeRawTcpWriter()

    async def connector(
        **kwargs: object,
    ) -> tuple[FakeRawTcpReader, FakeRawTcpWriter]:
        return reader, writer

    async def run() -> str:
        session = RawTcpConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        return await session.read(1)

    assert asyncio.run(run()) == "Would you like to enter setup?"
    assert reader.read_count == 3


def test_raw_tcp_console_session_logs_buffered_output(
    caplog: pytest.LogCaptureFixture,
) -> None:
    reader = FakeRawTcpReader([b"Router", b"#", b""])
    writer = FakeRawTcpWriter()

    async def connector(
        **kwargs: object,
    ) -> tuple[FakeRawTcpReader, FakeRawTcpWriter]:
        return reader, writer

    async def run() -> None:
        session = RawTcpConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        await session.read(1)

    with caplog.at_level(logging.DEBUG):
        asyncio.run(run())

    read_records = [
        record
        for record in caplog.records
        if record.message == "bootstrap_raw_tcp_console_read_completed"
    ]
    assert read_records[-1].output == "Router#"


def test_raw_tcp_console_session_rejects_read_before_connect() -> None:
    async def run() -> None:
        session = RawTcpConsoleSession(host="10.1.2.3", port=32769)
        await session.read(1)

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "not_connected"


def test_raw_tcp_console_session_wraps_connect_failure() -> None:
    async def connector(
        **kwargs: object,
    ) -> tuple[FakeRawTcpReader, FakeRawTcpWriter]:
        raise OSError("connection refused")

    async def run() -> None:
        session = RawTcpConsoleSession(
            host="10.1.2.3",
            port=32769,
            connector=connector,
        )
        await session.connect()

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "connect_failed"


def test_raw_tcp_console_session_wraps_send_failure() -> None:
    reader = FakeRawTcpReader([b"Router#"])

    class FailingWriter(FakeRawTcpWriter):
        def write(self, data: bytes) -> None:
            raise OSError("broken pipe")

    async def connector(
        **kwargs: object,
    ) -> tuple[FakeRawTcpReader, FailingWriter]:
        return reader, FailingWriter()

    async def run() -> None:
        session = RawTcpConsoleSession(
            host="10.1.2.3",
            port=32769,
            connector=connector,
        )
        await session.connect()
        await session.send("enable\r\n")

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "send_failed"
