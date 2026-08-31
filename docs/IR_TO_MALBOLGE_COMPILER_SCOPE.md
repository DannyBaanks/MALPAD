# IR→Malbolge stateful compiler — scope (frozen boundary)

> Status: **FUTURE RESEARCH / REQUIRED FOR M3**. This is a scope document only —
> no compiler framework is built here, no 30-module backend architecture is
> invented. It exists so the problem can be resumed without reconstructing it
> from narrative. It is not a TODO, not "impossible", not "basically solved".

## Goal

Incrementally demonstrate the **lowering primitives** needed to make a Malbolge
specimen reproduce `tests/editor_state_vectors.json`, validated on independent
interpreters (`generator != oracle`).

## Target (frozen, immovable)

`tests/editor_state_vectors.json` — 8 vectors, each an input byte sequence and
its expected `@MALPAD:` event stream + final buffer/cursor/state.

## Minimum primitives (not all need to be direct Malbolge ops)

For each: **IR semantic operation → lowering strategy → Malbolge mechanism →
independent validation**, marked DEMONSTRATED / PARTIAL / NOT_DEMONSTRATED.

| IR semantic op | Lowering strategy | Malbolge mechanism | Independent validation |
|----------------|-------------------|--------------------|------------------------|
| read_input | direct opcode | `/` (Appendix C / reference: getc; EOF→59048) | DEMONSTRATED (M1 echo, M2 truth-machine) |
| compare_input | value-combine + branch | crazy (`p`) to derive a pointer, then `i`/`j` jump | PARTIAL (truth-machine branches 0 vs 1; not a general comparator) |
| branch | conditional jump | `i` (c=[d]) / `j` (d=[d]) after comparator | PARTIAL |
| mutable_cell_load | read a tape cell as data | `[d]` read via `p`/`*`/`j` | PARTIAL (echo reads input cell) |
| mutable_cell_store | write a tape cell | `p`/`*` write back to `[d]` | PARTIAL (truth-machine mutates a cell across loop) |
| cursor/index state | persistent counter cell | tape cell mutated across loop iterations | NOT_DEMONSTRATED |
| buffer (append/insert/delete) | persistent array + shift | multiple cells + crazy/rotate | NOT_DEMONSTRATED |
| emit_event | output byte(s) | `<` | DEMONSTRATED (echo/output) |
| halt/loop semantics | conditional halt | `v` (opcode 81) / loop on non-halt | DEMONSTRATED (truth-machine: `0`→halt, `1`→loop) |

## Key open problems (NOT_DEMONSTRATED)

1. **General input comparison** — truth-machine does a specific 0/1 branch;
   a ~6-way dispatch on arbitrary bytes (printable + control keys) needs a
   repeatable value-comparison primitive.
2. **Persistent mutable buffer across loop iterations** — a multi-cell buffer
   that survives and mutates across the input loop.
3. **Cursor as mutable state** — an index that increments/decrements/clamps.

## Validation rule

Every lowering primitive is validated on independent interpreters (Walbolge,
Malbolge-Engine, malbolge-oracle, Autobolge), never by its own generator. The
end specimen must reproduce `editor_state_vectors.json` exactly.

## Resumption point

When returning, do NOT "write a Malbolge editor". Do: *demonstrate each
lowering primitive above incrementally, verifying each on independent
interpreters, until the full vector set is reproduced.*

BLOCKER CLASS: **TOOLING / COMPILATION GAP**. No impossibility claim.