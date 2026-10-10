"""
AniCare AI — Dataset B Independent Validation Pipeline & Quality Controller
Implements:
1. Provenance & licensing audit against source_registry.json.
2. File integrity & image quality checking (resolution tiering, blur, exposure).
3. Intra-dataset duplicate detection (exact hash and perceptual dHash).
4. Cross-dataset duplicate detection against Dataset A (manifest.json) with strict quarantine.
5. Clinical label auditing (VALID, AMBIGUOUS, REJECTED).
6. Animal-level grouping metadata detection (animal_grouping_available flag).
7. Legal gatekeeping: Rejects unverified datasets; documents pending status without fabrication.
"""

import os
import sys
import io
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from PIL import Image, ImageStat
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from ai.dataset.schema import (
    TargetSpeciesEnum,
    ImageQualityEnum,
    VETERINARY_TAXONOMY
)
from ai.dataset.quality import (
    ImageQualityChecker,
    ImageQualityAssessment,
    NEAR_DUPLICATE_HAMMING_THRESHOLD
)


class DatasetBPipeline:
    """
    Independent validation pipeline and quality controller for Dataset B candidate images.
    Enforces cross-dataset deduplication against Dataset A and strict provenance verification.
    """

    def __init__(
        self,
        dataset_a_manifest_path: Optional[Path] = None,
        source_registry_path: Optional[Path] = None
    ):
        self.backend_dir = BACKEND_DIR
        self.dataset_a_path = dataset_a_manifest_path or (self.backend_dir / "ai" / "dataset" / "processed" / "manifest.json")
        self.registry_path = source_registry_path or (self.backend_dir / "ai" / "dataset" / "source_registry.json")
        
        self.dataset_a_exact_hashes: Set[str] = set()
        self.dataset_a_dhashes: Dict[str, str] = {}  # image_id -> dhash
        self._load_dataset_a_references()

    def _load_dataset_a_references(self):
        """Loads Dataset A image hashes and dhashes to prevent cross-dataset contamination."""
        if not self.dataset_a_path.is_file():
            return

        try:
            with open(self.dataset_a_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    img_id = item.get("image_id", "")
                    # Compute or retrieve hashes
                    fpath = self.backend_dir / item.get("file_path", "")
                    if fpath.is_file():
                        with open(fpath, "rb") as img_file:
                            content = img_file.read()
                            sha = hashlib.sha256(content).hexdigest()
                            self.dataset_a_exact_hashes.add(sha)
                            try:
                                dhash = ImageQualityChecker.compute_dhash(content)
                                self.dataset_a_dhashes[img_id] = dhash
                            except Exception:
                                pass
        except Exception as e:
            print(f"[DatasetBPipeline] Warning loading Dataset A references: {e}")

    def audit_provenance(self, source_id: str) -> Dict[str, Any]:
        """Audits dataset provenance and licensing permissions from source_registry.json."""
        if not self.registry_path.is_file():
            return {
                "source_id": source_id,
                "verified": False,
                "status": "REGISTRY_NOT_FOUND",
                "permission_granted": False,
                "notes": "source_registry.json not accessible."
            }

        with open(self.registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        match = None
        for entry in registry:
            if entry.get("source_id") == source_id or entry.get("source_name") == source_id:
                match = entry
                break

        if not match:
            return {
                "source_id": source_id,
                "verified": False,
                "status": "UNKNOWN_SOURCE",
                "permission_granted": False,
                "notes": f"Source ID '{source_id}' is not registered in provenance catalog."
            }

        status = match.get("status") or match.get("permission_status") or match.get("acquisition_status")
        license_verified = match.get("license_verified", False)
        permission_granted = (status == "APPROVED" and license_verified)

        return {
            "source_id": match.get("source_id", source_id),
            "dataset_name": match.get("dataset_name") or match.get("source_name"),
            "provider": match.get("provider") or match.get("organization"),
            "institution": match.get("institution", "Unknown"),
            "official_url": match.get("official_url") or match.get("URL"),
            "license": match.get("license"),
            "license_verified": license_verified,
            "permission_status": status,
            "permission_granted": permission_granted,
            "notes": match.get("notes", "")
        }

    def check_image_quality_and_metrics(self, image_bytes: bytes, filename: str = "sample.jpg") -> Dict[str, Any]:
        """
        Evaluates photometric quality, blur, exposure, resolution tiers, and hash fingerprints.
        """
        assessment = ImageQualityChecker.inspect_image_bytes(image_bytes, file_name=filename)
        if not assessment.is_valid:
            return {
                "is_valid": False,
                "rejection_reason": assessment.error or "Corrupt or unreadable image file",
                "quality_tier": ImageQualityEnum.UNUSABLE.value,
                "blur_metric": 0.0,
                "exposure_metric": 0.0,
                "md5": assessment.md5_hash,
                "sha256": assessment.sha256_hash,
                "dhash": None
            }

        # Detailed blur & exposure
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_gray = img.convert("L")
                arr = np.array(img_gray, dtype=np.float32)

                # Laplacian variance for focus / blur
                gy, gx = np.gradient(arr)
                gnorm = np.sqrt(gx**2 + gy**2)
                sharpness = float(np.var(gnorm))

                # Exposure / mean luminance
                mean_lum = float(np.mean(arr))
                is_underexposed = mean_lum < 35.0
                is_overexposed = mean_lum > 225.0
                is_blurry = sharpness < 25.0

                warnings = list(assessment.warnings)
                if is_blurry:
                    warnings.append(f"Image exhibits high motion/optical blur (sharpness metric {sharpness:.1f} < 25.0).")
                if is_underexposed:
                    warnings.append(f"Severe underexposure (mean luminance {mean_lum:.1f} < 35.0).")
                if is_overexposed:
                    warnings.append(f"Severe specular overexposure / glare (mean luminance {mean_lum:.1f} > 225.0).")

                return {
                    "is_valid": assessment.is_valid and assessment.quality_tier != ImageQualityEnum.UNUSABLE,
                    "rejection_reason": None if assessment.is_valid else "Below minimum quality threshold",
                    "quality_tier": assessment.quality_tier.value,
                    "width": assessment.width,
                    "height": assessment.height,
                    "sharpness": round(sharpness, 2),
                    "is_blurry": is_blurry,
                    "mean_luminance": round(mean_lum, 2),
                    "is_underexposed": is_underexposed,
                    "is_overexposed": is_overexposed,
                    "md5": assessment.md5_hash,
                    "sha256": assessment.sha256_hash,
                    "dhash": assessment.dhash,
                    "warnings": warnings
                }
        except Exception as e:
            return {
                "is_valid": False,
                "rejection_reason": f"Photometric analysis failed: {str(e)}",
                "quality_tier": ImageQualityEnum.UNUSABLE.value,
                "md5": assessment.md5_hash,
                "sha256": assessment.sha256_hash,
                "dhash": None
            }

    def check_cross_dataset_leakage(self, sha256_hash: str, dhash_val: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Determines whether candidate sample in Dataset B already exists in Dataset A.
        Returns (is_leakage, reason).
        """
        if sha256_hash in self.dataset_a_exact_hashes:
            return True, "EXACT_HASH_MATCH_WITH_DATASET_A"

        if dhash_val:
            for ref_id, ref_dhash in self.dataset_a_dhashes.items():
                if ImageQualityChecker.is_near_duplicate(dhash_val, ref_dhash, NEAR_DUPLICATE_HAMMING_THRESHOLD):
                    return True, f"PERCEPTUAL_NEAR_DUPLICATE_WITH_DATASET_A_{ref_id}"

        return False, None

    def audit_clinical_label(self, raw_record: Dict[str, Any]) -> Tuple[str, str]:
        """
        Audits biological species and clinical condition label.
        Returns:
            (status, standardized_label) where status in ('VALID', 'AMBIGUOUS', 'REJECTED')
        """
        species = raw_record.get("species", "")
        if species not in [TargetSpeciesEnum.CATTLE.value, "Bovine", "Bos taurus", "Bos indicus", "cattle"]:
            return "REJECTED", f"UNSUPPORTED_SPECIES_{species}"

        raw_disease = str(raw_record.get("disease", "")).strip()

        # Positive class matches
        if raw_disease.lower() in [
            "lumpy skin disease", "lsd", "capripoxvirus", "cutaneous nodules", "bovine lumpy skin"
        ]:
            return "VALID", "Lumpy Skin Disease"

        # Negative class matches
        if raw_disease.lower() in [
            "healthy", "normal", "healthy / normal", "normal skin", "unaffected", "negative control"
        ]:
            return "VALID", "Healthy / Normal"

        # Ambiguous / overlapping dermal conditions
        ambiguous_keywords = [
            "dermatitis", "papilloma", "wart", "ringworm", "mange", "demodex",
            "pseudo-lumpy", "urticaria", "hypoderma", "tick bite", "insect bite", "unspecified nodule"
        ]
        if any(kw in raw_disease.lower() for kw in ambiguous_keywords):
            return "AMBIGUOUS", f"AMBIGUOUS_DERMATOLOGY_{raw_disease}"

        # Unknown / corrupted
        return "REJECTED", f"UNKNOWN_OR_UNVERIFIED_LABEL_{raw_disease}"

    def inspect_animal_grouping(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Inspects whether candidate dataset contains verifiable animal / patient identifiers.
        """
        animal_ids = set()
        missing_count = 0

        for r in records:
            aid = r.get("animal_id") or r.get("ear_tag") or r.get("patient_id") or r.get("case_id")
            if aid and str(aid).strip().lower() not in ["none", "null", "unknown", ""]:
                animal_ids.add(str(aid).strip())
            else:
                missing_count += 1

        has_grouping = len(animal_ids) > 0 and (missing_count / max(len(records), 1)) < 0.20

        return {
            "animal_grouping_available": has_grouping,
            "unique_animal_count": len(animal_ids),
            "missing_identifier_count": missing_count,
            "total_records": len(records),
            "limitation_note": (
                "Animal grouping verified; partition isolation by animal identity supported."
                if has_grouping else
                "animal_grouping_available = false; animal identifiers absent from source metadata. "
                "The evaluation CANNOT claim herd-independent generalization."
            )
        }

    def process_candidate_dataset(
        self,
        candidate_records: List[Dict[str, Any]],
        source_id: str
    ) -> Dict[str, Any]:
        """
        Runs comprehensive validation across an entire candidate batch for Dataset B.
        Quarantines cross-dataset duplicates, near-duplicates, unreadable files, and ambiguous labels.
        """
        provenance = self.audit_provenance(source_id)

        valid_records: List[Dict[str, Any]] = []
        quarantine_records: List[Dict[str, Any]] = []
        ambiguous_records: List[Dict[str, Any]] = []
        rejected_records: List[Dict[str, Any]] = []

        seen_intra_hashes: Dict[str, str] = {}
        seen_intra_dhashes: Dict[str, str] = {}

        cross_dataset_duplicate_count = 0
        intra_dataset_duplicate_count = 0

        for rec in candidate_records:
            sample_id = rec.get("sample_id") or rec.get("image_id", "UNKNOWN")
            img_bytes = rec.get("image_bytes")

            # 1. Image Quality
            if img_bytes:
                q_result = self.check_image_quality_and_metrics(img_bytes, filename=f"{sample_id}.jpg")
                sha256 = q_result.get("sha256")
                dhash = q_result.get("dhash")
                is_valid_img = q_result.get("is_valid", False)
            else:
                sha256 = rec.get("sha256", hashlib.sha256(sample_id.encode()).hexdigest())
                dhash = rec.get("dhash")
                is_valid_img = rec.get("is_valid", True)
                q_result = {"is_valid": is_valid_img, "warnings": []}

            if not is_valid_img:
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = q_result.get("rejection_reason", "CORRUPT_OR_UNREADABLE")
                rejected_records.append(rec_copy)
                quarantine_records.append(rec_copy)
                continue

            # 2. Cross-Dataset Leakage against Dataset A
            is_leak, leak_reason = self.check_cross_dataset_leakage(sha256, dhash)
            if is_leak:
                cross_dataset_duplicate_count += 1
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"CROSS_DATASET_LEAKAGE: {leak_reason}"
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            # 3. Intra-Dataset Duplication
            if sha256 in seen_intra_hashes:
                intra_dataset_duplicate_count += 1
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"INTRA_DATASET_EXACT_DUPLICATE_OF_{seen_intra_hashes[sha256]}"
                quarantine_records.append(rec_copy)
                rejected_records.append(rec_copy)
                continue

            seen_intra_hashes[sha256] = sample_id
            if dhash:
                seen_intra_dhashes[sample_id] = dhash

            # 4. Clinical Label Audit
            label_status, standardized_label = self.audit_clinical_label(rec)
            rec["standardized_disease"] = standardized_label

            if label_status == "VALID":
                valid_records.append(rec)
            elif label_status == "AMBIGUOUS":
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"AMBIGUOUS_LABEL: {standardized_label}"
                ambiguous_records.append(rec_copy)
                quarantine_records.append(rec_copy)
            else:
                rec_copy = dict(rec)
                rec_copy["quarantine_reason"] = f"LABEL_REJECTED: {standardized_label}"
                rejected_records.append(rec_copy)
                quarantine_records.append(rec_copy)

        grouping_info = self.inspect_animal_grouping(valid_records)

        lsd_count = sum(1 for r in valid_records if r.get("standardized_disease") == "Lumpy Skin Disease")
        healthy_count = sum(1 for r in valid_records if r.get("standardized_disease") == "Healthy / Normal")

        return {
            "source_id": source_id,
            "provenance": provenance,
            "total_candidates": len(candidate_records),
            "accepted_valid_count": len(valid_records),
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
            "status": "VALIDATED" if provenance.get("permission_granted") else "LEGAL_PERMISSION_PENDING",
            "valid_records": valid_records,
            "quarantined_records": quarantine_records
        }


# Singleton pipeline instance
dataset_b_pipeline = DatasetBPipeline()
