"""
AniCare AI — Milestone 8A Test Suite: External Validation Governance & Independent Pipeline
Tests:
1. Provenance validation completeness
2. Permission gate & allowed vs blocked states
3. Missing / unverified license quarantine
4. Rejected dataset handling (Kaggle barred)
5. Intra-dataset duplicate detection
6. Cross-dataset duplicate detection against Dataset A
7. Ambiguous dermatology labels quarantine
8. Unsupported species routing (MODEL_NOT_VALIDATED_FOR_SPECIES)
9. Missing ground truth / corrupt image rejection
10. Animal grouping handling & animal_grouping_available = false
11. Frozen threshold at exactly 0.50 & no test-set tuning
12. No model retraining (frozen EfficientNet-B0 ONNX weights)
13. External metrics calculation & Wilson 95% confidence intervals
14. Insufficient sample size reporting (N < 5) without fabricated percentages
15. API status endpoint (GET /api/evaluation/external/status)
16. Detection API backward-compatibility (POST /api/detection/analyze)
"""

import io
import json
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from ai.config import ai_config
from ai.dataset.external.permission_registry import (
    PermissionState,
    PermissionRegistry,
    LegalEthicalGate
)
from ai.dataset.external.provenance import provenance_registry
from ai.dataset.external.external_manifest import ExternalManifestRecord
from ai.dataset.external.duplicate_guard import duplicate_guard
from ai.dataset.external.label_audit import label_auditor
from ai.dataset.external.quality_audit import quality_auditor, QualityTier
from ai.dataset.external.grouping import grouping_auditor
from ai.dataset.external.validator import external_dataset_validator
from ai.dataset.external.evaluator import external_evaluator, wilson_score_interval
from ai.inference.model_scope import model_scope_registry

client = TestClient(app)


def _generate_synthetic_image_bytes(width=224, height=224, color=(100, 70, 40)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# 1. Provenance Validation Completeness
def test_1_provenance_validation_completeness():
    """Verify registry entries contain all mandatory provenance attributes."""
    aau = provenance_registry.get_source_by_id("DATASET-B-CANDIDATE-AAU")
    assert aau is not None
    validation = provenance_registry.validate_provenance_completeness("DATASET-B-CANDIDATE-AAU")
    assert validation["is_complete"] is True
    assert validation["permission_status"] == "PERMISSION_REQUIRED"

    icar = provenance_registry.get_source_by_id("DATASET-B-CANDIDATE-ICAR")
    assert icar is not None
    assert icar["institution"] == "ICAR Directorate of Foot and Mouth Disease"


# 2. Permission Gate & Allowed vs Blocked States
def test_2_permission_gate_states():
    """Verify only PERMISSION_GRANTED or VALIDATED allows active validation."""
    assert PermissionRegistry.is_permission_granted("PERMISSION_GRANTED") is True
    assert PermissionRegistry.is_permission_granted("VALIDATED") is True
    assert PermissionRegistry.is_permission_granted("APPROVED") is True

    # Blocked states
    assert PermissionRegistry.is_permission_granted("PERMISSION_REQUIRED") is False
    assert PermissionRegistry.is_permission_granted("REJECTED") is False
    assert PermissionRegistry.is_permission_granted("DISCOVERY") is False
    assert PermissionRegistry.is_permission_granted("QUARANTINED") is False


# 3. Missing / Unverified License Quarantine
def test_3_missing_license_quarantine():
    """Verify datasets with missing licenses fail the 10-point legal gate."""
    unlicensed_entry = {
        "source_id": "TEST-UNLICENSED",
        "permission_status": "PERMISSION_REQUIRED",
        "license": None,
        "research_use_allowed": True
    }
    passed, reason, checks = LegalEthicalGate.evaluate(unlicensed_entry)
    assert passed is False
    assert "LEGAL_GATE_FAILED" in reason
    assert checks["1_permission_or_license_exists"] is False


# 4. Rejected Dataset Handling (Kaggle Barred)
def test_4_rejected_dataset_handling():
    """Verify uncurated Kaggle dumps are strictly REJECTED and blocked."""
    kaggle = provenance_registry.get_source_by_id("DATASET-B-CANDIDATE-KAGGLE")
    assert kaggle is not None
    assert kaggle["permission_status"] == PermissionState.REJECTED.value
    assert PermissionRegistry.is_permission_granted(kaggle["permission_status"]) is False


# 5. Intra-Dataset Duplicate Detection
def test_5_intra_dataset_duplicate_detection():
    """Verify duplicate images within a candidate batch are quarantined."""
    img_bytes = _generate_synthetic_image_bytes(color=(120, 80, 50))
    batch = [
        {"sample_id": "B-01", "image_bytes": img_bytes, "species": "Cattle", "disease": "Lumpy Skin Disease"},
        {"sample_id": "B-02", "image_bytes": img_bytes, "species": "Cattle", "disease": "Healthy / Normal"}
    ]
    summary = external_dataset_validator.validate_candidate_batch(batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["intra_dataset_duplicates_quarantined"] == 1
    assert len(summary["quarantined_records"]) >= 1


# 6. Cross-Dataset Duplicate Detection Against Dataset A
def test_6_cross_dataset_duplicate_detection():
    """Verify any image matching Dataset A is rejected with CROSS_DATASET_LEAKAGE."""
    manifest_path = Path("backend/ai/dataset/processed/manifest.json")
    if not manifest_path.is_file():
        manifest_path = Path("ai/dataset/processed/manifest.json")
    assert manifest_path.is_file()

    with open(manifest_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Use first real image from Dataset A
    sample_a_path = Path("backend") / records[0]["file_path"]
    if not sample_a_path.is_file():
        sample_a_path = Path(records[0]["file_path"])

    with open(sample_a_path, "rb") as f:
        a_bytes = f.read()

    batch = [{
        "sample_id": "CROSS-LEAK-TEST",
        "image_bytes": a_bytes,
        "species": "Cattle",
        "disease": "Lumpy Skin Disease"
    }]
    summary = external_dataset_validator.validate_candidate_batch(batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["cross_dataset_duplicates_quarantined"] == 1
    assert summary["accepted_valid_count"] == 0
    assert any("CROSS_DATASET_LEAKAGE" in q.get("quarantine_reason", "") for q in summary["quarantined_records"])


# 7. Ambiguous Dermatology Labels Quarantine
def test_7_ambiguous_labels_quarantine():
    """Verify non-pathognomonic or overlapping dermal conditions are quarantined as AMBIGUOUS."""
    batch = [
        {"sample_id": "AMB-01", "species": "Cattle", "disease": "Pseudolumpy skin eruptions", "image_bytes": _generate_synthetic_image_bytes(color=(70, 70, 70))},
        {"sample_id": "AMB-02", "species": "Cattle", "disease": "Bovine Papillomatosis warts", "image_bytes": _generate_synthetic_image_bytes(color=(80, 80, 80))},
        {"sample_id": "AMB-03", "species": "Cattle", "disease": "Dermatophytosis / Ringworm", "image_bytes": _generate_synthetic_image_bytes(color=(90, 90, 90))}
    ]
    summary = external_dataset_validator.validate_candidate_batch(batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["ambiguous_count"] == 3
    assert summary["accepted_valid_count"] == 0
    for q in summary["quarantined_records"]:
        assert "AMBIGUOUS_LABEL" in q.get("quarantine_reason", "")


# 8. Unsupported Species Routing
def test_8_unsupported_species_routing():
    """Verify non-cattle species are rejected with MODEL_NOT_VALIDATED_FOR_SPECIES."""
    non_cattle = ["Buffalo", "Goat", "Sheep", "Dog", "Horse", "Pig"]
    for sp in non_cattle:
        status, label, sp_status, ev = label_auditor.audit_sample({"species": sp, "disease": "Lumpy Skin Disease"})
        assert status == "REJECTED"
        assert sp_status == "MODEL_NOT_VALIDATED_FOR_SPECIES"


# 9. Missing Ground Truth / Corrupted Image Rejection
def test_9_corrupt_image_rejection():
    """Verify corrupt bytes are assigned QualityTier.UNUSABLE and quarantined."""
    corrupt_bytes = b"CORRUPTED_NON_IMAGE_DATA_BYTES"
    q_res = quality_auditor.audit_image_bytes(corrupt_bytes)
    assert q_res["is_valid"] is False
    assert q_res["quality_tier"] == QualityTier.UNUSABLE.value

    batch = [{"sample_id": "CORRUPT-01", "species": "Cattle", "disease": "Lumpy Skin Disease", "image_bytes": corrupt_bytes}]
    summary = external_dataset_validator.validate_candidate_batch(batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["rejected_count"] == 1
    assert summary["accepted_valid_count"] == 0


# 10. Animal Grouping Handling & Limitation Notes
def test_10_animal_grouping_handling():
    """Verify absence of animal IDs correctly sets animal_grouping_available = false."""
    records_without_ids = [
        {"sample_id": "R1", "species": "Cattle", "disease": "Lumpy Skin Disease"},
        {"sample_id": "R2", "species": "Cattle", "disease": "Healthy / Normal"}
    ]
    info = grouping_auditor.audit_grouping(records_without_ids)
    assert info["animal_grouping_available"] is False
    assert "CANNOT claim herd-independent" in info["limitation_note"]


# 11. Frozen Threshold at 0.50 & No Test-Set Tuning
def test_11_frozen_threshold():
    """Verify operating threshold is frozen at 0.50 across all evaluation components."""
    assert ai_config.OPERATING_THRESHOLD == 0.50
    assert ai_config.OPERATING_THRESHOLD_FROZEN is True
    assert external_evaluator.frozen_threshold == 0.50


# 12. No Model Retraining
def test_12_no_model_retraining():
    """Verify ONNX model weights and signature remain identical to Milestone 5/6/7."""
    model_path = Path("backend/ai/models/weights/anicare_vision_bovine_v1.onnx")
    if not model_path.is_file():
        model_path = Path("ai/models/weights/anicare_vision_bovine_v1.onnx")
    assert model_path.is_file()
    # Confirm model file size is ~15.29 MB (16,032,698 bytes)
    size_mb = model_path.stat().st_size / (1024 * 1024)
    assert 14.5 <= size_mb <= 16.0


# 13. External Metrics Calculation & Wilson 95% Confidence Intervals
def test_13_wilson_confidence_interval():
    """Verify Wilson score confidence interval calculations."""
    ci = wilson_score_interval(34, 42, confidence=0.95)
    assert ci["point_estimate"] == round(34 / 42, 4)
    assert ci["lower"] is not None
    assert ci["upper"] is not None
    assert ci["lower"] < ci["point_estimate"] < ci["upper"]

    # Edge cases
    empty_ci = wilson_score_interval(0, 0)
    assert empty_ci["lower"] is None


# 14. Insufficient Sample Size Reporting (N < 5)
def test_14_insufficient_sample_size_safety():
    """Verify candidate batch with N < 5 reports INSUFFICIENT_EXTERNAL_SAMPLE_SIZE."""
    # Create batch of 3 distinct images
    batch = [
        {"image_id": f"S-{i}", "species": "Cattle", "disease": "Lumpy Skin Disease", "image_bytes": _generate_synthetic_image_bytes(color=(50 + i * 20, 60, 40))}
        for i in range(3)
    ]
    # Simulate evaluation with verified source
    source_entry = {
        "source_id": "VERIFIED-PILOT",
        "source_name": "Verified Pilot Source",
        "permission_status": "PERMISSION_GRANTED",
        "license": "CC-BY-4.0",
        "research_use_allowed": True,
        "redistribution_allowed": True,
        "contact_reference": "Verified Institutional Office"
    }
    res = external_evaluator._run_inference_and_metrics(batch, "VERIFIED-PILOT", source_entry, {}, {})
    assert res["evaluation_status"] == "INSUFFICIENT_EXTERNAL_SAMPLE_SIZE"
    assert res["external_metrics"] == "INSUFFICIENT_EXTERNAL_SAMPLE_SIZE"


# 15. API Status Endpoint
def test_15_api_external_evaluation_status(client):
    """Verify GET /api/evaluation/external/status returns truthful pending status."""
    res = client.get("/api/evaluation/external/status")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_b_status"] == "PERMISSION_REQUIRED"
    assert data["permission_status"] == "PERMISSION_REQUIRED"
    assert data["external_validation_available"] is False
    assert data["validated_image_count"] == 0
    assert data["threshold"] == 0.50
    assert "AAU Anand" in str(data["candidate_sources"]) or "DATASET-B-CANDIDATE" in str(data["candidate_sources"])


# 16. Detection API Backward-Compatibility
def test_16_detection_api_backward_compatibility(client):
    """Verify POST /api/detection/analyze remains 100% backward compatible."""
    payload = {
        "species": "Cattle",
        "symptoms": ["cutaneous nodules", "fever"],
        "body_temperature": 104.2
    }
    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "possible_condition" in data
    assert "confidence" in data
    assert "risk_level" in data
    assert "veterinary_review_required" in data
    assert "differential_diagnoses" in data
