"""MALPAD M4 — terminal model (logical render from @MALPAD: events).

The renderer PRESENTS state; it never decides editor semantics. It consumes
@MALPAD: event frames from a NEUTRAL boundary (oracle, fixture, or a future
Malbolge specimen are indistinguishable). Same event stream => same model.

The model is deliberately presentation-only: it applies CLEAR/LINE/MOVE/STATUS
directives and ignores the semantics of edit ops (CHAR) — it displays exactly
what the core says to draw.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

FRAME = "@MALPAD:"


@dataclass
class TerminalModel:
    lines: Dict[int, str] = field(default_factory=dict)
    cursor_col: int = 0
    cursor_row: int = 0
    status: str = ""
    halted: bool = False

    def snapshot(self) -> dict:
        return {
            "lines": {int(k): v for k, v in sorted(self.lines.items())},
            "cursor": {"col": self.cursor_col, "row": self.cursor_row},
            "status": self.status, "halted": self.halted,
        }


def _parse_line_frame(arg: str):
    # LINE:<row>:<text>
    row_s, _, text = arg.partition(":")
    return int(row_s), text


def _parse_move_frame(arg: str):
    # MOVE:<col>:<row>
    c_s, _, r_s = arg.partition(":")
    return int(c_s), int(r_s)


def consume(model: TerminalModel, frame_line: str) -> None:
    """Apply one @MALPAD: frame to the model. Ignores unknown/non-presentation."""
    line = frame_line.strip()
    if not line.startswith(FRAME):
        return
    body = line[len(FRAME):]
    event, _, arg = body.partition(":")
    if event == "CLEAR":
        model.lines.clear()
    elif event == "LINE":
        row, text = _parse_line_frame(arg)
        model.lines[row] = text
    elif event == "MOVE":
        model.cursor_col, model.cursor_row = _parse_move_frame(arg)
    elif event == "STATUS":
        model.status = arg
    elif event == "QUIT":
        model.halted = True
    # CHAR, SAVE, SAVED, SAVE_DENIED, SAVE_ERROR, BOOT, ERR: presentation ignores
    # edit-op and authority signals; it shows only what the core draws.


def render_stream(model: TerminalModel, frame_lines: List[str]) -> TerminalModel:
    for fl in frame_lines:
        consume(model, fl)
    return model


def model_from_stream(frame_lines: List[str]) -> TerminalModel:
    return render_stream(TerminalModel(), frame_lines)


if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().splitlines()
    m = model_from_stream(lines)
    print(m.snapshot())