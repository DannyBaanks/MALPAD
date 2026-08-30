# MALPAD — Host boundary (M0, frozen)

> Status: **HOST_BOUNDARY_EXPLICIT** (2026-08-30).

## 1. The rule

```
Malbolge decides WHAT to do.
The host only transports input/output and, when applicable,
materializes explicitly requested host capabilities.
```

**If the adapter had to "understand" what editing to do, we cheated.**

## 2. Adapter MAY do (allowed)

| Capability | Notes |
|-----------|-------|
| Put terminal in raw mode | transport |
| Read raw bytes from the keyboard | transport |
| Normalize terminal key sequences to the protocol token bytes (§2.2 PROTOCOL) | transport only — mapping, not semantics |
| Render `@MALPAD:` event frames to the terminal (ANSI escapes) | renderer |
| Create a window / paint text / move a cursor (Win32, M10) | renderer |
| Write a file **only upon an explicit `@MALPAD:SAVE` request**, subject to its own policy | materialized authority |
| Return `SAVE_ACK` / `SAVE_DENIED` / `SAVE_ERROR` as the next input byte | transport |

## 3. Adapter MUST NOT do (forbidden — would violate the boundary)

| Forbidden | Why |
|-----------|-----|
| Decide which character to insert | editor semantics |
| Decide how the cursor moves | editor semantics |
| Decide when/how to delete | editor semantics |
| Decide the meaning of a key | editor semantics |
| Decide when to save or quit | editor semantics |
| Mutate the buffer directly | buffer is Malbolge-owned |
| Choose the logical cursor position | cursor is Malbolge-owned |
| Emit `@MALPAD:` frames as if they were editor decisions | adapter is a transport, not the core |

## 4. Save authority flow (no fake syscalls, no implicit filesystem)

```
Malbolge core                        Host adapter
─────────────────                    ────────────────
READY + SAVE
  → @MALPAD:SAVE ────────────────────►  policy check
  → state WAIT_SAVE_ACK                   allowed? → write to allowed destination
                                          denied?  → (no write)
                                          error?   → (failed)
                                     ◄──────────── byte ACK/DENIED/ERROR
WAIT_SAVE_ACK + ACK → @MALPAD:SAVED
```

- The core emits only a **request** (`@MALPAD:SAVE`). It never assumes authority.
- The adapter decides whether it has **permission** and writes **only to the
  allowed destination**.
- The adapter must run in `--deny-write` mode too, returning `SAVE_DENIED`
  without breaking the editor (tested in M7).

## 5. Security attribution (M9 — Antivirusbolge self-audit)

| Layer | HOST_EFFECT |
|-------|-------------|
| Malbolge specimen (editor core) | NONE (pure VM; no host primitive reachable) |
| ANSI adapter | terminal capability only |
| file adapter | filesystem capability **present**; write **exercised** only after an explicit `@MALPAD:SAVE` request |

The core never exercises a host capability directly. Filesystem authority is
declared and exercised by the adapter, behind the explicit request.

## 6. Freeze record

- Gate: **HOST_BOUNDARY_EXPLICIT**.
- Reinforced in M7 (SAVE_ALLOWED / SAVE_DENIED / SAVE_ERROR) and M9
  (Antivirusbolge attribution).