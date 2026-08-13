# json-chamber

**Chamber** — JSON sealing with φ-split keyword shares.

Pure security product from **Slid Phi Labs**. No TRU8 compression engine in this package.

## Pricing — two SKUs, no conflict

| Product | What it is | Price | License |
|---------|------------|-------|---------|
| **json-chamber** (this package) | Pure JSON cloaking — φ-split, AES-256-GCM, keyword shares | **$99 one-time / domain** | BSL-1.1 — 24h free eval, then hard kill |
| **tru8-chamber** | TRU8 + chamber — smaller asset bundles + same cloaking | **$1,900 / project / year** | Proprietary — never open-sourced |

**Funnel:** $99 indie impulse buy → studio upsell to $1,900 when they need compression + sealing.

Chamber public unlock: https://www.slidphilabs.com/chamber

## Install

```bash
pip install -e .
```

## Quick start

```python
from json_chamber import cloak_json, open_json

sealed = cloak_json({"api_key": "sk-...", "level": "boss_fight", "hp": 100})
original = open_json(sealed)
```

## 24h hard kill

- **0–24h:** fully functional
- **24h00m01s:** writes `~/.chamber/KILLED` — all cloak/open bricked
- **Unlock:** set `VERIFIEDDR_API_KEY=vdr_purchased_…` after $99 Stripe payment

## Format specification

**[Chamber Format Spec v1](./CHAMBER-FORMAT-v1.md)** — wire format only.

## Environment

| Variable | Purpose |
|----------|---------|
| `CHAMBER_MASTER_SECRET` | High-entropy master (preferred) |
| `JSON_CHAMBER_MASTER` | Alias |
| `VERIFIEDDR_API_KEY` | `vdr_purchased_…` = permanent unlock |

## API

| Function | Description |
|----------|-------------|
| `cloak_json(obj)` | Seal any JSON-serialisable object |
| `open_json(sealed)` | Open (requires live license) |
| `cloak_bytes` / `open_bytes` | Binary seal/open |
| `license_status()` | Non-raising status probe |

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

[Business Source License 1.1](./LICENSE) — Change Date 2030-08-13 → Apache-2.0.  
TRU8 is **not** in this package.

## Links

- Product: https://www.slidphilabs.com/chamber
- Format: [CHAMBER-FORMAT-v1.md](./CHAMBER-FORMAT-v1.md)
- Contact: corey@slidphilabs.com
