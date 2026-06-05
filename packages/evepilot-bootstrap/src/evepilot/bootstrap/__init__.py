"""Console bootstrap primitives for EvePilot."""

from evepilot.bootstrap.detector import detect_console_state
from evepilot.bootstrap.models import ConsolePrepareResult, ConsoleState
from evepilot.bootstrap.models import ConsoleStateDetection

__all__ = [
    "ConsolePrepareResult",
    "ConsoleState",
    "ConsoleStateDetection",
    "detect_console_state",
]
