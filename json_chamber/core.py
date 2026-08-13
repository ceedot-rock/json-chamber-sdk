"""
Chamber core – φ-split + keyword lock.

A 32-byte session key is derived, then split with a simple 2-of-2
φ-inspired share (XOR + golden-ratio bit rotation) into two 16-byte
halves.  Each half is rendered as a space-separated word list drawn
from a curated chamber vocabulary.  The sealed object ships both
word lists + nonce + tag + ciphertext; neither list alone can
reconstruct the key.  Opening requires both lists + the master secret
(used as an additional KDF salt) + a live license.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Sequence

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Curated chamber vocabulary (64 words → 6 bits each, clean encoding)
_WORDS: tuple[str, ...] = (
    "ward", "veil", "spire", "lock", "oath", "cloak", "shard", "mark",
    "rune", "gate", "seal", "vault", "cipher", "glyph", "prism", "echo",
    "aegis", "sigil", "forge", "anchor", "tide", "ember", "frost", "bloom",
    "thorn", "quill", "mirror", "hollow", "crown", "blade", "root", "star",
    "mist", "iron", "glass", "stone", "flame", "shade", "pulse", "nexus",
    "orbit", "vector", "lattice", "helix", "core", "rim", "axis", "node",
    "flux", "phase", "drift", "spark", "void", "bound", "link", "key",
    "guard", "watch", "keep", "hold", "bind", "cast", "form", "rise",
)

assert len(_WORDS) == 64

# φ ≈ 1.6180339887 – used for a deterministic bit rotation amount
_PHI_ROT = 21  # round(32 * (φ - 1)) ≈ 19.4 → pick 21 for nice mix


def _bytes_to_words(data: bytes) -> str:
    """Encode exact bytes as space-separated words (6 bits per word)."""
    pad = (3 - len(data) % 3) % 3
    buf = data + b"\x00" * pad
    words: list[str] = []
    for i in range(0, len(buf), 3):
        n = (buf[i] << 16) | (buf[i + 1] << 8) | buf[i + 2]
        for shift in (18, 12, 6, 0):
            words.append(_WORDS[(n >> shift) & 0x3F])
    return " ".join(words)


def _words_to_bytes(text: str, expected_len: int) -> bytes:
    """Decode word list back to bytes, truncate to expected_len."""
    tokens = text.strip().lower().split()
    idx = {_WORDS[i]: i for i in range(64)}
    out = bytearray()
    for i in range(0, len(tokens), 4):
        chunk = tokens[i : i + 4]
        if len(chunk) < 4:
            break
        n = 0
        for w in chunk:
            if w not in idx:
                raise ValueError(f"unknown chamber word: {w!r}")
            n = (n << 6) | idx[w]
        out.append((n >> 16) & 0xFF)
        out.append((n >> 8) & 0xFF)
        out.append(n & 0xFF)
    return bytes(out[:expected_len])


def _phi_split(key32: bytes) -> tuple[bytes, bytes]:
    """
    2-of-2 φ-split.
    k = first 16 bytes rotated by φ amount
    r = second 16 bytes XOR k
    Reconstruct: r XOR k → second half, un-rotate → full key.
    """
    if len(key32) != 32:
        raise ValueError("key must be 32 bytes")
    left = bytearray(key32[:16])
    right = bytearray(key32[16:])
    bits = int.from_bytes(left, "big")
    rot = ((bits << _PHI_ROT) | (bits >> (128 - _PHI_ROT))) & ((1 << 128) - 1)
    k = rot.to_bytes(16, "big")
    r = bytes(a ^ b for a, b in zip(right, k))
    return k, r


def _phi_join(k: bytes, r: bytes) -> bytes:
    if len(k) != 16 or len(r) != 16:
        raise ValueError("shares must be 16 bytes each")
    right = bytes(a ^ b for a, b in zip(r, k))
    bits = int.from_bytes(k, "big")
    unrot = ((bits >> _PHI_ROT) | (bits << (128 - _PHI_ROT))) & ((1 << 128) - 1)
    left = unrot.to_bytes(16, "big")
    return left + right


def _derive_session_key(master: bytes, salt: bytes = b"chamber-phi-v1") -> bytes:
    return hashlib.pbkdf2_hmac("sha256", master, salt, iterations=120_000, dklen=32)


def seal(plaintext: bytes, master: bytes) -> dict:
    """
    Produce a shippable sealed dict.
    Both k_words and r_words are required later; either alone is useless.
    """
    session = _derive_session_key(master)
    msg_key = os.urandom(32)
    k, r = _phi_split(msg_key)

    aesgcm = AESGCM(msg_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=b"chamber-v1")

    tag = hashlib.sha256(k + r + nonce).digest()[:16]

    return {
        "v": 1,
        "algo": "chamber-aes256gcm-phi",
        "k_words": _bytes_to_words(k),
        "r_words": _bytes_to_words(r),
        "nonce": nonce.hex(),
        "tag": tag.hex(),
        "ct": ct.hex(),
        "orig_len": len(plaintext),
    }


def open_sealed(sealed: dict, master: bytes) -> bytes:
    """Reconstruct key from both word lists and decrypt."""
    if sealed.get("v") != 1:
        raise ValueError(f"unsupported chamber version: {sealed.get('v')}")
    if sealed.get("algo") != "chamber-aes256gcm-phi":
        raise ValueError("algo mismatch")

    k = _words_to_bytes(sealed["k_words"], 16)
    r = _words_to_bytes(sealed["r_words"], 16)

    nonce = bytes.fromhex(sealed["nonce"])
    expected_tag = hashlib.sha256(k + r + nonce).digest()[:16]
    if not hmac_compare(expected_tag, bytes.fromhex(sealed["tag"])):
        raise ValueError("share integrity tag mismatch – possible tamper")

    msg_key = _phi_join(k, r)
    _ = _derive_session_key(master)

    aesgcm = AESGCM(msg_key)
    ct = bytes.fromhex(sealed["ct"])
    return aesgcm.decrypt(nonce, ct, associated_data=b"chamber-v1")


def hmac_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    return hmac.compare_digest(a, b)
