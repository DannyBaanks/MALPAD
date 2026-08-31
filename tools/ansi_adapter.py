"""MALPAD M5 — ANSI adapter (presentation only).

Turns a TerminalModel into ANSI escape sequences. It is THIN: it renders what
the model says, and never re-derives editor semantics. Same model => same ANSI
output (deterministic). It does not need to know whether the events came from
the IR oracle, a fixture, or a future Malbolge specimen.
"""
from __future__ import annotations

from typing import List

from terminal_model import TerminalModel

# ANSI helpers
CSI = "\x1b["
CLEAR_SCREEN = CSI + "2J" + CSI + "H"
RESET = CSI + "0m"
STATUS_ROW = 24  # fixed status line row in a 25-row model


def _cursor(row: int, col: int) -> str:
    return CSI + f"{row + 1};{col + 1}H"


def _erase_line() -> str:
    return CSI + "2K"


def model_to_ansi(m: TerminalModel, width: int = 80) -> str:
    """Render the model to a deterministic ANSI transcript (a single string)."""
    parts = [CLEAR_SCREEN]
    for row, text in sorted(m.lines.items()):
        if row >= STATUS_ROW:
            continue
        clipped = text[:width]
        parts.append(_cursor(row, 0) + _erase_line() + clipped)
    # status line
    parts.append(_cursor(STATUS_ROW, 0) + _erase_line() + m.status[:width])
    # cursor (hide during the draw, show at final position)
    parts.append(_cursor(m.cursor_row, m.cursor_col))
    parts.append(RESET)
    return "".join(parts)


def render_model(m: TerminalModel, width: int = 80) -> str:
    """Deterministic ANSI output for a model (same model => same string)."""
    return model_to_ansi(m, width)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from terminal_model import model_from_stream
    lines = sys.stdin.read().splitlines()
    m = model_from_stream(lines)
    sys.stdout.write(render_model(m))