"""MALPAD compiler — lowering pipeline (honest status).

The compiler refuses to emit a Malbolge program that assumes unproven stateful
primitives. DEMONSTRATED primitives (read/emit/halt) lower; stateful ones
(compare_general, mutable_cell, cursor, buffer) are NOT_DEMONSTRATED and raise.
This is the honest front of the M3 wall: the framework exists, the brain does not.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from malbolge_compiler import (  # noqa: E402
    build_plan, compile_state_machine, state_test_1_plan,
)


def test_demonstrated_primitives_lower():
    plan = build_plan("t", ["read_input", "emit_event", "halt_loop"])
    assert plan.all_demonstrated
    statuses = {o.ir_op: o.status for o in plan.operations}
    assert statuses == {"read_input": "DEMONSTRATED",
                        "emit_event": "DEMONSTRATED",
                        "halt_loop": "DEMONSTRATED"}


def test_branch_simple_is_partial():
    plan = build_plan("t", ["branch_simple"])
    assert not plan.all_demonstrated
    assert plan.operations[0].status == "PARTIAL"


@pytest.mark.parametrize("op", ["compare_input", "mutable_cell_load",
                                "mutable_cell_store", "cursor_state",
                                "buffer_mutate"])
def test_stateful_primitives_not_demonstrated(op):
    plan = build_plan("t", [op])
    assert plan.operations[0].status == "NOT_DEMONSTRATED"


def test_compiler_refuses_to_emit_with_unproven_state():
    # An editor state machine needs mutable buffer/cursor -> NOT_DEMONSTRATED.
    with pytest.raises(NotImplementedError):
        compile_state_machine(["read_input", "compare_input",
                               "mutable_cell_store", "buffer_mutate",
                               "emit_event"])


def test_state_test_1_requires_mutable_cell():
    # STATE TEST #1 (remember a value across inputs) needs persistent state.
    plan = state_test_1_plan()
    assert not plan.all_demonstrated
    m = {o.ir_op: o.status for o in plan.operations}
    assert m["mutable_cell_store"] == "NOT_DEMONSTRATED"
    assert m["mutable_cell_load"] == "NOT_DEMONSTRATED"
    # and the compiler must not emit a fake counter for it
    with pytest.raises(NotImplementedError):
        compile_state_machine([o.ir_op for o in plan.operations])