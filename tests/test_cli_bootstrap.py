import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from evepilot.bootstrap.schemas import (
    BootstrapConfigApplyResult,
    BootstrapConfigApplySummary,
    BootstrapConsoleEndpoint,
    BootstrapConsolePrepareResult,
    BootstrapPreparationResult,
)
from evepilot_cli.commands.bootstrap import app

runner = CliRunner()


def test_bootstrap_flow_list_command_lists_builtin_flows() -> None:
    result = runner.invoke(app, ["flow", "list"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["code"] == "bootstrap.flow.list.completed"
    assert payload["meta"]["duration_seconds"] >= 0
    assert payload["data"]["source"] == "built-in"
    assert any(
        flow["name"] == "cisco-router-first-boot"
        for flow in payload["data"]["flows"]
    )


def test_bootstrap_flow_list_rejects_custom_source() -> None:
    result = runner.invoke(app, ["flow", "list", "--source", "custom"])

    assert result.exit_code != 0
    assert "unsupported_flow_source" in result.output


def test_bootstrap_flow_show_command_prints_builtin_yaml() -> None:
    result = runner.invoke(app, ["flow", "show", "built-in:cisco-router-first-boot"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["code"] == "bootstrap.flow.show.completed"
    assert payload["data"]["source"] == "built-in:cisco-router-first-boot"
    assert "name: cisco-router-first-boot" in payload["data"]["text"]
    assert "states:" in payload["data"]["text"]


def test_bootstrap_flow_show_rejects_non_builtin_source() -> None:
    result = runner.invoke(app, ["flow", "show", "flows/example.yaml"])

    assert result.exit_code != 0
    assert "unsupported_flow_reference" in result.output


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
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["code"] == "bootstrap.flow.export.completed"
    assert payload["data"]["output"] == str(output)


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
    assert "flow_export_output_exists" in result.output


def test_bootstrap_prepare_calls_service_with_cli_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    async def fake_prepare_console(**kwargs: Any) -> BootstrapConsolePrepareResult:
        captured.update(kwargs)
        return BootstrapConsolePrepareResult(
            node="CSR-1",
            console=BootstrapConsoleEndpoint(
                protocol="telnet",
                host="10.1.2.3",
                port=32769,
            ),
            flow=kwargs["flow_ref"],
            transport=kwargs["transport"],
            result=BootstrapPreparationResult(
                flow_name="cisco-router-first-boot",
                final_state="privileged_exec_prompt",
                actions=["ready"],
                output_sample="Router#",
                ready=True,
            ),
            duration_seconds=1.1,
        )

    monkeypatch.setattr(
        "evepilot_cli.commands.bootstrap.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr(
        "evepilot_cli.commands.bootstrap.prepare_console",
        fake_prepare_console,
    )

    result = runner.invoke(
        app,
        [
            "prepare",
            "--lab",
            "EIGRP/Basics.unl",
            "--node",
            "CSR-1",
            "--flow",
            "built-in:cisco-router-first-boot",
            "--transport",
            "raw-tcp",
            "--detect-console-timeout",
            "30",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["code"] == "bootstrap.prepare.completed"
    assert payload["data"]["node"] == "CSR-1"
    assert captured["lab_path"] == "EIGRP/Basics.unl"
    assert captured["node_name"] == "CSR-1"
    assert captured["flow_ref"] == "built-in:cisco-router-first-boot"
    assert captured["transport"] == "raw-tcp"
    assert captured["detect_console_timeout_seconds"] == 30.0


def test_bootstrap_apply_calls_service_with_cli_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    config_file = tmp_path / "CSR-1.txt"
    config_file.write_text("hostname CSR-1", encoding="utf-8")

    def fake_run_with_eve_ng_client(command: Any) -> object:
        return command(object())

    async def fake_apply_rendered_config(**kwargs: Any) -> BootstrapConfigApplyResult:
        captured.update(kwargs)
        return BootstrapConfigApplyResult(
            node="CSR-1",
            console=BootstrapConsoleEndpoint(
                protocol="telnet",
                host="10.1.2.3",
                port=32769,
            ),
            flow=kwargs["flow_ref"],
            transport=kwargs["transport"],
            config_path=str(kwargs["config_path"]),
            prepared=True,
            preparation=BootstrapPreparationResult(
                flow_name="cisco-router-first-boot",
                final_state="privileged_exec_prompt",
                actions=["ready"],
                output_sample="Router#",
                ready=True,
            ),
            config_apply=BootstrapConfigApplySummary(
                commands_total=1,
                commands_sent=1,
                ready=False,
                final_state=None,
                apply_duration_seconds=0.01,
            ),
            duration_seconds=1.2,
        )

    monkeypatch.setattr(
        "evepilot_cli.commands.bootstrap.run_with_eve_ng_client",
        fake_run_with_eve_ng_client,
    )
    monkeypatch.setattr(
        "evepilot_cli.commands.bootstrap.apply_rendered_config",
        fake_apply_rendered_config,
    )

    result = runner.invoke(
        app,
        [
            "apply",
            "--lab",
            "EIGRP/Basics.unl",
            "--node",
            "CSR-1",
            "--file",
            str(config_file),
            "--flow",
            "built-in:cisco-router-first-boot",
            "--transport",
            "raw-tcp",
            "--detect-console-timeout",
            "30",
            "--config-read-timeout",
            "4",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["code"] == "bootstrap.apply.completed"
    assert payload["data"]["node"] == "CSR-1"
    assert captured["lab_path"] == "EIGRP/Basics.unl"
    assert captured["node_name"] == "CSR-1"
    assert captured["config_path"] == config_file
    assert captured["flow_ref"] == "built-in:cisco-router-first-boot"
    assert captured["transport"] == "raw-tcp"
    assert captured["detect_console_timeout_seconds"] == 30.0
    assert captured["config_read_timeout_seconds"] == 4.0


def test_bootstrap_flow_list_supports_text_format() -> None:
    result = runner.invoke(app, ["flow", "list", "--format", "text"])

    assert result.exit_code == 0
    assert "OK bootstrap.flow.list.completed" in result.stdout
    assert "cisco-router-first-boot" in result.stdout
    assert '"ok"' not in result.stdout


def test_bootstrap_flow_show_supports_text_format() -> None:
    result = runner.invoke(
        app,
        ["flow", "show", "built-in:cisco-router-first-boot", "--format", "text"],
    )

    assert result.exit_code == 0
    assert "OK bootstrap.flow.show.completed" in result.stdout
    assert "name: cisco-router-first-boot" in result.stdout
