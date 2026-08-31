"""MALPAD — mutable_cell attempt: input-driven primitive (synthesized).

The Autobolge relational synthesizer produced a Malbolge program that READS
input and outputs it (input-driven, not fixed). Verified cross-backend. The
memory primitive (store a value across inputs and retrieve it later) was
attempted (reverse test) and could NOT be synthesized — mutable_cell stays
NOT_DEMONSTRATED. This is data, recorded honestly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ID_MAL = ROOT / "evidence" / "mutable_cell" / "input_driven.mal"


def _oracle(inp, prog=None):
    import sys as _s
    d = r"C:\Development\ISyCo Git\malbolge-oracle"
    if d not in _s.path:
        _s.path.insert(0, d)
    from oracle import Oracle
    o = Oracle()
    o.load_ascii(prog or ID_MAL.read_text(encoding="utf-8").strip())
    o.provide_input(inp)
    return o.run(2000)


def _engine(inp, prog=None):
    import subprocess, json
    exe = r"C:\Development\ISyCo Git\Malbolge-Engine\malbolge-ipc.exe"
    if not Path(exe).exists():
        pytest.skip("malbolge-engine not present")
    p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    json.loads(p.stdout.readline())
    p.stdin.write(json.dumps({"id": 1, "op": "run",
                              "program": prog or ID_MAL.read_text(encoding="utf-8").strip(),
                              "steps": 2000, "input": inp}) + "\n")
    p.stdin.flush()
    r = json.loads(p.stdout.readline())
    p.kill()
    return r


def test_input_driven_program_cross_backend():
    if not ID_MAL.exists():
        pytest.skip("synthesized input-driven program not present")
    for inp, exp in (("XY", "X"), ("AY", "A"), ("BY", "B")):
        ro = _oracle(inp)
        re_ = _engine(inp)
        assert ro.output == exp, f"oracle input {inp}: {ro.output!r}"
        assert re_["output"] == exp, f"engine input {inp}: {re_['output']!r}"


def test_memory_reverse_not_demonstrated():
    # The reverse test (input "AB" -> output "BA") requires persistent memory.
    # We attempted it with the synthesizer and it failed. This test records that
    # the primitive is NOT demonstrated — the synthesizer produced only the
    # second char, not a stored-and-retrieved first char.
    from malbolge_compiler import state_test_1_plan, compile_state_machine
    plan = state_test_1_plan()
    assert not plan.all_demonstrated
    with pytest.raises(NotImplementedError):
        compile_state_machine([o.ir_op for o in plan.operations])