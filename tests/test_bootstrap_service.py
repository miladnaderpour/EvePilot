import asyncio
from pathlib import Path

import pytest

from evepilot.bootstrap.errors import (
    BootstrapConfigApplyError,
    BootstrapFlowRunError,
    BootstrapFlowServiceError,
)
from evepilot.bootstrap.service import (
    TRANSPORT_RAW_TCP,
    TRANSPORT_TELNET,
    apply_rendered_config,
    export_flow,
    list_flows,
    prepare_console,
    select_console_transport,
    show_flow,
)
from evepilot.bootstrap.transport.console import AsyncConsoleSession
from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.models import EveNgNode


class FakeEveNgClient:
    def __init__(self, node: EveNgNode) -> None:
        self.node = node
        self.requests: list[tuple[str, str]] = []

    def get_node_by_name(self, lab_path: str, node_name: str) -> EveNgNode:
        self.requests.append((lab_path, node_name))
        return self.node


class FakeConsoleSession(AsyncConsoleSession):
    def __init__(self, reads: list[str]) -> None:
        self.reads = reads
        self.sent: list[str] = []
        self.connected = False
        self.closed = False

    async def connect(self) -> None:
        self.connected = True

    async def read(self, timeout_seconds: float) -> str:
        if not self.reads:
            return ""
        return self.reads.pop(0)

    async def send(self, text: str) -> None:
        self.sent.append(text)

    async def close(self) -> None:
        self.closed = True


def test_select_console_transport_uses_raw_tcp_for_dynamips_auto() -> None:
    node = EveNgNode(id=20, name="R-20", type="dynamips")

    assert select_console_transport(node, "auto") == TRANSPORT_RAW_TCP


def test_select_console_transport_uses_telnet_for_qemu_auto() -> None:
    node = EveNgNode(id=1, name="CSR-1", type="qemu")

    assert select_console_transport(node, "auto") == TRANSPORT_TELNET


def test_select_console_transport_rejects_unknown_transport() -> None:
    node = EveNgNode(id=1, name="CSR-1", type="qemu")

    with pytest.raises(BootstrapConfigApplyError) as exc_info:
        select_console_transport(node, "ssh")

    assert exc_info.value.details["reason"] == "unsupported_transport"
    assert exc_info.value.details["transport"] == "ssh"


def test_list_flows_returns_builtin_flow_summaries() -> None:
    result = list_flows()

    assert result.source == "built-in"
    assert any(flow.name == "cisco-router-first-boot" for flow in result.flows)


def test_list_flows_rejects_unknown_source() -> None:
    with pytest.raises(BootstrapFlowServiceError) as exc_info:
        list_flows(source="custom")

    assert exc_info.value.details["reason"] == "unsupported_flow_source"
    assert exc_info.value.details["source"] == "custom"


def test_show_flow_returns_builtin_flow_text() -> None:
    result = show_flow("built-in:cisco-router-first-boot")

    assert result.source == "built-in:cisco-router-first-boot"
    assert "name: cisco-router-first-boot" in result.text


def test_export_flow_writes_builtin_flow(tmp_path: Path) -> None:
    output = tmp_path / "flows" / "cisco-router-first-boot.yaml"

    result = export_flow(
        source="built-in:cisco-router-first-boot",
        output=output,
    )

    assert result.output == str(output)
    assert "name: cisco-router-first-boot" in output.read_text(encoding="utf-8")


def test_export_flow_rejects_existing_file_without_force(tmp_path: Path) -> None:
    output = tmp_path / "flow.yaml"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(BootstrapFlowServiceError) as exc_info:
        export_flow(source="built-in:cisco-router-first-boot", output=output)

    assert exc_info.value.details["reason"] == "flow_export_output_exists"


def test_apply_rendered_config_prepares_and_applies_config(tmp_path: Path) -> None:
    config_path = tmp_path / "CSR-1.txt"
    config_path.write_text(
        "\n".join(
            [
                "!",
                "configure terminal",
                "hostname CSR-1",
            ]
        ),
        encoding="utf-8",
    )
    console = FakeConsoleSession(
        [
            "Router#",
            "Router(config)#",
            "CSR-1(config)#",
        ]
    )
    node = EveNgNode(
        id=1,
        name="CSR-1",
        type="qemu",
        console=ConsoleEndpoint(protocol="telnet", host="10.1.2.3", port=32769),
    )

    result = asyncio.run(
        apply_rendered_config(
            eve_ng_client=FakeEveNgClient(node),  # type: ignore[arg-type]
            lab_path="EIGRP/Basics.unl",
            node_name="CSR-1",
            config_path=config_path,
            flow_ref="built-in:cisco-router-first-boot",
            console_session_factory=lambda **_: console,
        )
    )

    assert console.connected is True
    assert console.closed is True
    assert console.sent == ["configure terminal\r\n", "hostname CSR-1\r\n"]
    assert result.node == "CSR-1"
    assert result.console.host == "10.1.2.3"
    assert result.transport == TRANSPORT_TELNET
    assert result.prepared is True
    assert result.preparation.ready is True
    assert result.config_apply.commands_total == 2
    assert result.config_apply.commands_sent == 2
    assert result.config_apply.apply_duration_seconds is not None
    assert result.duration_seconds >= 0


def test_prepare_console_runs_flow_and_returns_schema() -> None:
    console = FakeConsoleSession(["Router#"])
    node = EveNgNode(
        id=1,
        name="CSR-1",
        type="qemu",
        console=ConsoleEndpoint(protocol="telnet", host="10.1.2.3", port=32769),
    )

    result = asyncio.run(
        prepare_console(
            eve_ng_client=FakeEveNgClient(node),  # type: ignore[arg-type]
            lab_path="EIGRP/Basics.unl",
            node_name="CSR-1",
            flow_ref="built-in:cisco-router-first-boot",
            console_session_factory=lambda **_: console,
        )
    )

    assert console.connected is True
    assert console.closed is True
    assert result.node == "CSR-1"
    assert result.console.host == "10.1.2.3"
    assert result.transport == TRANSPORT_TELNET
    assert result.result.ready is True
    assert result.result.final_state == "privileged_exec_prompt"
    assert result.duration_seconds >= 0


def test_apply_rendered_config_closes_console_when_preparation_fails(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "CSR-1.txt"
    config_path.write_text("hostname CSR-1", encoding="utf-8")
    console = FakeConsoleSession(["Router booting", "", "", ""])
    node = EveNgNode(
        id=1,
        name="CSR-1",
        type="qemu",
        console=ConsoleEndpoint(protocol="telnet", host="10.1.2.3", port=32769),
    )

    with pytest.raises(BootstrapFlowRunError):
        asyncio.run(
            apply_rendered_config(
                eve_ng_client=FakeEveNgClient(node),  # type: ignore[arg-type]
                lab_path="EIGRP/Basics.unl",
                node_name="CSR-1",
                config_path=config_path,
                detect_console_timeout_seconds=0.01,
                console_session_factory=lambda **_: console,
            )
        )

    assert console.closed is True
    assert "hostname CSR-1\r\n" not in console.sent
