# MALPAD — compiler gate evidence (lowering pipeline, honest front)

Date: 2026-08-30.

## Status

**FRAMEWORK: PRESENT. STATEFUL BRAIN: NOT_DEMONSTRATED.**

The IR→Malbolge compiler scaffolding exists (`tools/malbolge_compiler.py`) and
is honest: it lowers the DEMONSTRATED primitives and **refuses to emit** a
Malbolge program that assumes any NOT_DEMONSTRATED primitive (never "a ver si
jala").

## Primitive lowering status (from the compiler)

| IR op | Status | Mechanism |
|-------|--------|-----------|
| read_input | DEMONSTRATED | `/` (reference: getc; EOF→59048) |
| emit_event | DEMONSTRATED | `<` (putc) |
| halt_loop | DEMONSTRATED | `v` + jump (truth-machine) |
| branch_simple | PARTIAL | truth-machine 0/1 only; not general |
| compare_input | NOT_DEMONSTRATED | general value comparison not lowered |
| mutable_cell_load / store | NOT_DEMONSTRATED | persistent cell across loop not demonstrated |
| cursor_state | NOT_DEMONSTRATED | mutable index not demonstrated |
| buffer_mutate | NOT_DEMONSTRATED | insert/delete over persistent buffer not demonstrated |

## STATE TEST #1 (the "first neuron")

> A Malbolge program that REMEMBERS it received A when processing the next
> input. Requires persistent mutable state (mutable_cell_load/store).

The compiler builds the plan for STATE TEST #1 and correctly reports it is
blocked on `mutable_cell_store` / `mutable_cell_load` (NOT_DEMONSTRATED). It
does NOT emit a fake counter. This is the honest front of the M3 wall,
expressed as code.

## The law the compiler enforces

- `generator != oracle`: any emitted specimen is validated on independent
  interpreters, never by its own generator.
- The compiler refuses to emit unproven primitives.
- M3 stays NOT_DEMONSTRATED until a real specimen reproduces
  `editor_state_vectors.json` cross-backend.

## Artifacts

- `tools/malbolge_compiler.py`
- `tests/test_compiler.py` (52 total tests pass)
- Blockers: compare/mutable_cell/cursor/buffer — NOT_DEMONSTRATED (tooling /
  compilation gap; NOT a language-impossibility claim).