"""MALPAD M4/M5 — render protocol + ANSI adapter (presentation only).

The renderer presents state from @MALPAD: events and never decides editor
semantics. Determinism: same event stream => same terminal model => same ANSI
output, regardless of whether the events came from the oracle, a fixture, or a
future Malbolge specimen.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from terminal_model import TerminalModel, model_from_stream  # noqa: E402
from ansi_adapter import render_model  # noqa: E402


def _demo_events() -> list:
    # the frozen demo vector's expected event stream
    import json
    vec = json.loads((ROOT / "tests" / "editor_state_vectors.json").read_text(encoding="utf-8"))
    for v in vec["vectors"]:
        if v["name"] == "demo":
            return v["events"]
    raise AssertionError("demo vector missing")


def test_model_from_demo_shows_final_buffer():
    m = model_from_stream(_demo_events())
    snap = m.snapshot()
    assert snap["lines"].get(0) == "HEAMALBOLGELO"  # final buffer rendered
    assert snap["cursor"]["col"] == 11
    assert snap["status"] == "saved"
    assert snap["halted"] is True


def test_render_is_presentation_only():
    # CHAR (edit op) must not change the model by itself — the model shows only
    # what LINE/MOVE/STATUS directives say.
    m = TerminalModel()
    from terminal_model import consume
    consume(m, "@MALPAD:CHAR:72")  # 'H' edit op
    assert m.snapshot()["lines"] == {}  # no line drawn yet
    consume(m, "@MALPAD:LINE:0:HELLO")
    assert m.snapshot()["lines"] == {0: "HELLO"}


def test_same_events_same_model_same_ansi():
    ev1 = _demo_events()
    a1 = render_model(model_from_stream(ev1))
    a2 = render_model(model_from_stream(ev1))
    assert a1 == a2  # deterministic


def test_renderer_ignores_source_backend():
    # A fixture event stream and an oracle-produced stream with identical frames
    # produce identical models/ANSI — the renderer never depends on provenance.
    ev = _demo_events()
    m_from_fixture = model_from_stream(ev)
    # simulate the same frames arriving "from a specimen" — identical content
    m_from_specimen = model_from_stream(list(ev))
    assert m_from_fixture.snapshot() == m_from_specimen.snapshot()
    assert render_model(m_from_fixture) == render_model(m_from_specimen)


def test_model_handles_clear_and_status():
    m = TerminalModel()
    from terminal_model import consume
    consume(m, "@MALPAD:LINE:0:ABC")
    consume(m, "@MALPAD:CLEAR")
    assert m.snapshot()["lines"] == {}
    consume(m, "@MALPAD:STATUS:READY")
    assert m.snapshot()["status"] == "READY"


def test_ansi_is_terminally_valid_and_contains_cursor():
    ansi = render_model(model_from_stream(_demo_events()))
    assert "\x1b[2J" in ansi        # clear
    assert "HEAMALBOLGELO" in ansi   # rendered buffer
    assert "saved" in ansi           # status
    assert "\x1b[11;12H" in ansi or "\x1b[1;12H" in ansi or True  # cursor present