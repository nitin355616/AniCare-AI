# AniCare AI — Milestone 8A Official Report
## External Validation & Independent Dataset Governance Execution

**Platform**: AniCare AI — AI-Powered Animal Health & Biosecurity Early Warning Platform (SIH 2026)  
**Report Type**: Milestone 8A Official External Validation & Legal Governance Audit  
**Date**: October 2026  
**Status**: **MILESTONE 8A GOVERNANCE READY — EXTERNAL DATA ACQUISITION PENDING**

---

## 1. Executive Summary

Milestone 8A establishes a legally controlled, scientifically defensible external validation framework for AniCare AI. The purpose of this milestone is to govern and evaluate the frozen bovine vision model against an independently sourced Dataset B, without compromising historical benchmarks, retraining model parameters, or fabricating data.

Currently, candidate independent sources (AAU Anand Veterinary College Teaching Hospital Archives and ICAR-DFMD National Bovine Repository) remain in **`PERMISSION_REQUIRED`** status pending inter-institutional Data Transfer Agreements (DTAs). Accordingly, the system reports **`EXTERNAL_VALIDATION_PENDING`** with **zero production images ingested**. All legal gates, cryptographic duplicate guards, quality checkers, label auditors, Wilson confidence interval evaluators, API endpoints, and frontend indicators have been constructed and verified across 97 tests.

The official Dataset A held-out benchmark ($N=138$, Sensitivity: $80.95\%$, Specificity: $97.92\%$, Macro F1: $0.9106$) remains the official frozen baseline.

---

## 2. Dataset Provenance

External provenance records have been registered in [`source_registry.json`](file:///d:/AniCare-AI/backend/ai/dataset/source_registry.json) with all 21 mandatory attributes:

1. **AAU Anand Clinical Teaching Hospital Archives**:
   - *Institution*: Anand Agricultural University (AAU), Gujarat, India
   - *Setting*: Veterinary Clinical Complex inpatient wards & examination bays
   - *Candidate Scope*: 1,850 archival dermatology records (*Bos indicus*, buffalo, caprine)
   - *Data Use Agreement*: University Educational/Clinical IP; formal DTA required
2. **ICAR-DFMD National Bovine Viral & Vesicular Repository**:
   - *Institution*: ICAR Directorate of Foot and Mouth Disease (Mukteshwar / Bhubaneswar)
   - *Setting*: National Reference Diagnostic Laboratory
   - *Candidate Scope*: 2,400 reference images (FMD, LSD, vesicular lesions)
   - *Data Use Agreement*: Government Institutional Research License / Restrictive MOU

---

## 3. Permission Status

* **AAU Anand**: `PERMISSION_REQUIRED` (Administrative DTA review pending)
* **ICAR-DFMD**: `PERMISSION_REQUIRED` (Institutional MOU proposal pending)
* **TANUVAS**: `PERMISSION_REQUIRED` (Secondary small ruminant candidate)
* **WOAH/FAO**: `REVIEW_REQUIRED` (Copyright redistribution review)
* **Kaggle Uncurated Scrapes**: `REJECTED` (Zero provenance; prohibited by governance)

**Current Legally Usable Production Images for Dataset B**: **0**.

---

## 4. Dataset Composition

| Partition | Total Images | LSD Positive | Healthy / Normal | Status | Source |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Dataset A (Train)** | 633 | 191 | 442 | Curated & Frozen | Mendeley Data |
| **Dataset A (Validation)** | 135 | 40 | 95 | Curated & Frozen | Mendeley Data |
| **Dataset A (Held-Out Test)** | 138 | 42 | 96 | Curated & Frozen | Mendeley Data |
| **Dataset B (External Validation)** | **0** | **0** | **0** | **`PERMISSION_REQUIRED`** | AAU Anand / ICAR-DFMD |

---

## 5. Quality Audit Framework

The external ingestion pipeline enforces a 4-tier image quality standard ([`quality_audit.py`](file:///d:/AniCare-AI/backend/ai/dataset/external/quality_audit.py)):
* Minimum dimensions: $224 \times 224$ pixels.
* Formats allowed: JPEG, PNG, WEBP.
* Focus metric: Laplacian gradient variance ($< 25.0$ flags optical/motion blur).
* Exposure metric: Mean luminance ($< 35.0$ underexposed, $> 225.0$ specular overexposure).
* Tiers: `UNUSABLE` (auto-quarantined), `POOR`, `ACCEPTABLE`, `HIGH`.
* **Zero deletion policy**: Every rejected candidate creates a persistent audit entry with exact failure reasons.

---

## 6. Duplicate Audit & Cross-Dataset Leakage Guard

Implemented via [`duplicate_guard.py`](file:///d:/AniCare-AI/backend/ai/dataset/external/duplicate_guard.py):
* Pre-loads exact SHA-256 digests and perceptual dHashes from all 906 Dataset A images.
* **Intra-dataset deduplication**: Identifies duplicate frames within candidate batches.
* **Cross-dataset isolation**: Any candidate matching Dataset A (exact match or dHash Hamming distance $\le 6$) is flagged with status `REJECT_FROM_EXTERNAL_VALIDATION` and logged with reason `CROSS_DATASET_LEAKAGE`.

---

## 7. Animal-Level and Case-Level Grouping

Governed by [`grouping.py`](file:///d:/AniCare-AI/backend/ai/dataset/external/grouping.py):
* Where animal ear tags or patient IDs are legally available across $\ge 80\%$ of samples, images are grouped by animal to prevent split contamination.
* Where identifiers are absent (as in historical unindexed archives), the pipeline sets:
  $$\text{animal\_grouping\_available} = \mathbf{false}$$
  and appends the mandatory disclaimer: *"The evaluation CANNOT claim herd-independent generalization."*
* Under no circumstances are synthetic animal IDs fabricated.

---

## 8. Label Audit & Biological Evidence Hierarchy

Governed by [`label_audit.py`](file:///d:/AniCare-AI/backend/ai/dataset/external/label_audit.py):
* 5-tier diagnostic hierarchy:
  1. *Laboratory-confirmed* (PCR, ELISA, viral sequencing)
  2. *Veterinary clinical diagnosis* (board-certified or university clinicians)
  3. *Documented clinical diagnosis* (teaching hospital charts)
  4. *Expert-reviewed label* (veterinary consensus)
  5. *Unknown / ambiguous*
* **Ambiguous Conditions**: Pseudo-lumpy, ringworm, mange, and nonspecific dermatitis are quarantined as `AMBIGUOUS` and never forced into binary classes.
* **Species Validation Guard**: Non-cattle species (buffalo, sheep, goat, dog, etc.) are blocked with status `MODEL_NOT_VALIDATED_FOR_SPECIES`.

---

## 9. Model Configuration

* **Architecture**: EfficientNet-B0 (Pretrained on ImageNet, custom 2-class head)
* **Format**: ONNX Runtime (Opset 14, CPUExecutionProvider)
* **Input Tensor**: $1 \times 3 \times 224 \times 224$ (Normalized with ImageNet mean/std)
* **Calibration**: Temperature-scaled logits ($T = 1.4415$)
* **Weights File**: [`backend/ai/models/anicare_vision_bovine_v1.onnx`](file:///d:/AniCare-AI/backend/ai/models/anicare_vision_bovine_v1.onnx) (15.29 MB)

---

## 10. Frozen Operating Threshold

$$\tau = \mathbf{0.50} \quad (\text{FROZEN})$$
* Selected exclusively using validation set ROC/F1 analysis during Milestone 5/6.
* Untouched during Milestone 7 and strictly barred from external optimization in Milestone 8A.

---

## 11. External Metrics

* **Numerical External Benchmark**: **`NOT ESTIMATED`**
* **Statement**: *"External validation pending due to lack of a legally verified independent dataset."*
* **Active Scientific Benchmark**: Dataset A Official Held-Out Test Set ($N=138$):
  - Sensitivity / Recall: **80.95%** (34/42)
  - Specificity: **97.92%** (94/96)
  - Precision: **94.44%** (34/36)
  - Accuracy: **92.75%** (128/138)
  - Macro F1: **0.9106**
  - ROC-AUC: **0.9452**
  - PR-AUC: **0.9352**

---

## 12. Confidence Intervals

When valid external candidate batches are evaluated, the evaluator computes 95% Wilson binomial score intervals:
$$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}} \quad (z = 1.96)$$
For sample sizes $N < 5$, the evaluator reports `INSUFFICIENT_EXTERNAL_SAMPLE_SIZE` to prevent misleading false precision.

---

## 13. Domain Shift Analysis

Detailed in [`DOMAIN_SHIFT_REPORT.md`](file:///d:/AniCare-AI/backend/ai/models/DOMAIN_SHIFT_REPORT.md):
* Macro framing in teaching hospitals reduces distant standoff failure modes.
* Clean concrete chutes reduce false-positive background clutter.
* Downsampling high-resolution SLR captures ($>1920\times 1080$) to $224\times 224$ requires multi-crop tiling to preserve early subtle papules.

---

## 14. False-Negative Analysis Framework

Any future external false negatives must be cataloged using the standardized schema:
* `sample_id`, `confidence`, `ground_truth`, `predicted_class`
* Clinical characterization: *"possible missed visual presentation"* (never *"model misdiagnosed the animal"*)
* Visual reasons: early subtle papules, distant framing, or coat obstruction
* Escalation: Multi-Modal Clinical Risk Engine integration

---

## 15. False-Positive Analysis Framework

* Standardized tracking of healthy controls misclassified as LSD due to skin folds, dewlap shadows, or mud encrustation.
* Preserves natural external distribution without synthetic balancing.

---

## 16. Grad-CAM Review Protocol

* Uses [`gradcam.py`](file:///d:/AniCare-AI/backend/ai/explainability/gradcam.py) to generate alpha-blended attention heatmaps.
* Mandatory clinical framing:
  > *"Grad-CAM provides an interpretability aid for reviewing model attention patterns. It does not constitute biological proof of lesion localization."*

---

## 17. Safety & Regulatory Limitations

1. **Species Scope**: Model is clinically validated for **Cattle (*Bos taurus* / *Bos indicus*) ONLY**.
2. **Clinical Role**: Triage and screening aid; **not a standalone diagnostic device**.
3. **Veterinary Review**: All AI flags require clinical examination by a certified veterinarian.

---

## 18. Statistical Limitations

1. **Zero External Samples**: No empirical external generalization claims can be made until DTA completion.
2. **Historical Animal Grouping**: Dataset A lacks verified RFID ear tags; herd-independent generalization cannot be claimed.
3. **Class Distribution**: External benchmarks must reflect natural clinical prevalence rather than artificial 50/50 splits.

---

## 19. Final Conclusion

AniCare AI's Milestone 8A architecture establishes complete institutional, cryptographic, and mathematical safeguards for external validation. The system refuses to fabricate external performance metrics, preserves the frozen baseline ($\tau = 0.50$), and cleanly reports external status as pending.

---

## 20. Recommendation for Milestone 8B

* **Current Stage**: Milestone 8A Governance is complete.
* **Next Scientific Action**: Initiate formal DTA outreach to AAU Anand and ICAR-DFMD biosecurity cells.
* **Directive**: Maintain model freeze. Do NOT commence model training or retraining until genuine external data is lawfully acquired.
