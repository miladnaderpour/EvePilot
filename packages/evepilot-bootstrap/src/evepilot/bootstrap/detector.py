"""Console state detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern

from evepilot.bootstrap.models import ConsoleState, ConsoleStateDetection

DEFAULT_SAMPLE_LIMIT = 2000


@dataclass(frozen=True, slots=True)
class DetectionPattern:
    """Ordered console state detection pattern."""

    state: ConsoleState
    label: str
    pattern: Pattern[str]


DETECTION_PATTERNS: tuple[DetectionPattern, ...] = (
    DetectionPattern(
        ConsoleState.INITIAL_CONFIG_DIALOG,
        "initial configuration dialog",
        re.compile(r"would you like to enter the initial configuration dialog", re.I),
    ),
    DetectionPattern(
        ConsoleState.PRESS_RETURN,
        "Press RETURN to get started",
        re.compile(r"press return to get started", re.I),
    ),
    DetectionPattern(
        ConsoleState.ROMMON,
        "rommon",
        re.compile(r"(^|\n)\s*rommon\s*\d*\s*>", re.I),
    ),
    DetectionPattern(
        ConsoleState.BOOTING,
        "System Bootstrap",
        re.compile(r"system bootstrap|loading|self decompressing", re.I),
    ),
    DetectionPattern(
        ConsoleState.CONFIG_PROMPT,
        "(config)#",
        re.compile(r"(^|\n).+\(config[^)]*\)#\s*$", re.I),
    ),
    DetectionPattern(
        ConsoleState.LOGIN_PROMPT,
        "Username:",
        re.compile(r"(^|\n)\s*username:\s*$", re.I),
    ),
    DetectionPattern(
        ConsoleState.PASSWORD_PROMPT,
        "Password:",
        re.compile(r"(^|\n)\s*password:\s*$", re.I),
    ),
    DetectionPattern(
        ConsoleState.PRIVILEGED_EXEC_PROMPT,
        "# at line end",
        re.compile(r"(^|\n)[^\n#]+#\s*$"),
    ),
    DetectionPattern(
        ConsoleState.USER_EXEC_PROMPT,
        "> at line end",
        re.compile(r"(^|\n)[^\n>]+>\s*$"),
    ),
)


def detect_console_state(output: str) -> ConsoleStateDetection:
    """Detect the current console state from output text."""

    sample = _sample_output(output)
    if output == "":
        return ConsoleStateDetection(
            state=ConsoleState.UNKNOWN,
            sample=sample,
        )

    for detection_pattern in DETECTION_PATTERNS:
        if detection_pattern.pattern.search(output):
            return ConsoleStateDetection(
                state=detection_pattern.state,
                matched_pattern=detection_pattern.label,
                sample=sample,
            )

    return ConsoleStateDetection(
        state=ConsoleState.UNKNOWN,
        sample=sample,
    )


def _sample_output(output: str) -> str:
    if len(output) <= DEFAULT_SAMPLE_LIMIT:
        return output
    return output[-DEFAULT_SAMPLE_LIMIT:]
