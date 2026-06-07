import asyncio
import logging

import pytest

from evepilot.bootstrap.errors import BootstrapConsoleError
from evepilot.bootstrap.transport.console import TelnetConsoleSession


class FakeTelnetReader:
    def __init__(self, outputs: list[object]) -> None:
        self.outputs = outputs
        self.read_count = 0

    async def read(self, read_bytes: int) -> object:
        self.read_count += 1
        if not self.outputs:
            await asyncio.sleep(1)
            return ""
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output


class FakeTelnetWriter:
    def __init__(self) -> None:
        self.writes: list[str] = []
        self.closed = False
        self.drained = False
        self.waited_closed = False

    def write(self, text: str) -> None:
        self.writes.append(text)

    async def drain(self) -> None:
        self.drained = True

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        self.waited_closed = True


def test_telnet_console_session_connect_read_send_close() -> None:
    reader = FakeTelnetReader(["Router#"])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        assert kwargs == {"host": "10.1.2.3", "port": 32769}
        return reader, writer

    async def run() -> None:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )

        await session.connect()
        output = await session.read(1)
        await session.send("enable\n")
        await session.close()

        assert output == "Router#"
        assert reader.read_count == 3
        assert writer.writes == ["enable\n"]
        assert writer.drained is True
        assert writer.closed is True
        assert writer.waited_closed is True

    asyncio.run(run())


def test_telnet_console_session_decodes_bytes_output() -> None:
    reader = FakeTelnetReader([b"Router#"])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        return reader, writer

    async def run() -> str:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        return await session.read(1)

    assert asyncio.run(run()) == "Router#"


def test_telnet_console_session_buffers_chunked_output_until_quiet() -> None:
    reader = FakeTelnetReader(["Would you like t", "o enter setup?", ""])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        return reader, writer

    async def run() -> str:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        return await session.read(1)

    assert asyncio.run(run()) == "Would you like to enter setup?"
    assert reader.read_count == 3


def test_telnet_console_session_logs_buffered_output(caplog: pytest.LogCaptureFixture) -> None:
    reader = FakeTelnetReader(["Router", "#", ""])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        return reader, writer

    async def run() -> None:
        session = TelnetConsoleSession(
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
        if record.message == "bootstrap_telnet_console_read_completed"
    ]
    assert read_records[-1].output == "Router#"


def test_telnet_console_session_reads_beyond_minimum_attempts_until_quiet() -> None:
    reader = FakeTelnetReader(["Router", "#", "\r\n", ""])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        return reader, writer

    async def run() -> str:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        return await session.read(1)

    assert asyncio.run(run()) == "Router#\r\n"
    assert reader.read_count == 4


def test_telnet_console_session_read_timeout_returns_empty_string() -> None:
    reader = FakeTelnetReader([])
    writer = FakeTelnetWriter()

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        return reader, writer

    async def run() -> str:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            read_drain_timeout_seconds=0.01,
            connector=connector,
        )
        await session.connect()
        return await session.read(0.01)

    assert asyncio.run(run()) == ""


def test_telnet_console_session_rejects_read_before_connect() -> None:
    async def run() -> None:
        session = TelnetConsoleSession(host="10.1.2.3", port=32769)
        await session.read(1)

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "not_connected"


def test_telnet_console_session_wraps_connect_failure() -> None:
    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FakeTelnetWriter]:
        raise OSError("connection refused")

    async def run() -> None:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            connector=connector,
        )
        await session.connect()

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "connect_failed"


def test_telnet_console_session_wraps_send_failure() -> None:
    reader = FakeTelnetReader(["Router#"])

    class FailingWriter(FakeTelnetWriter):
        def write(self, text: str) -> None:
            raise OSError("broken pipe")

    async def connector(**kwargs: object) -> tuple[FakeTelnetReader, FailingWriter]:
        return reader, FailingWriter()

    async def run() -> None:
        session = TelnetConsoleSession(
            host="10.1.2.3",
            port=32769,
            connector=connector,
        )
        await session.connect()
        await session.send("enable\n")

    with pytest.raises(BootstrapConsoleError) as exc_info:
        asyncio.run(run())

    assert exc_info.value.details["reason"] == "send_failed"
