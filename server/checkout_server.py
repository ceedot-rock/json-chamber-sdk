"""
Stripe Checkout Server — mints vdr_purchased_ keys after $99 json-chamber payment.

Run:
  pip install flask stripe
  export STRIPE_SECRET_KEY=sk_live_...
  export STRIPE_WEBHOOK_SECRET=whsec_...
  export STRIPE_PRICE_ID=price_...
  export DOMAIN=https://www.slidphilabs.com
  export JSON_CHAMBER_MASTER=...
  python server/checkout_server.py
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
DOMAIN = os.getenv("DOMAIN", "https://www.slidphilabs.com").rstrip("/")
MASTER_RAW = os.getenv("JSON_CHAMBER_MASTER") or os.getenv(
    "CHAMBER_MASTER_SECRET", "chamber-demo-master-secret-32b!!"
)
MASTER = MASTER_RAW.encode()
if len(MASTER) < 32:
    MASTER = hashlib.sha256(MASTER).digest()

DB_PATH = Path(os.getenv("CHAMBER_LICENSE_DB", "./licenses.json"))

try:
    import stripe

    stripe.api_key = STRIPE_SECRET_KEY
except ImportError:
    stripe = None  # type: ignore


def _load_db() -> dict:
    if not DB_PATH.exists():
        return {}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _save_db(db: dict) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2), encoding="utf-8")


def mint_license_key(email: str, domain: str = "", session_id: str = "") -> str:
    ts = int(time.time())
    rand = secrets.token_hex(8)
    payload = f"{email}|{domain}|{session_id}|{ts}|{rand}"
    sig = hmac.new(MASTER, payload.encode(), hashlib.sha256).hexdigest()[:24]
    key = f"vdr_purchased_live_{rand}_{sig}"
    db = _load_db()
    db[key] = {
        "email": email,
        "domain": domain,
        "session_id": session_id,
        "ts": ts,
        "active": True,
        "product": "json-chamber",
        "price_usd": 99,
    }
    _save_db(db)
    return key


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if stripe is None or not STRIPE_SECRET_KEY:
        return jsonify({"error": "stripe not configured"}), 500
    email = (request.json or {}).get("email", "")
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": PRICE_ID, "quantity": 1}],
        success_url=f"{DOMAIN}/chamber?success=1&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/chamber?canceled=1",
        customer_email=email or None,
        metadata={"product": "json-chamber", "price_usd": "99"},
    )
    return jsonify({"url": session.url, "id": session.id})


@app.route("/webhook", methods=["POST"])
def webhook():
    if stripe is None:
        return jsonify({"error": "stripe not configured"}), 500
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            event = json.loads(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        email = (session.get("customer_details") or {}).get("email") or session.get(
            "customer_email"
        ) or ""
        domain = (session.get("metadata") or {}).get("domain", "")
        key = mint_license_key(email, domain, session.get("id", ""))
        print(f"MINTED KEY for {email}: {key}")
    return jsonify({"received": True})


@app.route("/verify/<key>")
def verify_key(key: str):
    db = _load_db()
    rec = db.get(key)
    if not rec or not rec.get("active"):
        return jsonify({"valid": False})
    return jsonify(
        {
            "valid": True,
            "purchased": True,
            "email": rec.get("email"),
            "domain": rec.get("domain"),
            "product": rec.get("product", "json-chamber"),
        }
    )


@app.route("/health")
def health():
    return jsonify({"ok": True, "product": "json-chamber", "price_usd": 99})


if __name__ == "__main__":
    print("Stripe license server on :4242")
    print("Set STRIPE_SECRET_KEY, STRIPE_PRICE_ID, DOMAIN, JSON_CHAMBER_MASTER")
    app.run(port=4242, debug=False)
