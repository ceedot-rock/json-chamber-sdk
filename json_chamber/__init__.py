"""
json_chamber – public surface

  cloak_json(obj)  →  sealed dict  (safe to ship; shares alone are useless)
  open_json(sealed) → original obj (requires both shares + master + live license)

No TRU8 compression engine is present. This is pure Chamber security.
"""

from .api import cloak_json, open_json, cloak_bytes, open_bytes
from .license import LicenseError, require_alive, license_status

__all__ = [
    "cloak_json",
    "open_json",
    "cloak_bytes",
    "open_bytes",
    "LicenseError",
    "require_alive",
    "license_status",
]

__version__ = "0.1.0"
