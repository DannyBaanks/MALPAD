"""MALPAD IR→Malbolge compiler — lowering pipeline scaffolding.

This is the COMPILER FRAMEWORK (honest structure). It lowers the frozen editor
IR toward Malbolge. The DEMONSTRATED primitives (read/emit/halt, and the
truth-machine branch pattern) lower to known Malbolge fragments. The STATEFUL
primitives (compare_general, mutable_cell, cursor, buffer) are NOT_DEMONSTRATED
and RAISE — they are never silently assumed to work.

Scaffolding is NOT evidence. This module reports, per primitive, its lowering
status; the stateful ones stay NOT_DEMONSTRATED until a real Malbolge specimen
reproduces editor_state_vectors.json on independent interpreters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LoweringResult:
    ir_op: str
    status: str          # DEMONSTRATED / PARTIAL / NOT_DEMONSTRATED
    mechanism: str       # Malbolge mechanism
    malbolge_fragment: str  # actual Malbolge code or reference to one
    note: str = ""


# The truth-machine (esolangs) is the reference for input+branch+halt:
#   read input ('/'), branch on 0 vs 1, halt on 0 / loop on 1.
TRUTH_MACHINE = "truth-machine (esolangs): read + 0/1 branch + conditional halt"
# The cat/echo (M1) is the reference for read+emit+repeat:
CAT = "esolangs cat (M1): read + emit + repeat loop"


@dataclass
class CompilerPlan:
    target: str
    operations: List[LoweringResult] = field(default_factory=list)

    @property
    def all_demonstrated(self) -> bool:
        return all(op.status == "DEMONSTRATED" for op in self.operations)

    def to_dict(self) -> dict:
        return {"target": self.target,
                "all_demonstrated": self.all_demonstrated,
                "operations": [{"ir_op": o.ir_op, "status": o.status,
                                "mechanism": o.mechanism,
                                "malbolge_fragment": o.malbolge_fragment,
                                "note": o.note} for o in self.operations]}


def _lower_op(ir_op: str) -> LoweringResult:
    """Return the lowering for one IR op (status honest; stateful raises later)."""
    if ir_op == "read_input":
        return LoweringResult("read_input", "DEMONSTRATED", "opcode '/' (getc)",
                              TRUTH_MACHINE + " / " + CAT,
                              "reads a byte; EOF->59048 (reference semantics)")
    if ir_op == "emit_event":
        return LoweringResult("emit_event", "DEMONSTRATED", "opcode '<' (putc)",
                              CAT, "outputs a byte")
    if ir_op == "halt_loop":
        return LoweringResult("halt_loop", "DEMONSTRATED", "opcode 'v' + jump",
                              TRUTH_MACHINE, "truth-machine: 0->halt, 1->loop")
    if ir_op == "branch_simple":
        return LoweringResult("branch_simple", "PARTIAL", "crazy-derived pointer + i/j",
                              TRUTH_MACHINE, "truth-machine branches 0 vs 1 only; not a general comparator")
    if ir_op == "compare_input":
        return LoweringResult("compare_input", "NOT_DEMONSTRATED", "?", "",
                              "general input->value comparison not yet lowered")
    if ir_op == "mutable_cell_load":
        return LoweringResult("mutable_cell_load", "NOT_DEMONSTRATED", "?", "",
                              "persistent cell read across loop iterations not demonstrated")
    if ir_op == "mutable_cell_store":
        return LoweringResult("mutable_cell_store", "NOT_DEMONSTRATED", "?", "",
                              "persistent cell write across loop iterations not demonstrated")
    if ir_op == "cursor_state":
        return LoweringResult("cursor_state", "NOT_DEMONSTRATED", "?", "",
                              "mutable cursor index not demonstrated")
    if ir_op == "buffer_mutate":
        return LoweringResult("buffer_mutate", "NOT_DEMONSTRATED", "?", "",
                              "insert/delete over a persistent buffer not demonstrated")
    raise ValueError(f"unknown IR op: {ir_op}")


def build_plan(target: str, ir_ops: List[str]) -> CompilerPlan:
    """Plan the lowering of an IR op sequence. Stateful ops stay NOT_DEMONSTRATED."""
    return CompilerPlan(target=target,
                        operations=[_lower_op(op) for op in ir_ops])


def compile_state_machine(ir_ops: List[str]) -> CompilerPlan:
    """Attempt to lower a state-machine op sequence to Malbolge.

    Raises if a required op is NOT_DEMONSTRATED — the compiler refuses to emit a
    Malbolge program that assumes unproven primitives (never 'a ver si jala').
    """
    plan = build_plan("editor_state_machine", ir_ops)
    if not plan.all_demonstrated:
        missing = [o.ir_op for o in plan.operations
                   if o.status != "DEMONSTRATED"]
        raise NotImplementedError(
            f"cannot lower editor state machine: unproven primitives {missing}. "
            f"BLOCKER: TOOLING / COMPILATION GAP (NOT_DEMONSTRATED, not impossible).")
    return plan


def state_test_1_plan() -> CompilerPlan:
    """MALBOLGE STATE TEST #1: a program that REMEMBERS a value between inputs.

    Input: A then ?. Output must demonstrate the program remembered A.
    Requires persistent mutable state (mutable_cell) — the missing primitive.
    """
    return build_plan("state_test_1 (remember a value across inputs)",
                      ["read_input", "mutable_cell_store",
                       "mutable_cell_load", "emit_event"])