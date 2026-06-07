import asyncio

from evepilot.bootstrap.config_apply.models import ConfigLine
from evepilot.bootstrap.config_apply.runner import apply_config_lines
from evepilot.bootstrap.transport.console import AsyncConsoleSession


class InMemoryConsoleSession(AsyncConsoleSession):
    def __init__(self, reads: list[str]) -> None:
        self.reads = reads
        self.sent: list[str] = []

    async def connect(self) -> None:
        return None

    async def read(self, timeout_seconds: float) -> str:
        if not self.reads:
            return ""
        return self.reads.pop(0)

    async def send(self, text: str) -> None:
        self.sent.append(text)

    async def close(self) -> None:
        return None


def test_apply_config_lines_sends_all_lines_with_default_line_ending() -> None:
    console = InMemoryConsoleSession(["R1(config)#", "R1(config)#"])
    lines = [
        ConfigLine(number=1, text="configure terminal"),
        ConfigLine(number=2, text="hostname R1"),
    ]

    result = asyncio.run(apply_config_lines(lines=lines, console=console))

    assert console.sent == ["configure terminal\r\n", "hostname R1\r\n"]
    assert result.commands_total == 2
    assert result.commands_sent == 2
    assert [item.line_number for item in result.command_results] == [1, 2]
    assert [item.command for item in result.command_results] == [
        "configure terminal",
        "hostname R1",
    ]
    assert result.apply_duration_seconds is not None


def test_apply_config_lines_captures_output_samples() -> None:
    console = InMemoryConsoleSession(["output one", "output two"])
    lines = [
        ConfigLine(number=10, text="interface GigabitEthernet1"),
        ConfigLine(number=11, text=" description Uplink"),
    ]

    result = asyncio.run(apply_config_lines(lines=lines, console=console))

    assert [item.output_sample for item in result.command_results] == [
        "output one",
        "output two",
    ]


def test_apply_config_lines_handles_empty_line_list() -> None:
    console = InMemoryConsoleSession([])

    result = asyncio.run(apply_config_lines(lines=[], console=console))

    assert console.sent == []
    assert result.commands_total == 0
    assert result.commands_sent == 0
    assert result.command_results == []


def test_apply_config_lines_supports_custom_line_ending() -> None:
    console = InMemoryConsoleSession(["Router#"])
    lines = [ConfigLine(number=1, text="show version")]

    asyncio.run(apply_config_lines(lines=lines, console=console, line_ending="\n"))

    assert console.sent == ["show version\n"]


def test_apply_config_lines_bounds_output_sample() -> None:
    console = InMemoryConsoleSession(["x" * 600])
    lines = [ConfigLine(number=1, text="show logging")]

    result = asyncio.run(apply_config_lines(lines=lines, console=console))

    assert len(result.command_results[0].output_sample) == 500
