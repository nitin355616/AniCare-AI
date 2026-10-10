"""
AniCare AI — External Dataset Ingestion & Validation Controller
Coordinates provenance verification, 10-point legal gate, quality checks,
duplicate guard, label audit, and animal grouping into a unified pipeline.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib

from ai.dataset.external.permission_registry import PermissionRegistry, LegalEthicalGate, PermissionState
from ai.dataset.external.provenance import provenance_registry
from ai.dataset.external.quality_audit import quality_auditor, QualityTier
from ai.dataset.external.duplicate_guard import duplicate_guard
from ai.dataset.external.label_audit import label_auditor
from ai.dataset.external.grouping import grouping_auditor
from ai.dataset.external.external_manifest import ExternalManifestRecord, ExternalDatasetManifest


class ExternalDatasetValidator:
    """End-to-end validator for independent candidate datasets."""

    def __init__(self):
        self.duplicate_guard = duplicate_guard
        self.provenance_registry = provenance_registry

    def validate_candidate_batch(
        self,
        candidate_records: List[Dict[str, Any]],
        source_id: str,
        source_entry: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive validation across an entire batch of external candidate records.
        Quarantines any failures and outputs full audit breakdown.
        """
        source = source_entry or self.provenance_registry.get_source_by_id(source_id) or {
            "source_id": source_id,
            "permission_status": PermissionState.PERMISSION_REQUIRED.value,
            "license": "Unverified",
            "research_use_allowed": False
        }

        perm_status = source.get("permission_status", PermissionState.PERMISSION_REQUIRED.value)
        is_permission_granted = PermissionRegistry.is_permission_granted(perm_status)

        valid_manifest_records: List[ExternalManifestRecord] = []
        quarantine_records: List[Dict[str, Any]] = []
        rejected_records: List[Dict[str, Any]] = []
        ambiguous_records: List[Dict[str, Any]] = []

        seen_intra_hashes: Dict[str, str] = {}
        cross_dataset_duplicate_count = 0
        intra_dataset_duplicate_count = 0

        for rec in candidate_records:
            sample_id = rec.get("sample_id") or rec.get("image_id", "UNKNOWN_SAMPLE")
            img_bytes = rec.get("image_bytes")

            # 1. 10-Point Legal & Ethical Gate
            gate_passed, gate_reason, gate_checks = LegalEthicalGate.evaluate(source, rec)
            if not gate_passed:
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = gate_reason
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            # 2. Quality Audit
            if img_bytes:
                q_res = quality_auditor.audit_image_bytes(img_bytes, filename=f"{sample_id}.jpg")
                sha256 = q_res.get("sha256")
                is_valid_img = q_res.get("is_valid", False)
                quality_status = q_res.get("quality_tier", QualityTier.UNUSABLE.value)
                rejection_reason = q_res.get("rejection_reason")
                width = q_res.get("width", 0)
                height = q_res.get("height", 0)
                dhash = self.duplicate_guard.compute_dhash_bytes(img_bytes)
            else:
                sha256 = rec.get("sha256", hashlib.sha256(sample_id.encode()).hexdigest())
                is_valid_img = rec.get("is_valid", True)
                quality_status = rec.get("quality_status", QualityTier.ACCEPTABLE.value)
                rejection_reason = rec.get("rejection_reason")
                width = rec.get("image_width", 224)
                height = rec.get("image_height", 224)
                dhash = rec.get("dhash")

            if not is_valid_img or quality_status == QualityTier.UNUSABLE.value:
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = rejection_reason or "IMAGE_QUALITY_BELOW_THRESHOLD"
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            # 3. Cross-Dataset Leakage Guard against Dataset A
            is_cross_dup, dup_status, dup_reason = self.duplicate_guard.check_candidate_sample(sample_id, sha256, dhash)
            if is_cross_dup:
                cross_dataset_duplicate_count += 1
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = dup_reason
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            # 4. Intra-Dataset Deduplication
            if sha256 in seen_intra_hashes:
                intra_dataset_duplicate_count += 1
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"INTRA_DATASET_EXACT_DUPLICATE_OF_{seen_intra_hashes[sha256]}"
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            seen_intra_hashes[sha256] = sample_id

            # 5. Label & Species Scope Audit
            label_status, standardized_disease, species_status, evidence_level = label_auditor.audit_sample(rec)

            if label_status == "REJECTED":
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"LABEL_REJECTED: {standardized_disease}"
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue
            elif label_status == "AMBIGUOUS":
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"AMBIGUOUS_LABEL: {standardized_disease}"
                quarantine_records.append(rec_copy)
                ambiguous_records.append(rec_copy)
                continue

            # 6. Build immutable sanitized manifest record
            manifest_rec = ExternalManifestRecord.create_sanitized(
                image_id=sample_id,
                source_id=source_id,
                species="Cattle",
                ground_truth=standardized_disease,
                clinical_condition=standardized_disease,
                image_path=rec.get("image_path", f"external/{source_id}/{sample_id}.jpg"),
                sha256=sha256,
                image_width=width,
                image_height=height,
                license_status=source.get("license", "Unknown"),
                permission_status=perm_status,
                raw_animal_id=rec.get("animal_id"),
                raw_case_id=rec.get("case_id"),
                quality_status=quality_status,
                duplicate_status="UNIQUE"
            )
            valid_manifest_records.append(manifest_rec)

        # 7. Animal grouping audit
        valid_raw = [r.model_dump() for r in valid_manifest_records]
        grouping_info = grouping_auditor.audit_grouping(valid_raw)

        lsd_count = sum(1 for r in valid_manifest_records if r.ground_truth == "Lumpy Skin Disease")
        healthy_count = sum(1 for r in valid_manifest_records if r.ground_truth == "Healthy / Normal")

        return {
            "source_id": source_id,
            "permission_status": perm_status,
            "permission_granted": is_permission_granted,
            "total_candidates": len(candidate_records),
            "accepted_valid_count": len(valid_manifest_records),
            "quarantined_total_count": len(quarantine_records),
            "rejected_count": len(rejected_records),
            "ambiguous_count": len(ambiguous_records),
            "cross_dataset_duplicates_quarantined": cross_dataset_duplicate_count,
            "intra_dataset_duplicates_quarantined": intra_dataset_duplicate_count,
            "disease_distribution": {
                "Lumpy Skin Disease": lsd_count,
                "Healthy / Normal": healthy_count
            },
            "animal_grouping": grouping_info,
            "status": "VALIDATED" if is_permission_granted else "PERMISSION_REQUIRED",
            "valid_records": [r.model_dump() for r in valid_manifest_records],
            "quarantined_records": quarantine_records
        }


external_dataset_validator = ExternalDatasetValidator()
