from pathlib import Path

import pytest

from evepilot.bootstrap.config_apply.config_file import load_config_lines
from evepilot.bootstrap.errors import BootstrapConfigApplyError


def test_load_config_lines_filters_sample_config() -> None:
    lines = load_config_lines(Path("examples/configs/cisco-iosxe-basic.txt"))

    assert len(lines) == 38
    assert lines[0].number == 1
    assert lines[0].text == "conf t"
    assert all(line.text.strip() for line in lines)
    assert all(not line.text.strip().startswith("!") for line in lines)
    assert any(line.text == " description Link-1" for line in lines)
    assert any(line.text == "ip domain name evepilot.io" for line in lines)


def test_load_config_lines_preserves_indentation_and_original_line_numbers(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.txt"
    config_path.write_text(
        "\n"
        "!\n"
        "interface GigabitEthernet1\n"
        " description Uplink\n"
        "  nested-looking command\n",
        encoding="utf-8",
    )

    lines = load_config_lines(config_path)

    assert [line.number for line in lines] == [3, 4, 5]
    assert [line.text for line in lines] == [
        "interface GigabitEthernet1",
        " description Uplink",
        "  nested-looking command",
    ]


def test_load_config_lines_skips_lines_starting_with_bang_after_strip(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.txt"
    config_path.write_text(
        "hostname R1\n"
        " ! generated comment\n"
        "! separator\n"
        "end\n",
        encoding="utf-8",
    )

    lines = load_config_lines(config_path)

    assert [line.text for line in lines] == ["hostname R1", "end"]


def test_load_config_lines_does_not_skip_hash_lines(tmp_path: Path) -> None:
    config_path = tmp_path / "config.txt"
    config_path.write_text("# generated comment\nhostname R1\n", encoding="utf-8")

    lines = load_config_lines(config_path)

    assert [line.text for line in lines] == ["# generated comment", "hostname R1"]


def test_load_config_lines_rejects_missing_file(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.txt"

    with pytest.raises(BootstrapConfigApplyError) as exc_info:
        load_config_lines(config_path)

    assert exc_info.value.details["reason"] == "config_file_not_found"
    assert exc_info.value.details["path"] == str(config_path)


def test_load_config_lines_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(BootstrapConfigApplyError) as exc_info:
        load_config_lines(tmp_path)

    assert exc_info.value.details["reason"] == "config_path_not_file"
    assert exc_info.value.details["path"] == str(tmp_path)
