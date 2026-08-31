# MALPAD — M4/M5 gate evidence (render protocol + ANSI adapter)

Date: 2026-08-30.

## M4 gate: `LOGICAL_RENDER_DEMONSTRATED` + `ANSI_ADAPTER_THIN`

**Status: DEMONSTRATED.**

## M5 gate: `MALPAD_TUI_V0` (presentation layer)

**Status: DEMONSTRATED (presentation; the Malbolge core remains M3-NOT_DEMONSTRATED).**

## What M4/M5 demonstrate

The renderer consumes `@MALPAD:` events from a **neutral boundary** and produces
a deterministic terminal model → ANSI output. It is presentation-only: it
applies CLEAR/LINE/MOVE/STATUS directives and never re-derives editing.

| Requirement | Status | Evidence |
|-------------|--------|----------|
| clear/render | DEMONSTRATED | CLEAR + LINE directives build the screen model |
| cursor position | DEMONSTRATED | MOVE directive sets model cursor |
| buffer display | DEMONSTRATED | LINE:0 shows the full edited line; demo → `HEAMALBOLGELO` |
| status line | DEMONSTRATED | STATUS directive; demo → `saved` |
| deterministic rendering from event vectors | DEMONSTRATED | same events → same model → same ANSI (test) |
| no state semantics hidden in renderer | DEMONSTRATED | CHAR (edit op) does not mutate the model; only LINE/MOVE/STATUS do |
| backend independence | DEMONSTRATED | renderer cannot tell oracle vs fixture vs future specimen (identical frames → identical output) |

## Render-protocol refinement (documented in PROTOCOL.md)

The core now emits a full `LINE` + `MOVE` redraw after **every** buffer
mutation (not only backspace), so the renderer only presents. **Logical editor
semantics (buffer/cursor/state) are unchanged** — the frozen
`editor_state_vectors.json` final states are identical. This is a presentation
addition, not a generator-accommodating change to M3's target.

## Key proof

> The renderer produces the same output whether the events came from the IR
> oracle, a fixture, or (in future) a Malbolge specimen — it depends only on the
> frame content, not the provenance.

## Artifacts

- `tools/terminal_model.py`, `tools/ansi_adapter.py`
- `tests/test_m45_render.py` (M4/M5 tests)
- `tests/editor_state_vectors.json` (regenerated events; final states unchanged)
- Gates: **LOGICAL_RENDER_DEMONSTRATED**, **ANSI_ADAPTER_THIN**,
  **MALPAD_TUI_V0 (presentation)**.