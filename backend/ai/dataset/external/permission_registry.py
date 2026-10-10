"""
AniCare AI — External Dataset Permission & Legal/Ethical Gate Registry
Governs legal and ethical compliance for external and candidate datasets (Milestone 8A).

Enforces:
1. Strict 10-point Legal / Ethical Gate prior to image ingestion.
2. Machine-readable permission status tracking.
3. Zero-tolerance policy against unverified, unauthorized, or scraped data.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import re


class PermissionState(str, Enum):
    """Permitted permission lifecycle states for external datasets."""
    DISCOVERY = "DISCOVERY"
    CONTACTED = "CONTACTED"
    PERMISSION_REQUESTED = "PERMISSION_REQUESTED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    REJECTED = "REJECTED"
    ACQUIRED = "ACQUIRED"
    QUARANTINED = "QUARANTINED"
    VALIDATED = "VALIDATED"


class LegalEthicalGate:
    """
    Evaluates candidates against the mandatory 10 legal and ethical requirements:
    1. Permission or valid license exists.
    2. Research use is permitted.
    3. Images can legally be processed.
    4. Patient/owner identifying information is removed.
    5. No phone numbers.
    6. No addresses.
    7. No personal identifiers.
    8. No unauthorized veterinary records are exposed.
    9. Image redistribution restrictions are documented.
    10. Source attribution requirements are recorded.
    """

    PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    @classmethod
    def evaluate(
        cls,
        provenance_entry: Dict[str, Any],
        sample_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Dict[str, bool]]:
        """
        Executes the 10-point legal & ethical gate check.
        Returns: (passed, failure_reason_if_any, check_results_dict)
        """
        checks: Dict[str, bool] = {}
        sample = sample_metadata or {}

        perm_status = str(provenance_entry.get("permission_status", "")).upper()
        license_name = provenance_entry.get("license")

        # Rejection by governance policy (e.g. uncurated Kaggle scrape)
        if perm_status == PermissionState.REJECTED.value:
            checks["1_permission_or_license_exists"] = False
            checks["2_research_use_permitted"] = False
            checks["3_legal_to_process"] = False
            checks["4_owner_pii_removed"] = True
            checks["5_no_phone_numbers"] = True
            checks["6_no_addresses"] = True
            checks["7_no_personal_identifiers"] = True
            checks["8_no_unauthorized_records"] = True
            checks["9_redistribution_documented"] = False
            checks["10_attribution_recorded"] = False
            return False, "LEGAL_GATE_FAILED: SOURCE_REJECTED_BY_GOVERNANCE", checks

        # 1. Permission or valid license exists
        has_license = bool(license_name and str(license_name).strip().lower() not in ["none", "null", "unverified", ""])
        checks["1_permission_or_license_exists"] = has_license

        # 2. Research use is permitted
        checks["2_research_use_permitted"] = bool(provenance_entry.get("research_use_allowed", False))

        # 3. Images can legally be processed
        checks["3_legal_to_process"] = checks["1_permission_or_license_exists"] and checks["2_research_use_permitted"]

        # Metadata text blob for PII scans
        meta_str = " ".join([str(v) for k, v in sample.items() if k not in ["image_bytes", "features"]])

        # 4. Patient/owner identifying information is removed
        has_owner_id = any(k in sample for k in ["owner_name", "farmer_name", "owner_id", "aadhaar", "national_id"])
        checks["4_owner_pii_removed"] = not has_owner_id

        # 5. No phone numbers
        checks["5_no_phone_numbers"] = not bool(cls.PHONE_REGEX.search(meta_str))

        # 6. No addresses
        has_address = any(k in sample for k in ["street_address", "residential_address", "postal_code", "zip_code"])
        checks["6_no_addresses"] = not has_address

        # 7. No personal identifiers
        checks["7_no_personal_identifiers"] = not bool(cls.EMAIL_REGEX.search(meta_str))

        # 8. No unauthorized veterinary records exposed
        has_unauth_records = sample.get("unauthorized_medical_record", False)
        checks["8_no_unauthorized_records"] = not has_unauth_records

        # 9. Image redistribution restrictions documented
        redist_doc = provenance_entry.get("redistribution_allowed") is not None
        checks["9_redistribution_documented"] = redist_doc

        # 10. Source attribution requirements recorded
        checks["10_attribution_recorded"] = bool(provenance_entry.get("citation_required") is not None or provenance_entry.get("contact_reference") is not None)

        all_passed = all(checks.values())
        if all_passed:
            return True, "PASSED_ALL_GATES", checks

        failed_gates = [k for k, v in checks.items() if not v]
        reason = f"LEGAL_GATE_FAILED: {failed_gates[0]}"
        return False, reason, checks


class PermissionRegistry:
    """Manages external dataset permission states and validates legal access."""

    ALLOWED_STATES = [s.value for s in PermissionState]

    @classmethod
    def is_permission_granted(cls, permission_status: str) -> bool:
        """Determines whether a permission state permits active model validation."""
        clean_status = str(permission_status).upper().strip()
        return clean_status in [PermissionState.PERMISSION_GRANTED.value, PermissionState.VALIDATED.value, "APPROVED"]

    @classmethod
    def is_quarantine_required(cls, permission_status: str) -> bool:
        """Determines whether dataset must remain quarantined."""
        return not cls.is_permission_granted(permission_status)
