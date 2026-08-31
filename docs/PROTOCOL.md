# MALPAD — Protocol (M0, frozen)

> Status: **PROTOCOL_FROZEN** (2026-08-30). Changes after freeze require bumping
> the protocol version and a migration note in `evidence/m0/`.

The MALPAD protocol is the contract between the **Malbolge core** (the editor
state machine) and **host adapters** (terminal / Win32). Malbolge owns editor
semantics; the adapter transports input and renders events.

## 1. Version

`MALPAD-PROTOCOL/1`

## 2. Input encoding — 1 byte = 1 input token

The core consumes a stream of bytes on stdin. Each byte is exactly one token.

### 2.1 Printable ASCII (0x20–0x7E)

The byte is the character to insert at the cursor. → `INSERT_CHAR`.

### 2.2 Control / special keys (host normalizes to these bytes before sending)

| Byte | Name | Semantics (v0) |
|------|------|----------------|
| `0x08` | BACKSPACE | delete char before cursor |
| `0x0A` | ENTER | reserved (single-line v0: no-op). Active in M6 (multiline) |
| `0x11` | LEFT | cursor left (clamp 0) |
| `0x12` | RIGHT | cursor right (clamp buffer_len) |
| `0x13` | UP | reserved (M6 multiline). v0: no-op |
| `0x14` | DOWN | reserved (M6 multiline). v0: no-op |
| `0x17` | SAVE | emit `SAVE_REQUEST`, enter WAIT_SAVE_ACK |
| `0x04` | QUIT | emit `QUIT`, halt |
| `0x41` | SAVE_ACK | host → core ACK (valid only in WAIT_SAVE_ACK) |
| `0x44` | SAVE_DENIED | host → core DENIED (valid only in WAIT_SAVE_ACK) |
| `0x45` | SAVE_ERROR | host → core ERROR (valid only in WAIT_SAVE_ACK) |

The SAVE/QUIT/ACK bytes were chosen to avoid collisions with the arrow keys
(0x11–0x14), BACKSPACE (0x08) and ENTER (0x0A). All control tokens are distinct
from printable ASCII (0x20–0x7E).

### 2.3 Unknown / reserved byte

Any byte not listed (including 0x00–0x07, 0x0B–0x10, 0x15–0x16, 0x18–0x1F,
0x7F) is **INVALID**. The core ignores it and emits `ERR:INVALID_BYTE`, stays in
the current state (defensive; see HOST_BOUNDARY / hardening M11).

## 3. Output / event encoding — `@MALPAD:` frames

The core emits one frame per line on stdout. A frame is `@MALPAD:<EVENT>[:<arg>]`
followed by `\n`.

| Frame | Args | Meaning |
|-------|------|---------|
| `@MALPAD:BOOT` | — | core started, state READY, buffer empty, cursor 0 |
| `@MALPAD:CLEAR` | — | adapter should clear the view |
| `@MALPAD:CHAR:<byte>` | byte 0–255 | insert this character at current cursor (logical) |
| `@MALPAD:MOVE:<col>:<row>` | col,row ints | place cursor at logical position |
| `@MALPAD:LINE:<row>:<text>` | row int, text | render full line `<row>` as `<text>` |
| `@MALPAD:STATUS:<text>` | text | render status bar text |
| `@MALPAD:SAVE` | — | save **request** (no authority; adapter decides) |
| `@MALPAD:SAVED` | — | save acknowledged by adapter |
| `@MALPAD:SAVE_DENIED` | — | adapter refused (policy) |
| `@MALPAD:SAVE_ERROR` | — | adapter write failed |
| `@MALPAD:QUIT` | — | core halting cleanly |
| `@MALPAD:ERR:<code>` | code | protocol/state error (defensive) |

### 3.1 Frames the Malbolge core may emit

`BOOT`, `CLEAR`, `CHAR`, `MOVE`, `LINE`, `STATUS`, `SAVE`, `SAVED`,
`SAVE_DENIED`, `SAVE_ERROR`, `QUIT`, `ERR`.

> **Render redraw (M4 refinement).** After every buffer mutation the core emits a
> full `LINE:<row>:<text>` redraw of the edited line plus a `MOVE:<col>:<row>`
> cursor directive, so the renderer only *presents* state and never re-derives
> editing. `CHAR` remains the edit-op signal; the renderer displays what the
> `LINE`/`MOVE` directives say. Logical editor semantics (buffer/cursor/state)
> are unaffected by this presentation addition.

### 3.2 Frames the adapter only ever receives

All of the above. The adapter never emits `@MALPAD:` frames to the core; the
core's only input is the byte stream in §2.

## 4. Why one byte per token

A single byte per token keeps the Malbolge input loop minimal (read one byte,
dispatch). Multi-byte framing (e.g. `ESC[...`) was rejected at M0 because it
adds parse state to the Malbolge core for no semantic gain; the host adapter
normalizes terminal sequences to the token bytes above.

## 5. Freeze record

- Contract docs: `docs/PROTOCOL.md`, `docs/STATE_MODEL.md`, `docs/HOST_BOUNDARY.md`.
- Executable reference: `tools/editor_ir.py` (the contract oracle).
- Fixtures: `tests/fixtures/keystrokes/` + `tests/fixtures/expected/`.
- Gate: **PROTOCOL_FROZEN**.