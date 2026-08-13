"""
High-level and low-level Chamber APIs.

  cloak_bytes / open_bytes  – raw binary
  cloak_json  / open_json   – JSON objects (public surface)
"""

from __future__ import annotations

import json
import os
from typing import Any

from . import core
from .license import require_alive, LicenseError


def _master() -> bytes:
    raw = os.environ.get("CHAMBER_MASTER_SECRET") or os.environ.get(
        "TRU8_MASTER_SECRET", "chamber-demo-master-secret-32b!!"
    )
    b = raw.encode("utf-8")
    if len(b) < 32:
        import hashlib
        b = hashlib.sha256(b).digest()
    return b


def cloak_bytes(data: bytes) -> dict:
    """Seal arbitrary bytes. Raises LicenseError if chamber is dead."""
    require_alive()
    return core.seal(data, _master())


def open_bytes(sealed: dict) -> bytes:
    """Open a sealed dict. Requires both shares + live license + master."""
    require_alive()
    return core.open_sealed(sealed, _master())


def cloak_json(obj: Any) -> dict:
    """
    Seal any JSON-serialisable object.

    Returns a dict containing k_words, r_words, nonce, tag, ct.
    Safe to store or ship – a single share is useless.
    """
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return cloak_bytes(raw)


def open_json(sealed: dict) -> Any:
    """
    Open a previously cloaked JSON object.
    Requires both keyword shares, the master secret, and a live license
    (24-hour trial or purchased VerifiedDR unlock).
    """
    raw = open_bytes(sealed)
    return json.loads(raw.decode("utf-8"))
