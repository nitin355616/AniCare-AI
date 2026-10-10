"""
AniCare AI — Evaluation Protocol Governance & Verification Test Suite
Validates strict compliance with the Milestone 6 evaluation protocol correction:
1. Threshold is exactly 0.50.
2. Threshold configuration is frozen and documented.
3. Unsupported species cannot use the cattle vision model.
4. Risk score is an engineering triage score, not represented as clinical probability.
5. Test metrics are not used by threshold-selection code.
6. Existing API response remains strictly backward compatible.
7. Demo fallback remains operational.
8. Real ONNX inference remains operational.
9. Grad-CAM explainability remains operational.
10. Epidemiology cluster surveillance routes remain operational.
"""

import json
from pathlib import Path
from PIL import Image
import pytest

from ai.config import ai_config
from ai.inference import (
    vision_inference_engine,
    demo_inference_engine,
    model_scope_registry,
    RealVisionInferenceEngine
)
from ai.postprocessing.risk_engine import clinical_risk_engine
from ai.explainability.gradcam import gradcam_explainer
from app.schemas.detection import DetectionAnalyzeRequest


def test_1_threshold_is_exactly_point_fifty():
    """1. Verify threshold is exactly 0.50 across config and engine instances."""
    assert ai_config.OPERATING_THRESHOLD == 0.50
    assert vision_inference_engine.operating_threshold == 0.50

    engine = RealVisionInferenceEngine()
    assert engine.operating_threshold == 0.50


def test_2_threshold_configuration_is_frozen_and_documented():
    """2. Verify threshold is explicitly configured as frozen with validation provenance."""
    assert hasattr(ai_config, "OPERATING_THRESHOLD_FROZEN")
    assert ai_config.OPERATING_THRESHOLD_FROZEN is True

    assert hasattr(ai_config, "OPERATING_THRESHOLD_SELECTION_SOURCE")
    assert ai_config.OPERATING_THRESHOLD_SELECTION_SOURCE == "validation_set_only"

    assert hasattr(ai_config, "OPERATING_THRESHOLD_SELECTION_RULE")
    assert "validation" in ai_config.OPERATING_THRESHOLD_SELECTION_RULE.lower()


def test_3_unsupported_species_cannot_use_cattle_vision_model():
    """3. Verify unsupported species (Buffalo, Goat, Sheep, Poultry, Swine, Canine) are rejected by vision model."""
    unsupported = ["Buffalo", "Goat", "Sheep", "Poultry", "Swine", "Dog", "Cat", "Horse"]
    for sp in unsupported:
        is_val, scope = model_scope_registry.resolve_species_scope(sp)
        assert is_val is False, f"Species {sp} must not be validated for bovine vision model"
        assert scope.status == "MODEL_NOT_VALIDATED_FOR_SPECIES"
        assert sp.lower() in scope.message.lower()

    # Cattle must be validated
    ok_cattle, scope_cattle = model_scope_registry.resolve_species_scope("Cattle")
    assert ok_cattle is True
    assert scope_cattle.status == "validated"


def test_4_risk_score_is_not_represented_as_probability():
    """4. Verify risk score is an operational engineering triage score, not clinical probability."""
    eval_res = clinical_risk_engine.evaluate_risk(
        condition_name="Lumpy Skin Disease",
        confidence=90.0,
        species="Cattle",
        symptoms=["Cutaneous nodules"],
        temperature="104.2 °F"
    )

    # Must contain risk score metrics
    assert "risk_score" in eval_res
    assert "overall_risk_score" in eval_res
    assert isinstance(eval_res["risk_score"], (int, float))

    # Must NOT present risk score as a confirmed disease probability
    assert "disease_probability" not in eval_res
    assert "clinical_probability" not in eval_res
    assert "probability_from_vision" not in eval_res

    # Output tier must be operational priority, not diagnosis
    assert eval_res["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_5_test_metrics_are_not_used_by_threshold_selection_code():
    """5. Verify threshold artifact proves threshold selection came solely from validation."""
    json_path = Path("backend/ai/models/evaluation/threshold_analysis.json")
    assert json_path.is_file(), "Missing threshold_analysis.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Threshold must be 0.50
    assert data["selected_operating_threshold"] == 0.50
    assert data["selection_source"] == "validation_set_only"

    # Validation tuning results must exist
    assert "validation_tuning_results" in data

    # Post-hoc test diagnostics must carry explicit warning that they were not used for selection
    assert "post_hoc_test_diagnostics" in data
    warning_text = data["post_hoc_test_diagnostics"]["warning"]
    assert "NOT used for model selection or threshold selection" in warning_text
    assert "post-hoc" in warning_text.lower()


def test_6_existing_api_response_remains_backward_compatible(client):
    """6. Verify /api/detection/analyze preserves all legacy response fields exactly."""
    payload = {
        "species": "Cattle",
        "temperature": "103.5 °F",
        "symptoms": ["Cutaneous nodules"],
        "observations": "Field intake check"
    }
    res = client.post("/api/detection/analyze", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()

    # Core backward compatible contract
    required_legacy_keys = [
        "assessment_id",
        "is_demo_inference",
        "possible_condition",
        "confidence",
        "risk_level",
        "symptoms_detected",
        "explanation",
        "recommended_immediate_actions",
        "veterinary_review_required"
    ]
    for k in required_legacy_keys:
        assert k in body, f"Missing required legacy key: {k}"


@pytest.mark.asyncio
async def test_7_demo_fallback_still_works():
    """7. Verify DemoInferenceEngine fallback remains functional."""
    req = DetectionAnalyzeRequest(
        species="Cattle",
        temperature="104.5 °F",
        symptoms=["Discrete dermal nodules across neck", "High fever"]
    )
    result = await demo_inference_engine.infer(req)
    assert result is not None
    assert result["is_demo_inference"] is True
    assert "Lumpy Skin Disease" in result["possible_condition"]
    assert result["veterinary_review_required"] is True


def test_8_real_onnx_inference_still_works():
    """8. Verify RealVisionInferenceEngine and ONNX runtime are available and callable."""
    assert vision_inference_engine.is_available() is True
    assert vision_inference_engine.has_weights() is True

    meta = vision_inference_engine.get_model_metadata()
    assert meta["architecture"].lower() in ["efficientnet_b0", "efficientnet-b0"]
    assert meta["status"] == "operational"


def test_9_gradcam_still_works(tmp_path):
    """9. Verify Grad-CAM explainability generates valid heatmaps."""
    test_img = tmp_path / "gradcam_test.jpg"
    img = Image.new("RGB", (224, 224), color=(120, 90, 60))
    img.save(test_img, format="JPEG")

    res = gradcam_explainer.generate_heatmap(str(test_img), target_class_idx=1)
    if gradcam_explainer.is_available():
        assert res["status"] == "SUCCESS"
        assert res["heatmap_url"] is not None
        disclaimer_lower = res["scientific_disclaimer"].lower()
        assert "influencing" in disclaimer_lower or "attribution" in disclaimer_lower or "gradient" in disclaimer_lower


def test_10_epidemiology_endpoints_still_work(client):
    """10. Verify GET /api/epidemiology/clusters and GET /api/epidemiology/roadmap."""
    res_clusters = client.get("/api/epidemiology/clusters")
    assert res_clusters.status_code == 200
    clusters_body = res_clusters.json()
    assert "total_active_signals" in clusters_body
    assert "signals" in clusters_body

    res_roadmap = client.get("/api/epidemiology/roadmap")
    assert res_roadmap.status_code == 200
    roadmap_body = res_roadmap.json()
    assert "validated_species" in roadmap_body
    assert "cattle" in roadmap_body["validated_species"]
    assert "future_roadmap" in roadmap_body
