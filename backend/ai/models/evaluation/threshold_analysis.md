# AniCare AI — Validation-Only Operating Threshold Analysis & Post-Hoc Diagnostics

**Milestone**: Milestone 6 — Evaluation Protocol Correction & Multi-Modal Intelligence  
**Methodology**: Threshold selection was performed **exclusively on the 135-sample validation set**.  
**Frozen Threshold**: `TAU = 0.50` (selected on validation only; test data was NOT used for threshold selection).  

> [!IMPORTANT]
> **TEST-SET TERMINOLOGY & SCIENTIFIC INTEGRITY DECLARATION**:  
> The held-out test set was not used for model training or validation-based threshold selection. During Milestone 6, post-hoc threshold diagnostics were additionally computed on the test set for analysis. Therefore, these post-hoc test diagnostics must not be used for model or threshold selection. The validation operating-point target was met during validation, but the final held-out test LSD sensitivity was 80.95%, so the 92% test-sensitivity target was not achieved.

---

## 1. Validation Set Threshold Sweep (135 Images: 40 LSD, 95 Healthy)

*Threshold Selection was conducted strictly on this validation partition:*

| Threshold | LSD Recall (Sens.) | Healthy Specificity | LSD Precision | Macro F1 | False Negative Rate (FNR) | False Positive Rate (FPR) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `0.30` | 95.00% | 66.32% | 54.29% | **0.7392** | 5.00% | 33.68% |
| `0.35` | 95.00% | 73.68% | 60.32% | **0.7881** | 5.00% | 26.32% |
| `0.40` | 95.00% | 82.11% | 69.09% | **0.8457** | 5.00% | 17.89% |
| `0.45` | 95.00% | 89.47% | 79.17% | **0.8989** | 5.00% | 10.53% |
| `0.50` **(Selected & Frozen)** | 92.50% | 95.79% | 90.24% | **0.9383** | 7.50% | 4.21% |
| `0.55` | 85.00% | 95.79% | 89.47% | **0.9099** | 15.00% | 4.21% |
| `0.60` | 75.00% | 97.89% | 93.75% | **0.8864** | 25.00% | 2.11% |
| `0.65` | 67.50% | 97.89% | 93.10% | **0.8540** | 32.50% | 2.11% |
| `0.70` | 47.50% | 98.95% | 95.00% | **0.7643** | 52.50% | 1.05% |

---

## 2. Selection Rationale (Validation Only)

- **Frozen Operating Threshold**: **`TAU = 0.50`**
- **Validation-Only Selection Rule**: `maximize recall subject to specificity >= 90% on validation`.
- **Validation Metrics at Selected Threshold**: Sensitivity = **92.50%**, Specificity = **95.79%**, Macro F1 = **0.9383**.
- **Decoupled Deployment**: The threshold is frozen at `0.50` for all real-time inference runs. Test metrics were not consulted during selection.

---

## 3. Official Held-Out Test Set Benchmark (`TAU = 0.50`)

Evaluated on the held-out test partition (138 images: 42 LSD, 96 Healthy):

| Metric | Value | Interpretation |
| :--- | :---: | :--- |
| **Overall Accuracy** | **92.75%** | 128 / 138 total correct classifications |
| **Macro F1-Score** | **0.9106** | Balanced harmonic mean across both classes |
| **LSD Sensitivity (Recall)** | **80.95%** | **34 / 42** confirmed LSD lesions detected (**8 false negatives**) |
| **LSD Precision** | **94.44%** | 34 / 36 positive alerts were true lesions (**2 false alarms**) |
| **Healthy Bovine Specificity** | **97.92%** | **94 / 96** healthy bovines correctly screened |
| **ROC-AUC** | **0.9452** | Area under receiver operating characteristic |
| **PR-AUC** | **0.9352** | Area under precision-recall curve |
| **Calibrated ECE** | **0.1673** | Expected Calibration Error after Platt temperature scaling ($T=1.4415$) |

> [!WARNING]
> **TARGET RESULT DECLARATION**:  
> The validation operating-point target was met during validation, but the final held-out test LSD sensitivity was 80.95%, so the 92% test-sensitivity target was not achieved.

---

## 4. Post-Hoc Test-Set Diagnostic Analysis

> [!CAUTION]
> **POST-HOC DIAGNOSTICS WARNING**:  
> Post-hoc test-set diagnostic analysis — **NOT used for model selection or threshold selection**. These test-set threshold diagnostics were computed after the model/operating point had been defined and are reported only for error analysis. They must not be interpreted as independent threshold-selection evidence.

| Threshold | Test LSD Recall | Test Specificity | Test Precision | Test Macro F1 | Test FNs (Missed) | Test FPs (Alarms) | Diagnostic Context |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `0.30` | 92.86% | 68.75% | 56.52% | 0.7514 | 3 | 30 | Diagnostic exploratory point |
| `0.35` | 90.48% | 76.04% | 62.30% | 0.7909 | 4 | 23 | Diagnostic exploratory point |
| `0.40` | 90.48% | 85.42% | 73.08% | 0.8548 | 4 | 14 | Diagnostic exploratory point |
| `0.45` | 85.71% | 95.83% | 90.00% | 0.9133 | 6 | 4 | Diagnostic exploratory point |
| `0.50` | 80.95% | 97.92% | 94.44% | 0.9106 | 8 | 2 | **Official Operating Point** |
| `0.55` | 80.95% | 98.96% | 97.14% | 0.9189 | 8 | 1 | Diagnostic exploratory point |
| `0.60` | 76.19% | 98.96% | 96.97% | 0.8993 | 10 | 1 | Diagnostic exploratory point |
| `0.65` | 71.43% | 98.96% | 96.77% | 0.8789 | 12 | 1 | Diagnostic exploratory point |
| `0.70` | 66.67% | 100.00% | 100.00% | 0.8660 | 14 | 0 | Diagnostic exploratory point |

---

## 5. Regulatory & Veterinary Safety Principles

1. **Frozen Operating Threshold**: Operating threshold `TAU = 0.50` is permanently frozen in `ai_config.OPERATING_THRESHOLD`.
2. **Transparent Risk Decoupling**: The system presents raw calibrated probability, visual triage tier, and multi-modal clinical risk score independently.
3. **Human-in-the-Loop Veterinary Mandate**: Neither threshold guarantees 100% sensitivity; physical on-site examination by a registered veterinary officer remains mandatory for all cases.