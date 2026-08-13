"""
Chamber license – 24-hour eval kill-switch + purchase unlock.

Tiered product line (Slid Phi Labs):
  json-chamber  – $99 one-time / domain (this package, BSL-1.1)
  tru8-chamber  – $1,900 / project / year (proprietary; not in this repo)

- First run writes a signed license.json under ~/.chamber/
- After 24 hours (hard cut, no grace) the box hard-kills unless purchased
- Any tamper of the license file → immediate kill
- VERIFIEDDR_API_KEY containing purchased / pro / live_ unlocks permanently
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

LICENSE_DIR = Path.home() / ".chamber"
LICENSE_FILE = LICENSE_DIR / "license.json"
KILL_FILE = LICENSE_DIR / "KILLED"

EVAL_DAYS = 1
GRACE_HOURS = 0

PURCHASE_URL = os.environ.get(
    "CHAMBER_PURCHASE_URL",
    "https://www.slidphilabs.com/chamber",
)
PRICE_USD = 99


class LicenseError(RuntimeError):
    """Raised when the chamber is dead, expired, or tampered."""


def _master_bytes() -> bytes:
    raw = (
        os.environ.get("CHAMBER_MASTER_SECRET")
        or os.environ.get("JSON_CHAMBER_MASTER")
        or os.environ.get("TRU8_MASTER_SECRET", "chamber-demo-master-secret-32b!!")
    )
    b = raw.encode("utf-8")
    if len(b) < 32:
        b = hashlib.sha256(b).digest()
    return b


def _sign(payload: dict[str, Any]) -> str:
    msg = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(_master_bytes(), msg, hashlib.sha256).hexdigest()


def _ensure_dir() -> None:
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)


def verifieddr_check() -> dict[str, Any]:
    """Env-key driven gate. Missing key = open-source eval allowed."""
    key = os.environ.get("VERIFIEDDR_API_KEY", "")
    if not key:
        return {
            "verified": True,
            "reason": "open-source eval (no VERIFIEDDR_API_KEY)",
            "purchased": False,
            "eval_mode": True,
            "tier": "json-chamber",
        }
    purchased = any(tok in key for tok in ("purchased", "pro", "live_"))
    tru8 = "tru8" in key.lower()
    return {
        "verified": True,
        "reason": "ok",
        "purchased": purchased,
        "eval_mode": not purchased,
        "tier": "tru8-chamber" if tru8 else "json-chamber",
        "app_id": "chamber",
    }


def _load_or_create() -> dict[str, Any]:
    _ensure_dir()
    if KILL_FILE.exists():
        raise LicenseError("Chamber hard-killed (KILLED marker present)")

    if LICENSE_FILE.exists():
        try:
            data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            KILL_FILE.write_text("tamper-parse", encoding="utf-8")
            raise LicenseError(f"license file unreadable – killed: {e}") from e

        sig = data.pop("sig", None)
        if not sig or not hmac.compare_digest(sig, _sign(data)):
            KILL_FILE.write_text("tamper-sig", encoding="utf-8")
            raise LicenseError("license signature mismatch – killed")
        return data

    now = int(time.time())
    lic = {
        "type": "eval",
        "product": "json-chamber",
        "first_run": now,
        "eval_expires": now + EVAL_DAYS * 86400,
        "purchased": False,
        "device_hash": hashlib.sha256(str(Path.home()).encode()).hexdigest()[:16],
    }
    signed = dict(lic)
    signed["sig"] = _sign(lic)
    LICENSE_FILE.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return lic


def require_alive() -> dict[str, Any]:
    """Call on every cloak/open. Raises LicenseError if dead."""
    if KILL_FILE.exists():
        raise LicenseError(
            f"Chamber hard-killed. json-chamber unlock: ${PRICE_USD} → {PURCHASE_URL}"
        )

    lic = _load_or_create()
    gate = verifieddr_check()

    if gate.get("purchased") or lic.get("purchased"):
        lic["purchased"] = True
        return {"license": lic, "gate": gate, "status": "purchased", "price": PRICE_USD}

    now = int(time.time())
    expires = int(lic.get("eval_expires", 0))
    if now > expires + GRACE_HOURS * 3600:
        KILL_FILE.write_text("expired", encoding="utf-8")
        raise LicenseError(
            f"json-chamber 24h eval ended. "
            f"Price ${PRICE_USD} one-time → {PURCHASE_URL} "
            f"(or set VERIFIEDDR_API_KEY=vdr_purchased_…)"
        )

    remaining = max(0, expires - now)
    return {
        "license": lic,
        "gate": gate,
        "status": "eval",
        "seconds_remaining": remaining,
        "price": PRICE_USD,
        "purchase_url": PURCHASE_URL,
    }


def license_status() -> dict[str, Any]:
    """Non-raising status probe."""
    try:
        return require_alive()
    except LicenseError as e:
        return {"status": "dead", "reason": str(e), "price": PRICE_USD, "purchase_url": PURCHASE_URL}
