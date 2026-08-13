# json-chamber

**Chamber** — JSON sealing with φ-split keyword shares + public-safe optimizer.

Pure security product from **Slid Phi Labs**. No TRU8 residual engine in this package.

## Pricing — two SKUs, no conflict

| Product | What it is | Price | License |
|---------|------------|-------|---------|
| **json-chamber** (this package) | JSON cloaking + optimizer helpers (`benefit_check`, delta, group, dedup analysis) | **$99 one-time / domain** | BSL-1.1 — 24h free eval, then hard kill |
| **tru8-chamber** | TRU8 residual engine + chamber — smaller asset bundles + same cloaking | **$1,900 / project / year** | Proprietary — never open-sourced |

**Funnel:** $99 always works → only advertise $1,900 when `benefit_check` says `compress=True`.

Unlock: https://www.slidphilabs.com/chamber

## Install

```bash
pip install -e .
```

## Quick start

```python
from json_chamber import (
    cloak_json, open_json,
    benefit_check, group_then_compress,
    delta_transform_positions, chunk_dedup,
)

sealed = cloak_json({"api_key": "sk-...", "level": "boss_fight", "hp": 100})
original = open_json(sealed)

check = benefit_check(asset_bytes)
if check["compress"]:
    print(check["est_saving"], check["action"])  # $1,900 path
else:
    sealed = cloak_json(meta)  # $99 security only
```

## Optimizer (public-safe)

| Helper | Role |
|--------|------|
| `benefit_check(data)` | Shannon + zero-bit bias + pair entropy → compress? |
| `group_then_pack` / `group_then_compress` | Tar many tiny files so structure appears |
| `delta_transform_positions([...])` | Mesh/animation floats → deltas |
| `chunk_dedup([file, ...])` | Cross-file 4KB fingerprint report |

**Honesty rule:** high-entropy PNG/JPG/encrypted → `compress=False` → seal only ($99).

## 24h hard kill

- **0–24h:** fully functional
- **24h00m01s:** `~/.chamber/KILLED` — cloak/open bricked
- **Unlock:** `VERIFIEDDR_API_KEY=vdr_purchased_…` after $99 Stripe payment

## Format specification

**[Chamber Format Spec v1](./CHAMBER-FORMAT-v1.md)** — wire format only (AES-256-GCM, φ-split).

## Environment

| Variable | Purpose |
|----------|---------|
| `CHAMBER_MASTER_SECRET` / `JSON_CHAMBER_MASTER` | Master secret |
| `VERIFIEDDR_API_KEY` | `vdr_purchased_…` = permanent unlock |

## Stripe unlock server

```bash
pip install flask stripe
export STRIPE_SECRET_KEY=sk_live_...
export STRIPE_PRICE_ID=price_...
export DOMAIN=https://www.slidphilabs.com
export JSON_CHAMBER_MASTER=...
python server/checkout_server.py
```

## License

[Business Source License 1.1](./LICENSE) — Change Date **2030-08-13** → Apache-2.0.  
**TRU8 is not in this package.**

## Links

- Product: https://www.slidphilabs.com/chamber
- Format: [CHAMBER-FORMAT-v1.md](./CHAMBER-FORMAT-v1.md)
- Contact: corey@slidphilabs.com · license@slidphilabs.com
