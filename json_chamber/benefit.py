"""
benefit_check — advisory only. No TRU8 engine.

Used by both tiers so:
  • $99 json-chamber always works (seal path)
  • $1,900 tru8-chamber is only advertised when entropy says
    structure-aware compression is likely to win

TRU8 residual engine is proprietary and is not imported here.
"""

from __future__ import annotations

import io
import math
import tarfile
from collections import Counter
from typing import Iterable, Mapping, Sequence


def shannon_entropy(data: bytes) -> float:
    """Bits of Shannon entropy per byte (0..8)."""
    if not data:
        return 0.0
    n = len(data)
    counts = Counter(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def benefit_check(data: bytes, *, min_bytes: int = 1024) -> dict:
    """
    Quick entropy gate for the TRU8 upsell funnel.

    Returns a dict studios can log / gate on:
      compress: bool   – whether structure-aware compression is worth trying
      entropy: float   – Shannon bits/byte
      reason: str      – human-readable decision
      recommend: str   – "json-chamber" | "tru8-chamber" | "group-first"

    Policy (mirrors zstd-style small-file / high-entropy refusal):
      • tiny payloads (< min_bytes) → do not advertise TRU8; seal only
      • entropy > 7.8 → already compressed/encrypted; seal only
      • otherwise → candidate for tru8-chamber ($1,900 tier)
    """
    if data is None:
        return {
            "compress": False,
            "entropy": 0.0,
            "reason": "empty payload",
            "recommend": "json-chamber",
            "price_hint": 99,
        }

    size = len(data)
    if size < min_bytes:
        return {
            "compress": False,
            "entropy": shannon_entropy(data) if size else 0.0,
            "bytes": size,
            "reason": f"tiny ({size} B) — use json-chamber only; or group_then_pack many small files first",
            "recommend": "group-first" if size < min_bytes else "json-chamber",
            "price_hint": 99,
        }

    H = shannon_entropy(data)
    if H > 7.8:
        return {
            "compress": False,
            "entropy": round(H, 3),
            "bytes": size,
            "reason": f"high entropy {H:.2f} — already compressed/encrypted; seal with json-chamber",
            "recommend": "json-chamber",
            "price_hint": 99,
        }

    return {
        "compress": True,
        "entropy": round(H, 3),
        "bytes": size,
        "reason": f"structured entropy {H:.2f} — candidate for tru8-chamber (project-aware compression)",
        "recommend": "tru8-chamber",
        "price_hint": 1900,
        "note": "TRU8 engine is proprietary; contact license@slidphilabs.com for the $1,900/project/year tier",
    }


# Back-compat alias used in internal notes
tru8_benefit_check = benefit_check


def group_then_pack(
    files: Mapping[str, bytes] | Sequence[tuple[str, bytes]],
    *,
    mode: str = "tar",
) -> bytes:
    """
    Pack many small payloads into one blob so structure-aware compression
    (or a single chamber seal) has something to work with.

    1000 × 2 KB JSONs → one ~2 MB archive → benefit_check can return compress=True.

    This helper does **not** run TRU8. It only creates grouping structure.
    """
    if isinstance(files, Mapping):
        items: Iterable[tuple[str, bytes]] = files.items()
    else:
        items = files

    if mode != "tar":
        raise ValueError("only mode='tar' is supported in the open package")

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, payload in items:
            info = tarfile.TarInfo(name=name.replace("\\", "/").lstrip("/"))
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


def benefit_report(*blobs: bytes, names: Sequence[str] | None = None) -> dict:
    """
    Run benefit_check on each blob and on a grouped pack of all of them.
    Useful for studio demos: "individually no; grouped yes".
    """
    per_file = []
    for i, b in enumerate(blobs):
        label = names[i] if names and i < len(names) else f"file_{i}"
        r = benefit_check(b)
        r["name"] = label
        per_file.append(r)

    if len(blobs) >= 2:
        packed = group_then_pack(
            {r["name"]: blobs[i] for i, r in enumerate(per_file)}
        )
        grouped = benefit_check(packed)
        grouped["name"] = "__grouped__"
        grouped["packed_bytes"] = len(packed)
    else:
        grouped = None

    any_compress = any(r.get("compress") for r in per_file) or (
        grouped.get("compress") if grouped else False
    )
    return {
        "files": per_file,
        "grouped": grouped,
        "any_compress_candidate": bool(any_compress),
        "funnel": (
            "tru8-chamber ($1,900/project/year)"
            if any_compress
            else "json-chamber ($99) — seal only"
        ),
    }
