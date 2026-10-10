# AniCare AI — Clinical Model Evaluation & Error Analytics Engine

## Overview

The `ai/evaluation` module implements the empirical audit, error taxonomy, validation threshold optimization, and spatial/crop robustness benchmarking for the AniCare AI Vision and Risk Intelligence systems.

---

## Architecture & Components

```
backend/ai/evaluation/
├── error_taxonomy.py           # Standardized FailureCategory enumeration & auditing rules
├── false_negative_analysis.py  # Empirical diagnostic audit for false negatives on test partition
├── threshold_analysis.py       # Validation-only ROC/Precision-Recall operating threshold sweep
├── robustness_analysis.py      # Multi-crop, spatial tiling, and augmentation benchmarking
└── README.md                   # System documentation
```

---

## 1. Clinical Error Taxonomy (`error_taxonomy.py`)

Defines 9 mutually exclusive failure categories rooted in veterinary dermatological presentation:

| Failure Category | Description | Primary Visual Trigger |
| :--- | :--- | :--- |
| `EARLY_SUBTLE_PAPULES` | Incipient 0.5–1.5cm papules before full nodular eruption | Flat lesions, minimal shadowing |
| `DISTANT_WHOLE_ANIMAL_FRAMING` | Long-shot framing (>2.5m) diluting lesion pixel ratio | Feature area < 2% of image |
| `SMALL_LESION_AREA` | Localized solitary lesions occupying limited bounding area | Low total lesion pixel count |
| `MUD_DEBRIS_OBSTRUCTION` | Dried fecal mud, wallow crust, or dust obscuring skin | High-frequency surface occluders |
| `POOR_LIGHTING` | Harsh backlighting, deep shade, or severe underexposure | Dynamic range compression |
| `OCCLUSION` | Pen railings, feeding troughs, vegetation, or halters | Structural foreground occlusion |
| `BACKGROUND_COMPLEXITY` | Corrugated metal, dense herd members, mottled ground | Distractor texture false correlation |
| `IMAGE_QUALITY` | Motion blur, heavy JPEG compression, severe low-res | Loss of high-frequency edge detail |
| `UNKNOWN_VISUAL_FAILURE` | Unclassified model misprediction | Near-boundary feature confusion |

---

## 2. False-Negative Audit Engine (`false_negative_analysis.py`)

Executes an exhaustive empirical audit over held-out test set false negatives:
- Evaluates raw logit and sigmoid output probabilities.
- Classifies each failure into the veterinary error taxonomy.
- Computes near-boundary proximity (cases within $[0.40, 0.50)$ probability window).
- Exports machine-readable audit report to `backend/ai/models/evaluation/false_negative_audit.json` and human-readable `backend/ai/models/evaluation/FALSE_NEGATIVE_ANALYSIS.md`.

### Key Empirical Findings:
- Total Held-out Test Set: 138 images (42 LSD, 96 Healthy).
- Test LSD False Negatives: 8 cases (Recall = 80.95%, 34 TP).
- **Near-Boundary Finding**: 4 of the 8 false negatives (50.0%) were predicted with probabilities between $0.422$ and $0.499$.
- Dominant failure modes: `EARLY_SUBTLE_PAPULES` (37.5%) and `DISTANT_WHOLE_ANIMAL_FRAMING` (25.0%).

---

## 3. Validation Threshold Optimization & Post-Hoc Diagnostics (`threshold_analysis.py`)

Evaluates binary decision thresholds $\tau \in [0.30, 0.70]$ in $0.05$ increments **exclusively on the 135-sample validation set** to prevent data snooping:
- Implements strict validation-guided threshold selection rule: `Max Recall subject to Specificity >= 90% on validation`.
- **Selected & Frozen Operating Threshold**: $\tau^* = 0.50$ (Validation Recall: 92.50%, Validation Specificity: 95.79%, Macro F1: 0.9383).
- **Official Held-Out Test Evaluation**: At $\tau^* = 0.50$: Test Recall = 80.95% (34/42 TP, 8 FNs), Specificity = 97.92% (94/96 TN, 2 FPs), Macro F1 = 0.9106.
- **Reporting Disclosure**: The validation operating-point target was met during validation, but the final held-out test LSD sensitivity was 80.95%, so the 92% test-sensitivity target was not achieved.
- **Post-Hoc Test Diagnostics Warning**: Post-hoc test diagnostics across candidate thresholds were computed after threshold freezing for error analysis only. The held-out test set was not used for model training or validation-based threshold selection. These post-hoc diagnostics must not be used for model or threshold selection.

---

## 4. Robustness & Tiling Benchmarking (`robustness_analysis.py`)

Compares single-pass inference against 5-crop spatial tiling (global view + 4 quadrants + center zoom):
- Benchmark results on validation set:
  - Single-Pass: Recall 92.50%, Macro F1 0.9383, Latency 24.23ms (CPU).
  - 5-Crop Tiling: Recall 95.00%, Macro F1 0.9317, Latency 98.55ms (CPU).
- **Architectural Policy**: Single-pass inference is preserved as the default real-time engine to honor the $<30$ms SLA. Spatial tiling is exposed as an optional high-precision secondary mode for ambiguous triage cases.

---

## Reproducibility & Testing

Run the full evaluation test suite:
```bash
python -m pytest backend/tests/test_milestone6_multimodal.py -k "taxonomy or threshold or false_negative or robustness" -v
```
