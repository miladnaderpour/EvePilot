"""Rendered config file loading."""

from pathlib import Path

from evepilot.bootstrap.config_apply.models import ConfigLine
from evepilot.bootstrap.errors import bootstrap_config_apply_error
from evepilot.core.logging import get_logger

log = get_logger(__name__)


def load_config_lines(path: Path) -> list[ConfigLine]:
    """Load command lines from an already-rendered plain text config file."""

    if not path.exists():
        raise bootstrap_config_apply_error(
            reason="config_file_not_found",
            details={"path": str(path)},
        )
    if not path.is_file():
        raise bootstrap_config_apply_error(
            reason="config_path_not_file",
            details={"path": str(path)},
        )

    lines = [
        ConfigLine(number=line_number, text=line)
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        )
        if (line := raw_line.rstrip("\r\n")) and _is_config_command(line)
    ]
    log.debug(
        "bootstrap_config_file_loaded",
        extra={"path": str(path), "command_count": len(lines)},
    )
    return lines


def _is_config_command(line: str) -> bool:
    stripped_line = line.strip()
    return bool(stripped_line) and not stripped_line.startswith("!")
