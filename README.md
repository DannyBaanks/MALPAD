# MALPAD

An interactive text editor whose **editing semantics execute in classic
Malbolge**. Host adapters only transport input/output and materialize explicitly
authorized capabilities.

```
Malbolge decides WHAT to do.
The host only transports input/output and, when applicable,
materializes explicitly requested host capabilities.
```

**If the adapter had to "understand" what editing to do, we cheated.**

## Status

- **M0** (contracts frozen): `PROTOCOL_FROZEN`, `STATE_MODEL_FROZEN`,
  `HOST_BOUNDARY_EXPLICIT`.
- **M1** (echo loop): **PARTIAL**. Echo loop demonstrated on 2 independent
  backends (Malbolge-Engine C + malbolge-oracle): A→A, ABC→ABC, HELLO→HELLO.
  Empty input → clean halt on engine. **Quit-on-specific-sentinel is
  NOT_DEMONSTRATED** (the program halts at EOF, not on a specific byte — the
  input-branching hard case is M2/M3). See `evidence/m1_echo/GATES.md`.
- **M2** (state/cursor): **PARTIAL**. The **input-branching primitive is
  DEMONSTRATED** via a Malbolge truth-machine on 2 independent backends (input
  `'0'` → halt, `'1'` → loop, identical on engine + oracle). The **full editor
  state machine (cursor+buffer+6-way dispatch) is NOT_DEMONSTRATED** — it needs
  an IR→Malbolge compiler for stateful input-branching programs. Frozen target:
  `tests/editor_state_vectors.json`. See `evidence/m2_state/GATES.md`.

## Core contract (frozen)

- **Input**: 1 byte = 1 token. Printable ASCII inserts; control bytes are
  normalized keys (BACKSPACE 0x08, ENTER 0x0A, LEFT/RIGHT/UP/DOWN 0x11–0x14,
  SAVE 0x17, QUIT 0x04, save ACK/DENIED/ERROR 0x41/0x44/0x45).
- **Output**: `@MALPAD:<EVENT>[:<arg>]` frames per line.
- **State**: BOOT → READY ⇄ WAIT_SAVE_ACK → HALTED. Buffer fixed 80 ASCII,
  single line (v0), cursor 0..buffer_len.
- **Host boundary**: adapter transports/renders/materializes; it never decides
  a character, cursor move, deletion, or save/quit intent.

Docs: `docs/PROTOCOL.md`, `docs/STATE_MODEL.md`, `docs/HOST_BOUNDARY.md`.

## Executable reference

`tools/editor_ir.py` is the **construction-time contract oracle** — it implements
the frozen state model verbatim so the contract is executable and testable. It
is NOT the shipping editor logic: M2+ requires a Malbolge specimen whose executed
behavior matches this IR, checked on independent interpreters.

## Tests

```bash
py -m pytest tests -q          # 18 tests
```

Fixtures: `tests/fixtures/keystrokes/*.keys.bin` → `tests/fixtures/expected/*.events.txt`.
The frozen first-demo vector `demo` types `HELLO ← ← ⌫ A ↵ MALBOLGE`, then
`SAVE ACK QUIT`, and must always end at buffer `HEAMALBOLGELO`, cursor 11.

Human operator guide: `GUIA.md`.

## Hard constraints (from ROADMAP_MALPAD.md)

- Malbolge owns editor state, buffer mutations, cursor semantics, command
  semantics, render decisions, save intent, quit intent.
- No hidden host logic. No fake syscalls. `capability != authority`.
- Same `.mal` + same keystroke script → same logical final state across
  independent classic Malbolge VMs and (later) across ANSI + Win32 frontends.
- No historical-novelty claim yet.