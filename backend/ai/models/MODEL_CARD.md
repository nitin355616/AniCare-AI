# Model Card: AniCare Bovine Vision v1 (`anicare_vision_bovine_v1`)

## 1. Model Details
- **Model Name**: AniCare Bovine Vision Classifier v1.0
- **Model Identifier**: `anicare_vision_bovine_v1`
- **Architecture**: EfficientNet-B0 (Compound Scaled MBConv blocks)
- **Framework**: PyTorch 2.14 / Exported to ONNX Opset 14
- **Parameters**: 4,010,110 (15.29 MB ONNX graph)
- **Deployment Runtime**: ONNX Runtime (`onnxruntime` CPUExecutionProvider)
- **Frozen Operating Threshold**: `TAU = 0.50` (selected strictly on validation partition; test metrics NOT used for selection)
- **Release Date**: October 2026
- **License**: CC BY 4.0 (Dataset derivative and project model)
- **Developer**: AniCare AI Engineering Team (Smart India Hackathon 2026)

---

## 2. Clinical Scope & Intended Use

### 2.1 Intended Use
- **Primary Use**: **AI-assisted visual assessment of possible bovine Lumpy Skin Disease from animal images.**
- **Target Task**: Binary visual triage: Bovine Lumpy Skin Disease (*Capripoxvirus*) cutaneous lesions vs. Healthy / Normal skin baseline.
- **Intended Users**: Field veterinary officers, para-veterinarians, dairy cooperative extension workers, and dairy farmers.

### 2.2 NOT Intended For (Prohibited Applications)
- **Definitive diagnosis** without physical examination and laboratory confirmation.
- **Autonomous veterinary prescription generation** or drug dosage calculation.
- **Laboratory-confirmed disease diagnosis** (PCR, ELISA, or histopathology remains mandatory).
- **Use on unsupported species** (Buffalo, Goat, Sheep, Poultry, Swine, Canine).
- Non-cutaneous pathologies (internal visceral, systemic, or ocular-only lesions).

### 2.3 Current Validated Species
- **Cattle Only (*Bos taurus* / *Bos indicus*)**.
- All non-cattle livestock are flagged as `MODEL_NOT_VALIDATED_FOR_SPECIES` and routed safely to syndromic clinical evaluation.

### 2.4 Current Validated Visual Disease Task
- **Bovine Lumpy Skin Disease vs. Healthy Skin Baseline**.

---

## 3. Training Data & Methodology
- **Source**: Mendeley Data (*Lumpy Skin Disease Dataset*, DOI: 10.17632/v5nd444p5b.2).
- **Curated Dataset Size**: 906 clean verified images (271 Lumpy Skin Disease, 635 Healthy / Normal).
- **Partitions**:
  - Train: 633 images (70%)
  - Validation: 135 images (15%)
  - Held-Out Test: 138 images (15%)
- **Training Strategy**: Two-phase transfer learning from ImageNet-1k backbone.
  - Phase 1: 5 epochs, classification head only ($LR = 1 \times 10^{-3}$).
  - Phase 2: Up to 8 epochs, top MBConv blocks fine-tuned ($LR = 1 \times 10^{-4}$ with Cosine Annealing).
- **Loss Function**: Multi-class Focal Loss ($\gamma = 2.0, \alpha = [1.0, 2.34]$).
- **Operating Threshold Selection**: Selected strictly on the validation set using the rule `maximize recall subject to specificity >= 90%`. Frozen at $\tau^* = 0.50$.

---

## 4. Quantitative Performance

### 4.1 Validation Set Performance (135 Images)
- **Validation Accuracy**: 94.81%
- **Validation Macro F1**: 0.9383
- **Validation LSD Sensitivity (Recall)**: 92.50% (37 / 40)
- **Validation Specificity**: 95.79% (91 / 95)

### 4.2 Official Held-Out Test Set Benchmark (`TAU = 0.50`, 138 Images)
| Metric | Value | Interpretation |
| :--- | :---: | :--- |
| **Accuracy** | **92.75%** | 128 / 138 total correct classifications |
| **Macro F1-Score** | **0.9106** | Balanced harmonic mean across both classes |
| **LSD Sensitivity (Recall)** | **80.95%** | **34 / 42** confirmed LSD cases detected (**8 false negatives**) |
| **LSD Precision** | **94.44%** | 34 / 36 positive calls were true lesions (**2 false alarms**) |
| **Healthy Specificity** | **97.92%** | **94 / 96** healthy bovines correctly cleared |
| **ROC-AUC** | **0.9452** | Area under receiver operating characteristic |
| **PR-AUC** | **0.9352** | Area under precision-recall curve |
| **Calibrated ECE** | **0.1673** | Expected Calibration Error after Platt temperature scaling ($T=1.4415$) |

> [!WARNING]
> ### SENSITIVITY TARGET DECLARATION
> The validation operating-point target was met during validation (**92.50%**), but the final held-out test LSD sensitivity was **80.95%**, so the 92% test-sensitivity target was **NOT ACHIEVED**.

### 4.3 Post-Hoc Test-Set Diagnostic Analysis
> [!CAUTION]
> **POST-HOC DIAGNOSTICS WARNING**:  
> Post-hoc test-set diagnostic analysis — **NOT used for model selection or threshold selection**. These test-set threshold diagnostics were computed after the model/operating point had been defined and are reported only for error analysis. They must not be interpreted as independent threshold-selection evidence.

| Threshold | Test LSD Recall | Test Specificity | Test Precision | Test Macro F1 | Test FNs (Missed) | Test FPs (Alarms) | Diagnostic Role |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `0.30` | 92.86% | 68.75% | 56.52% | 0.7514 | 3 | 30 | Post-hoc diagnostic exploratory point |
| `0.35` | 90.48% | 76.04% | 62.30% | 0.7909 | 4 | 23 | Post-hoc diagnostic exploratory point |
| `0.40` | 90.48% | 85.42% | 73.08% | 0.8548 | 4 | 14 | Post-hoc diagnostic exploratory point |
| `0.45` | 85.71% | 95.83% | 90.00% | 0.9133 | 6 | 4 | Post-hoc diagnostic exploratory point |
| **`0.50`** | **80.95%** | **97.92%** | **94.44%** | **0.9106** | **8** | **2** | **Official Frozen Operating Point** |
| `0.55` | 76.19% | 98.96% | 96.97% | 0.9023 | 10 | 1 | Post-hoc diagnostic exploratory point |
| `0.60` | 71.43% | 98.96% | 96.77% | 0.8803 | 12 | 1 | Post-hoc diagnostic exploratory point |

---

## 5. Known Limitations & Scientific Boundaries

1. **Relatively Small Curated Dataset**:
   - Total of 906 clean verified images. While curated to remove duplicates and artifacts, training scale is constrained.
2. **Animal-Level Grouping Unavailable in Source Dataset**:
   - `animal_grouping_available = false` in source repository. Individual cow RFID tags were not recorded in the original paper.
   - **Therefore, the model cannot scientifically claim herd-independent generalization.**
3. **External Validation Still Required**:
   - Model has been benchmarked on a split of the primary dataset; multi-center external validation on independent cohorts from differing states is planned for Milestone 7.
4. **Real-World Domain Shift Possible**:
   - Differences in climate, coat color, breeds (*Bos indicus* zebu vs *Bos taurus* crossbreds), and pen bedding can induce performance shifts.
5. **Early / Subtle Lesions Can Be Missed**:
   - Flat, non-ulcerated papules ($0.5–1.5$cm) accounted for 37.5% of false negatives (`EARLY_SUBTLE_PAPULES`).
6. **Distant Images Reduce Performance**:
   - Lesions occupying $<2\%$ of field of view can be attenuated during $224 \times 224$ resizing (`DISTANT_WHOLE_ANIMAL_FRAMING`).
7. **Mud, Debris, and Occlusion**:
   - Crusted mud, wallow soil, pen railings, and halters can mask cutaneous nodules.
8. **Test LSD Sensitivity Currently 80.95%**:
   - Missed 8 out of 42 test cases. Early detection requires multi-modal clinical risk scoring (vitals + symptoms) rather than visual reliance alone.
9. **Test Set Status**:
   - The held-out test set was not used for model training or validation-based threshold selection. During Milestone 6, post-hoc threshold diagnostics were additionally computed on the test set for analysis. Therefore, it should not be described as a pristine untouched benchmark for future development.

---

## 6. Multi-Modal Risk Scoring & Explainability Principles

- **Engineered Risk Scoring**: The multi-modal clinical risk engine synthesizes 5 subscores (visual, symptom, physiological, epidemiological, history). These represent a **transparent weighted clinical risk-scoring framework designed to prioritize veterinary review**, NOT clinically validated disease probabilities.
- **Grad-CAM Explainability**: Visual saliency heatmaps indicate **image regions contributing to the convolutional network's prediction**. Grad-CAM does NOT prove disease presence.
- **Veterinary Safety Directive**:
  > [!IMPORTANT]
  > This AI model predicts a **POSSIBLE VISUAL CONDITION** and assigns an operational triage risk level. It **DOES NOT** provide a confirmed medical diagnosis or issue pharmaceutical prescriptions. All high-risk indications must be confirmed on-site by a registered veterinary practitioner.
