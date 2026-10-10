# AniCare AI — Model Card Update (Milestone 7)

## Bovine Cutaneous Vision Model — EfficientNet-B0 (`anicare_vision_bovine_v1.onnx`)

**Model Identifier**: `anicare_vision_bovine_v1.onnx`  
**Current Milestone**: Milestone 7 — External Validation, Dataset Expansion & Field Robustness  
**Date**: October 2026  
**License**: MIT / Non-Commercial Educational Research  

---

## 1. Model Overview & Locked Configuration

- **Neural Architecture**: EfficientNet-B0 (Pretrained on ImageNet-1K, fine-tuned with Focal Loss $\gamma=2.0$).
- **Export Format**: ONNX Opset 14 (FP32, single dynamic batch).
- **Input Dimensions**: $3 \times 224 \times 224$ (RGB, normalized using ImageNet mean/std).
- **Temperature Scaling Parameter**: $T = 1.4415$ (Optimized via negative log-likelihood on validation set).
- **Operating Decision Threshold**: $\tau = 0.50$ (**PERMANENTLY FROZEN**, selected strictly on validation data).
- **Inference Runtime**: ONNX Runtime (CPU intra-op threads = 2, latency $\approx 5.8\text{ ms}$).

---

## 2. Intended Clinical Use & Prohibited Scopes

### Intended Use
- **Primary Purpose**: Visual dermatological screening assist tool for rural livestock farmers, para-veterinarians, and District Animal Husbandry Officers (DAHO).
- **Target Disease**: Bovine Lumpy Skin Disease (*Capripoxvirus* cutaneous eruptions).
- **Target Species**: **CATTLE ONLY (*Bos taurus* / *Bos indicus*)**.

### Prohibited & Out-of-Scope Uses
1. **Non-Cattle Species**:
   Prohibited for Buffalo, Goat, Sheep, Swine, Poultry, and Canine. Requests for non-cattle trigger `MODEL_NOT_VALIDATED_FOR_SPECIES` and route safely to non-visual syndromic triage with prominent veterinary review disclaimers.
2. **Autonomous Prescriptions**:
   The model does NOT prescribe antibiotics, antivirals, or dosages. Physical examination by a registered veterinary practitioner is legally mandatory.
3. **Stand-Alone Confirmatory Diagnosis**:
   Visual nodules cannot substitute for laboratory confirmation (Capripox real-time RT-PCR) during transboundary disease outbreaks.

---

## 3. Official Quantitative Performance (Locked Benchmark)

All historical benchmark metrics from Milestones 5 & 6 are permanently retained without alteration:

| Metric | Dataset A Validation ($N=135$) | Dataset A Held-Out Test ($N=138$) | Dataset B External ($N=\text{Pending}$) |
| :--- | :---: | :---: | :---: |
| **Selection / Use** | Threshold Selection Source | Post-Hoc Error Audit Only | Generalization Assessment |
| **Operating Threshold** | **0.50** | **0.50** | **0.50** |
| **LSD Sensitivity (Recall)** | **92.50%** (37/40) | **80.95%** (34/42) | *Pending verified dataset* |
| **Specificity** | **94.74%** (90/95) | **97.92%** (94/96) | *Pending verified dataset* |
| **Precision** | 88.10% (37/42) | 94.44% (34/36) | *Pending verified dataset* |
| **Macro F1 Score** | **0.9329** | **0.9106** | *Pending verified dataset* |
| **ROC-AUC** | 0.9855 | 0.9452 | *Pending verified dataset* |
| **False Negatives (FN)** | 3 | **8** | *Pending verified dataset* |
| **False Positives (FP)** | 5 | **2** | *Pending verified dataset* |
| **Average CPU Latency** | 5.82 ms | 5.86 ms | *Pending verified dataset* |

*Honest Reporting Rule: The 80.95% held-out test recall is the official baseline and is NEVER substituted with the 92.50% validation score.*

---

## 4. Milestone 7 Governance Upgrades

1. **Dataset B Validation Pipeline (`DatasetBPipeline`)**:
   - Enforces cross-dataset deduplication against Dataset A (quarantines exact SHA-256 and dHash $\le 5$ matches).
   - Provenance gatekeeper prevents unauthorized data ingestion.
2. **Field Robustness Taxonomy (12 Categories)**:
   - Identifies `MUD_DEBRIS_OBSTRUCTION`, `DISTANT_WHOLE_ANIMAL_FRAMING`, `SMALL_LESION_AREA`, and `EARLY_SUBTLE_PAPULES` as primary empirical failure drivers.
   - Enforces sample size threshold $n \ge 5$ before computing percentage metrics.
3. **Dataset C Pristine Benchmark Infrastructure**:
   - Established in `backend/ai/dataset/external/` with `STATUS = PENDING` and strict non-leakage locks.
4. **Explainability & Risk Score Boundaries**:
   - Grad-CAM visual heatmaps are documented as *model attention visualizations*, NOT clinical proofs.
   - 5-modality risk scores are transparent *clinical triage priority rankings*, NOT medical probabilities.
   - `animal_grouping_available = false` is formally recorded; herd-independent generalization is not claimed.
