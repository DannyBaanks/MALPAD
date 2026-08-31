# mutable_cell ? frontier map (robust negative, isolated)

## The frontier, isolated (2026-08-30)

Autobolge relational.synthesize produced programs for a ladder of input-driven
behaviors. Verified cross-backend (malbolge-oracle + Malbolge-Engine) and
cross-input.

| Behavior | Program | Input -> Output | Memory? | Status |
|----------|---------|-----------------|---------|--------|
| output 1st char | `first_char.mal` (`ub`) | AB->A, XY->X | no | DEMONSTRATED |
| output 2nd char | `second_char.mal` (`uta`) | AB->B, XY->Y | no | DEMONSTRATED |
| echo 2 inputs | `echo2.mal` (`ubs\``) | AB->AB, XY->XY | no | DEMONSTRATED |
| REVERSE (AB->BA) | ? | ? | **yes (store+retrieve)** | **NOT_DEMONSTRATED** |

## The isolation (why this is a precise, robust result)

The synthesizer CAN produce **multi-char output** (echo AB->AB) and **read
multiple inputs** (output 2nd/3rd char). The ONLY thing it cannot do is
**reorder** ? output B then re-emit A (reverse, AB->BA). That is precisely the
`mutable_cell` store-then-retrieve primitive.

The reverse failed on every seed and budget tried (5, 11, 99, 123; up to
max_evals=800k, max_len=200, beam 128). It converges to a partial "output last
char" and cannot extend to the store-retrieve. This is a **robust negative** for
the current synthesizer, not a tuning miss.

## The wall

`mutable_cell_load` / `mutable_cell_store`: **NOT_DEMONSTRATED**. BLOCKER:
TOOLING / COMPILATION GAP. The synthesizer's search cannot discover the
store-retrieve pattern; hand-writing it is beyond the current session. This is
NOT a language-impossibility claim ? Malbolge has persistent tape cells.
