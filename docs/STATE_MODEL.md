# MALPAD — State model (M0, frozen)

> Status: **STATE_MODEL_FROZEN** (2026-08-30).

## 1. Core data (owned by Malbolge)

| Field | v0 model |
|-------|----------|
| `buffer` | fixed-size ASCII buffer, max **80** bytes, single line |
| `buffer_len` | 0..80 |
| `cursor_col` | 0..buffer_len (cursor may sit one past last char) |
| `row` | always 0 in v0 (single line). Becomes multi-row in M6 |
| `state` | one of BOOT, READY, WAIT_SAVE_ACK, HALTED |

Invariants:
- `buffer_len` is the number of valid chars; cells ≥ `buffer_len` are undefined.
- `0 <= cursor_col <= buffer_len`.
- Characters are ASCII (0x20–0x7E). No control chars in `buffer`.

## 2. States

| State | Meaning |
|-------|---------|
| `BOOT` | initial; emits `BOOT`, becomes READY |
| `READY` | accepting edit input |
| `WAIT_SAVE_ACK` | `SAVE_REQUEST` emitted; awaiting host ACK/DENIED/ERROR byte |
| `HALTED` | after `QUIT`; terminal, no further processing |

## 3. Transitions

Notation: `STATE + INPUT → ACTION → next_state` with emitted event(s).

| # | State | Input | Action | next_state | Emits |
|---|-------|-------|--------|-----------|-------|
| T1 | BOOT | (start) | init buffer_len=0, cursor=0 | READY | `BOOT` |
| T2 | READY | printable ASCII c | insert c at cursor; cursor++ | READY | `CHAR:c` |
| T3 | READY | BACKSPACE (0x08) | if cursor>0: delete char at cursor-1; cursor-- | READY | `LINE:0:<buffer>` `MOVE:<cursor>:0` |
| T4 | READY | LEFT (0x11) | cursor = max(0, cursor-1) | READY | `MOVE:<cursor>:0` |
| T5 | READY | RIGHT (0x12) | cursor = min(buffer_len, cursor+1) | READY | `MOVE:<cursor>:0` |
| T6 | READY | ENTER (0x0A) | no-op (reserved M6) | READY | `STATUS:single-line` |
| T7 | READY | UP (0x13) | no-op (reserved M6) | READY | — |
| T8 | READY | DOWN (0x14) | no-op (reserved M6) | READY | — |
| T9 | READY | SAVE (0x17) | — | WAIT_SAVE_ACK | `SAVE` |
| T10 | READY | QUIT (0x04) | — | HALTED | `QUIT` |
| T11 | READY | invalid byte | ignore | READY | `ERR:INVALID_BYTE` |
| T12 | WAIT_SAVE_ACK | ACK (0x41) | — | READY | `SAVED` `STATUS:saved` |
| T13 | WAIT_SAVE_ACK | DENIED (0x44) | — | READY | `SAVE_DENIED` `STATUS:denied` |
| T14 | WAIT_SAVE_ACK | ERROR (0x45) | — | READY | `SAVE_ERROR` `STATUS:error` |
| T15 | WAIT_SAVE_ACK | any edit byte (printable/control) | ignore (state not accepting edit) | WAIT_SAVE_ACK | `ERR:NOT_ACCEPTING` |
| T16 | WAIT_SAVE_ACK | QUIT (0x04) | — | HALTED | `QUIT` |
| T17 | HALTED | any | ignore | HALTED | — |

## 4. Example trace (first demo script, frozen)

Input bytes:
```
BOOT
H E L L O LEFT LEFT BACKSPACE A ENTER M A L B O L G E SAVE A QUIT
```
- typing: H(0x48) E(0x45) L(0x4C) L O → buffer "HELLO", cursor 5
- LEFT LEFT → cursor 3
- BACKSPACE → deletes char at index 2 ('L') → "HELO", cursor 2
- A → insert at index 2 → "HEALO", cursor 3
- ENTER → no-op (STATUS:single-line)
- M A L B O L G E → inserted at cursor 3 → "HEA" + "MALBOLGE" + "LO" = "HEAMALBOLGELO", cursor 11
- SAVE (0x17) → emits `SAVE`, state WAIT_SAVE_ACK
- ACK (0x41) → emits `SAVED`, `STATUS:saved`, state READY
- QUIT (0x04) → emits `QUIT`, state HALTED

Final logical state: buffer **`HEAMALBOLGELO`**, cursor 11, state HALTED.
(Verified by `tools/editor_ir.py`, the frozen contract oracle.)

This exact trace is the frozen vector `demo` in `tests/fixtures/`.

## 5. Freeze record

- Executable reference: `tools/editor_ir.py` (implements this table verbatim).
- Vectors: `tests/fixtures/keystrokes/demo.keys.txt`,
  `tests/fixtures/expected/demo.events.txt`.
- Gate: **STATE_MODEL_FROZEN**.