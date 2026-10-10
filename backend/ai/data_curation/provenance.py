"""
AniCare AI — Data Provenance & Legal Governance
Tracks legal acquisition rights, dataset licenses, clinical evidence tiers,
and cryptographic digests for every prospective training sample.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field


class PermissionStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


class EvidenceLevel(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VET_REVIEWED = "VET_REVIEWED"
    LAB_CONFIRMED = "LAB_CONFIRMED"
    REJECTED = "REJECTED"


class DatasetCandidateItem(BaseModel):
    candidate_id: str
    source: str
    collection_date: str
    permission_status: PermissionStatus
    license: str
    species: str
    condition: str
    review_status: str  # "PENDING" | "APPROVED" | "REJECTED"
    evidence_level: EvidenceLevel
    sha256: str
    perceptual_hash: Optional[str] = None
    image_path: Optional[str] = None
    animal_id: Optional[str] = None
    notes: Optional[str] = None
    is_demo: bool = False

    def is_eligible_for_curation(self) -> Tuple[bool, str]:
        """
        Enforces strict legal and evidence admissibility rules:
        - Must be APPROVED or AVAILABLE
        - Must not be PERMISSION_REQUIRED, QUARANTINED, or REJECTED
        - Must have VET_REVIEWED or LAB_CONFIRMED evidence
        """
        if self.permission_status in [PermissionStatus.PERMISSION_REQUIRED, PermissionStatus.QUARANTINED, PermissionStatus.REJECTED]:
            return False, f"Ineligible: Legal permission status is '{self.permission_status.value}'"
        if self.evidence_level not in [EvidenceLevel.VET_REVIEWED, EvidenceLevel.LAB_CONFIRMED]:
            return False, f"Ineligible: Evidence level '{self.evidence_level.value}' is insufficient (requires VET_REVIEWED or LAB_CONFIRMED)"
        if not self.license or self.license.upper() in ["NONE", "UNKNOWN", "UNAUTHORIZED"]:
            return False, "Ineligible: Missing valid open-source or institutional data transfer license"
        return True, "Sample eligible for dataset curation."

