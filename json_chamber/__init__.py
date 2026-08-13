"""json-chamber — pure JSON sealing. No TRU8 engine."""

from .api import cloak_json, open_json, cloak_bytes, open_bytes
from .core import WORDLIST
from .license import LicenseError, license_status, require_alive, verifieddr_check

__all__ = [
    "cloak_json",
    "open_json",
    "cloak_bytes",
    "open_bytes",
    "WORDLIST",
    "LicenseError",
    "license_status",
    "require_alive",
    "verifieddr_check",
]
__version__ = "1.0.0"
