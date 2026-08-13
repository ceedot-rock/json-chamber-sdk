#!/usr/bin/env python3
"""
Minimal Chamber demo.

Lend this to ANY codebase – no TRU8 engine inside.
Both keyword shares + master + live license are required to open.
"""

from __future__ import annotations

import json
import os

# Demo credentials (eval mode).  Replace with real purchased key for unlock.
os.environ.setdefault("VERIFIEDDR_API_KEY", "vdr_demo_eval")
os.environ.setdefault("CHAMBER_MASTER_SECRET", "chamber-demo-master-secret-32b!!")

from json_chamber import cloak_json, open_json, license_status


def main() -> None:
    print("=== license status ===")
    print(json.dumps(license_status(), indent=2))
    print()

    payload = {
        "api_key": "sk-live-example-do-not-use",
        "config": {
            "region": "us-east-1",
            "features": ["seal", "phi-split"],
        },
    }

    print("=== cloaking ===")
    sealed = cloak_json(payload)
    print(json.dumps(sealed, indent=2))
    print()

    print("=== notes ===")
    print("• k_words alone is useless")
    print("• r_words alone is useless")
    print("• both shares + master + verifieddr address required to open")
    print()

    print("=== opening ===")
    original = open_json(sealed)
    print(json.dumps(original, indent=2))
    assert original == payload
    print()
    print("round-trip OK")


if __name__ == "__main__":
    main()
