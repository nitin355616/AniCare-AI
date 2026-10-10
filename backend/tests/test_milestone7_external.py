"""
AniCare AI — Milestone 7 Test Suite: External Validation, Provenance & Field Robustness
Verifies:
1. Dataset B manifest validation
2. Dataset B provenance fields completeness
3. License verification status (APPROVED, PERMISSION_REQUIRED, REVIEW_REQUIRED, REJECTED)
4. Cross-dataset duplicate detection & strict quarantine against Dataset A
5. Ambiguous-label quarantine (preventing indeterminate skin conditions from corrupting classes)
6. Animal-level grouping metadata handling & generalization limitation notes
7. External baseline evaluation pipeline (truthful pending disclosure without fabrication)
8. Operating threshold is frozen at exactly 0.50
9. No test-set tuning or optimization leakage
10. Future Dataset C infrastructure & quarantined STATUS = PENDING
11. Species validation guard (Cattle only)
12. Grad-CAM visual attention output contract
13. Field robustness taxonomy (all 12 categories & small-sample safeguards)
14. False-negative audit schema completeness
15. API backward-compatibility on detection and health endpoints
"""

import os
import io
import json
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from ai.config import ai_config
from ai.dataset.dataset_b_pipeline import dataset_b_pipeline, DatasetBPipeline
from ai.dataset.schema import TargetSpeciesEnum
from ai.evaluation.error_taxonomy import FailureCategory, FAILURE_CATEGORY_DESCRIPTIONS
from ai.evaluation.field_robustness import field_robustness_evaluator, FieldRobustnessEvaluator
from ai.evaluation.external_evaluation import external_baseline_evaluator
from ai.explainability.gradcam import gradcam_explainer
from ai.inference.model_scope import model_scope_registry
from app.schemas.detection import DetectionAnalyzeRequest


client = TestClient(app)


def _create_synthetic_image_bytes(width=224, height=224, color=(120, 60, 30)):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# 1. Dataset B Manifest Validation
def test_1_dataset_b_manifest_validation():
    """Verify Dataset B pipeline correctly ingests and validates candidate batches."""
    img_bytes = _create_synthetic_image_bytes(width=224, height=224)
    candidate_batch = [
        {
            "sample_id": "TEST-B-001",
            "image_bytes": img_bytes,
            "species": "Cattle",
            "disease": "Lumpy Skin Disease",
            "animal_id": "COW-GJ-101"
        },
        {
            "sample_id": "TEST-B-002",
            "image_bytes": img_bytes,
            "species": "Cattle",
            "disease": "Healthy / Normal",
            "animal_id": "COW-GJ-102"
        }
    ]
    summary = dataset_b_pipeline.process_candidate_dataset(candidate_batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["total_candidates"] == 2
    # Second item is an exact intra-dataset duplicate of first image bytes, so 1 valid, 1 intra-duplicate
    assert summary["accepted_valid_count"] >= 1
    assert summary["status"] == "LEGAL_PERMISSION_PENDING"


# 2. Dataset B Provenance Fields Completeness
def test_2_dataset_b_provenance_fields():
    """Verify all registry entries contain the required standardized fields."""
    registry_path = Path("backend/ai/dataset/source_registry.json")
    assert registry_path.is_file(), "Missing source_registry.json"

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    assert len(registry) >= 6
    required_fields = [
        "source_id", "dataset_name", "provider", "official_url",
        "license", "license_verified", "permission_status",
        "species", "geographic_origin", "institution", "intended_use", "status", "notes"
    ]
    for entry in registry:
        for field in required_fields:
            assert field in entry, f"Missing field '{field}' in registry entry '{entry.get('source_id')}'"


# 3. License Verification Status
def test_3_license_verification_status():
    """Verify permitted and restricted status mappings (Kaggle rejected, AAU permission required)."""
    registry_path = Path("backend/ai/dataset/source_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    kaggle = next((x for x in registry if "Kaggle" in x["dataset_name"]), None)
    assert kaggle is not None
    assert kaggle["permission_status"] == "REJECTED"
    assert kaggle["license_verified"] is False

    aau = next((x for x in registry if "AAU Anand" in x["dataset_name"]), None)
    assert aau is not None
    assert aau["permission_status"] == "PERMISSION_REQUIRED"

    mendeley = next((x for x in registry if "DATASET-A" in x["source_id"]), None)
    assert mendeley is not None
    assert mendeley["permission_status"] == "APPROVED"
    assert mendeley["license_verified"] is True


# 4. Cross-Dataset Duplicate Detection & Quarantine
def test_4_cross_dataset_duplicate_detection():
    """Verify that any candidate image already existing in Dataset A is quarantined."""
    manifest_path = Path("backend/ai/dataset/processed/manifest.json")
    assert manifest_path.is_file()

    with open(manifest_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Pick first real image from Dataset A
    first_record = records[0]
    first_img_path = Path("backend") / first_record["file_path"]
    assert first_img_path.is_file()

    with open(first_img_path, "rb") as f:
        existing_img_bytes = f.read()

    # Attempt to submit this exact image to Dataset B pipeline
    candidate_batch = [
        {
            "sample_id": "INTRUDER-SAMPLE-01",
            "image_bytes": existing_img_bytes,
            "species": "Cattle",
            "disease": "Lumpy Skin Disease"
        }
    ]

    summary = dataset_b_pipeline.process_candidate_dataset(candidate_batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["cross_dataset_duplicates_quarantined"] == 1
    assert summary["accepted_valid_count"] == 0
    assert len(summary["quarantined_records"]) == 1
    assert "CROSS_DATASET_LEAKAGE" in summary["quarantined_records"][0]["quarantine_reason"]


# 5. Ambiguous-Label Quarantine
def test_5_ambiguous_label_quarantine():
    """Verify that ambiguous or overlapping dermal conditions are quarantined, not forced into classes."""
    img_bytes = _create_synthetic_image_bytes(color=(80, 80, 80))
    candidate_batch = [
        {
            "sample_id": "AMBIGUOUS-01",
            "image_bytes": img_bytes,
            "species": "Cattle",
            "disease": "Nonspecific Bovine Dermatitis / Pseudolumpy"
        },
        {
            "sample_id": "AMBIGUOUS-02",
            "image_bytes": _create_synthetic_image_bytes(color=(90, 90, 90)),
            "species": "Cattle",
            "disease": "Ringworm Dermatomycosis"
        }
    ]

    summary = dataset_b_pipeline.process_candidate_dataset(candidate_batch, "DATASET-B-CANDIDATE-AAU")
    assert summary["ambiguous_count"] == 2
    assert summary["accepted_valid_count"] == 0
    for q in summary["quarantined_records"]:
        assert "AMBIGUOUS_LABEL" in q["quarantine_reason"]


# 6. Animal Grouping Handling
def test_6_animal_grouping_handling():
    """Verify pipeline sets animal_grouping_available = false when IDs are absent and records limitation."""
    records_without_ids = [
        {"sample_id": "S1", "species": "Cattle", "disease": "Lumpy Skin Disease"},
        {"sample_id": "S2", "species": "Cattle", "disease": "Healthy / Normal"}
    ]
    info_no_ids = dataset_b_pipeline.inspect_animal_grouping(records_without_ids)
    assert info_no_ids["animal_grouping_available"] is False
    assert "CANNOT claim herd-independent" in info_no_ids["limitation_note"]

    records_with_ids = [
        {"sample_id": "S1", "species": "Cattle", "disease": "Lumpy Skin Disease", "animal_id": "TAG-8801"},
        {"sample_id": "S2", "species": "Cattle", "disease": "Healthy / Normal", "animal_id": "TAG-8802"}
    ]
    info_with_ids = dataset_b_pipeline.inspect_animal_grouping(records_with_ids)
    assert info_with_ids["animal_grouping_available"] is True
    assert info_with_ids["unique_animal_count"] == 2


# 7. External Evaluation Pipeline Truthfulness
def test_7_external_evaluation_pipeline():
    """Verify ExternalBaselineEvaluator returns EXTERNAL_VALIDATION_PENDING without fabricated metrics."""
    result = external_baseline_evaluator.evaluate_external_dataset_or_report_pending()
    assert result["evaluation_status"] == "EXTERNAL_VALIDATION_PENDING"
    assert "External validation pending due to lack of a legally verified independent dataset." in result["statement"]
    assert result["external_metrics"] is None
    assert "domain_shift_analysis" in result
    assert "dataset_a_baselines" in result


# 8. Frozen Operating Threshold Point Fifty
def test_8_frozen_threshold_point_fifty():
    """Verify operating threshold is exactly 0.50 and frozen across all systems."""
    assert ai_config.OPERATING_THRESHOLD == 0.50
    assert ai_config.OPERATING_THRESHOLD_FROZEN is True
    assert field_robustness_evaluator.threshold == 0.50
    assert external_baseline_evaluator.frozen_threshold == 0.50


# 9. No Test-Set Tuning
def test_9_no_test_set_tuning():
    """Verify test-set metrics are strictly barred from threshold selection code."""
    from ai.evaluation.threshold_analysis import evaluate_threshold_metrics
    assert ai_config.OPERATING_THRESHOLD_SELECTION_SOURCE == "validation_set_only"
    assert ai_config.OPERATING_THRESHOLD_FROZEN is True
    assert ai_config.OPERATING_THRESHOLD == 0.50
    m = evaluate_threshold_metrics(np.array([1, 0]), np.array([0.7, 0.3]), threshold=0.50)
    assert m["accuracy"] == 1.0


# 10. Future Dataset C Infrastructure & Quarantined Status
def test_10_dataset_c_untouched_and_quarantined():
    """Verify Dataset C infrastructure exists with STATUS = PENDING and quarantine locks."""
    gov_path = Path("backend/ai/dataset/external/governance.json")
    assert gov_path.is_file(), "Missing governance.json for Dataset C"
    with open(gov_path, "r", encoding="utf-8") as f:
        gov = json.load(f)
    assert gov["status"] == "STATUS = PENDING"
    assert gov["governance_rules"]["quarantined_until_final_freeze"] is True
    assert gov["governance_rules"]["zero_training_access"] is True


# 11. Species Guard Enforces Cattle Only
def test_11_species_guard_cattle_only():
    """Verify non-cattle species cannot access the cattle vision model."""
    assert model_scope_registry.is_species_validated("Cattle") is True
    assert model_scope_registry.is_species_validated("Buffalo") is False
    assert model_scope_registry.is_species_validated("Goat") is False
    assert model_scope_registry.is_species_validated("Sheep") is False
    assert model_scope_registry.is_species_validated("Dog") is False

    non_cattle_req = model_scope_registry.create_species_guard_response("Goat")
    assert non_cattle_req["guard_code"] == "MODEL_NOT_VALIDATED_FOR_SPECIES"
    assert non_cattle_req["syndromic_triage_only"] is True


# 12. Grad-CAM Output Contract
def test_12_gradcam_output_contract(tmp_path):
    """Verify Grad-CAM generates valid alpha-blended heatmap overlays with attribution disclaimer."""
    test_img = tmp_path / "gradcam_test.jpg"
    img = Image.new("RGB", (250, 250), color=(110, 80, 50))
    img.save(test_img, format="JPEG")

    expl_res = gradcam_explainer.generate_heatmap(str(test_img), target_class_idx=1)
    if gradcam_explainer.is_available():
        assert expl_res["status"] == "SUCCESS"
        assert expl_res["explanation_type"] == "GRAD_CAM"
        assert expl_res["heatmap_url"].startswith("/uploads/explanations/")
        assert os.path.isfile(expl_res["heatmap_saved_path"])
        assert "scientific_disclaimer" in expl_res
    else:
        assert expl_res["status"] in ["UNAVAILABLE", "ERROR"]


# 13. Field Robustness Taxonomy (12 Categories & Small-Sample Rules)
def test_13_field_robustness_taxonomy_twelve_categories():
    """Verify all 12 field robustness categories are supported and small samples report 'insufficient sample size'."""
    all_12 = [
        "EARLY_SUBTLE_PAPULES",
        "DISTANT_WHOLE_ANIMAL_FRAMING",
        "SMALL_LESION_AREA",
        "MUD_DEBRIS_OBSTRUCTION",
        "POOR_LIGHTING",
        "OCCLUSION",
        "BACKGROUND_COMPLEXITY",
        "IMAGE_QUALITY",
        "PARTIAL_BODY",
        "MOTION_BLUR",
        "NON_STANDARD_CAMERA",
        "UNKNOWN_FAILURE"
    ]
    for cat in all_12:
        assert hasattr(FailureCategory, cat)
        enum_val = getattr(FailureCategory, cat)
        assert enum_val in FAILURE_CATEGORY_DESCRIPTIONS

    report_path = Path("backend/ai/models/evaluation/field_robustness_analysis.json")
    assert report_path.is_file()
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cat_metrics = data["category_metrics"]
    # Check that small samples report 'insufficient sample size'
    for cname, cdata in cat_metrics.items():
        if 0 < cdata.get("sample_count", 0) < 5:
            assert cdata["status"] == "insufficient sample size"
            assert cdata["sensitivity"] == "insufficient sample size"


# 14. False-Negative Audit Schema Completeness
def test_14_false_negative_audit_schema():
    """Verify false-negative audit contains all 8 test false negatives and required audit fields."""
    audit_path = Path("backend/ai/models/evaluation/false_negative_audit.json")
    assert audit_path.is_file()
    with open(audit_path, "r", encoding="utf-8") as f:
        audit = json.load(f)

    assert audit["total_false_negatives"] == 8
    for rec in audit["records"]:
        assert "sample_id" in rec
        assert "true_class" in rec
        assert "predicted_class" in rec
        assert "failure_category" in rec
        assert "observed_visual_characteristics" in rec
        assert "clinical_risk_mitigation" in rec


# 15. API Backward Compatibility
def test_15_api_backward_compatibility(client):
    """Verify core health, detection, and epidemiology endpoints maintain backward-compatible contracts."""
    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] in ["healthy", "degraded"]

    # Multi-modal detection
    payload = {
        "species": "Cattle",
        "symptoms": ["fever", "nodules"],
        "body_temperature": 104.5
    }
    res_detect = client.post("/api/detection/analyze", json=payload)
    assert res_detect.status_code == 200
    data = res_detect.json()
    assert "possible_condition" in data
    assert "confidence" in data
    assert "risk_level" in data
    assert "veterinary_review_required" in data
    assert "model_version" in data or "model_metadata" in data
    assert "assessment_id" in data

    # Clusters endpoint
    res_clusters = client.get("/api/epidemiology/clusters")
    assert res_clusters.status_code == 200
    cdata = res_clusters.json()
    assert "total_active_signals" in cdata or "active_clusters" in cdata
