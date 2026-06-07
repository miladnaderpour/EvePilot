import json

import pytest
import typer

from evepilot.core.exceptions import EvePilotError
from evepilot_cli.output import OutputFormat, run_json_command


def test_run_json_command_defaults_to_service_result_json(capsys: pytest.CaptureFixture[str]) -> None:
    run_json_command(
        code="test.completed",
        command=lambda: {"value": 1},
    )

    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is True
    assert payload["code"] == "test.completed"
    assert payload["data"] == {"value": 1}
    assert payload["error"] is None


def test_run_json_command_supports_text_output(capsys: pytest.CaptureFixture[str]) -> None:
    run_json_command(
        code="test.completed",
        command=lambda: {"value": 1},
        output_format=OutputFormat.TEXT,
    )

    output = capsys.readouterr().out

    assert "OK test.completed" in output
    assert '"value": 1' in output
    assert '"ok"' not in output


def test_run_json_command_formats_errors_as_text(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(typer.Exit):
        run_json_command(
            code="test.completed",
            command=lambda: _raise_error(),
            output_format=OutputFormat.TEXT,
        )

    captured = capsys.readouterr()

    assert "ERROR test.failed" in captured.err
    assert "Test failed." in captured.err


def _raise_error() -> None:
    raise EvePilotError(
        code="test.failed",
        message="Test failed.",
        details={"reason": "expected"},
    )
