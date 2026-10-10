"""
AniCare AI — Milestone 11 Automated Test Suite
AI Model Monitoring, Field Feedback, Drift Detection & Continuous Learning Architecture
Tests all governance rules, promotion gates, SHA-256 integrity, RBAC, and safety guardrails.
"""

import pytest
import os
from pathlib import Path

from ai.model_registry import model_registry, ModelStatus, ModelMetadataItem
from ai.monitoring import drift_detector, DriftStatus
from ai.data_curation import (
    curation_pipeline,
    PermissionStatus,
    EvidenceLevel,
    duplicate_detector,
    image_quality_analyzer,
    dataset_leakage_guard,
    DataLeakageError
)
from ai.experiments import experiment_tracker
from app.utils.security import create_access_token


def get_token(role: str, user_id: str = "USR-01", name: str = "User") -> str:
    return create_access_token({"sub": user_id, "name": name, "role": role})


# 1. Model Registry, Immutability & Cryptographic Integrity Tests

def test_production_model_registered_and_immutable():
    prod = model_registry.get_production_model("bovine", "lumpy_skin_disease_screening")
    assert prod is not None
    assert prod.model_id == "anicare_vision_bovine_v1"
    assert prod.version == "1.0.0"
    assert prod.status == ModelStatus.PRODUCTION
    assert prod.is_immutable is True
    assert prod.threshold == 0.50


def test_production_model_sha256_verification():
    integ = model_registry.verify_model_integrity("anicare_vision_bovine_v1")
    assert integ.is_valid is True
    assert integ.computed_sha256.lower() == "594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d"
    assert integ.error_message is None


def test_production_model_cannot_be_overwritten():
    bad_meta = ModelMetadataItem(
        model_id="anicare_vision_bovine_v1",
        version="1.0.1-hacked",
        species="bovine",
        condition="lumpy_skin_disease_screening",
        framework="onnx",
        architecture="EfficientNet-B0",
        sha256="fake_sha256",
        weights_path="models/weights/anicare_vision_bovine_v1.onnx",
        training_dataset="none",
        validation_dataset="none",
        test_dataset="none",
        created_at="2026-10-08T00:00:00Z"
    )
    ok, msg, _ = model_registry.register_model(bad_meta, user_role="admin")
    assert ok is False
    assert "immutable" in msg.lower() or "cannot be overwritten" in msg.lower()


def test_invalid_sha256_rejection_on_registration():
    test_meta = ModelMetadataItem(
        model_id="anicare_vision_test_bad_hash",
        version="1.0.0",
        species="bovine",
        condition="lumpy_skin_disease_screening",
        framework="onnx",
        architecture="EfficientNet-B0",
        sha256="0000000000000000000000000000000000000000000000000000000000000000",
        weights_path="models/weights/anicare_vision_bovine_v1.onnx",
        training_dataset="Dataset_A",
        validation_dataset="Dataset_A_val",
        test_dataset="Dataset_A_test",
        created_at="2026-10-08T00:00:00Z"
    )
    ok, msg, _ = model_registry.register_model(test_meta, user_role="admin")
    assert ok is False
    assert "checksum mismatch" in msg.lower()


# 2. Veterinary Clinical Feedback & Role-Based Access Control Tests

def test_veterinarian_can_submit_feedback(client):
    vet_tok = get_token("veterinarian", "USR-VET-001", "Dr. Rajesh Patel")
    payload = {
        "prediction_id": "PRED-TEST-VET-01",
        "animal_id": "AN-GJ-2024-0104",
        "model_version": "anicare_vision_bovine_v1",
        "ai_prediction": "Lumpy Skin Disease",
        "ai_confidence": 0.88,
        "veterinary_assessment": "Confirmed mild cutaneous nodules; stage 1 LSD.",
        "feedback_type": "AI_ACCEPTED",
        "clinical_notes": "Clinical palpation confirms circumscribed nodules.",
        "evidence_level": "VET_REVIEWED"
    }
    res = client.post(
        "/api/ai-feedback",
        json=payload,
        headers={"Authorization": f"Bearer {vet_tok}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["feedback_type"] == "AI_ACCEPTED"
    assert data["review_status"] == "VET_REVIEWED"
    assert "FB-" in data["feedback_id"]


def test_farmer_is_forbidden_from_submitting_feedback(client):
    farmer_tok = get_token("farmer", "USR-FARMER-01", "Ramesh Kumar")
    payload = {
        "prediction_id": "PRED-TEST-FARMER-01",
        "model_version": "anicare_vision_bovine_v1",
        "ai_prediction": "Lumpy Skin Disease",
        "ai_confidence": 0.85,
        "veterinary_assessment": "Farmer trying to diagnose",
        "feedback_type": "AI_ACCEPTED",
        "evidence_level": "UNVERIFIED"
    }
    res = client.post(
        "/api/ai-feedback",
        json=payload,
        headers={"Authorization": f"Bearer {farmer_tok}"}
    )
    assert res.status_code == 403
    data = res.json()
    error_msg = str(data.get("error") or data.get("detail", ""))
    assert "forbidden" in error_msg.lower()


def test_feedback_with_lab_confirmed_status(client):
    vet_tok = get_token("veterinarian", "USR-VET-001", "Dr. Rajesh Patel")
    payload = {
        "prediction_id": "PRED-TEST-LAB-01",
        "animal_id": "AN-GJ-2024-0412",
        "model_version": "anicare_vision_bovine_v1",
        "ai_prediction": "Lumpy Skin Disease",
        "ai_confidence": 0.92,
        "veterinary_assessment": "PCR assay positive for Capripoxvirus DNA.",
        "feedback_type": "AI_ACCEPTED",
        "clinical_notes": "State animal health lab real-time PCR Ct=22.4.",
        "evidence_level": "LAB_CONFIRMED",
        "lab_test_name": "Capripox PCR",
        "lab_test_result": "POSITIVE"
    }
    res = client.post(
        "/api/ai-feedback",
        json=payload,
        headers={"Authorization": f"Bearer {vet_tok}"}
    )
    assert res.status_code == 201
    assert res.json()["evidence_level"] == "LAB_CONFIRMED"


# 3. Dataset Provenance, Duplicate Detection & Partition Leakage Tests

def test_quarantine_if_permission_required():
    test_file = Path("backend/uploads/test_cand.jpg")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    if not test_file.exists():
        from PIL import Image
        img = Image.new("RGB", (224, 224), color=(128, 128, 128))
        img.save(test_file)

    res = curation_pipeline.process_feedback_for_curation(
        image_path=str(test_file),
        species="Cattle",
        condition="LSD",
        veterinary_decision="Confirmed",
        clinical_evidence=EvidenceLevel.LAB_CONFIRMED,
        permission_status=PermissionStatus.PERMISSION_REQUIRED,
        license_str="Unknown"
    )
    assert res.success is False
    assert res.is_quarantined is True
    assert "prohibits dataset inclusion" in res.message.lower()


def test_exact_duplicate_detection_sha256():
    test_file = Path("backend/uploads/test_cand.jpg")
    h1 = duplicate_detector.compute_sha256(str(test_file))
    res = duplicate_detector.find_duplicates(
        candidate_sha=h1,
        candidate_dhash=None,
        known_registry=[{"candidate_id": "CAND-001", "sha256": h1}]
    )
    assert res["is_duplicate"] is True
    assert res["match_type"] == "EXACT"


def test_near_duplicate_detection_dhash():
    test_file = Path("backend/uploads/test_cand.jpg")
    dh = duplicate_detector.compute_dhash(str(test_file))
    dist = duplicate_detector.hamming_distance(dh, dh)
    assert dist == 0

    res = duplicate_detector.find_duplicates(
        candidate_sha="different_hash",
        candidate_dhash=dh,
        known_registry=[{"candidate_id": "CAND-002", "perceptual_hash": dh}]
    )
    assert res["is_duplicate"] is True
    assert res["match_type"] == "NEAR_DUPLICATE"


def test_dataset_leakage_guard_rejects_overlap():
    train = [{"sha256": "hash_a", "animal_id": "AN-01"}]
    val = [{"sha256": "hash_b", "animal_id": "AN-02"}]
    test_leak = [{"sha256": "hash_a", "animal_id": "AN-03"}]

    report = dataset_leakage_guard.audit_partitions(train, val, test_leak)
    assert report.has_leakage is True
    assert report.train_test_overlap_count == 1

    with pytest.raises(DataLeakageError):
        dataset_leakage_guard.assert_zero_leakage(train, val, test_leak)


# 4. Statistical Drift Monitoring & Population Stability Index Tests

def test_normal_distribution_drift_report():
    normal_confs = (
        [0.05] * 1 +
        [0.15] * 2 +
        [0.25] * 2 +
        [0.35] * 2 +
        [0.45] * 4 +
        [0.55] * 6 +
        [0.65] * 8 +
        [0.75] * 9 +
        [0.85] * 10 +
        [0.95] * 6
    )
    normal_preds = ["Lumpy Skin Disease"] * 15 + ["Healthy / Normal"] * 35
    report = drift_detector.evaluate_drift(normal_confs, normal_preds)
    assert report.drift_status in [DriftStatus.NORMAL, DriftStatus.WATCH]
    assert report.overall_psi < 0.15
    assert report.current_sample_count == 50


def test_insufficient_samples_drift_safety():
    report = drift_detector.evaluate_drift([0.85, 0.90], ["LSD", "LSD"])
    assert report.drift_status == DriftStatus.NORMAL
    assert "insufficient" in report.interpretation.lower()


def test_demo_drift_simulation_does_not_change_production_model(client):
    prod_before = model_registry.get_production_model()
    assert prod_before.model_id == "anicare_vision_bovine_v1"

    res = client.post(
        "/api/ai-monitoring/drift/simulate-demo",
        json={"simulate_shift": True, "target_status": "WATCH"}
    )
    assert res.status_code == 200

    drift_res = client.get("/api/ai-monitoring/drift")
    assert drift_res.status_code == 200
    assert drift_res.json()["drift_status"] == "WATCH"

    prod_after = model_registry.get_production_model()
    assert prod_after.model_id == "anicare_vision_bovine_v1"
    assert prod_after.status == ModelStatus.PRODUCTION
    assert prod_after.threshold == 0.50

    # Reset
    client.post(
        "/api/ai-monitoring/drift/simulate-demo",
        json={"simulate_shift": False, "target_status": "NORMAL"}
    )


# 5. Pre-Promotion Safety Gates & Production Rollback Governance Tests

def test_promotion_gates_reject_incomplete_model():
    gate_res = model_registry.evaluate_promotion_gates("anicare_vision_bovine_v2", ModelStatus.PRODUCTION)
    assert gate_res.can_promote is False
    assert any("human" in b.lower() or "sign-off" in b.lower() for b in gate_res.blocking_reasons)


def test_farmer_cannot_promote_or_rollback_models(client):
    farmer_tok = get_token("farmer", "USR-FARMER-01", "Ramesh Kumar")
    res1 = client.post(
        "/api/ai-monitoring/models/anicare_vision_bovine_v2/promote",
        json={"promoted_by": "Farmer", "reason": "Self-promotion"},
        headers={"Authorization": f"Bearer {farmer_tok}"}
    )
    assert res1.status_code in [400, 403]

    res2 = client.post(
        "/api/ai-monitoring/models/rollback",
        json={"target_model_id": "anicare_vision_bovine_v1", "reason": "Farmer rollback"},
        headers={"Authorization": f"Bearer {farmer_tok}"}
    )
    assert res2.status_code in [400, 403]


def test_experiment_tracking_comparison():
    comp = experiment_tracker.get_model_comparison("anicare_vision_bovine_v1", "anicare_vision_bovine_v2")
    assert comp.baseline_model_id == "anicare_vision_bovine_v1"
    assert comp.candidate_model_id == "anicare_vision_bovine_v2"
    assert len(comp.metrics_comparison) >= 5
    assert comp.shadow_agreement_rate > 90.0


# 6. Clinical Safety, Domain Boundaries & Image Quality Tests

def test_unsupported_species_triggers_guard():
    report = image_quality_analyzer.analyze_image("backend/uploads/test_cand.jpg", species="Dog")
    assert report.status == "MODEL_NOT_VALIDATED_FOR_SPECIES"
    assert report.is_sufficient is False
    assert "exclusively for cattle" in report.message.lower()


def test_summary_endpoint_reports_production_health(client):
    res = client.get("/api/ai-monitoring/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["production_model"]["model_id"] == "anicare_vision_bovine_v1"
    assert data["production_model"]["is_integrity_valid"] is True
    assert data["production_model"]["threshold"] == 0.50
    assert data["data_quality_summary"]["dataset_b_status"] == "PERMISSION_REQUIRED"
    assert data["is_healthy"] is True
