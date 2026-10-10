"""
Unit & Integration Tests for AniCare AI Dataset Intelligence, Label Schema & Validation
Tests taxonomy validation, PII redaction, image quality & corruption, exact & perceptual duplicates,
cross-split leakage, same-animal leakage, class imbalance, and epidemiology event contracts.
"""

import os
import io
import pytest
from PIL import Image
from pydantic import ValidationError

from ai.dataset.schema import (
    TargetSpeciesEnum,
    DiseaseCategoryEnum,
    DatasetSplitEnum,
    ImageQualityEnum,
    AnnotationStatusEnum,
    VETERINARY_TAXONOMY,
    DatasetManifestRecord,
)
from ai.dataset.quality import (
    ImageQualityChecker,
    ImageQualityAssessment,
    NEAR_DUPLICATE_HAMMING_THRESHOLD,
)
from ai.dataset.validator import DatasetManifestValidator
from ai.dataset.manifest import DatasetManifestManager
from ai.epidemiology.event_schema import (
    EpidemiologyEvent,
    GeoLocation,
    VaccinationStatusEnum,
    EventSourceEnum,
    VerificationStatusEnum,
)


def _create_synthetic_image_bytes(width: int = 256, height: int = 256, color=(128, 64, 32), format: str = "JPEG") -> bytes:
    """Helper creating memory buffer of an in-memory test image."""
    img = Image.new("RGB", (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


class TestVeterinaryTaxonomyAndSchema:
    """Tests for veterinary label schema and biological taxonomies."""

    def test_all_seven_species_present_in_taxonomy(self):
        """Verify all 7 core livestock and companion species are fully defined."""
        expected_species = [
            TargetSpeciesEnum.CATTLE.value,
            TargetSpeciesEnum.BUFFALO.value,
            TargetSpeciesEnum.GOAT.value,
            TargetSpeciesEnum.SHEEP.value,
            TargetSpeciesEnum.PIG.value,
            TargetSpeciesEnum.POULTRY.value,
            TargetSpeciesEnum.DOG.value,
        ]
        for sp in expected_species:
            assert sp in VETERINARY_TAXONOMY
            assert len(VETERINARY_TAXONOMY[sp]) >= 3
            assert "Healthy / Normal" in VETERINARY_TAXONOMY[sp]

    def test_valid_manifest_record_creation(self):
        """Verify a compliant record parses with all required metadata."""
        rec = DatasetManifestRecord(
            image_id="IMG-TEST-001",
            file_path="raw/cattle/lsd/IMG-TEST-001.jpg",
            species=TargetSpeciesEnum.CATTLE,
            disease="Lumpy Skin Disease",
            disease_category=DiseaseCategoryEnum.VISUAL_ASSESSABLE,
            body_region="skin_cutaneous",
            clinical_sign="Circumscribed dermal nodules",
            image_source="AAU_Anand_Clinical_Repository",
            source_organization="Anand Agricultural University",
            geographic_region="Gujarat, India",
            license="CC-BY-4.0",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            consent_provenance="Institutional Research Protocol On File",
            split=DatasetSplitEnum.TRAIN,
            animal_id="COW-TAG-991",
            image_quality=ImageQualityEnum.HIGH,
            notes="Confirmed via Capripox PCR at CADRAD."
        )
        assert rec.image_id == "IMG-TEST-001"
        assert rec.species == TargetSpeciesEnum.CATTLE
        assert rec.disease == "Lumpy Skin Disease"

    def test_invalid_class_detection_biological_mismatch(self):
        """Verify cross-species disease mismatches are rejected by schema."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetManifestRecord(
                image_id="IMG-TEST-002",
                file_path="raw/cattle/IMG-TEST-002.jpg",
                species=TargetSpeciesEnum.CATTLE,
                disease="Canine Demodicosis (Mange)",  # Biologically invalid for Cattle
                disease_category=DiseaseCategoryEnum.VISUAL_ASSESSABLE,
                body_region="muzzle",
                clinical_sign="Alopecia",
                image_source="Test_Source",
                source_organization="Test Org",
                geographic_region="Test Region",
                license="CC-BY-4.0",
                license_url="https://creativecommons.org/licenses/by/4.0/",
                consent_provenance="Test Protocol",
                split=DatasetSplitEnum.TRAIN
            )
        assert "Biological Mismatch" in str(exc_info.value)

    def test_pii_sanitization_rejects_personal_phone_numbers(self):
        """Verify personal phone numbers in notes trigger privacy security exceptions."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetManifestRecord(
                image_id="IMG-TEST-003",
                file_path="raw/cattle/IMG-TEST-003.jpg",
                species=TargetSpeciesEnum.CATTLE,
                disease="Lumpy Skin Disease",
                disease_category=DiseaseCategoryEnum.VISUAL_ASSESSABLE,
                body_region="skin_cutaneous",
                clinical_sign="Nodules",
                image_source="Test_Source",
                source_organization="Test Org",
                geographic_region="Test Region",
                license="CC-BY-4.0",
                license_url="https://creativecommons.org/licenses/by/4.0/",
                consent_provenance="Test Protocol",
                notes="Farmer contact mobile: 9876543210 please call"
            )
        assert "PII Security Violation" in str(exc_info.value)


class TestImageQualityAndDuplicates:
    """Tests image corruption, resolution tiering, and duplicate detection."""

    def test_corrupt_image_detection(self):
        """Verify corrupted bytes fail gracefully with UNUSABLE tier."""
        corrupt_bytes = b"NOT_A_VALID_JPEG_HEADER_CORRUPT_BYTES_XYZ"
        assessment = ImageQualityChecker.inspect_image_bytes(corrupt_bytes, file_name="corrupt.jpg")
        assert not assessment.is_valid
        assert assessment.quality_tier == ImageQualityEnum.UNUSABLE
        assert assessment.error is not None

    def test_resolution_tiering(self):
        """Verify resolution thresholds: unusable (<64), poor (<224), acceptable, high (>=512)."""
        # Unusable <64
        bytes_32 = _create_synthetic_image_bytes(32, 32)
        res_32 = ImageQualityChecker.inspect_image_bytes(bytes_32)
        assert not res_32.is_valid
        assert res_32.quality_tier == ImageQualityEnum.UNUSABLE

        # Poor <224
        bytes_128 = _create_synthetic_image_bytes(128, 128)
        res_128 = ImageQualityChecker.inspect_image_bytes(bytes_128)
        assert res_128.is_valid
        assert res_128.quality_tier == ImageQualityEnum.POOR

        # Acceptable >= 224
        bytes_256 = _create_synthetic_image_bytes(256, 256)
        res_256 = ImageQualityChecker.inspect_image_bytes(bytes_256)
        assert res_256.is_valid
        assert res_256.quality_tier == ImageQualityEnum.ACCEPTABLE

        # High >= 512
        bytes_512 = _create_synthetic_image_bytes(512, 512)
        res_512 = ImageQualityChecker.inspect_image_bytes(bytes_512)
        assert res_512.is_valid
        assert res_512.quality_tier == ImageQualityEnum.HIGH

    def test_exact_duplicate_hash_calculation(self):
        """Verify identical images yield identical SHA-256 and MD5."""
        img_bytes = _create_synthetic_image_bytes(256, 256, color=(100, 150, 200))
        hashes1 = ImageQualityChecker.compute_exact_hashes(img_bytes)
        hashes2 = ImageQualityChecker.compute_exact_hashes(img_bytes)
        assert hashes1["sha256"] == hashes2["sha256"]
        assert hashes1["md5"] == hashes2["md5"]

    def test_near_duplicate_dhash_detection(self):
        """Verify perceptual similarity detection via dHash Hamming distance."""
        # Create base image
        img1 = Image.new("RGB", (256, 256), color=(200, 100, 50))
        # Create slightly shifted image (near duplicate)
        img2 = Image.new("RGB", (256, 256), color=(202, 102, 52))

        hash1 = ImageQualityChecker.compute_dhash(img1)
        hash2 = ImageQualityChecker.compute_dhash(img2)
        dist = ImageQualityChecker.hamming_distance(hash1, hash2)

        assert dist <= NEAR_DUPLICATE_HAMMING_THRESHOLD
        assert ImageQualityChecker.is_near_duplicate(hash1, hash2)


class TestManifestValidationAndLeakage:
    """Tests cross-split leakage, same-animal leakage, license warnings, and reports."""

    def _make_record(self, img_id: str, split: DatasetSplitEnum, animal_id: str = None, license_str: str = "CC-BY-4.0") -> DatasetManifestRecord:
        return DatasetManifestRecord(
            image_id=img_id,
            file_path=f"raw/cattle/{img_id}.jpg",
            species=TargetSpeciesEnum.CATTLE,
            disease="Lumpy Skin Disease",
            disease_category=DiseaseCategoryEnum.VISUAL_ASSESSABLE,
            body_region="skin_cutaneous",
            clinical_sign="Nodules",
            image_source="AAU_Anand_Clinical_Repository",
            source_organization="Anand Agricultural University",
            geographic_region="Gujarat, India",
            license=license_str,
            license_url="https://creativecommons.org/licenses/by/4.0/",
            consent_provenance="Consent On File",
            split=split,
            animal_id=animal_id
        )

    def test_same_animal_leakage_warning(self):
        """Verify warning when the same animal appears in both train and validation splits."""
        records = [
            self._make_record("IMG-001", DatasetSplitEnum.TRAIN, animal_id="COW-881"),
            self._make_record("IMG-002", DatasetSplitEnum.VALIDATION, animal_id="COW-881"),  # Same animal in validation!
            self._make_record("IMG-003", DatasetSplitEnum.TEST, animal_id="COW-992"),
        ]
        report = DatasetManifestValidator.validate_manifest(records)
        assert any("Same-Animal Leakage" in w for w in report["leakage_warnings"])
        assert any("COW-881" in w for w in report["leakage_warnings"])

    def test_exact_hash_cross_split_leakage(self):
        """Verify warning when identical image hashes exist across train and test."""
        records = [
            self._make_record("IMG-A", DatasetSplitEnum.TRAIN),
            self._make_record("IMG-B", DatasetSplitEnum.TEST),
        ]
        shared_sha = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        image_hashes = {
            "IMG-A": {"sha256": shared_sha, "dhash": "0000ffff0000ffff"},
            "IMG-B": {"sha256": shared_sha, "dhash": "0000ffff0000ffff"},
        }
        report = DatasetManifestValidator.validate_manifest(records, image_hashes=image_hashes)
        assert any("Exact Duplicate Leakage" in w for w in report["leakage_warnings"])

    def test_missing_and_unverified_license_warning(self):
        """Verify warning when license is missing or unverified."""
        records = [
            self._make_record("IMG-001", DatasetSplitEnum.TRAIN, license_str="unknown"),
            self._make_record("IMG-002", DatasetSplitEnum.TRAIN, license_str="All Rights Reserved"),
        ]
        report = DatasetManifestValidator.validate_manifest(records)
        assert len(report["license_warnings"]) == 2
        assert any("Unverified License" in w for w in report["license_warnings"])

    def test_class_imbalance_warning(self):
        """Verify extreme class ratio (>10:1) triggers imbalance warning."""
        records = []
        # 30 records of Lumpy Skin Disease
        for i in range(30):
            records.append(self._make_record(f"IMG-LSD-{i}", DatasetSplitEnum.TRAIN))
        # 1 record of Dermatophytosis (Ringworm)
        records.append(DatasetManifestRecord(
            image_id="IMG-RING-1",
            file_path="raw/cattle/ringworm.jpg",
            species=TargetSpeciesEnum.CATTLE,
            disease="Dermatophytosis (Ringworm)",
            disease_category=DiseaseCategoryEnum.VISUAL_ASSESSABLE,
            body_region="periocular",
            clinical_sign="Circular crusts",
            image_source="AAU_Anand_Clinical_Repository",
            source_organization="Anand Agricultural University",
            geographic_region="Gujarat, India",
            license="CC-BY-4.0",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            consent_provenance="Consent On File",
            split=DatasetSplitEnum.TRAIN
        ))

        report = DatasetManifestValidator.validate_manifest(records)
        assert any("Extreme Class Imbalance" in w for w in report["quality_warnings"])

    def test_animal_level_group_partitioning(self):
        """Verify DatasetManifestManager cleanly partitions animals without leakage."""
        records = [
            self._make_record("IMG-1A", DatasetSplitEnum.TRAIN, animal_id="COW-A"),
            self._make_record("IMG-1B", DatasetSplitEnum.TRAIN, animal_id="COW-A"),
            self._make_record("IMG-2A", DatasetSplitEnum.TRAIN, animal_id="COW-B"),
            self._make_record("IMG-3A", DatasetSplitEnum.TRAIN, animal_id="COW-C"),
            self._make_record("IMG-4A", DatasetSplitEnum.TRAIN, animal_id="COW-D"),
            self._make_record("IMG-5A", DatasetSplitEnum.TRAIN, animal_id="COW-E"),
        ]

        partitioned = DatasetManifestManager.split_by_animal(
            records, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=123
        )
        report = DatasetManifestValidator.validate_manifest(partitioned)

        # There must be zero same-animal leakage after animal-level partitioning
        same_animal_warnings = [w for w in report["leakage_warnings"] if "Same-Animal Leakage" in w]
        assert len(same_animal_warnings) == 0

        # All images of COW-A must share the same split
        cow_a_splits = {r.split for r in partitioned if r.animal_id == "COW-A"}
        assert len(cow_a_splits) == 1

    def test_json_and_csv_serialization(self, tmp_path):
        """Verify JSON and CSV manifest export and import round-trips."""
        records = [
            self._make_record("IMG-IO-1", DatasetSplitEnum.TRAIN, animal_id="COW-X"),
            self._make_record("IMG-IO-2", DatasetSplitEnum.TEST, animal_id="COW-Y"),
        ]

        # JSON Roundtrip
        json_path = str(tmp_path / "manifest.json")
        DatasetManifestManager.save_to_json(records, json_path)
        loaded_json = DatasetManifestManager.load_from_json(json_path)
        assert len(loaded_json) == 2
        assert loaded_json[0].image_id == "IMG-IO-1"

        # CSV Roundtrip
        csv_path = str(tmp_path / "manifest.csv")
        DatasetManifestManager.save_to_csv(records, csv_path)
        loaded_csv = DatasetManifestManager.load_from_csv(csv_path)
        assert len(loaded_csv) == 2
        assert loaded_csv[1].image_id == "IMG-IO-2"


class TestEpidemiologyEventSchema:
    """Tests epidemiological outbreak surveillance contracts."""

    def test_valid_epidemiology_event(self):
        """Verify conforming outbreak event parses successfully."""
        event = EpidemiologyEvent(
            event_id="EPI-GJ-2026-001",
            disease="Foot and Mouth Disease",
            species=TargetSpeciesEnum.CATTLE,
            location=GeoLocation(state="Gujarat", district="Anand", block_or_taluk="Anand", latitude=22.56, longitude=72.95),
            date="2026-03-20",
            affected_count=12,
            suspected_count=30,
            confirmed_count=10,
            mortality_count=1,
            vaccination_status=VaccinationStatusEnum.UNVACCINATED,
            source=EventSourceEnum.AI_VISUAL_DETECTION,
            verification_status=VerificationStatusEnum.FIELD_INVESTIGATION_PENDING
        )
        assert event.event_id == "EPI-GJ-2026-001"
        assert event.confirmed_count == 10

    def test_epidemiology_invalid_date_format(self):
        """Verify invalid date strings fail validation."""
        with pytest.raises(ValidationError):
            EpidemiologyEvent(
                event_id="EPI-002",
                disease="Foot and Mouth Disease",
                species=TargetSpeciesEnum.CATTLE,
                location=GeoLocation(state="Gujarat", district="Anand"),
                date="20-03-2026",  # Must be YYYY-MM-DD
                source=EventSourceEnum.FARMER_SYMPTOM_REPORT
            )

    def test_epidemiology_inconsistent_counts(self):
        """Verify confirmed count cannot exceed total affected + suspected animals."""
        with pytest.raises(ValidationError) as exc_info:
            EpidemiologyEvent(
                event_id="EPI-003",
                disease="Foot and Mouth Disease",
                species=TargetSpeciesEnum.CATTLE,
                location=GeoLocation(state="Gujarat", district="Anand"),
                date="2026-03-20",
                affected_count=5,
                suspected_count=5,
                confirmed_count=25,  # 25 > 10 (mathematically impossible)
                source=EventSourceEnum.OFFICIAL_DAHD_NOTIFICATION
            )
        assert "Count inconsistency" in str(exc_info.value)


class TestRealAcquiredDatasetValidation:
    """Verifies that the actual downloaded and normalized dataset satisfies all requirements."""

    def test_real_manifest_loads_and_has_906_clean_samples(self):
        """Verify the generated processed manifest contains exactly 906 deduplicated records."""
        from collections import Counter
        manifest_path = os.path.join(os.path.dirname(__file__), "..", "ai", "dataset", "processed", "manifest.json")
        assert os.path.exists(manifest_path), f"Processed manifest missing at {manifest_path}"
        
        records = DatasetManifestManager.load_from_json(manifest_path)
        assert len(records) == 906
        
        # Check species and valid classes
        species_set = {r.species.value for r in records}
        assert species_set == {TargetSpeciesEnum.CATTLE.value}
        
        disease_counts = Counter(r.disease for r in records)
        assert disease_counts["Lumpy Skin Disease"] == 271
        assert disease_counts["Healthy / Normal"] == 635
        
        # Check splits
        split_counts = Counter(r.split.value for r in records)
        assert split_counts["train"] == 633
        assert split_counts["validation"] == 135
        assert split_counts["test"] == 138

    def test_real_dataset_report_integrity(self):
        """Verify dataset_report.json has zero leakage and zero errors."""
        import json
        report_path = os.path.join(os.path.dirname(__file__), "..", "ai", "dataset", "processed", "dataset_report.json")
        assert os.path.exists(report_path)
        
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        prov = data["provenance_metadata"]
        assert prov["actual_downloaded_count"] == 1024
        assert prov["final_validated_count"] == 906
        assert prov["quarantined_count"] == 118
        assert prov["animal_grouping_available"] is False
        assert prov["license"] == "CC-BY-4.0"
        
        metrics = data["validation_metrics"]
        assert metrics["total_images"] == 906
        assert metrics["invalid_images"] == 0
        assert len(metrics["leakage_warnings"]) == 0
        assert len(metrics["license_warnings"]) == 0

    def test_real_acquisition_manifest_records(self):
        """Verify acquisition manifest recorded 1 approved and 2 review_required datasets."""
        import json
        acq_path = os.path.join(os.path.dirname(__file__), "..", "ai", "dataset", "acquisition", "acquisition_manifest.json")
        assert os.path.exists(acq_path)
        with open(acq_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            
        assert len(items) == 3
        lsd = next(x for x in items if "Lumpy Skin" in x["dataset_name"])
        assert lsd["verified"] is True
        assert lsd["download_status"] == "DOWNLOADED_AND_VERIFIED"
        assert lsd["image_count_downloaded"] == 1024
        
        unverified = [x for x in items if not x["verified"]]
        assert len(unverified) == 2
        for u in unverified:
            assert u["download_status"] == "REVIEW_REQUIRED"
            assert u["image_count_downloaded"] == 0

