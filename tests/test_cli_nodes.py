import json
from typing import Any

import pytest
from typer.testing import CliRunner

from evepilot.eve_ng.schemas import EveNgConsoleEndpoint
from evepilot.eve_ng.schemas import EveNgNodeConsoleResult, EveNgNodeResult
from evepilot.eve_ng.schemas import EveNgNodesResult
from evepilot_cli.commands.nodes import app

runner = CliRunner()


def test_nodes_all_calls_service(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    def fake_list_nodes(**kwargs: Any) -> EveNgNodesResult:
        captured.update(kwargs)
        return EveNgNodesResult(nodes=[_node_result()])

    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr("evepilot_cli.commands.nodes.list_nodes", fake_list_nodes)

    result = runner.invoke(app, ["all", "--lab", "EIGRP/Basics.unl"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["code"] == "nodes.all.completed"
    assert payload["data"]["nodes"][0]["name"] == "CSR-1"
    assert captured["lab_path"] == "EIGRP/Basics.unl"


def test_nodes_get_calls_service(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    def fake_get_node(**kwargs: Any) -> EveNgNodeResult:
        captured.update(kwargs)
        return _node_result()

    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr("evepilot_cli.commands.nodes.get_eve_ng_node", fake_get_node)

    result = runner.invoke(
        app,
        ["get", "--lab", "EIGRP/Basics.unl", "--node", "CSR-1"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["code"] == "nodes.get.completed"
    assert payload["data"]["name"] == "CSR-1"
    assert captured["node_name"] == "CSR-1"


def test_nodes_get_supports_text_format(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.get_eve_ng_node",
        lambda **_: _node_result(),
    )

    result = runner.invoke(
        app,
        [
            "get",
            "--lab",
            "EIGRP/Basics.unl",
            "--node",
            "CSR-1",
            "--format",
            "text",
        ],
    )

    assert result.exit_code == 0
    assert "OK nodes.get.completed" in result.stdout
    assert "CSR-1" in result.stdout


def test_node_console_payload_calls_service(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    def fake_get_node_console(**kwargs: Any) -> EveNgNodeConsoleResult:
        captured.update(kwargs)
        return EveNgNodeConsoleResult(node="CSR-1", console=_console_result())

    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr(
        "evepilot_cli.commands.nodes.get_node_console",
        fake_get_node_console,
    )

    from evepilot_cli.commands.nodes import node_console_payload

    node_console_payload("EIGRP/Basics.unl", "CSR-1")

    assert captured["lab_path"] == "EIGRP/Basics.unl"
    assert captured["node_name"] == "CSR-1"


def _node_result() -> EveNgNodeResult:
    return EveNgNodeResult(
        id=1,
        name="CSR-1",
        status=2,
        type="qemu",
        url="telnet://10.1.2.3:32769",
        console=_console_result(),
    )


def _console_result() -> EveNgConsoleEndpoint:
    return EveNgConsoleEndpoint(protocol="telnet", host="10.1.2.3", port=32769)
