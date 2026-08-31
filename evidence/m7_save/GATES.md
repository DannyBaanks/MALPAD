# MALPAD — M7 gate evidence (save authority seam)

Date: 2026-08-30.

## Gate: `FILESYSTEM_AUTHORITY_SEPARATED`

**Status: DEMONSTRATED.**

## Principle

**SAVE CAPABILITY != SAVE AUTHORITY.**

The Malbolge core emits `@MALPAD:SAVE` (a **request**). It has no filesystem
authority. The host `SaveAdapter` owns the authority boundary: it decides
whether the host is permitted to write, writes ONLY to the allowed destination,
and returns ACK/DENIED/ERROR as the next input byte to the core (in
WAIT_SAVE_ACK). It never writes without an explicit request.

## Flow (as built)

```
core + SAVE
  → @MALPAD:SAVE (request)     [core enters WAIT_SAVE_ACK]
  → host SaveAdapter: policy check
       allow_write=False → SAVE_DENIED (no write)
       allow_write=True  → write allowed_path only → SAVED
       write fails        → SAVE_ERROR
  → adapter injects ACK/DENIED/ERROR byte → core returns to READY
```

## Distinctions demonstrated

| State | Meaning | Test |
|-------|---------|------|
| editor requested save | `@MALPAD:SAVE` emitted | yes |
| save authorized | adapter `allow_write=True` | yes |
| write attempted | adapter on allowed path | yes |
| write succeeded | receipt `wrote=True`, path/hash | yes |
| write failed | receipt `SAVE_ERROR` | yes |
| save intent alone | `SAVE` present, `SAVED` absent, core WAIT_SAVE_ACK | yes |
| core never writes FS directly | core has no adapter → no file | yes |

## Receipt

`SaveReceipt`: requested / authorized / attempted_write / wrote / path /
bytes_written / sha256 / result. Exact path + bytes + sha256 recorded.

## Never

"core said save" ⇒ "file saved". The core never writes; the host writes only
behind the explicit request and policy.

## Artifacts

- `tools/save_adapter.py`, `tools/host_runner.py`
- `tests/test_m7_save.py` (M7 tests)
- Gate: **FILESYSTEM_AUTHORITY_SEPARATED**.