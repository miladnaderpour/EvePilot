import json
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from evepilot.eve_ng.models import EveNgNode
from evepilot_cli.commands.bootstrap import (
    TRANSPORT_RAW_TCP,
    TRANSPORT_TELNET,
    app,
    select_console_transport,
)

runner = CliRunner()


def test_select_console_transport_uses_raw_tcp_for_dynamips_auto() -> None:
    node = EveNgNode(id=20, name="R-20", type="dynamips")

    assert select_console_transport(node, "auto") == TRANSPORT_RAW_TCP


def test_select_console_transport_uses_telnet_for_qemu_auto() -> None:
    node = EveNgNode(id=1, name="CSR-1", type="qemu")

    assert select_console_transport(node, "auto") == TRANSPORT_TELNET


def test_select_console_transport_keeps_explicit_transport() -> None:
    node = EveNgNode(id=20, name="R-20", type="dynamips")

    assert select_console_transport(node, "telnet") == TRANSPORT_TELNET
    assert select_console_transport(node, "raw-tcp") == TRANSPORT_RAW_TCP


def test_select_console_transport_rejects_unknown_transport() -> None:
    node = EveNgNode(id=20, name="R-20", type="dynamips")

    with pytest.raises(typer.BadParameter):
        select_console_transport(node, "ssh")


def test_bootstrap_flow_list_command_lists_builtin_flows() -> None:
    result = runner.invoke(app, ["flow", "list"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload[0]["source"] == "built-in"
    assert any(flow["name"] == "cisco-router-first-boot" for flow in payload)


def test_bootstrap_flow_list_rejects_custom_source() -> None:
    result = runner.invoke(app, ["flow", "list", "--source", "custom"])

    assert result.exit_code != 0
    assert "Only built-in flow listing is supported" in result.output


def test_bootstrap_flow_show_command_prints_builtin_yaml() -> None:
    result = runner.invoke(app, ["flow", "show", "built-in:cisco-router-first-boot"])

    assert result.exit_code == 0
    assert "name: cisco-router-first-boot" in result.stdout
    assert "states:" in result.stdout


def test_bootstrap_flow_show_rejects_non_builtin_source() -> None:
    result = runner.invoke(app, ["flow", "show", "flows/example.yaml"])

    assert result.exit_code != 0
    assert "Only built-in flow sources are supported" in result.output


def test_bootstrap_flow_export_command_writes_builtin_yaml(tmp_path: Path) -> None:
    output = tmp_path / "flows" / "cisco-router-first-boot.yaml"

    result = runner.invoke(
        app,
        [
            "flow",
            "export",
            "built-in:cisco-router-first-boot",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert "name: cisco-router-first-boot" in output.read_text(encoding="utf-8")


def test_bootstrap_flow_export_rejects_existing_file_without_force(
    tmp_path: Path,
) -> None:
    output = tmp_path / "flow.yaml"
    output.write_text("existing", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "flow",
            "export",
            "built-in:cisco-router-first-boot",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code != 0
    assert "Output file already exists" in result.output
