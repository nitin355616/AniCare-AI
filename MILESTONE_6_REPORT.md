# AniCare AI — Milestone 6 Final Report
**Evaluation Protocol Correction, Multi-Modal Clinical Intelligence & Early-Warning Surveillance**

**Project**: AniCare AI — AI-Powered Animal Health & Disease Early-Warning Platform  
**Hackathon**: Smart India Hackathon (SIH 2026)  
**Milestone**: Milestone 6 — Clinical Dataset Expansion, False-Negative Reduction & Multi-Modal Early-Warning Intelligence  
**Date**: October 2026  
**Status**: **COMPLETE — Evaluation Protocol Corrected & 57/57 Tests Passing (100%)**

---

## 1. Executive Summary

Milestone 6 for **AniCare AI** achieves two fundamental engineering and scientific objectives:
1. **Multi-Modal Veterinary Intelligence Architecture**: Upgraded the system from single-modality vision to a comprehensive multi-modal early-warning platform incorporating a 5-modality clinical risk engine, spatial-temporal disease cluster detection, Gradient-weighted Class Activation Mapping (Grad-CAM) visual explainability, and strict species validation guardrails.
2. **Scientific Evaluation Protocol Correction**: Addressed the evaluation protocol hygiene by decoupling validation-based threshold selection from post-hoc test diagnostics. The operating decision threshold is frozen at `TAU = 0.50` based strictly on validation partition metrics (`maximize recall subject to specificity >= 90% on validation`). The held-out test partition metrics at `TAU = 0.50` serve as the official final benchmark. Post-hoc multi-threshold diagnostics on the test partition are explicitly labeled as exploratory error diagnostics and are strictly barred from being used for threshold selection.

All 57 backend, AI engine, vision, dataset intelligence, and multi-modal tests pass with 100% compliance.

---

## 2. What Was Improved

- **False-Negative Error Audit**: Established a 9-category clinical error taxonomy in `backend/ai/evaluation/error_taxonomy.py` and executed an empirical logit margin audit of all 8 missed cases on the held-out test split.
- **Threshold Freezing**: Permanently frozen `OPERATING_THRESHOLD = 0.50` in `ai_config.OPERATING_THRESHOLD` and `RealVisionInferenceEngine` based purely on validation performance.
- **Biological Data Augmentation**: Designed biologically conservative transformations (`RandomResizedCrop(0.85, 1.0)`, `GaussianBlur(3x3)`, and mild color jitter) preserving delicate epidermal nodular boundaries.
- **Spatial Tiling Architecture**: Built `TiledPreprocessor` with 5-crop spatial evaluation (global, center zoom, 4 quadrants) and benchmarked its latency/sensitivity trade-off.
- **Multi-Modal Clinical Risk Engine**: Decoupled risk assessment from visual confidence across 5 modalities: Visual, Symptom, Physiological, Epidemiological, and Animal History.
- **Outbreak Cluster Surveillance**: Implemented spatio-temporal cluster surveillance (`ClusterDetector`) flagging $\ge 3$ at-risk animals in the same village within a 7-day window.
- **Visual Explainability**: Built penultimate-layer Grad-CAM saliency heatmaps with alpha-blended overlays for cattle photographs.
- **Species Validation Guard**: Restricted vision inference strictly to Cattle, safely routing non-bovine livestock to syndromic assessment.

---

## 3. Final Model Specifications

- **Architecture**: EfficientNet-B0 (Compound Scaled MBConv blocks)
- **Input Dimensions**: $224 \times 224 \times 3$ (RGB, ImageNet normalized)
- **Loss Function**: Multi-Class Focal Loss ($\gamma = 2.0, \alpha = [1.0, 2.34]$)
- **Parameters**: 4,010,110 (15.29 MB ONNX graph)
- **Deployment Format**: ONNX Opset 14 (`backend/ai/models/weights/anicare_vision_bovine_v1.onnx`)
- **Runtime Execution**: ONNX Runtime (`CPUExecutionProvider`, intra-op threads = 2)
- **Inference Latency**: Single-pass CPU latency: **~24.2 ms** (Total API cycle: ~35 ms)
- **Numerical Parity**: Max logit divergence vs PyTorch: $0.000002$ ($2 \times 10^{-6}$)
- **Calibration**: Platt Temperature Scaling ($T = 1.4415$, optimized on validation set)
- **Frozen Operating Threshold**: `TAU = 0.50` (selected on validation only)

---

## 4. Validation Operating Point (Validation Results Only)

All threshold selection, model comparison, and calibration decisions were performed **exclusively on the 135-sample validation partition** (40 LSD, 95 Healthy) to strictly prevent data snooping:

- **Validation Selection Rule**: `maximize recall subject to specificity >= 90% on validation`
- **Selected Operating Threshold**: **`TAU = 0.50`**

### Validation Threshold Sweep Table
| Threshold | Val LSD Recall (Sens.) | Val Healthy Specificity | Val LSD Precision | Val Macro F1 | FNR | FPR | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `0.30` | 95.00% | 66.32% | 54.29% | 0.7392 | 5.00% | 33.68% | Exploratory candidate |
| `0.35` | 95.00% | 73.68% | 60.32% | 0.7881 | 5.00% | 26.32% | Exploratory candidate |
| `0.40` | 95.00% | 82.11% | 69.09% | 0.8457 | 5.00% | 17.89% | Exploratory candidate |
| `0.45` | 95.00% | 89.47% | 79.17% | 0.8989 | 5.00% | 10.53% | Exploratory candidate |
| **`0.50`** | **92.50%** | **95.79%** | **90.24%** | **0.9383** | **7.50%** | **4.21%** | **Selected & Frozen ($\tau^*$)** |
| `0.55` | 85.00% | 95.79% | 89.47% | 0.9099 | 15.00% | 4.21% | Sub-optimal recall |
| `0.60` | 75.00% | 97.89% | 93.75% | 0.8864 | 25.00% | 2.11% | Unacceptable FNR (25%) |

*Validation Conclusion*: At $\tau^* = 0.50$, the model met the clinical sensitivity target on the validation set (**92.50%**, 37/40 true positives) while maintaining **95.79% specificity** (only 4 false alarms).

---

## 5. Final Test Benchmark (Official Test Results)

The official benchmark was evaluated on the held-out test split (138 images: 42 LSD, 96 Healthy) using the frozen operating threshold $\tau^* = 0.50$:

| Metric | Official Test Value | Clinical Meaning & Details |
| :--- | :---: | :--- |
| **Overall Accuracy** | **92.75%** | 128 / 138 total correct classifications |
| **Macro F1-Score** | **0.9106** | Balanced harmonic mean across both classes |
| **LSD Sensitivity (Recall)** | **80.95%** | **34 / 42 confirmed LSD cases detected** (**8 false negatives**) |
| **LSD Precision** | **94.44%** | 34 / 36 positive calls were true lesions (**2 false alarms**) |
| **Healthy Specificity** | **97.92%** | **94 / 96 healthy bovines correctly cleared** |
| **ROC-AUC** | **0.9452** | Area under receiver operating characteristic |
| **PR-AUC** | **0.9352** | Area under precision-recall curve |
| **Calibrated ECE** | **0.1673** | Expected Calibration Error ($T=1.4415$) |

> [!WARNING]
> ### OFFICIAL SENSITIVITY DECLARATION
> **The validation operating-point target was met during validation (92.50%), but the final held-out test LSD sensitivity was 80.95%, so the 92% test-sensitivity target was NOT ACHIEVED.**
> 
> Under strict scientific integrity guidelines for SIH 2026, test set results are reported transparently and not substituted with validation metrics.

---

## 6. Error Taxonomy & Post-Hoc Test Diagnostics

### 6.1 Clinical Error Taxonomy Analysis
Audit of the 8 false negatives on the held-out test partition revealed:
1. `EARLY_SUBTLE_PAPULES` (37.5%, 3 cases): Incipient 0.5–1.5cm flat papules before circumscribed nodular necrosis.
2. `DISTANT_WHOLE_ANIMAL_FRAMING` (25.0%, 2 cases): Wide pasture shots where lesions occupied $<2\%$ of field-of-view.
3. `MUD_DEBRIS_OBSTRUCTION` (12.5%, 1 case): Dried mud crust obscuring lower flank lesions.
4. `IMAGE_QUALITY` (12.5%, 1 case): Severe JPEG compression and motion blur in field capture.
5. `BACKGROUND_COMPLEXITY` (12.5%, 1 case): Complex mottled stall background.

**Near-Boundary Finding**: **50.0% (4 of 8) of false negatives had predicted probabilities between $0.422$ and $0.499$** (margin $< 0.08$ from the 0.50 threshold).

### 6.2 Post-Hoc Test-Set Diagnostic Analysis
> [!CAUTION]
> **POST-HOC DIAGNOSTICS WARNING**:  
> Post-hoc test-set diagnostic analysis — **NOT used for model selection or threshold selection**. These test-set threshold diagnostics were computed after the model/operating point had been defined and are reported only for error analysis. They must not be interpreted as independent threshold-selection evidence.

| Threshold | Test LSD Recall | Test Specificity | Test Precision | Test Macro F1 | Test FNs | Test FPs | Role / Interpretation |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `0.30` | 92.86% | 68.75% | 56.52% | 0.7514 | 3 | 30 | Post-hoc diagnostic exploratory point |
| `0.35` | 90.48% | 76.04% | 62.30% | 0.7909 | 4 | 23 | Post-hoc diagnostic exploratory point |
| `0.40` | 90.48% | 85.42% | 73.08% | 0.8548 | 4 | 14 | Post-hoc diagnostic exploratory point |
| `0.45` | 85.71% | 95.83% | 90.00% | 0.9133 | 6 | 4 | Post-hoc diagnostic exploratory point |
| **`0.50`** | **80.95%** | **97.92%** | **94.44%** | **0.9106** | **8** | **2** | **Official Frozen Operating Point** |
| `0.55` | 76.19% | 98.96% | 96.97% | 0.9023 | 10 | 1 | Post-hoc diagnostic exploratory point |
| `0.60` | 71.43% | 98.96% | 96.77% | 0.8803 | 12 | 1 | Post-hoc diagnostic exploratory point |

---

## 7. Multimodal Clinical Risk Engine

Implemented in [`backend/ai/postprocessing/risk_engine.py`](file:///d:/AniCare-AI/backend/ai/postprocessing/risk_engine.py):
- Decouples visual confidence from clinical priority into a **transparent weighted clinical risk-scoring framework** designed to prioritize veterinary review.
- Scores 5 independent dimensions ($0 - 100$):
  1. `visual_risk_score` (30% weight): Calibrated vision probability, lesion severity, image quality factor.
  2. `symptom_risk_score` (25% weight): Cutaneous nodules (+25), oral vesicles (+30), respiratory distress (+25), anorexia (+15), recumbency (+25).
  3. `physiological_risk_score` (20% weight): Severe hyperpyrexia $\ge 105^\circ\text{F}$ (+45), marked pyrexia $\ge 103.5^\circ\text{F}$ (+25), tachypnea $>50$ bpm (+15).
  4. `epidemiological_risk_score` (15% weight): Active village cluster (+35), nearby cases (+30), herd cohort spread (+20).
  5. `history_risk_score` (10% weight): Unvaccinated status (+25), juvenile calf vulnerability (+15).

### Non-Linear Clinical Escalation Overrides:
- **Severe Hyperpyrexia + Nodules/Vesicles**: When temperature $\ge 105.0^\circ\text{F}$ is paired with cutaneous or vesicular signs, risk escalates directly to **CRITICAL ($\ge 88.0$)**, overriding visual-only scores.
- **Pathological Baseline Floor**: High-consequence systemic conditions (BRD, Mastitis) with fever $\ge 103.0^\circ\text{F}$ enforce a minimum **HIGH risk floor ($\ge 65.0$)**.
- **Mild Localized Cap**: Benign conditions (Ringworm) without systemic signs remain capped at $\le 40.0$ (`LOW` or `MODERATE`).

---

## 8. Epidemiological Cluster Detection

Implemented in [`backend/ai/epidemiology/cluster_detector.py`](file:///d:/AniCare-AI/backend/ai/epidemiology/cluster_detector.py) and [`outbreak_risk.py`](file:///d:/AniCare-AI/backend/ai/epidemiology/outbreak_risk.py):
- **Spatial Windowing**: Groups incoming health telemetry by administrative boundary (village/block) and 7-day sliding time window.
- **Cluster Threshold**: Flags a `POSSIBLE_CLUSTER` when $\ge 3$ at-risk animals in the same village exhibit high-risk contagious signs.
- **Biosecurity Containment Tiers**:
  - `TIER_1_ROUTINE`: Sporadic baseline cases.
  - `TIER_2_RING_SURVEILLANCE`: Cluster detected; recommended 5km radius ring surveillance.
  - `TIER_3_RED_ALERT`: Epidemic trajectory; alerts District Animal Husbandry Officer (DAHO) and recommends immediate quarantine.

---

## 9. Grad-CAM Explainability

Implemented in [`backend/ai/explainability/gradcam.py`](file:///d:/AniCare-AI/backend/ai/explainability/gradcam.py):
- Hooks into the penultimate convolutional block of EfficientNet-B0 (`base.features[-1]`).
- Generates coarse 2D saliency heatmaps highlighting **image regions contributing to the model's visual representation**.
- Blends JET colormap overlays ($\alpha = 0.45$) saved to `backend/uploads/explanations/`.
- **Mandatory Disclaimer**: Saliency indicates convolutional feature correlation, not proof of disease presence.

---

## 10. Species Validation Guard

Implemented in [`backend/ai/inference/model_scope.py`](file:///d:/AniCare-AI/backend/ai/inference/model_scope.py):
- **Current Validated Scope**: **Cattle Only (*Bos taurus* / *Bos indicus*)**.
- For Buffalo, Goat, Sheep, Poultry, Swine, and Canine:
  - Vision model execution is blocked.
  - Returns explicit status: `MODEL_NOT_VALIDATED_FOR_SPECIES`.
  - Safely routes requests to syndromic symptom evaluation.
  - Emits mandatory species notice: *"Vision model validated exclusively for Cattle. Assessment conducted via syndromic symptoms only. On-site veterinary examination required."*

---

## 11. API Changes & Backward Compatibility

- **`POST /api/detection/analyze`**:
  - Accepts both legacy payloads and multi-modal extensions (`heart_rate`, `respiratory_rate`, `vaccination_status`, `recent_nearby_cases`, `cluster_warning_active`).
  - Returns all existing frontend fields plus additive subscores (`visual_risk_score`, `symptom_risk_score`, `physiological_risk_score`, `epidemiological_risk_score`, `history_risk_score`, `overall_risk_score`, `model_scope`, `operating_threshold`, `explainability`).
- **`GET /api/epidemiology/clusters`**:
  - Serves live and syndromic cluster alerts for veterinary dashboards.
- **`GET /api/epidemiology/roadmap`**:
  - Serves validated species registry and future validation roadmap.

---

## 12. Automated Test Results

Executed complete test suite across all subsystems:
```bash
python -m pytest backend/tests -v
```

```
============================= test session starts =============================
collected 57 items

backend/tests/test_ai_engine.py::test_demo_engine_fallback PASSED        [  1%]
backend/tests/test_ai_engine.py::test_vision_engine_unavailable_fallback PASSED [  3%]
backend/tests/test_ai_engine.py::test_risk_engine_decoupling_and_severity PASSED [  5%]
backend/tests/test_ai_engine.py::test_api_response_compatibility PASSED  [  7%]
backend/tests/test_ai_engine.py::test_invalid_image_handling PASSED      [  8%]
backend/tests/test_ai_engine.py::test_model_metadata PASSED              [ 10%]
backend/tests/test_ai_engine.py::test_safety_flags_and_disclaimer PASSED [ 12%]
backend/tests/test_backend.py::test_root_discovery PASSED                [ 14%]
backend/tests/test_backend.py::test_health_check PASSED                  [ 15%]
backend/tests/test_backend.py::test_auth_workflow PASSED                 [ 17%]
backend/tests/test_backend.py::test_animals_crud PASSED                  [ 19%]
backend/tests/test_backend.py::test_health_records PASSED                [ 21%]
backend/tests/test_backend.py::test_detection_photo_upload_and_validation PASSED [ 22%]
backend/tests/test_backend.py::test_disease_detection_analysis PASSED    [ 24%]
backend/tests/test_backend.py::test_veterinary_workflow_and_license_guard PASSED [ 26%]
backend/tests/test_backend.py::test_alerts_workflow PASSED               [ 28%]
backend/tests/test_dataset_intelligence.py (20 tests) PASSED              [ 63%]
backend/tests/test_milestone6_multimodal.py (13 tests) PASSED            [ 85%]
backend/tests/test_vision_model.py (8 tests) PASSED                      [100%]

======================= 57 passed, 1 warning in 12.50s ========================
```
**Pass Rate: 100% (57 passed, 0 failed)**.

---

## 13. Limitations & Clinical Boundaries

1. **Relatively Small Curated Dataset**: Total 906 clean verified images (271 LSD, 635 Healthy).
2. **Animal-Level Grouping Unavailable in Source Dataset**: `animal_grouping_available = false` in source repository. Individual cow RFID tags were not recorded in the original paper. **Therefore, the model cannot scientifically claim herd-independent generalization.**
3. **External Validation Still Required**: Model has been benchmarked on a split of the primary dataset; multi-center external validation on independent cohorts from differing states is planned for Milestone 7.
4. **Real-World Domain Shift Possible**: Differences in climate, coat color, breeds (*Bos indicus* zebu vs *Bos taurus* crossbreds), and pen bedding can induce performance shifts.
5. **Early / Subtle Lesions Can Be Missed**: Incipient flat papules ($0.5–1.5$cm) accounted for 37.5% of false negatives (`EARLY_SUBTLE_PAPULES`).
6. **Distant Images Reduce Performance**: Lesions occupying $<2\%$ of field-of-view can be attenuated during $224 \times 224$ resizing (`DISTANT_WHOLE_ANIMAL_FRAMING`).
7. **Mud, Debris, and Occlusion**: Crusted mud, wallow soil, pen railings, and halters can mask cutaneous nodules.
8. **Test LSD Sensitivity Currently 80.95%**: Missed 8 out of 42 test cases. Early detection requires multi-modal clinical risk scoring (vitals + symptoms) rather than visual reliance alone.
9. **Engineering Risk Scoring**: Risk engine outputs an operational triage priority, NOT a clinically validated disease probability.

---

## 14. Evaluation Protocol Correction

> [!IMPORTANT]
> ### SCIENTIFIC HYGIENE DECLARATION
> 1. **Partition Roles**:
>    - **Training Set (633)**: Model fitting, conservative augmentation, loss optimization.
>    - **Validation Set (135)**: Architecture comparison, threshold selection, calibration temperature fitting.
>    - **Held-Out Test Set (138)**: Final one-time benchmark evaluation at frozen $\tau^* = 0.50$.
> 2. **Terminology Correction**:
>    - **The held-out test set was not used for model training or validation-based threshold selection.**
>    - During Milestone 6, post-hoc threshold diagnostics were additionally computed on the test set for analysis.
>    - Therefore, these post-hoc test diagnostics **must not be used for model or threshold selection**.
>    - The test set is described as: *"Held-out during training and model selection, but subsequently accessed for post-hoc diagnostic threshold analysis."*
>    - It must **NOT** be described as a pristine untouched benchmark for future development.

---

## 15. Future Validation Plan (Milestone 7 Roadmap)

To maintain scientific rigor after Milestone 6's post-hoc diagnostics on the test partition, Milestone 7 will follow a 3-tier dataset protocol:

```
+---------------------------------------------------------------------------------------------------+
|                              MILESTONE 7 EXTERNAL VALIDATION ARCHITECTURE                         |
+------------------------------------+-----------------------------------+--------------------------+
| DATASET A                          | DATASET B                         | FUTURE DATASET C         |
| Primary Development                | Independent External Validation   | Pristine Held-Out Benchmark|
+------------------------------------+-----------------------------------+--------------------------+
| • Existing 906 Mendeley images     | • Newly acquired independent      | • Separate clinical site |
| • Curated bovine cutaneous dataset |   veterinary institutional source |   or prospectively logged|
| • Used for ongoing model training  | • Zero parameter or threshold     |   field cohort           |
|   and validation tuning            |   tuning allowed                  | • Strictly untouched     |
+------------------------------------+-----------------------------------+--------------------------+
```

### External Acquisition Quality Requirements:
1. **Verified Provenance & License**: Documented institutional source, DOI, and open research license (e.g. CC BY 4.0).
2. **Clinical Disease Confirmation**: Polymerase Chain Reaction (PCR), ELISA, or certified veterinary officer clinical diagnosis.
3. **Diverse Acquisition Conditions**: Different agro-climatic zones, varied farm lighting (open pasture vs shaded stall), and varied smartphone cameras.
4. **Animal-Level RFID Metadata**: Ear-tag identifiers to enable strict group-level partitioning and prevent same-animal image leakage.
5. **No Pre-Evaluation Tuning**: Dataset B and Dataset C must **NEVER** be used to tune models, calibrate temperatures, or select thresholds prior to final external reporting.

---

> **Milestone 7 Progress**: Milestone 7 is complete. Dataset B validation pipeline, 12-category field robustness framework, cross-dataset leakage prevention, and Dataset C infrastructure (`STATUS = PENDING`) are operational. Refer to [`MILESTONE_7_DATASET_REPORT.md`](file:///d:/AniCare-AI/backend/ai/models/MILESTONE_7_DATASET_REPORT.md) and [`EXTERNAL_VALIDATION_REPORT.md`](file:///d:/AniCare-AI/backend/ai/models/EXTERNAL_VALIDATION_REPORT.md).
