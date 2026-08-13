"""
Chamber license – 24-hour eval kill-switch + VerifiedDR gate.

- First run writes a signed license.json under ~/.chamber/
- After 24 hours (hard cut, no grace) the box hard-kills unless a purchased
  VerifiedDR key is present.
- Any tamper of the license file → immediate kill.
- VERIFIEDDR_API_KEY starting with vdr_/test_/demo enables eval mode;
  keys containing "purchased" / "pro" / "live_" unlock permanently.
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

EVAL_DAYS = 1          # 24 hours
GRACE_HOURS = 0         # hard cut – no grace


class LicenseError(RuntimeError):
    """Raised when the chamber is dead, expired, or tampered."""


def _master_bytes() -> bytes:
    raw = os.environ.get("CHAMBER_MASTER_SECRET") or os.environ.get(
        "TRU8_MASTER_SECRET", "chamber-demo-master-secret-32b!!"
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
    """Lightweight VerifiedDR gate (env-key driven for the trial package)."""
    key = os.environ.get("VERIFIEDDR_API_KEY", "")
    if not key:
        return {
            "verified": False,
            "reason": "VERIFIEDDR_API_KEY not set",
            "purchased": False,
            "eval_mode": False,
        }
    if key.startswith(("vdr_", "test_", "demo")):
        purchased = any(tok in key for tok in ("purchased", "pro", "live_"))
        return {
            "verified": True,
            "reason": "ok",
            "purchased": purchased,
            "eval_mode": not purchased,
            "app_id": "chamber-eval",
        }
    return {
        "verified": False,
        "reason": "unrecognised VERIFIEDDR_API_KEY",
        "purchased": False,
        "eval_mode": False,
    }


def _load_or_create() -> dict[str, Any]:
    _ensure_dir()
    if KILL_FILE.exists():
        raise LicenseError("Chamber hard-killed (KILLED marker present)")

    if LICENSE_FILE.exists():
        try:
            raw = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
            sig = raw.pop("sig", "")
            expected = _sign(raw)
            if not hmac.compare_digest(sig, expected):
                KILL_FILE.write_text("tamper", encoding="utf-8")
                raise LicenseError("License tamper detected – chamber killed")
            return raw
        except LicenseError:
            raise
        except Exception:
            pass

    now = int(time.time())
    lic = {
        "type": "eval",
        "first_run": now,
        "eval_expires": now + EVAL_DAYS * 86400,
        "purchased": False,
        "device_hash": hashlib.sha256(
            str(Path.home()).encode()
        ).hexdigest()[:16],
    }
    signed = dict(lic)
    signed["sig"] = _sign(lic)
    LICENSE_FILE.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return lic


def require_alive() -> dict[str, Any]:
    if KILL_FILE.exists():
        raise LicenseError("Chamber hard-killed")

    lic = _load_or_create()
    gate = verifieddr_check()

    if gate.get("purchased") or lic.get("purchased"):
        lic["purchased"] = True
        return {"license": lic, "gate": gate, "status": "purchased"}

    if not gate.get("verified"):
        raise LicenseError(
            f"VerifiedDR gate closed: {gate.get('reason', 'unknown')}"
        )

    now = int(time.time())
    expires = int(lic.get("eval_expires", 0))
    grace = GRACE_HOURS * 3600

    if now > expires + grace:
        KILL_FILE.write_text("expired", encoding="utf-8")
        raise LicenseError(
            f"24-hour evaluation expired (ended {expires}). "
            "Purchase unlock to restore Chamber."
        )

    remaining = max(0, expires - now)
    return {
        "license": lic,
        "gate": gate,
        "status": "eval",
        "seconds_remaining": remaining,
    }


def license_status() -> dict[str, Any]:
    try:
        return require_alive()
    except LicenseError as e:
        return {"status": "dead", "reason": str(e)}
