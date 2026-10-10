# AniCare AI — Clinical Model Evaluation Protocol & Governance Standard

## 1. Executive Principles: Asymmetric Risk & Scientific Hygiene in Veterinary AI

In veterinary disease early warning, classification errors carry severely asymmetric clinical costs:
- **False Negative for a Notifiable Epizootic (e.g. Foot and Mouth Disease, Lumpy Skin Disease, Anthrax)**: Leads to delayed quarantine, rapid community herd transmission, devastating livestock mortality, and agricultural trade embargoes.
- **False Positive**: Triggers a precautionary physical inspection or rapid field diagnostic swab by a registered veterinary officer.

> [!IMPORTANT]
> **Sensitivity (Recall) on high-risk and contagious epizootics MUST take precedence over overall accuracy.**  
> An algorithm reporting 98% overall accuracy is medically unacceptable if its recall on 20 minority outbreak cases is only 40%. The 98% accuracy merely reflects the overwhelming numerical dominance of healthy cattle images.

---

## 2. Partition Governance & Data Roles

To prevent data snooping, target leakage, and over-optimistic performance claims, AniCare AI strictly enforces partition isolation:

```
+--------------------------------------------------------------------------------------------------+
|                                    DATASET PARTITION GOVERNANCE                                  |
+------------------------------------+----------------------------------+--------------------------+
| 1. TRAINING SET (70%)              | 2. VALIDATION SET (15%)          | 3. HELD-OUT TEST SET (15%)|
+------------------------------------+----------------------------------+--------------------------+
| • Model parameter fitting (weights)| • Model architecture comparison  | • Final official benchmark|
| • Conservative augmentations       | • Hyperparameter decisions       | • NO model tuning        |
| • Loss function optimization       | • Operating threshold selection  | • NO threshold selection |
| • Feature representation learning  | • Temperature calibration (ECE)  | • NO architecture choice |
+------------------------------------+----------------------------------+--------------------------+
```

### 2.1 Training Set (633 Images)
Used strictly for:
- Model parameter fitting and backpropagation.
- Biological data augmentation (conservative resizing, subtle blur, mild lighting jitter).
- Loss function optimization (Focal Loss $\gamma=2.0$).

### 2.2 Validation Set (135 Images)
Used strictly for:
- Comparative model selection across candidate backbones (MobileNetV3 vs EfficientNet-B0).
- Platt temperature scaling parameter optimization ($T = 1.4415$).
- **Operating threshold selection**: Frozen at $\tau^* = 0.50$ via the clinical rule `maximize recall subject to specificity >= 90% on validation`.
- Hyperparameter decisions and early stopping.

### 2.3 Held-Out Test Set (138 Images)
Used strictly for:
- Final one-time benchmark evaluation at the frozen operating point ($\tau^* = 0.50$).
- **Strict Prohibition**: No model tuning, no weight updates, no architecture selection, and no threshold optimization.

> [!WARNING]
> ### POST-HOC TEST ACCESS DISCLOSURE & TERMINOLOGY CORRECTION
> The held-out test set was not used for model training or validation-based threshold selection. During Milestone 6, post-hoc threshold diagnostics were additionally computed on the test set for error and boundary analysis.
> 
> Therefore:
> 1. These post-hoc test diagnostics **must not be used for model or threshold selection**.
> 2. The test partition is accurately defined as: **"Held-out during training and model selection, but subsequently accessed for post-hoc diagnostic threshold analysis."**
> 3. It **must NOT be described as a pristine untouched benchmark for future development**. Future model versions require an independent external test benchmark.

---

## 3. Core Quantitative Metrics Standard

### 3.1 Overall Accuracy
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
- **Role**: High-level screening metric only.
- **Clinical Limitation**: Severely misleading under class imbalance. In a dataset where 95% of images are "Healthy / Normal", a dummy classifier always predicting "Healthy" achieves 95% accuracy while failing 100% of diseased animals.

### 3.2 Precision (Positive Predictive Value)
$$\text{Precision} = \frac{TP}{TP + FP}$$
- **Clinical Meaning**: Out of all animals flagged by the AI as having a specific disease, what fraction genuinely have that condition?
- **Importance**: High precision prevents alarm fatigue among veterinary field officers.

### 3.3 Sensitivity / Recall (True Positive Rate)
$$\text{Recall} = \frac{TP}{TP + FN}$$
- **Clinical Meaning**: Out of all animals that genuinely have the disease, what fraction did the AI detect?
- **Official Milestone 6 Result**: On the held-out test partition at $\tau = 0.50$, **LSD Sensitivity is 80.95% (34 / 42 confirmed cases detected, 8 false negatives)**.
- **Reporting Rule**: The validation operating-point target was met during validation (92.50%), but the final held-out test LSD sensitivity was 80.95%, so the 92% test-sensitivity target was not achieved. Never substitute validation recall for test recall.

### 3.4 Specificity (True Negative Rate)
$$\text{Specificity} = \frac{TN}{TN + FP}$$
- **Official Result**: On the held-out test partition at $\tau = 0.50$, **Healthy Bovine Specificity is 97.92% (94 / 96 healthy bovines correctly cleared, 2 false positives)**.

### 3.5 Macro-Averaged F1 Score ($\text{Macro } F_1$)
$$\text{Macro } F_1 = \frac{1}{K} \sum_{k=1}^K F_{1, k} \quad \text{where} \quad F_{1, k} = 2 \cdot \frac{\text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$
- **Official Result**: **0.9106** on the held-out test partition. Primary balanced benchmark across minority disease and majority healthy classes.

### 3.6 Expected Calibration Error (ECE)
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
- **Official Result**: Calibrated ECE on test set is **0.1673** following validation Platt temperature scaling ($T = 1.4415$).

---

## 4. Multi-Modal Risk Scoring vs Probability Governance

The multi-modal clinical risk engine synthesizes 5 operational risk subscores:
1. `visual_risk_score` (30% weight)
2. `symptom_risk_score` (25% weight)
3. `physiological_risk_score` (20% weight)
4. `epidemiological_risk_score` (15% weight)
5. `history_risk_score` (10% weight)

> [!CAUTION]
> **GOVERNANCE ON RISK TERMINOLOGY**:
> - These engineered weights represent a **transparent weighted clinical risk-scoring framework** and an **engineering risk score designed to prioritize veterinary review**.
> - They **MUST NEVER** be described as "clinically validated disease probabilities".
> - Documentation and APIs must not state "30% probability from vision" or "85% clinical probability".
> - The platform assigns an operational triage risk level (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), NOT a confirmed epidemiological probability.

---

## 5. Visual Explainability (Grad-CAM) Governance

- Grad-CAM heatmaps represent a **visual explanation of convolutional image regions contributing to the model prediction**.
- Documentation, UI, and reports **MUST NOT** claim that "Grad-CAM proves the disease is present" or "Grad-CAM confirms diagnosis".
- Saliency maps show spatial correlation, not microbiological etiology. All heatmaps carry a mandatory veterinary review disclaimer.

---

## 6. Multi-Species Scoping Governance

- **Current Validated Model Scope**: **CATTLE ONLY (*Bos taurus* / *Bos indicus*)**.
- For Buffalo, Goat, Sheep, Poultry, Swine, and Canine:
  - The system must **NOT** present the bovine vision model as validated.
  - The API returns `MODEL_NOT_VALIDATED_FOR_SPECIES` status.
  - Requests are safely routed to syndromic symptom assessment accompanied by a mandatory veterinary review notice.

---

## 7. Future Clean External Validation Plan (Milestone 7 Roadmap)

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
