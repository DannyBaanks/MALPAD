# MALPAD — M0 gate evidence

Date: 2026-08-30. Milestone: **M0 (contract freeze)**.

## Gates

| Gate | Status | Evidence |
|------|--------|----------|
| `PROTOCOL_FROZEN` | PASS | `docs/PROTOCOL.md` — 1-byte tokens; `@MALPAD:` frames; no collisions among control keys |
| `STATE_MODEL_FROZEN` | PASS | `docs/STATE_MODEL.md` — BOOT/READY/WAIT_SAVE_ACK/HALTED; transition table T1..T17; demo vector |
| `HOST_BOUNDARY_EXPLICIT` | PASS | `docs/HOST_BOUNDARY.md` — allowed/forbidden adapter ops; save-authority flow; no implicit filesystem |

## Executable reference

`tools/editor_ir.py` implements the frozen state model verbatim (the
construction-time contract oracle, NOT the shipping editor logic).

## Tests

`py -m pytest tests -q` → **18 passed**:
- 7 fixture vectors (keystroke → expected event stream) match exactly.
- Hand-computed invariants (demo final state `HEAMALBOLGELO`/cursor 11, cursor
  clamps, backspace-at-start, save allowed/denied/error, WAIT_SAVE_ACK rejects
  edit input, invalid byte → `ERR:INVALID_BYTE`, buffer full → `ERR:BUFFER_FULL`,
  determinism, HALTED ignores input).

## Artifacts

- `docs/PROTOCOL.md`, `docs/STATE_MODEL.md`, `docs/HOST_BOUNDARY.md`
- `tools/editor_ir.py`
- `tests/test_contract.py`, `tests/fixtures/keystrokes/*.keys.bin`,
  `tests/fixtures/expected/*.events.txt`
- `evidence/m0/manifest.json`, `evidence/m0/hashes.sha256`

## Known limitations (M0)

- Single line, fixed 80-byte ASCII buffer. ENTER/UP/DOWN are reserved no-ops
  until M6 (multiline).
- The editor state machine is specified as a Python IR oracle; no Malbolge
  specimen exists yet. M2+ must produce a Malbolge program whose executed
  behavior matches this IR, validated on independent interpreters (the IR never
  self-validates).

## Next gate

**M1_PASS** — Malbolge echo loop (classic 3^10, stdin/stdout, reproducible on
>=2 independent interpreters), per `ROADMAP_MALPAD.md`.