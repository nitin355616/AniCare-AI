# AniCare AI — Model Improvement Baseline & Dataset A Audit
## Scientific Pre-Experiment Verification Protocol (Milestone 8B)

**Date**: October 2026  
**Auditor**: AniCare AI Research & Governance Architecture  
**Dataset Target**: Dataset A (Mendeley Bovine LSD Image Benchmark, Curated $N=906$)  
**Baseline Model**: `AniCare-Bovine-Vision v1.0-ONNX` (`EfficientNet-B0`, $\tau = 0.50$ Frozen)  
**Governance Directive**: Absolute partition isolation; zero test set leakage into training, validation, augmentation tuning, or threshold selection.

---

## 1. Dataset Partition Audit & Class Distribution

| Partition | Total Images | Lumpy Skin Disease (LSD) | Healthy / Normal | Positive Prevalence | Partition Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Training Split** | **633** | 189 (29.86%) | 444 (70.14%) | ~1 : 2.35 ratio | Parameter learning & augmentation training |
| **Validation Split** | **135** | 40 (29.63%) | 95 (70.37%) | ~1 : 2.38 ratio | Architecture comparison, threshold tuning, calibration |
| **Held-Out Test Split** | **138** | 42 (30.43%) | 96 (69.57%) | ~1 : 2.29 ratio | **STRICTLY UNTOUCHED FINAL BENCHMARK** |
| **Total Clean Dataset** | **906** | **271** (29.91%) | **635** (70.09%) | ~1 : 2.34 ratio | Curated from 1,024 raw files (118 quarantined) |

---

## 2. Cryptographic Isolation & Data Leakage Verification

An automated SHA-256 integrity scan was executed across all 906 physical image files:

- **Total Unique File Hashes**: **906 / 906** (100.0% distinct cryptographic fingerprints).
- **Train $\cap$ Validation Overlap**: **0 images** (0.0%).
- **Train $\cap$ Test Overlap**: **0 images** (0.0%).
- **Validation $\cap$ Test Overlap**: **0 images** (0.0%).
- **Data Leakage Confirmation**:
  > **CONFIRMED**: Zero test images enter training. Zero test images enter validation. Zero test images are accessible to model selection or threshold search routines.

---

## 3. Physical Image Specifications & Preprocessing

- **Native Resolution**: Standardized to $256 \times 256$ pixels (JPEG format, 24-bit RGB color mode).
- **Input Geometry for V1 Baseline**: Resized to $224 \times 224$ pixels via bilinear interpolation.
- **Color Normalization**:
  $$\text{Mean} = [0.485, 0.456, 0.406], \quad \text{Std} = [0.229, 0.224, 0.225]$$
  (Standard ImageNet channel statistics applied across all models).
- **Label Encoding**:
  - Index `0`: `Healthy / Normal` (Negative class)
  - Index `1`: `Lumpy Skin Disease` (Positive target class)

---

## 4. Class Imbalance & Loss Configurations

In the training split, negative samples ($n=444$) outnumber positive samples ($n=189$) by approximately $2.35 : 1$.

### A. Focal Loss Configuration (Baseline V1)
$$\mathcal{L}_{\text{focal}}(p_t) = -\alpha_t (1 - p_t)^\gamma \log(p_t)$$
- Focusing parameter: $\gamma = 2.0$.
- Class balance weighting: $\alpha_0 = 0.2986$ (Healthy), $\alpha_1 = 0.7014$ (LSD), calculated dynamically from class proportions to penalize false negatives.

### B. Weighted Cross-Entropy Configuration (Alternative Candidate)
- Class weights: $w_0 = \frac{633}{2 \times 444} \approx 0.7128$, $w_1 = \frac{633}{2 \times 189} \approx 1.6746$.

---

## 5. Augmentation Pipeline Specifications

### Current Baseline V1 Pipeline
- Resize: $(224, 224)$
- RandomHorizontalFlip ($p = 0.5$)
- RandomRotation ($\pm 10^\circ$)
- ColorJitter (Brightness $\pm 0.10$, Contrast $\pm 0.10$)

### Proposed Robustness Augmentation Pipeline (Milestone 8B)
Targeting the 8 known empirical failure modes without synthetic distortion:
- **`RandomResizedCrop`** (Scale: $0.85 - 1.0$, Ratio: $0.95 - 1.05$): Directly targets `SMALL_LESION_AREA` and `DISTANT_WHOLE_ANIMAL_FRAMING`.
- **`GaussianBlur`** (Kernel: $3 \times 3$, $\sigma \in [0.1, 1.0]$): Simulates `MOTION_BLUR` and sensor softness.
- **`ColorJitter`** (Brightness $\pm 0.15$, Contrast $\pm 0.15$): Simulates `POOR_LIGHTING` and barn shadow occlusion.
- **Clinical Boundary Guard**: Extreme affine warping, elastic shear, and heavy color inversion remain strictly barred to preserve circumscribed nodule morphology.

---

## 6. Reproducibility & Random Seeds

- Global deterministic seed: **`42`** (Fixed across Python `random`, NumPy `np.random`, and PyTorch `torch.manual_seed`).
- Deterministic CuDNN / CPU execution enabled.

---

## 7. Baseline Model Reference V1 Protection Status

- Production Model: `anicare_vision_bovine_v1.onnx` (15.29 MB, Opset 14).
- Production Operating Threshold: $\tau = \mathbf{0.50}$ (FROZEN).
- Backup & Reference Archive: [`backend/ai/models/experiments/baseline_v1/`](file:///d:/AniCare-AI/backend/ai/models/experiments/baseline_v1/) (`baseline_lock.json`).
- Baseline Model Designation: **`MODEL_BASELINE_V1`** (Read-only, fully recoverable).
