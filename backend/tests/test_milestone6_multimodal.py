"""
AniCare AI — Milestone 6 Automated Test Suite
Verifies:
1. Error taxonomy & false negative audit integrity
2. Validation threshold analysis
3. Multi-modal clinical risk engine & escalation rules
4. Spatial-temporal cluster detector & early-warning service
5. Multi-species architectural guard
6. Tiled multi-crop preprocessor
7. Grad-CAM visual explainability
8. API backward-compatibility and new endpoints
"""

import os
import json
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from backend.ai.evaluation.error_taxonomy import FailureCategory, FAILURE_CATEGORY_DESCRIPTIONS
from backend.ai.postprocessing.risk_engine import clinical_risk_engine
from backend.ai.epidemiology.cluster_detector import cluster_detector
from backend.ai.epidemiology.outbreak_risk import outbreak_risk_evaluator
from backend.ai.epidemiology.early_warning import early_warning_service
from backend.ai.inference.model_scope import model_scope_registry
from backend.ai.preprocessing.tiled_preprocessor import tiled_preprocessor
from backend.ai.explainability.gradcam import gradcam_explainer
from backend.app.schemas.detection import DetectionAnalyzeRequest


def test_error_taxonomy_completeness():
    """1. Verify error taxonomy covers all required failure categories."""
    required_cats = [
        "EARLY_SUBTLE_PAPULES",
        "SMALL_LESION_AREA",
        "DISTANT_WHOLE_ANIMAL_FRAMING",
        "MUD_DEBRIS_OBSTRUCTION",
        "POOR_LIGHTING",
        "OCCLUSION",
        "BACKGROUND_COMPLEXITY",
        "IMAGE_QUALITY",
        "UNKNOWN_VISUAL_FAILURE"
    ]
    for c in required_cats:
        assert hasattr(FailureCategory, c)
        enum_val = getattr(FailureCategory, c)
        assert enum_val in FAILURE_CATEGORY_DESCRIPTIONS


def test_false_negative_audit_report_exists():
    """2. Verify FALSE_NEGATIVE_ANALYSIS.md and audit JSON are generated and populated."""
    md_path = Path("backend/ai/models/evaluation/FALSE_NEGATIVE_ANALYSIS.md")
    json_path = Path("backend/ai/models/evaluation/false_negative_audit.json")

    assert md_path.is_file(), "Missing FALSE_NEGATIVE_ANALYSIS.md"
    assert json_path.is_file(), "Missing false_negative_audit.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_false_negatives"] == 8
    assert len(data["records"]) == 8
    for r in data["records"]:
        assert r["true_class"] == "Lumpy Skin Disease"
        assert r["predicted_class"] == "Healthy / Normal"
        assert r["failure_category"] in [c.value for c in FailureCategory]


def test_validation_threshold_analysis_integrity():
    """3. Verify threshold analysis is validation-only and produces structured metrics."""
    json_path = Path("backend/ai/models/evaluation/threshold_analysis.json")
    assert json_path.is_file()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["candidate_thresholds"]) >= 7
    assert "validation_tuning_results" in data
    assert "selected_operating_threshold" in data
    assert "test_comparison" in data

    # Check that recall increases as threshold drops
    results = data["validation_tuning_results"]
    r_30 = next(r["lsd_recall"] for r in results if r["threshold"] == 0.30)
    r_70 = next(r["lsd_recall"] for r in results if r["threshold"] == 0.70)
    assert r_30 >= r_70


def test_multi_modal_clinical_risk_engine_modalities():
    """4. Verify multi-modal risk engine calculates transparent scores across all 5 modalities."""
    eval_res = clinical_risk_engine.evaluate_risk(
        condition_name="Lumpy Skin Disease",
        confidence=85.0,
        species="Cattle",
        symptoms=["Cutaneous nodules", "Enlarged lymph nodes"],
        temperature="104.2 °F",
        appetite="Reduced",
        activity_level="Lethargic",
        breathing_condition="Rapid",
        vaccination_status="UNVACCINATED",
        recent_nearby_cases=3,
        cluster_warning_active=True
    )

    # Check all 5 modality scores exist
    assert "visual_risk_score" in eval_res
    assert "symptom_risk_score" in eval_res
    assert "physiological_risk_score" in eval_res
    assert "epidemiological_risk_score" in eval_res
    assert "history_risk_score" in eval_res
    assert "overall_risk_score" in eval_res

    assert eval_res["risk_level"] in ["HIGH", "CRITICAL"]
    assert eval_res["veterinary_review_required"] is True
    assert len(eval_res["contributing_factors"]) >= 3
    assert len(eval_res["risk_reasoning_list"]) >= 3


def test_physiological_and_symptom_critical_escalation():
    """5. Verify severe fever + cutaneous nodules trigger critical escalation override."""
    crit_eval = clinical_risk_engine.evaluate_risk(
        condition_name="Healthy / Normal",  # Even if vision returned healthy!
        confidence=90.0,
        species="Cattle",
        symptoms=["Cutaneous nodules on neck"],
        temperature="105.4 °F"  # Severe hyperpyrexia
    )

    # Overrides to CRITICAL due to severe hyperpyrexia and cutaneous lesion
    assert crit_eval["risk_level"] == "CRITICAL"
    assert crit_eval["overall_risk_score"] >= 85.0
    assert "SEVERE_HYPERPYREXIA" in crit_eval["escalation_flags"]


def test_species_validation_guard():
    """6. Verify species guard approves Cattle and rejects unvalidated species safely."""
    # Supported
    ok_cattle, def_cattle = model_scope_registry.resolve_species_scope("Cattle")
    assert ok_cattle is True
    assert def_cattle.status == "validated"

    ok_cow, def_cow = model_scope_registry.resolve_species_scope("Cow")
    assert ok_cow is True

    # Unsupported species
    for unk in ["Goat", "Poultry", "Dog", "Pig", "Buffalo"]:
        is_val, scope_def = model_scope_registry.resolve_species_scope(unk)
        assert is_val is False
        assert scope_def.status == "MODEL_NOT_VALIDATED_FOR_SPECIES"
        assert unk.lower() in scope_def.message.lower()


def test_spatial_temporal_cluster_detection():
    """7. Verify cluster detector flags 3+ at-risk animals in same village/window."""
    # Under-threshold (2 animals) -> No cluster
    few_assessments = [
        {"assessment_id": "A1", "animal_id": "C1", "species": "Cattle", "possible_condition": "Lumpy Skin Disease",
         "district": "Anand", "village": "Boriavi", "risk_level": "HIGH", "risk_score": 75.0, "created_at": "2026-10-01T10:00:00Z"},
        {"assessment_id": "A2", "animal_id": "C2", "species": "Cattle", "possible_condition": "Lumpy Skin Disease",
         "district": "Anand", "village": "Boriavi", "risk_level": "HIGH", "risk_score": 78.0, "created_at": "2026-10-02T10:00:00Z"}
    ]
    assert len(cluster_detector.detect_clusters(few_assessments)) == 0

    # Over-threshold (3 animals) -> Triggers cluster
    few_assessments.append(
        {"assessment_id": "A3", "animal_id": "C3", "species": "Cattle", "possible_condition": "Lumpy Skin Disease",
         "district": "Anand", "village": "Boriavi", "risk_level": "MODERATE", "risk_score": 55.0, "created_at": "2026-10-03T10:00:00Z"}
    )
    clusters = cluster_detector.detect_clusters(few_assessments)
    assert len(clusters) == 1
    assert clusters[0].total_animals == 3
    assert clusters[0].signal_status == "POSSIBLE_CLUSTER"
    assert clusters[0].district == "Anand"
    assert clusters[0].village_or_town == "Boriavi"


def test_early_warning_dashboard_feed():
    """8. Verify early warning service feed combines live and simulated demo clusters."""
    feed = early_warning_service.get_dashboard_early_warning_feed()
    assert feed["total_active_signals"] >= 2
    assert feed["simulated_demo_count"] >= 2
    assert "disclaimer" in feed

    # Verify signals contain all required fields
    for s in feed["signals"]:
        assert s["signal_type"] == "EARLY_WARNING_SIGNAL"
        assert "affected_animals" in s
        assert "recommended_veterinary_action" in s
        assert "containment_protocol" in s


def test_tiled_preprocessor_multi_crop(tmp_path):
    """9. Verify multi-crop preprocessor extracts 5 valid normalized tensors."""
    sample_img = tmp_path / "crop_test.jpg"
    img = Image.new("RGB", (400, 300), color=(120, 90, 60))
    img.save(sample_img, format="JPEG")

    crops, meta = tiled_preprocessor.extract_crops(str(sample_img))
    assert len(crops) == 6  # Global + center + 4 quadrants
    assert meta["original_dimensions"] == [400, 300]
    for c in crops:
        assert c.shape == (1, 3, 224, 224)

    # Test aggregation formula
    agg = tiled_preprocessor.aggregate_crop_predictions([0.30, 0.40, 0.50, 0.60, 0.70])
    assert "final_prob" in agg
    assert "max_patch_prob" in agg
    assert agg["max_patch_prob"] == 0.70
    assert agg["global_prob"] == 0.30


def test_gradcam_explainer(tmp_path):
    """10. Verify Grad-CAM generates heatmap overlay on valid image."""
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


def test_api_epidemiology_routes(client):
    """11. Verify new epidemiology API routes."""
    res1 = client.get("/api/epidemiology/clusters")
    assert res1.status_code == 200, res1.text
    d1 = res1.json()
    assert "total_active_signals" in d1
    assert "signals" in d1

    res2 = client.get("/api/epidemiology/roadmap")
    assert res2.status_code == 200, res2.text
    d2 = res2.json()
    assert "cattle" in d2["validated_species"]
    assert "future_roadmap" in d2


def test_api_multi_modal_detection_analyze(client):
    """12. Verify /api/detection/analyze handles multi-modal parameters and preserves backward compatibility."""
    payload = {
        "species": "Cattle",
        "temperature": "104.5 °F",
        "appetite": "Severely Reduced",
        "activity_level": "Lethargic",
        "symptoms": ["Circumscribed nodules on flank", "Fever"],
        "heart_rate": 84.0,
        "respiratory_rate": 44.0,
        "vaccination_status": "UNVACCINATED",
        "recent_nearby_cases": 2,
        "cluster_warning_active": True
    }

    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    # Core backward-compatible fields
    assert "possible_condition" in data
    assert "confidence" in data
    assert "risk_level" in data
    assert "symptoms_detected" in data
    assert data["veterinary_review_required"] is True

    # Multi-modal extensions
    assert "visual_risk_score" in data
    assert "symptom_risk_score" in data
    assert "physiological_risk_score" in data
    assert "epidemiological_risk_score" in data
    assert "history_risk_score" in data
    assert "overall_risk_score" in data
    assert "model_scope" in data
    assert data["model_scope"]["status"] == "validated"


def test_api_unsupported_species_safe_routing(client):
    """13. Verify requesting unvalidated species (e.g. Goat) safely routes with model scope notice."""
    payload = {
        "species": "Goat",
        "temperature": "103.8 °F",
        "symptoms": ["Papular crusts on lips"],
        "observations": "Caprine flock check"
    }

    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["is_demo_inference"] is True
    assert "model_scope" in data
    assert data["model_scope"]["status"] == "MODEL_NOT_VALIDATED_FOR_SPECIES"
    assert "SPECIES NOTICE" in data["disclaimer"]
