# Black Box Control Plane Policy (json-chamber shared)

**Status:** Locked 2026-08-18  
**Control plane:** `json_chamber.license`  
**Applies to:** json-chamber · tru8-chamber · chamber · trugame · future products

## Lifecycle

1. **First activation** → 24-hour trial starts (`first_run` + `eval_expires`).
2. **After 24 hours** → box turns **OFF** (hard kill). Stays off.
3. **Payment** (Stripe or manual `corey@slidphilabs.com`) → server issues a signed **entitlement token**.
4. **Client applies entitlement** → killswitch lifts; box turns **ON** for the purchased period.
5. **Offline after payment**
   - one-time ($99): 24 h grace after last successful check
   - project-year / time-limited: 30-day lease, then off until renew

## Entitlement token

Signed JSON object (`type: "entitlement"`, `v: 1`) produced by:

```python
from json_chamber import create_entitlement, apply_entitlement

token = create_entitlement(
    product="json-chamber",   # or tru8-chamber / chamber / trugame
    order_id="cs_...",
    email="buyer@example.com",
)
# server returns token → client:
apply_entitlement(token)
```

## Client gate

Every sensitive call (cloak, open, engine start, etc.):

```python
from json_chamber import require_alive, LicenseError

try:
    status = require_alive("trugame")   # or any product
except LicenseError as e:
    # box is OFF — direct user to purchase / support
    ...
```

## Server

`server/checkout_server.py` mints entitlement tokens on Stripe `checkout.session.completed` and exposes:

- `POST /create-checkout-session`
- `POST /webhook`
- `GET  /entitlement/<box_id>`
- `GET  /entitlement/by-order/<order_id>`
- `POST /mint` (manual / support path)

## Integrity

- Local `license.json` is HMAC-signed; any tamper → immediate kill.
- Entitlement tokens are HMAC-signed with the same master secret.
- Optional: run `benefit_check` on sealed payloads for structure/entropy gating.

## Contact

Support / manual PACKAGE ACCESS: **corey@slidphilabs.com**
