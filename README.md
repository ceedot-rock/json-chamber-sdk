# json-chamber

**Chamber** — JSON sealing with two independent keys.

Pure security product from **Slid Phi Labs**. No TRU8 engine in this package.

## Pricing

Live seats on https://www.slidphilabs.com/chamber

| Product | What it is | Price |
|---------|------------|-------|
| **Chamber** (this package) | Seal / open JSON | **$49 / month · $490 / year** |
| 24-hour try | Full cloak/open, then it stops | Free |

Not a $99 one-time SKU. Not a $1,900 compressor bundle.
TRU8 is a separate tool on the site. Chamber Year does not include TRU8.

Unlock: https://www.slidphilabs.com/chamber

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

## 24h try

- **0–24h:** cloak/open work
- After that: operational calls refuse until a Chamber seat is live

## Format

**[Chamber Format Spec v1](./CHAMBER-FORMAT-v1.md)** — wire format only.

## License

[Business Source License 1.1](./LICENSE) — Change Date **2030-08-13** → Apache-2.0.
**TRU8 is not in this package.**

## Links

- Product: https://www.slidphilabs.com/chamber
- MCP: https://github.com/ceedot-rock/json-chamber-mcp
- Contact: corey@slidphilabs.com
