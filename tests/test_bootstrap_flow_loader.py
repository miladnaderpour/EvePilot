from pathlib import Path

import pytest

from evepilot.bootstrap.errors import BootstrapFlowError
from evepilot.bootstrap.preparation.flow_loader import discover_builtin_flow_resources
from evepilot.bootstrap.preparation.flow_loader import list_builtin_flows
from evepilot.bootstrap.preparation.flow_loader import load_builtin_flow
from evepilot.bootstrap.preparation.flow_loader import load_builtin_flow_from_package
from evepilot.bootstrap.preparation.flow_loader import (
    load_flow_from_path,
    load_flow_from_text,
)
from evepilot.bootstrap.preparation.flow_loader import read_builtin_flow_text
from evepilot.bootstrap.preparation.models import FlowAction


def test_load_flow_from_text() -> None:
    flow = load_flow_from_text(
        """
        name: example
        version: 1
        states:
          privileged_exec_prompt:
            regex:
              - "[A-Za-z0-9_.-]+#\\\\s*$"
        steps:
          - name: ready
            when_state: privileged_exec_prompt
            action: ready
            mark_ready: true
        """
    )

    assert flow.name == "example"
    assert flow.version == 1
    assert flow.steps[0].action == FlowAction.READY
    assert flow.steps[0].mark_ready is True


def test_load_flow_from_path(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow.yaml"
    flow_path.write_text(
        """
        name: example
        version: 1
        states:
          user_exec_prompt:
            regex:
              - "[A-Za-z0-9_.-]+>\\\\s*$"
        steps:
          - name: enter-enable-mode
            when_state: user_exec_prompt
            action: send
            send: "enable\\n"
            next: detect
        """,
        encoding="utf-8",
    )

    flow = load_flow_from_path(flow_path)

    assert flow.name == "example"
    assert flow.steps[0].send == "enable\n"


def test_load_flow_from_text_supports_startup_wake_enter() -> None:
    flow = load_flow_from_text(
        """
        name: example
        version: 1
        startup:
          wake_enter: "\\n"
        states:
          privileged_exec_prompt:
            regex:
              - "[A-Za-z0-9_.-]+#\\\\s*$"
        steps:
          - name: ready
            when_state: privileged_exec_prompt
            action: ready
            mark_ready: true
        """
    )

    assert flow.startup.wake_enter == "\n"


def test_load_builtin_generic_cisco_router_flow() -> None:
    flow = load_builtin_flow("cisco-router-first-boot")

    assert flow.name == "cisco-router-first-boot"
    assert flow.startup.wake_enter == "\r\n"
    assert "initial_config_dialog" in flow.states
    assert flow.steps[-1].action == FlowAction.READY


def test_discover_builtin_flows_uses_filename_stem_as_public_reference() -> None:
    flows = discover_builtin_flow_resources()

    assert "cisco-router-first-boot" in flows


def test_list_builtin_flows_returns_summaries() -> None:
    summaries = list_builtin_flows()

    assert summaries
    assert summaries[0].source == "built-in"
    assert any(summary.name == "cisco-router-first-boot" for summary in summaries)


def test_read_builtin_flow_text_returns_original_yaml() -> None:
    text = read_builtin_flow_text("cisco-router-first-boot")

    assert "name: cisco-router-first-boot" in text
    assert "states:" in text


def test_load_builtin_flow_rejects_unknown_name() -> None:
    with pytest.raises(BootstrapFlowError) as exc_info:
        load_builtin_flow("missing-flow")

    assert exc_info.value.code == "bootstrap.flow_not_found"


def test_load_builtin_flow_rejects_path_like_name() -> None:
    with pytest.raises(BootstrapFlowError) as exc_info:
        load_builtin_flow("../cisco-router-first-boot")

    assert exc_info.value.code == "bootstrap.flow_not_found"


def test_load_builtin_flow_rejects_duplicate_filename_stems(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root = tmp_path / "sample_flows_duplicate"
    package_root.mkdir()
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    flow_text = """
    name: duplicate-flow
    version: 1
    states:
      ready:
        regex:
          - "[A-Za-z0-9_.-]+#\\\\s*$"
    steps:
      - name: ready
        when_state: ready
        action: ready
        mark_ready: true
    """
    (package_root / "duplicate-flow.yaml").write_text(flow_text, encoding="utf-8")
    (package_root / "duplicate-flow.yml").write_text(flow_text, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(BootstrapFlowError) as exc_info:
        load_builtin_flow_from_package("duplicate-flow", "sample_flows_duplicate")

    assert exc_info.value.details["reason"] == "duplicate_builtin_flow_name"


def test_load_builtin_flow_rejects_yaml_name_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root = tmp_path / "sample_flows_mismatch"
    package_root.mkdir()
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "expected-flow.yaml").write_text(
        """
        name: wrong-flow
        version: 1
        states:
          ready:
            regex:
              - "[A-Za-z0-9_.-]+#\\\\s*$"
        steps:
          - name: ready
            when_state: ready
            action: ready
            mark_ready: true
        """,
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(BootstrapFlowError) as exc_info:
        load_builtin_flow_from_package("expected-flow", "sample_flows_mismatch")

    assert exc_info.value.details["reason"] == "builtin_flow_name_mismatch"
    assert exc_info.value.details["reference"] == "expected-flow"
    assert exc_info.value.details["flow_name"] == "wrong-flow"
