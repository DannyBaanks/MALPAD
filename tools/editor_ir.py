"""MALPAD editor IR — executable reference state machine (M0 contract oracle).

This is the CONSTRUCTION-TIME oracle for the frozen contract. It implements
docs/STATE_MODEL.md verbatim. It is NOT the shipping editor logic: the final
claim (M2+) requires a Malbolge specimen whose executed behavior matches this
IR. The IR exists so the contract is executable and testable before any
Malbolge programming.

The IR is an oracle, not the only validator: the Malbolge specimen will later be
checked on independent interpreters against these same event vectors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

# ---- protocol constants (docs/PROTOCOL.md) --------------------------------
BACKSPACE = 0x08
ENTER = 0x0A
LEFT = 0x11
RIGHT = 0x12
UP = 0x13
DOWN = 0x14
SAVE = 0x17
QUIT = 0x04
ACK = 0x41
DENIED = 0x44
ERROR = 0x45

BUFFER_MAX = 80
SPECIAL = {BACKSPACE, ENTER, LEFT, RIGHT, UP, DOWN, SAVE, QUIT, ACK, DENIED, ERROR}


@dataclass
class EditorState:
    buffer: bytearray = field(default_factory=bytearray)
    cursor: int = 0
    row: int = 0
    state: str = "BOOT"

    def snapshot(self) -> dict:
        return {"buffer": bytes(self.buffer).decode("ascii", "replace"),
                "buffer_len": len(self.buffer), "cursor": self.cursor,
                "row": self.row, "state": self.state}


def is_printable(b: int) -> bool:
    return 0x20 <= b <= 0x7E


def step(st: EditorState, b: int) -> List[str]:
    """Apply one input byte to the state machine, return emitted frames."""
    out: List[str] = []
    if st.state == "BOOT":
        st.state = "READY"
        out.append("@MALPAD:BOOT")
        return out

    if st.state == "HALTED":
        return out

    if st.state == "WAIT_SAVE_ACK":
        if b == ACK:
            st.state = "READY"
            out.append("@MALPAD:SAVED")
            out.append("@MALPAD:STATUS:saved")
        elif b == DENIED:
            st.state = "READY"
            out.append("@MALPAD:SAVE_DENIED")
            out.append("@MALPAD:STATUS:denied")
        elif b == ERROR:
            st.state = "READY"
            out.append("@MALPAD:SAVE_ERROR")
            out.append("@MALPAD:STATUS:error")
        elif b == QUIT:
            st.state = "HALTED"
            out.append("@MALPAD:QUIT")
        else:
            out.append("@MALPAD:ERR:NOT_ACCEPTING")
        return out

    # READY
    if is_printable(b):
        if len(st.buffer) < BUFFER_MAX:
            st.buffer.insert(st.cursor, b)
            st.cursor += 1
            out.append(f"@MALPAD:CHAR:{b}")
            # M4 render-protocol: the core decides what to draw — it redraws the
            # full edited line + cursor after every mutation, so the renderer
            # only presents state (never re-derives editing).
            out.append(f"@MALPAD:LINE:0:{bytes(st.buffer).decode('ascii','replace')}")
            out.append(f"@MALPAD:MOVE:{st.cursor}:0")
        else:
            out.append("@MALPAD:STATUS:buffer-full")
            out.append("@MALPAD:ERR:BUFFER_FULL")
        return out
    if b == BACKSPACE:
        if st.cursor > 0:
            del st.buffer[st.cursor - 1]
            st.cursor -= 1
        out.append(f"@MALPAD:LINE:0:{bytes(st.buffer).decode('ascii','replace')}")
        out.append(f"@MALPAD:MOVE:{st.cursor}:0")
        return out
    if b == LEFT:
        st.cursor = max(0, st.cursor - 1)
        out.append(f"@MALPAD:MOVE:{st.cursor}:0")
        return out
    if b == RIGHT:
        st.cursor = min(len(st.buffer), st.cursor + 1)
        out.append(f"@MALPAD:MOVE:{st.cursor}:0")
        return out
    if b == ENTER:
        out.append("@MALPAD:STATUS:single-line")
        return out
    if b in (UP, DOWN):
        return out
    if b == SAVE:
        st.state = "WAIT_SAVE_ACK"
        out.append("@MALPAD:SAVE")
        return out
    if b == QUIT:
        st.state = "HALTED"
        out.append("@MALPAD:QUIT")
        return out
    # invalid byte
    out.append("@MALPAD:ERR:INVALID_BYTE")
    return out


def run_script(script: bytes) -> tuple:
    """Run a keystroke byte script; return (events, final_snapshot)."""
    st = EditorState()
    st.state = "BOOT"
    events: List[str] = []
    events.extend(step(st, 0))  # BOOT transition
    for b in script:
        events.extend(step(st, b))
        if st.state == "HALTED":
            break
    return events, st.snapshot()


def events_to_text(events: List[str]) -> str:
    return "\n".join(events) + "\n"


if __name__ == "__main__":
    import sys
    # read keystroke script as raw bytes from a file, print event stream
    if len(sys.argv) > 1:
        script = open(sys.argv[1], "rb").read()
        events, snap = run_script(script)
        sys.stdout.write(events_to_text(events))
        sys.stderr.write("FINAL " + repr(snap) + "\n")
    else:
        # demo
        ev, snap = run_script(b"HELLO\x11\x11\x08A\x0aMALBOLGE\x17A\x04")
        sys.stdout.write(events_to_text(ev))
        sys.stderr.write("FINAL " + repr(snap) + "\n")