# AniCare AI — External Dataset Validation & Governance Infrastructure

**Milestone 8A**: Legally Controlled External Validation Pipeline  
**Operating Policy**: Strict Provenance, Zero Fabrication, Frozen Operating Baseline ($\tau = 0.50$)

---

## 1. Governance Architecture

The `backend/ai/dataset/external/` package provides independent legal and scientific validation for external clinical benchmarks:

```
external/
├── __init__.py               <- Unified package interface
├── permission_registry.py    <- 10-point Legal / Ethical Gate & permission states
├── provenance.py             <- Institutional metadata & DTA tracking
├── external_manifest.py      <- Immutable sanitized manifest schema (SHA-256 ID hashing)
├── duplicate_guard.py        <- Exact SHA-256 & perceptual dHash cross-dataset isolation
├── label_audit.py            <- 5-tier diagnostic evidence hierarchy & disease scope
├── quality_audit.py          <- Photometric, dimension, blur, and exposure auditing
├── grouping.py               <- Animal/case cohort clustering without synthetic IDs
├── validator.py              <- Batch ingestion and validation orchestrator
├── evaluator.py              <- Frozen EfficientNet-B0 inference & Wilson 95% CIs
├── reports/                  <- Generated audit logs and summaries
└── README.md                 <- This documentation file
```

---

## 2. Dataset B Status: `PERMISSION_REQUIRED`

Candidate sources under institutional review:
1. **AAU Anand Veterinary College Teaching Hospital Archives** (Gujarat)
2. **ICAR Directorate of Foot and Mouth Disease (ICAR-DFMD)** (National Reference Lab)

**Current Status**: `PERMISSION_REQUIRED`  
**Verified Production Images**: **0**  
**Official Statement**: *"External validation pending due to lack of a legally verified independent dataset."*

---

## 3. Mandatory 10-Point Legal & Ethical Gate

Before any external image enters the evaluation manifest:
1. Permission or valid license exists.
2. Research use is permitted.
3. Images can legally be processed.
4. Patient/owner identifying information is removed.
5. No phone numbers.
6. No addresses.
7. No personal identifiers.
8. No unauthorized veterinary records exposed.
9. Image redistribution restrictions documented.
10. Source attribution requirements recorded.

If any check fails, the sample is immediately routed to **`QUARANTINE`**.

---

## 4. Cross-Dataset Leakage Prevention

No image from **Dataset A** (Mendeley LSD: 906 clean images) may enter Dataset B:
* **Exact SHA-256 match**: Auto-rejected with status `REJECT_FROM_EXTERNAL_VALIDATION`.
* **Perceptual dHash match** (Hamming distance $\le 6$): Auto-rejected with audit log.

---

## 5. Frozen Evaluation Contract

When legal permission is obtained:
* **Model**: EfficientNet-B0 ONNX (`anicare_vision_bovine_v1.onnx`)
* **Threshold**: $\tau = 0.50$ (FROZEN)
* **Retraining / Adaptation**: STRICTLY PROHIBITED
* **Confidence Intervals**: 95% Wilson binomial score intervals
* **Small Sample Safeguard**: Sample size $N < 5$ reports `INSUFFICIENT_EXTERNAL_SAMPLE_SIZE`
