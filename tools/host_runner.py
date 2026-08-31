"""MALPAD M7 — host runner: drives the core (oracle) and the save authority seam.

Runs the IR editor core over a keystroke script. When the core emits @MALPAD:SAVE
(entering WAIT_SAVE_ACK), the host SaveAdapter applies policy (write/deny/error)
and feeds the resulting ACK/DENIED/ERROR byte back into the core's input stream.

This keeps the authority boundary explicit: the core only ever issues a REQUEST;
writing happens on the host, behind the adapter, only after that request.
"""
from __future__ import annotations

from typing import List

from save_adapter import SaveAdapter

BACKSPACE, ENTER, LEFT, RIGHT, UP, DOWN, SAVE, QUIT, ACK, DENIED, ERROR = (
    0x08, 0x0A, 0x11, 0x12, 0x13, 0x14, 0x17, 0x04, 0x41, 0x44, 0x45)


def run_with_host(script: bytes, save_adapter: SaveAdapter):
    """Run the core over `script`; intercept SAVE; drive authority seam.

    Returns (events, final_state, [save receipts]).
    """
    from editor_ir import EditorState, step, is_printable
    st = EditorState()
    st.state = "BOOT"
    events: List[str] = []
    events.extend(step(st, 0))  # BOOT transition
    queue = bytearray(script)
    i = 0
    while i < len(queue):
        b = queue[i]
        i += 1
        if st.state == "HALTED":
            break
        before = st.state
        ev = step(st, b)
        events.extend(ev)
        # authority seam: if the core just entered WAIT_SAVE_ACK via SAVE,
        # the host performs the save and injects the ack byte.
        if "@MALPAD:SAVE" in ev and st.state == "WAIT_SAVE_ACK":
            ack = save_adapter.handle_save(_save_payload(st))
            queue.insert(i, ack[0])  # feed ACK/DENIED/ERROR as next input
    return events, st.snapshot(), save_adapter.receipts


def _save_payload(st) -> bytes:
    """The payload the host would persist: the current logical buffer."""
    return bytes(st.buffer)


if __name__ == "__main__":
    import sys, json
    from .save_adapter import SaveAdapter
    script = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else b"HI\x17\x41\x04"
    allowed = sys.argv[2] if len(sys.argv) > 2 else "evidence/m7_demo/saved.txt"
    allow = sys.argv[3] != "--deny-write" if len(sys.argv) > 3 else True
    sa = SaveAdapter(allowed, allow_write=allow)
    events, final, receipts = run_with_host(script, sa)
    sys.stdout.write("\n".join(events) + "\n")
    sys.stderr.write("FINAL " + json.dumps(final) + "\n")
    sys.stderr.write("RECEIPTS " + json.dumps([r.to_dict() for r in receipts]) + "\n")