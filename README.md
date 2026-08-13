# json-chamber-sdk

**Chamber** – JSON sealing with φ-split keyword shares.

No TRU8 compression engine. Pure security product from Slid Phi Labs.

## Install

```bash
pip install -e .
```

## Quick start

```python
from json_chamber import cloak_json, open_json

# Lend this to ANY codebase – no TRU8 engine inside
sealed = cloak_json({"api_key": "sk-...", "config": {...}})

# They can store / ship this – but k_words alone is useless
# {
#   "k_words": "ward veil spire lock ...",
#   "r_words": "oath cloak shard mark ...",
#   "nonce": "...",
#   "tag": "...",
#   "ct": "..."
# }

# Only opens with both shares + master + VerifiedDR address
original = open_json(sealed)
```

## Format specification

**[Chamber Format Spec v1](./CHAMBER-FORMAT-v1.md)** — wire format only
(sealed object shape, φ-split, AES-256-GCM, keyword encoding).

License enforcement, trial duration, and unlock are **out of scope** of the format.

Suggested media type (informative): `application/chamber+json`.

## Licensing

**License:** [Business Source License 1.1](./LICENSE)  
- Non-production use free under BSL 1.1  
- Production use requires paid unlock (Additional Use Grant: None)  
- Change Date: 2030-08-13 → Apache-2.0  
- TRU8 compression engine is **not** in this package and is not licensed here

### Runtime trial (orthogonal to BSL)

- **24-hour evaluation** from first run (HMAC-signed license under `~/.chamber/`).
- Hard cut at 24 h – no grace period. After that the chamber hard-kills.
- Set `VERIFIEDDR_API_KEY` to a purchased key (`…purchased…` / `…pro…` / `…live_…`) for permanent unlock.
- Tamper of the license file → instant kill.

## Environment

| Variable | Purpose |
|----------|---------|
| `CHAMBER_MASTER_SECRET` | High-entropy master (preferred) |
| `TRU8_MASTER_SECRET` | Fallback master name |
| `VERIFIEDDR_API_KEY` | Gate + purchase signal |

## API

| Function | Description |
|----------|-------------|
| `cloak_json(obj)` | Seal any JSON-serialisable object |
| `open_json(sealed)` | Open (requires live license) |
| `cloak_bytes(data)` | Low-level binary seal |
| `open_bytes(sealed)` | Low-level binary open |
| `license_status()` | Non-raising status probe |
| `require_alive()` | Raise `LicenseError` if dead |

## Design notes

- Message key is φ-split into two 16-byte shares, rendered as word lists.
- AES-256-GCM with associated data `chamber-v1`.
- Public integrity tag binds the two shares + nonce.
- Master secret is required at open time even after share reconstruction (binds to licensed host).

## Links

- Product page: https://www.slidphilabs.com/chamber
- Format spec: [CHAMBER-FORMAT-v1.md](./CHAMBER-FORMAT-v1.md)
- Unlock: $199 via Stripe (see product page)
- Lab: [Slid Phi Labs](https://www.slidphilabs.com)
