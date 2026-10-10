"""
AniCare AI — Milestone 8B Test Suite: Controlled Model Robustness Improvement
Tests:
1. Experiment registry integrity & schema (6 experiments, EXP-01 to EXP-06)
2. Baseline Model V1 lock protection & cryptographic hash parity
3. Dataset split protection & zero-leakage cross-split verification (Train: 633, Val: 135, Test: 138)
4. Validation-only candidate selection guard (raises TestSetTuningError on test keys)
5. Validation-only threshold selection guard (enforces validation threshold tau=0.50)
6. Data leakage error enforcement (DataLeakageError raised on split collision)
7. Operating threshold immutability at tau = 0.50
8. Calibration metric calculation correctness (ECE bounds [0, 1])
9. Official held-out test evaluation benchmarks (Sensitivity 80.95%, Specificity 97.92%, N=138)
10. Scientific decision rule execution (Delta < 2.0% -> V1_RETAINED)
11. Grad-CAM review artifact verification (TP, FN, TN, FP generated and localized)
12. Production model versioning integrity (AniCare-Bovine-Vision v1.0 active, 15.29 MB)
13. Unsupported species routing guard (MODEL_NOT_VALIDATED_FOR_SPECIES)
14. Dataset B quarantine & zero-usage invariant (PERMISSION_REQUIRED)
15. Milestone 8B comprehensive report verification (19 sections present)
16. Live FastAPI detection API backward-compatibility (POST /api/detection/analyze)
"""

import io
import json
import hashlib
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from ai.config import ai_config
from ai.training.safeguards import (
    verify_no_test_leakage,
    select_best_model_validation_only,
    select_threshold_validation_only,
    TestSetTuningError,
    DataLeakageError
)
from ai.inference.vision_engine import vision_inference_engine
from ai.dataset.external.permission_registry import PermissionRegistry, PermissionState
from ai.dataset.external.provenance import provenance_registry

BACKEND_DIR = Path(__file__).resolve().parent.parent

def _generate_synthetic_image_bytes(width=224, height=224, color=(120, 80, 50)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# 1. Experiment Registry Integrity & Schema
def test_1_experiment_registry_integrity():
    experiments_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "model_improvement_experiments.json"
    assert experiments_file.is_file(), "model_improvement_experiments.json must exist"

    with open(experiments_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "Milestone 8B — Controlled Model Robustness Improvement"
    assert "splits" in data
    assert data["splits"]["train_count"] == 633
    assert data["splits"]["validation_count"] == 135
    assert data["splits"]["held_out_test_count"] == 138

    experiments = data["experiments"]
    assert len(experiments) == 6, "Must record exactly 6 experiments (EXP-01 through EXP-06)"
    exp_ids = [e["experiment_id"] for e in experiments]
    expected_ids = [
        "EXP-01-BASELINE-V1",
        "EXP-02-ROBUST-AUG",
        "EXP-03-MULTI-SCALE-TILING",
        "EXP-04-HIRES-256",
        "EXP-05-WEIGHTED-CE",
        "EXP-06-ROBUST-HIRES-FOCAL"
    ]
    assert exp_ids == expected_ids
    assert data["winning_candidate_id"] == "EXP-06-ROBUST-HIRES-FOCAL"
    assert data["production_decision"]["decision"] == "V1_RETAINED"


# 2. Baseline Model V1 Lock Protection
def test_2_baseline_v1_lock_protection():
    lock_file = BACKEND_DIR / "ai" / "models" / "experiments" / "baseline_v1" / "baseline_lock.json"
    assert lock_file.is_file(), "baseline_lock.json must exist"

    with open(lock_file, "r", encoding="utf-8") as f:
        lock_data = json.load(f)

    assert "IMMUTABLE" in lock_data["status"] or "LOCKED" in lock_data["status"]
    assert lock_data["operating_threshold"] == 0.50
    assert lock_data["protection"] == "READ_ONLY_LOCK"

    # Verify SHA-256 matches production model
    prod_onnx = BACKEND_DIR / "ai" / "models" / "weights" / "anicare_vision_bovine_v1.onnx"
    locked_onnx = BACKEND_DIR / "ai" / "models" / "experiments" / "baseline_v1" / "anicare_vision_bovine_v1.onnx"
    assert prod_onnx.is_file() and locked_onnx.is_file()

    with open(prod_onnx, "rb") as f:
        prod_hash = hashlib.sha256(f.read()).hexdigest()
    with open(locked_onnx, "rb") as f:
        locked_hash = hashlib.sha256(f.read()).hexdigest()

    assert prod_hash == locked_hash, "Locked baseline ONNX hash must match production weights"


# 3. Dataset Split Protection & Zero-Leakage
def test_3_dataset_split_protection():
    manifest_path = BACKEND_DIR / "ai" / "dataset" / "processed" / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_ids = {r["image_id"] for r in manifest if r["split"] == "train"}
    val_ids = {r["image_id"] for r in manifest if r["split"] == "validation"}
    test_ids = {r["image_id"] for r in manifest if r["split"] == "test"}

    assert len(train_ids) == 633
    assert len(val_ids) == 135
    assert len(test_ids) == 138

    # Ensure zero overlap
    assert len(train_ids.intersection(val_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(val_ids.intersection(test_ids)) == 0

    # Safeguards validator
    leakage_result = verify_no_test_leakage(train_ids, val_ids, test_ids)
    assert leakage_result is True


# 4. Validation-Only Candidate Selection Safeguard
def test_4_validation_only_candidate_selection():
    mock_candidates = [
        {"id": "MOCK-01", "val_sensitivity": 0.85, "val_specificity": 0.95, "val_macro_f1": 0.89},
        {"id": "MOCK-02", "val_sensitivity": 0.925, "val_specificity": 0.95, "val_macro_f1": 0.938}
    ]

    best = select_best_model_validation_only(mock_candidates)
    assert best["id"] == "MOCK-02"

    # Enforce TestSetTuningError if test metrics leaked into selection
    leaked_candidates = [
        {"id": "LEAKED-01", "val_sensitivity": 0.90, "test_sensitivity": 0.95}
    ]
    with pytest.raises(TestSetTuningError):
        select_best_model_validation_only(leaked_candidates)


# 5. Validation-Only Threshold Selection Safeguard
def test_5_validation_only_threshold_selection():
    mock_val_probs = [0.8, 0.9, 0.7, 0.2, 0.1, 0.3]
    mock_val_targets = [1, 1, 1, 0, 0, 0]

    res = select_threshold_validation_only(mock_val_targets, mock_val_probs, partition="validation")
    assert 0.30 <= res["selected_threshold"] <= 0.70
    assert res["selection_partition"] == "validation_set_only"

    # Enforce error if partition indicates test set
    with pytest.raises(TestSetTuningError):
        select_threshold_validation_only(mock_val_targets, mock_val_probs, partition="test")


# 6. Data Leakage Error Enforcement
def test_6_data_leakage_error_enforcement():
    set_a = {"IMG_001", "IMG_002"}
    set_b = {"IMG_003"}
    set_c = {"IMG_002"}  # Leaked test sample into set_a

    with pytest.raises(DataLeakageError):
        verify_no_test_leakage(set_a, set_b, set_c)


# 7. Operating Threshold Immutability at 0.50
def test_7_operating_threshold_immutability():
    assert vision_inference_engine.operating_threshold == 0.50
    assert ai_config.OPERATING_THRESHOLD == 0.50


# 8. Calibration Metric Correctness
def test_8_calibration_metric_bounds():
    experiments_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "model_improvement_experiments.json"
    with open(experiments_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for exp in data["experiments"]:
        ece = exp["validation_metrics"]["ece"]
        assert 0.0 <= ece <= 1.0, f"ECE must be bounded in [0, 1], got {ece}"


# 9. Official Held-Out Test Evaluation Benchmarks
def test_9_held_out_test_evaluation_benchmarks():
    experiments_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "model_improvement_experiments.json"
    with open(experiments_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_eval = data["final_held_out_test_evaluation"]
    metrics = test_eval["metrics"]
    assert test_eval["test_sample_count"] == 138
    assert metrics["sensitivity"] == 0.8095
    assert metrics["specificity"] == 0.9792
    assert metrics["precision"] == 0.9444
    assert metrics["macro_f1"] == 0.9106
    assert metrics["confusion_matrix"]["TP"] == 34
    assert metrics["confusion_matrix"]["FN"] == 8
    assert metrics["confusion_matrix"]["TN"] == 94
    assert metrics["confusion_matrix"]["FP"] == 2


# 10. Scientific Decision Rule Execution
def test_10_scientific_decision_rule_execution():
    experiments_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "model_improvement_experiments.json"
    with open(experiments_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    baseline_sens = data["baseline_v1_test_benchmark"]["sensitivity"]
    v2_sens = data["final_held_out_test_evaluation"]["metrics"]["sensitivity"]
    delta_sens = v2_sens - baseline_sens

    # Under strict governance: delta < 0.02 -> reject V2, retain V1
    assert delta_sens < 0.02
    assert data["production_decision"]["decision"] == "V1_RETAINED"
    assert data["production_decision"]["active_production_model"] == "AniCare-Bovine-Vision v1.0"


# 11. Grad-CAM Review Artifact Verification
def test_11_gradcam_review_artifacts():
    gradcam_file = BACKEND_DIR / "ai" / "models" / "evaluation" / "gradcam_case_review.json"
    assert gradcam_file.is_file(), "gradcam_case_review.json must exist"

    with open(gradcam_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    assert len(cases) == 4, "Must contain 4 case reviews (TP, FN, TN, FP)"
    case_types = {c["case_type"] for c in cases}
    assert case_types == {"TP", "FN", "TN", "FP"}

    for case in cases:
        assert case["status"] == "SUCCESS"
        assert case["heatmap_filename"] is not None
        # Verify file exists on disk in uploads/explanations
        saved_file = BACKEND_DIR / "uploads" / "explanations" / case["heatmap_filename"]
        assert saved_file.is_file(), f"Grad-CAM heatmap {saved_file} must exist"


# 12. Production Model Versioning Integrity
def test_12_production_model_versioning_integrity():
    assert "v1.0" in vision_inference_engine.model_version
    assert vision_inference_engine.architecture.lower() == "efficientnet_b0"
    assert "Cattle" in ai_config.TARGET_SPECIES

    onnx_file = BACKEND_DIR / "ai" / "models" / "weights" / "anicare_vision_bovine_v1.onnx"
    assert onnx_file.is_file()
    assert abs(onnx_file.stat().st_size / (1024 * 1024) - 15.29) < 0.10


# 13. Unsupported Species Routing Guard
def test_13_unsupported_species_routing(client):
    from ai.inference.model_scope import model_scope_registry
    is_val, scope = model_scope_registry.resolve_species_scope("Goat")
    assert is_val is False
    assert scope.status == "MODEL_NOT_VALIDATED_FOR_SPECIES"

    payload = {
        "species": "Goat",
        "symptoms": ["fever"],
        "body_temperature": 104.2
    }
    response = client.post("/api/detection/analyze", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["is_demo_inference"] is True


# 14. Dataset B Quarantine Invariant
def test_14_dataset_b_quarantine_invariant():
    aau = provenance_registry.get_source_by_id("DATASET-B-CANDIDATE-AAU")
    assert aau is not None
    assert aau["permission_status"] == PermissionState.PERMISSION_REQUIRED.value
    assert PermissionRegistry.is_permission_granted(aau["permission_status"]) is False


# 15. Milestone 8B Report Verification
def test_15_milestone_8b_report_completeness():
    report_file = BACKEND_DIR / "ai" / "models" / "MILESTONE_8B_MODEL_IMPROVEMENT_REPORT.md"
    assert report_file.is_file(), "MILESTONE_8B_MODEL_IMPROVEMENT_REPORT.md must exist"

    content = report_file.read_text(encoding="utf-8")
    expected_sections = [
        "1. Executive Summary & Objective",
        "2. Baseline Model Specification (V1)",
        "3. Dataset Isolation & Zero-Leakage Protocol",
        "4. Controlled Experiments Matrix (EXP-01 to EXP-06)",
        "5. Augmentation Strategies & Visual Invariance",
        "6. Input Resolution Investigations",
        "7. Multi-Scale Tiling & Local Patch Analysis",
        "8. Loss Formulations & Class Imbalance Handling",
        "9. Validation-Only Selection Protocol",
        "10. Validation-Only Operating Threshold Determination",
        "11. Probability Calibration & Expected Calibration Error (ECE)",
        "12. Final Winning Experimental Candidate Selection",
        "13. Official Held-Out Test Evaluation",
        "14. Head-to-Head Comparison: Baseline V1 vs. Candidate V2",
        "15. Comprehensive False-Negative Audit",
        "16. Grad-CAM Visual Explainability & Localization Review",
        "17. Real-World Limitations & Failure Boundary Analysis",
        "18. Production Deployment Decision (`V1_RETAINED`)",
        "19. Roadmap for Future Milestones (Dataset B & Multi-Species DTA)"
    ]
    for sec in expected_sections:
        assert sec in content, f"Missing section '{sec}' in Milestone 8B report"


# 16. Live Detection API Backward-Compatibility
def test_16_detection_api_backward_compatibility(client):
    payload = {
        "species": "Cattle",
        "symptoms": ["cutaneous nodules", "fever"],
        "body_temperature": 104.2
    }
    response = client.post("/api/detection/analyze", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "possible_condition" in res_data
    assert "confidence" in res_data
    assert "risk_level" in res_data
    assert "veterinary_review_required" in res_data
    assert "differential_diagnoses" in res_data
