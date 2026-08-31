# MALPAD — M2 gate evidence

Date: 2026-08-30. Milestone: **M2 (state and logical cursor in Malbolge)**.

## Gate: `STATE_MACHINE_DEMONSTRATED`

**Status: PARTIAL.**

| M2 requirement | Status | Evidence |
|----------------|--------|----------|
| Malbolge branches on input value | **DEMONSTRATED** | Malbolge **truth-machine** (esolangs): input `'0'` → emits `'0'` and HALTS (136 steps, halt_opcode); input `'1'` → emits `'1'` and LOOPS. Both behaviors identical on Malbolge-Engine (C) and malbolge-oracle (Python reference) |
| conditional termination | DEMONSTRATED | truth-machine halts on `0`, not on `1` |
| maintain cursor_position / buffer_length / current_state (editor) | **NOT_DEMONSTRATED** | requires a multi-way input dispatch + buffer/cursor persistence in a Malbolge state machine; no such generator/compiler exists yet |
| insert / left / right / backspace in Malbolge | NOT_DEMONSTRATED | same reason |

## What is demonstrated: the input-branching primitive

The truth-machine is the hardest Malbolge primitive M2 needs: **read input, make
a value-dependent decision, and terminate conditionally**. Verified on two
independent 3^10 interpreters:

| input | oracle | engine | agreement |
|-------|--------|--------|-----------|
| `'0'` (0x30) | `'0'`, halt_opcode, 136 steps | OK, `'0'`, 136 steps | yes |
| `'1'` (0x31) | `'1'`..., loops (2000 steps) | TIMEOUT, `'1'`... (loops) | yes |

Program: `evidence/m2_state/truth_machine.mal` (esolangs Truth-machine#Malbolge).
Provenance: esolangs.org/wiki/Truth-machine.

## Why the full editor is NOT_DEMONSTRATED (honest)

An editor core needs a **~6-way input dispatch** (printable insert + LEFT/RIGHT/
BACKSPACE + QUIT) and **persistent cursor/buffer** across loop iterations. The
truth-machine proves the *decision+termination* primitive, but producing a
full editor state machine in Malbolge requires an IR→Malbolge **compiler** for
stateful input-branching programs — a major sub-project (roadmap §8/§9). The
frozen target for that specimen is `tests/editor_state_vectors.json` (from the
M0 IR oracle), and the specimen, once built, must be validated on independent
interpreters, never self-validated.

## Frozen target vectors

`tests/editor_state_vectors.json` — 8 vectors (demo, insert, left/right,
backspace, backspace-at-start, save_denied, save_error, quit) each with input
hex, expected `@MALPAD:` events, and final buffer/cursor/state. These are the
logical editor semantics the future Malbolge specimen must reproduce.

## Artifacts

- `evidence/m2_state/truth_machine.mal`, `out_oracle_{zero,one}.json`,
  `out_engine_{zero,one}.json`
- `tests/editor_state_vectors.json`
- `tests/test_m2_state.py` (27 total tests pass)

## Next

M3 — single-line editable buffer in Malbolge. The path is the IR→Malbolge
state-machine compiler (generate the editor core, verify on independent
interpreters). This is the acknowledged hard sub-project; M2 established the
input-branching primitive it builds on.