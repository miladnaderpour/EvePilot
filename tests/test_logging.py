import logging

import pytest

from evepilot.core.config import Settings
from evepilot.core.exceptions import EvePilotConfigError
from evepilot.core.logging import parse_log_targets, setup_logging


def test_parse_log_targets_from_json() -> None:
    targets = parse_log_targets(
        """
        [
          {
            "name": "stdout-json",
            "output": "stdout",
            "level": "INFO",
            "format": "json"
          },
          {
            "name": "file-text",
            "output": "file",
            "level": "DEBUG",
            "format": "text",
            "file_path": "logs/evepilot.log"
          }
        ]
        """
    )

    assert len(targets) == 2
    assert targets[0].name == "stdout-json"
    assert targets[0].output == "stdout"
    assert targets[1].file_path == "logs/evepilot.log"


def test_setup_logging_uses_simple_target() -> None:
    settings = Settings(
        _env_file=None,
        eve_ng_url="http://10.1.2.3",
        eve_ng_username="admin",
        eve_ng_password="eve",
        log_output="stdout",
        log_level="DEBUG",
        log_format="text",
    )

    setup_logging(settings)

    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert root.handlers[0].level == logging.DEBUG


def test_setup_logging_rejects_unsupported_output() -> None:
    settings = Settings(
        _env_file=None,
        eve_ng_url="http://10.1.2.3",
        eve_ng_username="admin",
        eve_ng_password="eve",
        log_output="redis",
    )

    with pytest.raises(EvePilotConfigError) as exc_info:
        setup_logging(settings)

    assert exc_info.value.code == "config.unsupported_log_output"
