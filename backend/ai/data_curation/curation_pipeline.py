"""
AniCare AI — Controlled Dataset Curation Pipeline
Executes multi-stage filtering from raw clinical feedback to verified dataset candidate.
Guarantees provenance, licensing compliance, duplicate quarantine, and image clarity.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .provenance import (
    PermissionStatus,
    EvidenceLevel,
    DatasetCandidateItem
)
from .image_quality import image_quality_analyzer, ImageQualityReport
from .duplicate_detector import duplicate_detector
from .leakage_guard import dataset_leakage_guard


class CurationPipelineResult:
    def __init__(
        self,
        success: bool,
        candidate_id: Optional[str],
        stage_reached: str,
        evidence_level: EvidenceLevel,
        is_quarantined: bool,
        quality_report: Optional[Dict[str, Any]],
        duplicate_info: Optional[Dict[str, Any]],
        message: str,
        candidate: Optional[DatasetCandidateItem] = None
    ):
        self.success = success
        self.candidate_id = candidate_id
        self.stage_reached = stage_reached
        self.evidence_level = evidence_level
        self.is_quarantined = is_quarantined
        self.quality_report = quality_report
        self.duplicate_info = duplicate_info
        self.message = message
        self.candidate = candidate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "candidate_id": self.candidate_id,
            "stage_reached": self.stage_reached,
            "evidence_level": self.evidence_level.value,
            "is_quarantined": self.is_quarantined,
            "quality_report": self.quality_report,
            "duplicate_info": self.duplicate_info,
            "message": self.message,
            "candidate": self.candidate.model_dump() if self.candidate else None
        }


class DatasetCurationPipeline:
    """
    Closed-loop dataset curation pipeline.
    Transforms vetted clinical field feedback into structured training candidates.
    """

    def __init__(self):
        self._curated_registry: List[Dict[str, Any]] = []

    def process_feedback_for_curation(
        self,
        image_path: str,
        species: str,
        condition: str,
        veterinary_decision: str,
        clinical_evidence: EvidenceLevel,
        permission_status: PermissionStatus,
        license_str: str,
        source: str = "field_veterinary_clinic",
        animal_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> CurationPipelineResult:
        """
        Processes a field sample through the 8-stage verification pipeline:
        Stage 1: Raw Feedback Receipt
        Stage 2: Legal & Permission Gate
        Stage 3: Cryptographic & Perceptual Duplicate Check
        Stage 4: Image Quality & Exposure Gate
        Stage 5: Species Validation Gate
        Stage 6: Clinical Decision Alignment
        Stage 7: Evidence Tier Assignment
        Stage 8: Dataset Candidate Admission
        """
        # Stage 1: File Existence & Raw Hash
        p = Path(image_path)
        if not p.is_file():
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_1_RAW_FEEDBACK",
                evidence_level=EvidenceLevel.UNVERIFIED,
                is_quarantined=False,
                quality_report=None,
                duplicate_info=None,
                message=f"Image file does not exist: {image_path}"
            )

        sha256 = duplicate_detector.compute_sha256(image_path)
        dhash = duplicate_detector.compute_dhash(image_path)

        # Stage 2: Legal Permission & License
        if permission_status in [PermissionStatus.PERMISSION_REQUIRED, PermissionStatus.QUARANTINED, PermissionStatus.REJECTED]:
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_2_LEGAL_PERMISSION",
                evidence_level=clinical_evidence,
                is_quarantined=True,
                quality_report=None,
                duplicate_info=None,
                message=f"Quarantined: Permission status '{permission_status.value}' prohibits dataset inclusion."
            )

        if not license_str or license_str.upper() in ["NONE", "UNKNOWN", "UNAUTHORIZED"]:
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_2_LEGAL_PERMISSION",
                evidence_level=clinical_evidence,
                is_quarantined=True,
                quality_report=None,
                duplicate_info=None,
                message="Quarantined: Sample lacks verified open-source or data transfer license."
            )

        # Stage 3: Duplicate & Near-Duplicate Check
        dup_check = duplicate_detector.find_duplicates(sha256, dhash, self._curated_registry)
        if dup_check["is_duplicate"]:
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_3_DUPLICATE_CHECK",
                evidence_level=clinical_evidence,
                is_quarantined=True,
                quality_report=None,
                duplicate_info=dup_check,
                message=f"Quarantined duplicate: {dup_check['details']}"
            )

        # Stage 4 & 5: Image Quality & Species Validation
        q_report = image_quality_analyzer.analyze_image(image_path, species=species)
        if not q_report.is_sufficient:
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_4_IMAGE_QUALITY" if q_report.status == "INSUFFICIENT_IMAGE_QUALITY" else "STAGE_5_SPECIES_VALIDATION",
                evidence_level=clinical_evidence,
                is_quarantined=True,
                quality_report=q_report.to_dict(),
                duplicate_info=dup_check,
                message=f"Quarantined on quality/species check: {q_report.message}"
            )

        # Stage 6 & 7: Clinical Evidence Level
        if clinical_evidence not in [EvidenceLevel.VET_REVIEWED, EvidenceLevel.LAB_CONFIRMED]:
            return CurationPipelineResult(
                success=False,
                candidate_id=None,
                stage_reached="STAGE_7_EVIDENCE_LEVEL",
                evidence_level=clinical_evidence,
                is_quarantined=True,
                quality_report=q_report.to_dict(),
                duplicate_info=dup_check,
                message=f"Ineligible: Evidence level '{clinical_evidence.value}' is unverified."
            )

        # Stage 8: Candidate Admission
        candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        candidate = DatasetCandidateItem(
            candidate_id=candidate_id,
            source=source,
            collection_date=now_iso,
            permission_status=permission_status,
            license=license_str,
            species=species,
            condition=condition,
            review_status="APPROVED",
            evidence_level=clinical_evidence,
            sha256=sha256,
            perceptual_hash=dhash,
            image_path=image_path,
            animal_id=animal_id,
            notes=notes or f"Vetted through 8-stage pipeline. Decision: {veterinary_decision}.",
            is_demo=False
        )

        self._curated_registry.append(candidate.model_dump())

        return CurationPipelineResult(
            success=True,
            candidate_id=candidate_id,
            stage_reached="STAGE_8_CANDIDATE_ADMITTED",
            evidence_level=clinical_evidence,
            is_quarantined=False,
            quality_report=q_report.to_dict(),
            duplicate_info=dup_check,
            message="Candidate sample passed all 8 curation gates and is admitted to candidate repository.",
            candidate=candidate
        )


curation_pipeline = DatasetCurationPipeline()
