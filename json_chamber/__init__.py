"""json-chamber — pure JSON sealing + shared Black Box control plane.

All products (json-chamber, tru8-chamber, chamber, trugame) use the same
license / killswitch / entitlement layer defined in .license.
"""

from .api import cloak_json, open_json, cloak_bytes, open_bytes
from .core import WORDLIST
from .license import (
    LicenseError,
    PRODUCTS,
    apply_entitlement,
    create_entitlement,
    license_status,
    require_alive,
    reset_for_testing,
    verifieddr_check,
    verify_entitlement,
)
from .benefit import (
    benefit_check,
    tru8_benefit_check,
    group_then_pack,
    group_then_compress,
    delta_transform_positions,
    delta_transform_bytes,
    chunk_dedup,
    benefit_report,
)

__all__ = [
    # Sealing
    "cloak_json",
    "open_json",
    "cloak_bytes",
    "open_bytes",
    "WORDLIST",
    # Shared Black Box control plane
    "LicenseError",
    "PRODUCTS",
    "require_alive",
    "license_status",
    "apply_entitlement",
    "create_entitlement",
    "verify_entitlement",
    "verifieddr_check",
    "reset_for_testing",
    # Optimizer / benefit
    "benefit_check",
    "tru8_benefit_check",
    "group_then_pack",
    "group_then_compress",
    "delta_transform_positions",
    "delta_transform_bytes",
    "chunk_dedup",
    "benefit_report",
]
__version__ = "1.2.0"
