# AniCare AI — Model Card Template: Veterinary Vision Inference Engine

Following the framework proposed by Mitchell et al. (*Model Cards for Model Reporting*, FAT* 2019) and adapted for veterinary healthcare intelligence.

---

## 1. Model Details

- **Model Identifier**: `anicare-vision-{species}-v{version}` (e.g. `anicare-vision-bovine-v1.0.0`)
- **Model Version**: `1.0.0`
- **Release Date**: `[YYYY-MM-DD]`
- **Model Type**: Deep Convolutional Neural Network / Vision Transformer (e.g., EfficientNet-B0)
- **Framework**: PyTorch / ONNX Runtime
- **Pretrained Weights**: ImageNet-1k (supervised) or self-supervised domain adaptation
- **Frozen Operating Threshold**: `TAU = [Value]` (Selected strictly using Validation set; test set not used for selection)
- **Licensing**: CC BY 4.0 / Apache 2.0 / MIT

---

## 2. Intended Use & Clinical Scope

### 2.1 Primary Intended Applications
- **AI-assisted visual assessment of possible animal diseases from photographic images.**
- Preliminary triage and decision support for frontline veterinary officers, para-veterinarians, and dairy farmers.
- Automated syndromic alerting to trigger timely field veterinary visits.

### 2.2 Out-of-Scope / Prohibited Applications
- **Definitive diagnosis** without on-site clinical examination and confirmatory laboratory testing.
- **Autonomous veterinary prescription generation** or drug dosage calculation.
- **Laboratory-confirmed disease diagnosis**.
- **Use on unsupported livestock species**.
- Autonomous certification of animal disease status for inter-state livestock movement or trade export.

### 2.3 Validated Species Scope
- Explicit declaration of species currently validated (e.g., Cattle only). Unvalidated species must return `MODEL_NOT_VALIDATED_FOR_SPECIES` and route to syndromic assessment.

### 2.4 Validated Disease Task
- Explicit definition of visual classification task (e.g., Bovine Lumpy Skin Disease vs. Healthy Skin baseline).

---

## 3. Data & Training Setup

- **Dataset Identifier**: Curated Veterinary Dataset Benchmark
- **Input Dimensions**: 224 × 224 × 3 (RGB), normalized to ImageNet mean and standard deviation.
- **Partitions**:
  - Training Set: Parameter fitting and optimization.
  - Validation Set: Model comparison, threshold selection, calibration temperature fitting, hyperparameter choices.
  - Held-Out Test Set: Final one-time benchmark evaluation at frozen operating threshold.
- **Data Augmentation Strategy**: Biologically conservative transforms (RandomResizedCrop, mild color jitter, subtle Gaussian blur) protecting veterinary dermatological signs.
- **Loss Function**: Multi-class Focal Loss ($\gamma = 2.0$) or class-weighted cross-entropy.

---

## 4. Quantitative Evaluation

### 4.1 Partition Governance
- **Validation-Guided Selection**: Operating thresholds must be chosen strictly on the validation set.
- **Post-Hoc Test Access Disclosure**: If post-hoc diagnostics are run on the test set, document clearly:
  *"The held-out test set was not used for model training or validation-based threshold selection. Post-hoc diagnostics computed on the test set must not be used for model or threshold selection."*

### 4.2 Official Metrics Table
| Metric | Target Standard | Validation Set | Official Test Set |
| :--- | :--- | :--- | :--- |
| **Top-1 Accuracy** | $\ge 90.0\%$ | *[Val Result]* | *[Test Result]* |
| **Macro F1 Score** | $\ge 0.90$ | *[Val Result]* | *[Test Result]* |
| **Disease Recall (Sensitivity)** | Target standard (e.g., $\ge 92\%$) | *[Val Result]* | *[Test Result]* |
| **Healthy Specificity** | $\ge 95.0\%$ | *[Val Result]* | *[Test Result]* |
| **Expected Calibration Error (ECE)** | $\le 0.15$ | *[Val Result]* | *[Test Result]* |

---

## 5. Known Limitations & Scientific Boundaries

1. **Dataset Scale & Diversity**: Sample count and breed coverage limitations.
2. **Animal Grouping Status**: Declare whether animal-level grouping was available (`animal_grouping_available = true/false`). Never claim herd-independent generalization if RFID grouping was absent.
3. **External Validation Requirement**: Multi-center external validation on independent cohorts from differing institutions.
4. **Real-World Domain Shift**: Variations in hair coat, mud, lighting, and camera sensors.
5. **Early or Subtle Lesions**: Incipient flat papules can be missed.
6. **Distant Framing & Occlusion**: Wide framing dilutes lesion pixel ratio; pen slats or mud can obscure lesions.
7. **Sensitivity Gap Disclosure**: Transparently declare whether target sensitivity was met on the test set.

---

## 6. Multi-Modal Risk Scoring & Explainability Principles

- **Engineered Risk Scoring**: Multi-modal risk scores represent a transparent weighted clinical risk-scoring framework to prioritize veterinary review, NOT clinically validated probabilities.
- **Grad-CAM Explainability**: Indicates image regions contributing to the convolutional network's prediction. Does NOT prove disease presence.
- **Mandatory Veterinary Safety Statement**:
  > [!IMPORTANT]
  > This AI model predicts a **POSSIBLE VISUAL CONDITION** and assigns an operational triage risk level. It **DOES NOT** provide a confirmed medical diagnosis or issue pharmaceutical prescriptions. All high-risk indications must be confirmed on-site by a registered veterinary practitioner.
