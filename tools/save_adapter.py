"""MALPAD M7 — save authority adapter (host side).

SAVE CAPABILITY != SAVE AUTHORITY.

The core emits @MALPAD:SAVE (a request). This adapter owns the *authority
boundary*: it decides whether the host is permitted to write, writes ONLY to the
allowed destination, and returns ACK/DENIED/ERROR as the next input byte to the
core (which is in WAIT_SAVE_ACK). It never writes without an explicit SAVE
request. It produces a truthful receipt (exact path / bytes / sha256 / result).

The adapter runs in --deny-write mode too, returning SAVE_DENIED without writing.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SaveReceipt:
    requested: bool = False
    authorized: bool = False
    attempted_write: bool = False
    wrote: bool = False
    path: Optional[str] = None
    bytes_written: int = 0
    sha256: Optional[str] = None
    result: str = "NONE"  # SAVED / SAVED_DENIED / SAVE_ERROR / NONE

    def to_dict(self) -> dict:
        return {
            "requested": self.requested, "authorized": self.authorized,
            "attempted_write": self.attempted_write, "wrote": self.wrote,
            "path": self.path, "bytes_written": self.bytes_written,
            "sha256": self.sha256, "result": self.result,
        }


class SaveAdapter:
    """Host-side save authority. Writes only to allowed_path, only on request."""

    def __init__(self, allowed_path: str, allow_write: bool = True,
                 force_failure: bool = False):
        self.allowed_path = Path(allowed_path)
        self.allow_write = allow_write
        self.force_failure = force_failure
        self.receipts: List[SaveReceipt] = []

    def handle_save(self, payload: bytes) -> bytes:
        """Handle a SAVE request. Returns the ACK/DENIED/ERROR input byte.

        Returns 0x41 (ACK) on success, 0x44 (DENIED) if not authorized,
        0x45 (ERROR) if the write failed. Never writes outside allowed_path.
        """
        r = SaveReceipt(requested=True, path=str(self.allowed_path))
        if not self.allow_write:
            r.result = "SAVE_DENIED"
            self.receipts.append(r)
            return b"\x44"  # DENIED
        # authorized: attempt write to allowed_path only
        r.authorized = True
        r.attempted_write = True
        try:
            if self.force_failure:
                raise OSError("injected write failure")
            self.allowed_path.parent.mkdir(parents=True, exist_ok=True)
            self.allowed_path.write_bytes(payload)
            r.wrote = True
            r.bytes_written = len(payload)
            r.sha256 = hashlib.sha256(payload).hexdigest()
            r.result = "SAVED"
            self.receipts.append(r)
            return b"\x41"  # ACK
        except OSError as exc:
            r.result = "SAVE_ERROR"
            r.sha256 = None
            self.receipts.append(r)
            return b"\x45"  # ERROR

    def last_receipt(self) -> Optional[SaveReceipt]:
        return self.receipts[-1] if self.receipts else None