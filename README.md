# json-chamber

**Chamber** — a protocol for storing a JSON secret. Two independent keys. Ciphertext does not expire.

Pure security product from **Slid Phi Labs**. No compressor engine in this package.

## What you buy

A **cloak license** — the right to seal *new* JSON for a term.

| SKU | What it is | Price |
|-----|------------|-------|
| 24-hour try | cloak new JSON | Free |
| Chamber month | cloak license | **$9 / month** |
| Chamber year | cloak license | **$99 / year** |

**Open** of an already-sealed blob is both keys, no extra payment, no clock. If the license lapses you cannot seal new JSON; you can still open what you already sealed.

Live checkout: https://www.slidphilabs.com/chamber

## Install

```bash
pip install -e .
```

## Quick start

```python
from json_chamber import cloak_json, open_json

sealed = cloak_json({"api_key": "sk-...", "level": "boss_fight", "hp": 100})
original = open_json(sealed)  # keys only — works even after the cloak license ends
```

## License gate

- `cloak_json` / `cloak_bytes` → `require_cloak()` (24h try, then month/year)
- `open_json` / `open_bytes` → keys only. Never killed by the license clock.

TruGame and other running engines still call `require_alive()` for themselves. That is not Chamber storage.

## Format

**[Chamber Format Spec v1](./CHAMBER-FORMAT-v1.md)** — wire format only.

## License

[Business Source License 1.1](./LICENSE) — Change Date **2030-08-13** → Apache-2.0.
**No compressor engine in this package.**

## Links

- Product: https://www.slidphilabs.com/chamber
- MCP: https://github.com/ceedot-rock/json-chamber-mcp
- Contact: corey@slidphilabs.com
