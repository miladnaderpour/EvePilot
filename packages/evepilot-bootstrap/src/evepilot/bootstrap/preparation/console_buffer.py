"""Console output buffer for flow-driven preparation."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ConsoleBuffer:
    """Accumulate console output across partial async reads."""

    lines: list[str] = field(default_factory=list)
    partial: str = ""

    def append(self, chunk: str) -> None:
        """Append output while preserving incomplete prompt fragments."""

        if not chunk:
            return

        text = self.partial + chunk
        self.partial = ""

        for item in text.splitlines(keepends=True):
            if item.endswith(("\n", "\r")):
                self.lines.append(item)
            else:
                self.partial = item

    def text(self) -> str:
        """Return all buffered output."""

        return "".join(self.lines) + self.partial

    def recent_text(self, max_lines: int = 50) -> str:
        """Return recent buffered output for state detection and diagnostics."""

        return "".join(self.lines[-max_lines:]) + self.partial

    def clear_completed_lines(self) -> None:
        """Drop completed lines while preserving an incomplete prompt."""

        self.lines.clear()

    def clear(self) -> None:
        """Drop all buffered output."""

        self.lines.clear()
        self.partial = ""
