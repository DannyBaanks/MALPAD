# mutable_cell ? frontier map (input-driven ladder)

## The frontier, precisely located (2026-08-30)

Autobolge relational.synthesize produced programs for a ladder of input-driven
behaviors. Each verified cross-backend (malbolge-oracle + Malbolge-Engine).

| Behavior | Program | Input -> Output | Memory needed? | Status |
|----------|---------|-----------------|----------------|--------|
| output 1st input char | `first_char.mal` (`ub`) | AB->A, XY->X | no | DEMONSTRATED |
| output 2nd input char | `second_char.mal` (`uta`) | AB->B, XY->Y, MALPAD->A | no (sequential read) | DEMONSTRATED |
| output 3rd input char | (transient) | ABC->C | no | DEMONSTRATED |
| REVERSE (AB->BA) | ? | ? | **yes (store+retrieve)** | **NOT_DEMONSTRATED** |

## What this shows

Malbolge (via the synthesizer) CAN do **sequential multi-input processing**
(read N inputs, output a chosen position). It CANNOT (with current tooling) do
**persistent storage** ? store a value on input 1 and re-emit it after input 2
(the reverse test failed on all seeds/budgets tried).

## The wall

`mutable_cell_load` / `mutable_cell_store` (store-and-retrieve out of order):
**NOT_DEMONSTRATED**. BLOCKER: TOOLING / COMPILATION GAP. Not a language-
impossibility claim ? Malbolge has persistent tape cells; we simply lack a
generator that emits a store-retrieve program, and hand-writing one is beyond
the current session.
