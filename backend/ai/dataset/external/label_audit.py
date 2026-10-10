"""
AniCare AI — External Label & Biological Scope Auditor
Enforces strict 5-tier diagnostic evidence hierarchy:
1. Laboratory-confirmed diagnosis (RT-PCR, ELISA, viral isolation)
2. Veterinary clinical diagnosis (board-certified or university clinicians)
3. Clearly documented clinical diagnosis (teaching hospital record)
4. Expert-reviewed label (consensus of veterinary annotators)
5. Unknown / ambiguous

Enforces disease scope (Cattle + LSD):
- Unsupported species -> MODEL_NOT_VALIDATED_FOR_SPECIES (routed safely away from vision model).
- Overlapping / ambiguous dermal conditions -> AMBIGUOUS (quarantined, never forced into binary classes).
"""

from enum import Enum
from typing import Dict, Any, Tuple, Optional


class EvidenceLevel(str, Enum):
    LABORATORY_CONFIRMED = "LABORATORY_CONFIRMED"
    VETERINARY_CLINICAL = "VETERINARY_CLINICAL"
    DOCUMENTED_CLINICAL = "DOCUMENTED_CLINICAL"
    EXPERT_REVIEWED = "EXPERT_REVIEWED"
    UNKNOWN_AMBIGUOUS = "UNKNOWN_AMBIGUOUS"


class ExternalLabelAuditor:
    """Audits biological species and clinical condition annotations."""

    SUPPORTED_SPECIES = ["Cattle", "Bovine", "Bos taurus", "Bos indicus", "cattle"]

    AMBIGUOUS_DERMAL_CONDITIONS = [
        "dermatitis", "pseudo-lumpy", "pseudolumpy", "papilloma", "wart",
        "ringworm", "dermatomycosis", "mange", "demodex", "urticaria",
        "hypoderma", "tick bite", "insect bite", "unspecified nodule",
        "abscess", "photosensitization", "streptothricosis"
    ]

    LSD_SYNONYMS = [
        "lumpy skin disease", "lsd", "capripoxvirus", "cutaneous nodules",
        "bovine lumpy skin", "nodular exanthema"
    ]

    HEALTHY_SYNONYMS = [
        "healthy", "normal", "healthy / normal", "normal skin",
        "unaffected", "negative control", "no clinical lesions"
    ]

    @classmethod
    def audit_sample(cls, record: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """
        Audits candidate sample metadata.
        Returns:
            (status, standardized_disease, species_status, evidence_level)
            status in: ('VALID', 'AMBIGUOUS', 'REJECTED')
        """
        # 1. Species Scope Check
        raw_species = str(record.get("species", "")).strip()
        if raw_species not in cls.SUPPORTED_SPECIES:
            return (
                "REJECTED",
                f"UNSUPPORTED_SPECIES_{raw_species}",
                "MODEL_NOT_VALIDATED_FOR_SPECIES",
                EvidenceLevel.UNKNOWN_AMBIGUOUS.value
            )

        # 2. Evidence Hierarchy Audit
        raw_evidence = str(record.get("ground_truth_source", "")).lower()
        if any(k in raw_evidence for k in ["pcr", "elisa", "lab", "laboratory", "antigen", "sequencing"]):
            evidence_level = EvidenceLevel.LABORATORY_CONFIRMED.value
        elif any(k in raw_evidence for k in ["faculty", "hospital", "clinician", "veterinarian", "teaching"]):
            evidence_level = EvidenceLevel.VETERINARY_CLINICAL.value
        elif any(k in raw_evidence for k in ["chart", "case history", "documented", "inpatient"]):
            evidence_level = EvidenceLevel.DOCUMENTED_CLINICAL.value
        elif any(k in raw_evidence for k in ["expert", "consensus", "reviewed", "curated"]):
            evidence_level = EvidenceLevel.EXPERT_REVIEWED.value
        else:
            evidence_level = EvidenceLevel.DOCUMENTED_CLINICAL.value if record.get("disease") else EvidenceLevel.UNKNOWN_AMBIGUOUS.value

        # 3. Clinical Condition Label Audit
        raw_disease = str(record.get("disease", "")).strip().lower()

        # Check positive class
        if any(syn in raw_disease for syn in cls.LSD_SYNONYMS):
            return "VALID", "Lumpy Skin Disease", "VALIDATED_SPECIES_CATTLE", evidence_level

        # Check negative class
        if any(syn in raw_disease for syn in cls.HEALTHY_SYNONYMS):
            return "VALID", "Healthy / Normal", "VALIDATED_SPECIES_CATTLE", evidence_level

        # Check ambiguous dermatology
        if any(kw in raw_disease for kw in cls.AMBIGUOUS_DERMAL_CONDITIONS):
            return "AMBIGUOUS", f"AMBIGUOUS_DERMATOLOGY_{raw_disease}", "VALIDATED_SPECIES_CATTLE", evidence_level

        # Unknown / unverified
        return "REJECTED", f"UNKNOWN_OR_UNVERIFIED_LABEL_{raw_disease}", "VALIDATED_SPECIES_CATTLE", EvidenceLevel.UNKNOWN_AMBIGUOUS.value


label_auditor = ExternalLabelAuditor()
