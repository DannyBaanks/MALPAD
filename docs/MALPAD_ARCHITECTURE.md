# MALPAD — architecture (Python body, Malbolge brain)

> Reframe (2026-08-30): **Malbolge does not need to know what Windows is.**
> Python is the body; Malbolge is the editor brain; the byte protocol is the
> cable between them.

```
        WINDOWS / WIN32 / ANSI / test
                    │
            physical key: ←
                    ▼
        ┌────────────────────────┐
        │  PYTHON FRONTEND       │   body (hands)
        │  key/mouse/GUI         │
        │  render                │
        │  filesystem authority  │
        └───────────┬────────────┘
                    │  MALPAD PROTOCOL (bytes)
                    │  H / E / 0x11(LEFT) / 0x08(BS) / 0x17(SAVE)
        ┌───────────▼────────────┐
        │  MIDDLEWARE            │   bridge: Python ↔ Malbolge VM
        │  VM hosting            │   stdin/stdout framing
        │  frame parsing         │
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  MALBOLGE BACKEND      │   brain (editor)
        │  buffer / cursor       │
        │  insert/delete         │
        │  left/right            │
        │  SAVE_REQUEST          │
        └────────────────────────┘
```

## The law (what each side may know)

**Python MAY know:** `VK_LEFT` means protocol token LEFT (0x11). It may
translate physical keys to protocol bytes.

**Python MUST NOT know:** `LEFT` means `cursor -= 1`. That belongs to the
backend.

- Valid: `if key == VK_LEFT: malbolge.send(LEFT)`
- **Cheat:** `if key == VK_LEFT: editor.cursor -= 1` — then Python IS the editor
  and Malbolge is a mascot.

**Save:** Malbolge emits `SAVE_REQUEST` (decides it wants to save, and what its
state means). Python owns the material ability to write to NTFS and does so only
behind policy + explicit request (M7).

## Development flow (Walbolge → Malbolge)

```
editor_core.wal
      ↓  Walbolge translator / compiler
editor_core.mal
      ↓  MALPAD runtime (bridge)
   Python frontends: ANSI terminal | Win32 GUI | test fixture
```

Python never needs the editor's semantics. It only needs:
`send_event(bytes)`, `receive_frame()`, `render_frame(model)`,
`fulfill_save_request(receipt)`.

## Where the real problem lives

The bridge (transport/render/save/VM hosting) is the *easy* part. The hard part
is the **stateful Malbolge backend**:

```
Malbolge:
  read input
    → decode command
    → mutate persistent buffer/cursor   ← M3 (the blocker)
    → wait for next input
    → use PREVIOUS state
    → emit resulting state
```

Win32 is a rear problem: once the brain exists, connecting any frontend is
mechanical, because M4/M5 already define the boundary.

## M3 relationship (honest)

The bridge does NOT paint M3 green. M3 still requires that the `.mal` behind the
bridge genuinely does `H → buffer H; E → buffer HE; LEFT → cursor; A → insert at
cursor; BS → mutate`, reproducing `editor_state_vectors.json`. The bridge is the
body; M3 is the brain. Neither substitutes for the other.

## Bridge command

`malpad-bridge.py` hosts a Malbolge backend behind the byte protocol, parses
`@MALPAD:` output frames, and feeds the renderer + save adapter. Same bridge,
any frontend; same bridge, any Malbolge backend.