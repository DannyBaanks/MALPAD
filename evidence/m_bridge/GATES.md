# MALPAD — bridge gate evidence (Python body ↔ Malbolge brain)

Date: 2026-08-30.

## What the bridge demonstrates

The MALPAD runtime transport, end-to-end with **real Malbolge**:
1. A **generated** Malbolge program (`evidence/m_bridge/frame_full.mal`, produced
   by the compact generator, not hand-written) emits `@MALPAD:` frames on
   stdout (`@MALPAD:STATUS:READY\n@MALPAD:QUIT\n`, halts, 970 steps).
2. The bridge feeds input bytes, reads the Malbolge output, parses the frames.
3. The frames drive the terminal model (M4) → ANSI (M5); save adapter (M7) plugs
   in on the host side.

**Backend-independence**: the same program produces identical frames on
malbolge-oracle and Malbolge-Engine (test).

**The law holds**: Python translates bytes and renders; it never decides editor
state (the frame-emitter's state is fixed by the Malbolge program, not by
Python).

## Honest status

| Layer | Status |
|-------|--------|
| transport (bytes in, frames out) | DEMONSTRATED |
| frame parsing → model → ANSI | DEMONSTRATED (reuses M4/M5) |
| VM hosting (oracle + engine) | DEMONSTRATED |
| backend-independence | DEMONSTRATED |
| **stateful editor brain (M3)** | **NOT_DEMONSTRATED** (unchanged) |

The bridge is the **body**. It transports/renders/hosts. It does NOT make M3
green: the frame-emitter emits a **fixed** frame sequence regardless of input; a
stateful editor that responds to `H E L L O LEFT LEFT A` per
`editor_state_vectors.json` still does not exist (M3, unchanged).

## The win

The M4/M5/M7 + bridge stack is independently testable and hostable **before**
the stateful Malbolge brain exists. When the M3 brain is built, it plugs into
this exact boundary — Python never changes, and it cannot tell (nor needs to)
whether the frames came from a generated frame-emitter, the IR oracle, or the
future stateful specimen.

## Artifacts

- `tools/malpad_bridge.py`
- `evidence/m_bridge/frame_full.mal` (+ manifest/op/word)
- `tests/test_bridge.py` (43 total tests pass)
- Gates: transport, parse, render, host — DEMONSTRATED. M3 — unchanged,
  NOT_DEMONSTRATED.