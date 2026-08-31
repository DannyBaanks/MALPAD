# MALPAD — M3 gate (frozen record)

> Date: 2026-08-30. This is the explicit, frozen M3 record. It is a technical
> result, not a failure narrative. The wall is data.

## CLAIM

> An editable runtime buffer (single-line, fixed-size, ASCII, with
> insert/backspace/left/right) implemented **inside Malbolge** and reproducing
> `tests/editor_state_vectors.json`.

## STATUS

**NOT_DEMONSTRATED.**

This status is frozen. It is not reduced, not softened, and not converted into
evidence by scaffolding or by shipping a large Malbolge specimen "hoping it
works". M3 earns green only when a real specimen is validated on independent
interpreters against the frozen vectors.

## DEMONSTRATED SO FAR

- runtime **input** is possible (M1 echo; M2 truth-machine);
- **branching on runtime input** is possible (M2 truth-machine: `'0'`→halt,
  `'1'`→loop, cross-backend);
- truth-machine behavior reproduced **cross-backend** (Malbolge-Engine C +
  malbolge-oracle);
- **frozen editor state vectors exist** as target semantics
  (`tests/editor_state_vectors.json`, from the M0 IR oracle).

## MISSING

- a specimen implementing mutable editable state;
- an IR→Malbolge **lowering** for the required stateful operations;
- **independent backend validation** of that specimen.

## BLOCKER CLASS

**TOOLING / COMPILATION GAP** — not a language-impossibility claim.

## Critical distinction (do not blur)

| Statement | Status |
|-----------|--------|
| A. "No reusable stateful Malbolge specimen was found." | DEMONSTRATED (inventory: echo/cat/hello/99bottles/truth-machine only) |
| B. "No generator for this stateful program class was found in the searched ecosystem." | DEMONSTRATED (malbolge-generator emits text-output programs only) |
| C. "Hand-writing one in this session is not realistic." | Engineering judgment / scope decision |
| D. "**Malbolge cannot implement mutable editor state.**" | **NOT DEMONSTRATED. DO NOT CLAIM.** |

The correct claim is: *"We do not currently possess a demonstrated construction
path for this stateful specimen."*

## Freeze of the target

`tests/editor_state_vectors.json` is the frozen oracle semantics. **It does not
move** to accommodate generator limitations. The future compiler must reach the
target; the target does not bend to make a compiler pass.

`generator != oracle`.

## Reference

- `evidence/m3_buffer/GATES.md` (the wall evidence)
- `tests/editor_state_vectors.json` (frozen target)