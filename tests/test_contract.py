"""MALPAD M0 contract tests.

These freeze the input/output protocol and state model. The contract oracle is
tools/editor_ir.py; a fixture keystroke script must produce its expected event
stream exactly, and the oracle's own output is checked against hand-computed
invariants so the oracle itself cannot silently drift.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from editor_ir import (  # noqa: E402
    run_script, BACKSPACE, ENTER, LEFT, RIGHT, UP, DOWN, SAVE, QUIT,
    ACK, DENIED, ERROR, BUFFER_MAX,
)

FIX = Path(__file__).resolve().parent / "fixtures"
KEYS = FIX / "keystrokes"
EXPECT = FIX / "expected"

ALL_VECTORS = ["demo", "simple", "backspace_clamp", "arrows_clamp",
               "save_denied", "save_error", "quit_only"]


def _run(name):
    script = (KEYS / f"{name}.keys.bin").read_bytes()
    events, snap = run_script(script)
    return events, snap


@pytest.mark.parametrize("name", ALL_VECTORS)
def test_fixture_matches_expected(name):
    events, _ = _run(name)
    expected = (EXPECT / f"{name}.events.txt").read_text(encoding="utf-8")
    assert "\n".join(events) + "\n" == expected


def test_demo_final_state():
    _, snap = _run("demo")
    assert snap["buffer"] == "HEAMALBOLGELO"
    assert snap["cursor"] == 11
    assert snap["state"] == "HALTED"


def test_insert_and_left_right():
    events, snap = run_script(b"ABC" + bytes([QUIT]))
    assert snap["buffer"] == "ABC"
    assert snap["cursor"] == 3
    # insert at middle
    events, snap = run_script(b"AB" + bytes([LEFT]) + b"X" + bytes([QUIT]))
    assert snap["buffer"] == "AXB"
    assert snap["cursor"] == 2


def test_backspace_clamps():
    events, snap = run_script(bytes([BACKSPACE]) + b"AB" + bytes([BACKSPACE, QUIT]))
    assert snap["buffer"] == "A"
    assert snap["cursor"] == 1
    # backspace at start is a no-op on the buffer
    events, snap = run_script(bytes([BACKSPACE, QUIT]))
    assert snap["buffer"] == ""


def test_cursor_clamps():
    events, snap = run_script(bytes([LEFT]) + b"X" + bytes([RIGHT, RIGHT]) + b"Y" + bytes([QUIT]))
    assert snap["buffer"] == "XY"
    assert snap["cursor"] == 2  # clamped to buffer_len


def test_save_flow_allowed():
    events, snap = run_script(b"HI" + bytes([SAVE, ACK, QUIT]))
    assert "@MALPAD:SAVE" in events
    assert "@MALPAD:SAVED" in events
    assert snap["state"] == "HALTED"


def test_save_flow_denied_and_error():
    for ack in (DENIED, ERROR):
        events, snap = run_script(b"HI" + bytes([SAVE, ack, QUIT]))
        frame = "@MALPAD:SAVE_DENIED" if ack == DENIED else "@MALPAD:SAVE_ERROR"
        assert frame in events


def test_save_wait_rejects_edit_input():
    # while WAIT_SAVE_ACK, an edit byte is rejected, not inserted
    events, snap = run_script(b"A" + bytes([SAVE]) + b"X" + bytes([ACK, QUIT]))
    assert "@MALPAD:ERR:NOT_ACCEPTING" in events
    assert snap["buffer"] == "A"  # 'X' not inserted


def test_invalid_byte_rejected():
    events, snap = run_script(bytes([0x00]) + b"A" + bytes([QUIT]))
    assert "@MALPAD:ERR:INVALID_BYTE" in events
    assert snap["buffer"] == "A"


def test_buffer_full():
    # fill to BUFFER_MAX, then one more insert is refused
    fill = b"Z" * BUFFER_MAX
    events, snap = run_script(fill + b"Q" + bytes([QUIT]))
    assert snap["buffer_len"] == BUFFER_MAX
    assert "@MALPAD:ERR:BUFFER_FULL" in events


def test_determinism():
    a1, _ = run_script(b"HELLO" + bytes([LEFT, BACKSPACE]) + b"!" + bytes([QUIT]))
    a2, _ = run_script(b"HELLO" + bytes([LEFT, BACKSPACE]) + b"!" + bytes([QUIT]))
    assert a1 == a2


def test_halted_ignores_input():
    events, snap = run_script(bytes([QUIT]) + b"XYZ")
    assert snap["state"] == "HALTED"
    assert not any("XYZ" in e for e in events)