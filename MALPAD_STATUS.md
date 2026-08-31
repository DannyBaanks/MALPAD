# MALPAD — status dashboard (honest, per-milestone)

No global "80% complete" metric. Each milestone is a distinct property with its
own gate and status.

| Milestone | Gate | Status | Evidence |
|-----------|------|--------|----------|
| M0 | contracts frozen | **DEMONSTRATED** | PROTOCOL/STATE_MODEL/HOST_BOUNDARY + 18 tests |
| M1 | echo loop | **PARTIAL** | echo cross-backend (A/ABC/HELLO); quit-on-sentinel NOT_DEMONSTRATED |
| M2 | input branching | **PARTIAL** | truth-machine cross-backend (0→halt, 1→loop); full editor state NOT_DEMONSTRATED |
| M3 | editable buffer in Malbolge | **NOT_DEMONSTRATED** | wall = IR→Malbolge compiler gap; frozen vectors as target |
| M4 | logical render | **DEMONSTRATED** | terminal model from @MALPAD: events, presentation-only |
| M5 | ANSI adapter | **DEMONSTRATED** | model → ANSI, deterministic, backend-independent |
| M7 | save authority seam | **DEMONSTRATED** | request vs authority separated; write/deny/fail + receipts |
| Bridge | Python body ↔ Malbolge brain | **DEMONSTRATED (transport)** | generated Malbolge emits @MALPAD: frames, parsed → model → ANSI, backend-independent |
| Compiler | IR→Malbolge lowering pipeline | **FRAMEWORK PRESENT / STATE NOT_DEMONSTRATED** | lowers read/emit/halt; refuses to emit unproven stateful primitives; input-driven primitive DEMONSTRATED (synthesized, cross-backend); mutable_cell memory NOT_DEMONSTRATED (reverse test failed) |

## Architecture (reframe)

Python is the **body**; Malbolge is the **editor brain**; the byte protocol is
the cable. Python MAY translate `VK_LEFT → LEFT`, NEVER `LEFT → cursor--`.
See `docs/MALPAD_ARCHITECTURE.md`. Win32 is a rear problem (M10); the bridge
+ M4/M5/M7 already define the boundary any frontend connects to.

## Compiler (future)

| IR→Malbolge stateful compiler | STATUS |
|-------------------------------|--------|
| overall | FUTURE RESEARCH / REQUIRED FOR M3 |
| read_input / emit / halt-loop primitives | DEMONSTRATED (via existing programs) |
| compare_input / branch | PARTIAL (truth-machine 0/1) |
| mutable_cell / cursor / buffer | NOT_DEMONSTRATED |
| validation | generator != oracle, on independent interpreters |

See `docs/IR_TO_MALBOLGE_COMPILER_SCOPE.md`.

## Claims earned (M4/M5/M7)

- The presentation layer (render) is independently testable and backend-neutral
  before the Malbolge stateful core exists.
- Save authority is a host-side seam: the core only issues requests; writes are
  behind policy + explicit request, with truthful receipts.
- These properties are orthogonal to M3: **they hold even while M3 is red**.

## Claims still forbidden

- "M3 works" / any Malbolge-implements-the-editor claim (NOT_DEMONSTRATED).
- "Malbolge cannot implement it" (NOT DEMONSTRATED — DO NOT CLAIM).
- "Save intent = file saved" (never).
- Any global completion metric.
- The compiler is not "basically solved", not "impossible", not a trivial TODO.

## Test suite

`py -m pytest tests -q` → **54 passed** (M0 18, M1 5, M2 4, M4/M5 6, M7 6,
bridge 4, compiler 9, mutable_cell 2).