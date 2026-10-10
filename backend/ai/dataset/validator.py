"""
AniCare AI — Dataset Manifest & Integrity Validator
Executes veterinary taxonomy checks, animal-level split leakage detection,
exact and near-duplicate cross-split leakage checks, class imbalance analysis,
unverified license flags, and generates the standardized dataset_report.json.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, Counter

try:
    from ai.dataset.schema import (
        DatasetManifestRecord,
        TargetSpeciesEnum,
        DiseaseCategoryEnum,
        DatasetSplitEnum,
        ImageQualityEnum,
        VETERINARY_TAXONOMY,
    )
    from ai.dataset.quality import ImageQualityChecker, NEAR_DUPLICATE_HAMMING_THRESHOLD
except ImportError:
    from backend.ai.dataset.schema import (
        DatasetManifestRecord,
        TargetSpeciesEnum,
        DiseaseCategoryEnum,
        DatasetSplitEnum,
        ImageQualityEnum,
        VETERINARY_TAXONOMY,
    )
    from backend.ai.dataset.quality import ImageQualityChecker, NEAR_DUPLICATE_HAMMING_THRESHOLD


UNVERIFIED_LICENSES = {
    "unknown", "none", "unspecified", "all rights reserved",
    "proprietary", "pending", "n/a", "tbd", "unclear"
}


class DatasetManifestValidator:
    """
    Validates a collection of DatasetManifestRecords against veterinary science standards,
    split leakage protocols, licensing standards, and statistical distributions.
    """

    @classmethod
    def validate_manifest(
        cls,
        records: List[DatasetManifestRecord],
        image_hashes: Optional[Dict[str, Dict[str, str]]] = None,
        check_near_duplicates: bool = False
    ) -> Dict[str, Any]:
        """
        Validates the entire dataset manifest.

        Args:
            records: List of parsed DatasetManifestRecord objects.
            image_hashes: Optional mapping of image_id -> {"sha256": str, "dhash": str}
            check_near_duplicates: Whether to compute cross-record dHash comparisons.

        Returns:
            Validation report dictionary matching the dataset_report.json schema.
        """
        total_images = len(records)
        invalid_records: List[Dict[str, str]] = []
        duplicate_records_count = 0

        # Aggregation structures
        classes_set: Set[str] = set()
        images_per_class: Dict[str, int] = defaultdict(int)
        species_distribution: Dict[str, int] = defaultdict(int)
        split_distribution: Dict[str, int] = defaultdict(int)

        leakage_warnings: List[str] = []
        license_warnings: List[str] = []
        quality_warnings: List[str] = []
        recommended_actions: List[str] = []

        if total_images == 0:
            return {
                "total_images": 0,
                "valid_images": 0,
                "invalid_images": 0,
                "duplicate_images": 0,
                "classes": [],
                "images_per_class": {},
                "species_distribution": {},
                "split_distribution": {},
                "leakage_warnings": ["Manifest is empty: 0 records present."],
                "license_warnings": [],
                "quality_warnings": [],
                "recommended_actions": ["Populate dataset manifest with verified veterinary records."]
            }

        # 1. Identifier uniqueness and duplicate image_id tracking
        seen_image_ids: Dict[str, DatasetManifestRecord] = {}
        split_by_image_id: Dict[str, str] = {}
        split_by_animal: Dict[str, Set[str]] = defaultdict(set)

        for rec in records:
            img_id = rec.image_id
            split_val = rec.split.value if hasattr(rec.split, "value") else str(rec.split)
            species_val = rec.species.value if hasattr(rec.species, "value") else str(rec.species)
            disease_val = rec.disease

            classes_set.add(disease_val)
            images_per_class[disease_val] += 1
            species_distribution[species_val] += 1
            split_distribution[split_val] += 1

            # Check for duplicate image_id
            if img_id in seen_image_ids:
                prev_rec = seen_image_ids[img_id]
                duplicate_records_count += 1
                if prev_rec.disease != rec.disease or prev_rec.species != rec.species:
                    invalid_records.append({
                        "image_id": img_id,
                        "error": f"Conflicting labels for duplicate image_id: '{prev_rec.species}:{prev_rec.disease}' vs '{rec.species}:{rec.disease}'"
                    })
                if prev_rec.split != rec.split:
                    leakage_warnings.append(
                        f"Image-ID Leakage: Image '{img_id}' assigned to multiple splits ('{prev_rec.split}' and '{rec.split}')."
                    )
            else:
                seen_image_ids[img_id] = rec
                split_by_image_id[img_id] = split_val

            # Animal-level tracking for same-animal leakage
            if rec.animal_id and rec.animal_id.strip():
                split_by_animal[rec.animal_id.strip()].add(split_val)

            # 2. Biological taxonomy validity check
            valid_diseases = VETERINARY_TAXONOMY.get(species_val, {})
            if valid_diseases and disease_val not in valid_diseases:
                invalid_records.append({
                    "image_id": img_id,
                    "error": f"Biological Mismatch: Disease '{disease_val}' not valid for species '{species_val}'"
                })

            # 3. License verification check
            lic = (rec.license or "").strip().lower()
            if not lic or lic in UNVERIFIED_LICENSES:
                license_warnings.append(
                    f"Unverified License for image '{img_id}': license='{rec.license or 'MISSING'}'. Not approved for training."
                )
            elif not rec.license_url or not rec.license_url.startswith("http"):
                license_warnings.append(
                    f"Missing or invalid license URL for image '{img_id}': url='{rec.license_url or 'MISSING'}'."
                )

            # 4. Image quality tier checks
            if rec.image_quality == ImageQualityEnum.UNUSABLE:
                quality_warnings.append(f"Image '{img_id}' is flagged as UNUSABLE quality.")
            elif rec.image_quality == ImageQualityEnum.POOR:
                quality_warnings.append(f"Image '{img_id}' is flagged as POOR quality (sub-resolution).")

        # 5. Same-Animal Leakage Analysis
        for animal_id, splits in split_by_animal.items():
            if len(splits) > 1:
                leakage_warnings.append(
                    f"Same-Animal Leakage: Animal ID '{animal_id}' spans multiple splits ({', '.join(sorted(splits))}). "
                    "Causes model to memorize individual coat patterns rather than disease pathology."
                )

        # 6. Cryptographic and Perceptual Cross-Split Hash Leakage
        if image_hashes:
            sha256_to_splits: Dict[str, Set[str]] = defaultdict(set)
            sha256_to_ids: Dict[str, List[str]] = defaultdict(list)
            dhash_records: List[Tuple[str, str, str]] = []  # (img_id, split, dhash)

            for img_id, hashes in image_hashes.items():
                split_val = split_by_image_id.get(img_id, "unknown")
                sha = hashes.get("sha256")
                dh = hashes.get("dhash")

                if sha:
                    sha256_to_splits[sha].add(split_val)
                    sha256_to_ids[sha].append(img_id)
                if dh:
                    dhash_records.append((img_id, split_val, dh))

            # Exact duplicates across splits
            for sha, splits in sha256_to_splits.items():
                if len(splits) > 1:
                    leakage_warnings.append(
                        f"Exact Duplicate Leakage: Byte-identical image (SHA-256: {sha[:12]}...) present across splits: {', '.join(sorted(splits))}."
                    )
                if len(sha256_to_ids[sha]) > 1:
                    duplicate_records_count += (len(sha256_to_ids[sha]) - 1)

            # Near-duplicates cross-split check
            if check_near_duplicates and len(dhash_records) < 500:  # Bound O(N^2) comparison
                for i in range(len(dhash_records)):
                    id_a, split_a, dh_a = dhash_records[i]
                    for j in range(i + 1, len(dhash_records)):
                        id_b, split_b, dh_b = dhash_records[j]
                        if split_a != split_b:
                            dist = ImageQualityChecker.hamming_distance(dh_a, dh_b)
                            if dist <= NEAR_DUPLICATE_HAMMING_THRESHOLD:
                                leakage_warnings.append(
                                    f"Near-Duplicate Leakage: Images '{id_a}' ({split_a}) and '{id_b}' ({split_b}) "
                                    f"are perceptually near-identical (Hamming distance {dist} <= {NEAR_DUPLICATE_HAMMING_THRESHOLD})."
                                )

        # 7. Statistical Imbalance Analysis
        class_counts = list(images_per_class.values())
        if class_counts:
            min_count = min(class_counts)
            max_count = max(class_counts)
            total_count = sum(class_counts)

            for disease_name, count in images_per_class.items():
                pct = (count / total_count) * 100
                if pct < 5.0 and total_count >= 20:
                    quality_warnings.append(
                        f"Severe Class Minority: '{disease_name}' constitutes only {pct:.1f}% ({count}/{total_count}) of dataset."
                    )

            if min_count > 0 and (max_count / min_count) > 10.0:
                quality_warnings.append(
                    f"Extreme Class Imbalance: Ratio between dominant class ({max_count}) and minority class ({min_count}) is {max_count/min_count:.1f}:1 (>10:1)."
                )

        # 8. Recommend Actions based on findings
        if leakage_warnings:
            recommended_actions.append(
                "Remediate data leakage immediately: enforce animal-level grouping split and remove duplicate hash cross-contamination."
            )
        if license_warnings:
            recommended_actions.append(
                "Quarantine records with unverified or missing licenses until formal provenance documentation is secured."
            )
        if any("Extreme Class Imbalance" in w for w in quality_warnings):
            recommended_actions.append(
                "Apply class re-weighting (Focal Loss / effective sample weights) and targeted data acquisition for minority veterinary conditions."
            )
        if invalid_records:
            recommended_actions.append(
                f"Correct {len(invalid_records)} taxonomically invalid or contradictory manifest records."
            )

        valid_count = total_images - len(invalid_records)

        return {
            "total_images": total_images,
            "valid_images": max(0, valid_count),
            "invalid_images": len(invalid_records),
            "duplicate_images": duplicate_records_count,
            "classes": sorted(list(classes_set)),
            "images_per_class": dict(images_per_class),
            "species_distribution": dict(species_distribution),
            "split_distribution": dict(split_distribution),
            "leakage_warnings": leakage_warnings,
            "license_warnings": license_warnings,
            "quality_warnings": quality_warnings,
            "recommended_actions": recommended_actions
        }
