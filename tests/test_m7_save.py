"""MALPAD M7 — save authority seam tests.

The core only ever issues a save REQUEST. Writing happens on the host, behind
the adapter, only after that request. We distinguish: requested / authorized /
write attempted / write succeeded / write failed. Save intent alone must NOT
become SAVE_DEMONSTRATED.
"""
from __future__ import annotations

import sys, json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from save_adapter import SaveAdapter  # noqa: E402
from host_runner import run_with_host  # noqa: E402

SAVE, QUIT, ACK, DENIED, ERROR = 0x17, 0x04, 0x41, 0x44, 0x45


def _host_run(script, allow_write=True, force_failure=False, allowed=None):
    allowed = allowed or str(ROOT / "evidence" / "m7_save" / "saved.txt")
    sa = SaveAdapter(allowed, allow_write=allow_write, force_failure=force_failure)
    events, final, receipts = run_with_host(script, sa)
    return events, final, receipts, sa


def test_save_requested_no_authority_no_write(tmp_path):
    allowed = str(tmp_path / "out.txt")
    events, final, receipts, _ = _host_run(b"HI" + bytes([SAVE, QUIT]),
                                           allow_write=False, allowed=allowed)
    assert "@MALPAD:SAVE" in events
    assert "@MALPAD:SAVE_DENIED" in events
    r = receipts[-1]
    assert r.requested and not r.authorized and not r.wrote
    assert r.result == "SAVE_DENIED"
    assert not (tmp_path / "out.txt").exists()  # no host write on denial


def test_save_requested_with_authority_writes(tmp_path):
    allowed = str(tmp_path / "out.txt")
    events, final, receipts, _ = _host_run(b"HI" + bytes([SAVE, QUIT]),
                                           allow_write=True, allowed=allowed)
    assert "@MALPAD:SAVE" in events and "@MALPAD:SAVED" in events
    r = receipts[-1]
    assert r.authorized and r.wrote
    assert r.bytes_written == 2 and r.sha256
    written = (tmp_path / "out.txt").read_bytes()
    assert written == b"HI"  # exact buffer persisted


def test_write_failure_reflected_truthfully(tmp_path):
    allowed = str(tmp_path / "out.txt")
    events, final, receipts, _ = _host_run(b"HI" + bytes([SAVE, QUIT]),
                                           allow_write=True, force_failure=True,
                                           allowed=allowed)
    assert "@MALPAD:SAVE_ERROR" in events
    r = receipts[-1]
    assert r.result == "SAVE_ERROR" and not r.wrote


def test_save_intent_alone_not_demonstrated():
    # A bare @MALPAD:SAVE is a REQUEST, not a write. Run the core with SAVE but
    # no host ack: SAVE is emitted, SAVED is not, and the core waits for ack.
    import sys as _s
    _s.path.insert(0, str(ROOT / "tools"))
    from editor_ir import run_script
    events, snap = run_script(b"AB" + bytes([SAVE]))
    assert any(e == "@MALPAD:SAVE" for e in events)
    assert not any(e == "@MALPAD:SAVED" for e in events)
    assert snap["state"] == "WAIT_SAVE_ACK"  # waiting for host, not saved


def test_core_never_writes_filesystem_directly(tmp_path):
    # The core (editor_ir) has no save authority — only the adapter writes.
    # Running the core with SAVE but no adapter must not create the file.
    import sys as _s
    _s.path.insert(0, str(ROOT / "tools"))
    from editor_ir import run_script
    events, snap = run_script(b"HI" + bytes([SAVE, ACK, QUIT]))
    assert "@MALPAD:SAVE" in events
    assert not (tmp_path / "anywhere.txt").exists()


def test_receipt_has_path_and_hash():
    import tempfile, os, hashlib
    d = tempfile.mkdtemp()
    allowed = os.path.join(d, "out.txt")
    events, final, receipts, _ = _host_run(b"HI" + bytes([SAVE, QUIT]),
                                           allow_write=True, allowed=allowed)
    r = receipts[-1].to_dict()
    assert r["path"] == allowed
    assert r["bytes_written"] == 2
    assert r["sha256"] == hashlib.sha256(b"HI").hexdigest()
    assert r["result"] == "SAVED"