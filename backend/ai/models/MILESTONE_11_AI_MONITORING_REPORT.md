# AniCare AI — Milestone 11 Technical & Governance Report
## AI Model Monitoring, Field Feedback, Drift Detection & Continuous Learning Architecture

**Project**: AniCare AI — AI-Powered Animal Health & Disease Early Warning System (SIH 2026)  
**Milestone**: Milestone 11  
**Status**: COMPLETE & VERIFIED  
**Date**: October 2026  
**Test Suite Pass Rate**: 100% (173/173 backend pytest tests passing)  

---

## 1. Executive Summary & Core Invariants

Milestone 11 establishes a robust, clinically safe **Continuous Learning and Model Governance Architecture** for AniCare AI. In rural livestock veterinary deployments, production vision models face distribution shifts due to variable smartphone sensors, inconsistent outdoor lighting, seasonal coat changes, and atypical lesion presentations. 

Unlike naive automated systems that risk catastrophic model degradation or data contamination, AniCare AI implements a **closed-loop clinical governance framework** where:
1. **Production Model Immutability**: The official baseline model (`anicare_vision_bovine_v1.onnx`, 15.29 MB, EfficientNet-B0, opset 14, SHA-256: `594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d`) and its operating threshold ($\tau = 0.50$) remain **100% frozen and untouched**.
2. **Held-Out Test Set Preservation**: The Dataset A held-out test set ($N=138$, 42 LSD positive, 96 healthy) is strictly isolated and never contaminated with training or feedback samples.
3. **Legal Dataset Quarantine**: External Dataset B remains strictly quarantined under `PERMISSION_REQUIRED` status in compliance with Milestone 8A governance.
4. **No Autonomous Promotion**: Drift alerts and veterinary reviews never trigger automated retraining or autonomous production deployment; all model promotions require explicit human governance sign-off and satisfy 7 mandatory promotion gates.
5. **Role-Based Feedback Gate**: Only certified veterinarians with statutory registration credentials can submit ground-truth diagnostic reviews. Farmer submissions are strictly blocked ($403\text{ Forbidden}$).

---

## 2. System Architecture

```text
               +-------------------------------------------------------------+
               |              Livestock Visual Screening Event                |
               +-------------------------------------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |           Inference Telemetry & Quality Engine              |
               |  - Gradient energy blur score  - Lighting luminance check   |
               |  - Species anomaly detection   - Low-confidence tagging     |
               +-------------------------------------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |             Frozen Production Inference Engine              |
               |  - EfficientNet-B0 ONNX (15.29 MB)                          |
               |  - Frozen Operating Threshold tau = 0.50                    |
               +-------------------------------------------------------------+
                         |                                       |
                         v                                       v
        +----------------------------------+   +----------------------------------+
        |   Statistical Drift Monitor      |   |   Veterinary Clinical Review     |
        |   - Population Stability Index   |   |   - Licensed Vet Decision Gate   |
        |   - Confidence Decile Shifts     |   |   - Agreement / Modify / Reject  |
        |   - Prevalence & Blur Monitors   |   |   - Farmers Blocked (HTTP 403)   |
        +----------------------------------+   +----------------------------------+
                         |                                       |
                         v                                       v
        +----------------------------------+   +----------------------------------+
        |   Governance Alerts & Dashboard  |   |   8-Stage Data Curation Pipeline |
        |   - Normal / Watch / Warning     |   |   - SHA-256 + 64-bit dHash Dedupe|
        |   - Multi-Signal Recommendations |   |   - 0% Cross-Split Leakage Guard |
        +----------------------------------+   |   - Licensing & Tier Provenance  |
                                               +----------------------------------+
                                                                 |
                                                                 v
                                               +----------------------------------+
                                               |   Candidate Dataset Admission    |
                                               |   - Train / Validation Split     |
                                               |   - Held-Out Test Set UNTOUCHED  |
                                               +----------------------------------+
                                                                 |
                                                                 v
                                               +----------------------------------+
                                               |   Cryptographic Model Registry   |
                                               |   - Shadow Evaluation Matrix     |
                                               |   - 7 Gated Promotion Checks     |
                                               |   - Emergency Rollback Protocol  |
                                               +----------------------------------+
```

---

## 3. Cryptographic Model Registry & Lifecycle Engine

The Model Registry enforces cryptographic accountability for all model weights and metadata:

### 3.1 Singleton Production Invariant
- Exactly **one** model can occupy `PRODUCTION` status across the entire system.
- Promoting a candidate model atomically transitions the active production model to `RETIRED`.
- Any attempt to register multiple simultaneous production models is rejected with a validation error.

### 3.2 Model Lifecycle States
| Lifecycle State | Description | Routing Behavior |
| :--- | :--- | :--- |
| `EXPERIMENTAL` | Newly registered candidate undergoing initial smoke testing | Inactive in production |
| `VALIDATION` | Offline benchmarking against validation splits | Inactive in production |
| `SHADOW` | Silent parallel evaluation alongside production on live telemetry | Generates shadow predictions without affecting farmer/vet output |
| `APPROVED` | Satisfied all benchmark and leakage gates; signed off by governance committee | Eligible for promotion |
| `PRODUCTION` | Active authoritative clinical inference model | 100% live traffic |
| `RETIRED` | Previous production model archived for emergency rollback | Standby target |
| `REJECTED` | Failed one or more promotion gates or exhibited clinical regression | Quarantined |

### 3.3 Cryptographic Integrity Verification
On startup and prior to every promotion, the registry computes the SHA-256 digest of the physical ONNX weights on disk and verifies exact matching against the model manifest:
- **Baseline Model SHA-256**: `594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d`
- **Integrity Status**: `VALID`
- **Immutability Lock**: `ENABLED`

---

## 4. 8-Stage Feedback Curation & Leakage Guard Pipeline

Raw field images and feedback cannot enter retraining datasets without rigorous screening. The 8-stage curation pipeline enforces:

1. **Format & Integrity Check**: Verifies MIME types (`image/jpeg`, `image/png`), parses image headers, and filters out corrupted payloads.
2. **Image Quality Gate**:
   - Resolution check (minimum $224 \times 224$).
   - Brightness check (rejecting severe underexposure $<30$ or overexposure $>230$).
   - Blur energy score: Evaluates Sobel/Laplacian gradient energy to detect motion blur.
3. **Out-of-Domain & Species Gate**: Identifies unsupported species (e.g. canine, avian) or non-animal imagery, routing them to out-of-domain telemetry.
4. **Perceptual & Cryptographic Deduplication**:
   - SHA-256 exact matching.
   - 64-bit difference hash (`dHash`) with Hamming distance threshold $\le 5$ to detect cropped, resized, or re-compressed duplicates.
5. **Licensing & Permission Verification**: Confirms verified open-access CC-BY or institutional ethics authorization. All Dataset B samples remain blocked under `PERMISSION_REQUIRED`.
6. **Clinical Ground-Truth Tiering**:
   - `Tier 1: LAB_CONFIRMED` (RT-PCR, ELISA, viral isolation).
   - `Tier 2: VET_REVIEWED` (Licensed veterinary officer physical examination).
   - `Tier 3: UNVERIFIED` (Rejected from candidate training).
7. **Leakage Guard (0% Cross-Split Contamination)**:
   - Enforces animal-level clustering (`animal_id`) so all images of a specific animal reside strictly in either train or validation, preventing intra-subject identity leakage.
   - Zero overlap with Dataset A held-out test set ($N=138$).
8. **Candidate Dataset Admission**: Writes sanitized metadata and image tensors into versioned candidate pools.

---

## 5. Statistical Population Drift Monitoring (PSI Engine)

The drift engine monitors real-world field telemetry against the frozen baseline distribution:

### 5.1 Population Stability Index (PSI) Formulation
For 10 confidence deciles $b \in \{[0.0, 0.1), [0.1, 0.2), \dots, [0.9, 1.0]\}$:
$$\text{PSI} = \sum_{b=1}^{10} \Big( P_{\text{actual}}(b) - P_{\text{baseline}}(b) \Big) \times \ln\left( \frac{P_{\text{actual}}(b) + \epsilon}{P_{\text{baseline}}(b) + \epsilon} \right)$$
where $\epsilon = 10^{-6}$ protects against zero division.

### 5.2 Regulatory Drift Tiers
- **NORMAL** ($\text{PSI} < 0.10$): Population distribution stable. Production inference healthy.
- **WATCH** ($0.10 \le \text{PSI} < 0.20$): Minor shift detected. Increase telemetry frequency.
- **WARNING** ($0.20 \le \text{PSI} < 0.25$): Notable shift. Alert veterinary officers and audit input image lighting/blur.
- **CRITICAL** ($\text{PSI} \ge 0.25$): Severe distribution shift. Flag for urgent clinical review and shadow model benchmarking.

### 5.3 Multi-Signal Detection
In addition to confidence PSI, the drift engine evaluates:
- **Prevalence Shift**: Compares the proportion of positive LSD screenings against the baseline test prevalence ($42 / 138 = 30.43\%$).
- **Illumination Shift**: Monitors the fraction of underexposed or overexposed field photos.
- **Blur Shift**: Tracks the percentage of images flagged with high motion blur.
- **Out-of-Domain Anomaly Rate**: Flags sudden surges in unsupported species or non-lesional queries.

---

## 6. Model Benchmark Matrix (Dataset A Held-Out Test, $N=138$)

| Metric | Production V1 (`EXP-01`) | Candidate V2 Shadow (`EXP-011`) | Relative Delta | Promotion Gate Status |
| :--- | :--- | :--- | :--- | :--- |
| **Model Weights** | `anicare_vision_bovine_v1.onnx` | `anicare_vision_bovine_v2_experimental.onnx` | — | Cryptographically Distinct |
| **Model Size** | 15.29 MB | 15.29 MB | 0.00 MB | $\le 25$ MB Passed |
| **Architecture** | EfficientNet-B0 | EfficientNet-B0 + Hard Negatives | — | Standardized |
| **Threshold ($\tau$)** | **0.50 (Frozen)** | **0.50 (Frozen)** | **0.00** | Immutability Preserved |
| **Sensitivity** | 80.95% (34/42) | 83.33% (35/42) | +2.38% | Non-Inferior ($\ge 80.95\%$) |
| **Specificity** | 97.92% (94/96) | 97.92% (94/96) | 0.00% | Non-Inferior ($\ge 97.92\%$) |
| **Precision** | 94.44% | 94.59% | +0.15% | Non-Inferior |
| **Macro F1** | 0.9106 | 0.9214 | +0.0108 | Improved |
| **ROC-AUC** | 0.9452 | 0.9510 | +0.0058 | Improved |
| **PR-AUC** | 0.9352 | 0.9420 | +0.0068 | Improved |
| **ECE (Calibration)**| 0.1673 | 0.1412 | -0.0261 (Better) | $\le 0.20$ Passed |
| **Latency (p95)** | 142 ms | 146 ms | +4 ms | $< 500$ ms Passed |
| **Leakage Contamination**| 0.0% | 0.0% | 0.0% | Zero Leakage Passed |

---

## 7. Seven Non-Negotiable Promotion Gates

Before any candidate model can be promoted to `PRODUCTION`:
1. **Gate 1 — Cryptographic Integrity**: Binary digest matches registered SHA-256 manifest exactly.
2. **Gate 2 — Zero Leakage**: Cross-split leakage between candidate training, validation, and Dataset A held-out test is verified at strictly $0.0\%$.
3. **Gate 3 — Verified Dataset Licensing**: All admitted samples have verified open research or statutory ethics licensing.
4. **Gate 4 — Non-Inferior Clinical Benchmark**:
   - Sensitivity $\ge 80.95\%$
   - Specificity $\ge 97.92\%$
   - Macro F1 $\ge 0.9106$
5. **Gate 5 — Calibration Quality**: Expected Calibration Error $\text{ECE} \le 0.20$ at operating threshold $\tau = 0.50$.
6. **Gate 6 — Latency Constraint**: Mean inference latency $< 500$ ms on standard CPU runtime.
7. **Gate 7 — Human Governance Sign-Off**: Immutable audit log entry signed by authorized veterinary officer or AI governance lead.

---

## 8. Emergency Rollback Protocol

If an unexpected post-promotion anomaly is detected in the field:
1. The emergency rollback endpoint (`POST /api/ai-monitoring/rollback`) or UI button is triggered.
2. The system locates the most recent model in `RETIRED` status that was previously in production.
3. The current production model is transitioned to `RETIRED`.
4. The previous model is restored to `PRODUCTION` with an immutable audit entry.
5. All live inference requests immediately switch over within $<50$ ms with zero server downtime.

---

## 9. Verification & Pytest Results

The entire AniCare AI backend test suite was executed:
```text
======================= 173 passed, 1 warning in 21.21s =======================
```
- `test_milestone11_ai_monitoring.py`: **19/19 passed** (100%)
- `test_milestone9c_outbreak_intelligence.py`: **8/8 passed** (100%)
- `test_vision_model.py`: **8/8 passed** (100%)
- Full regression (all 15 test suites): **173/173 passed** (100%)
- Frontend Vite production build: **Compiled in 15.64s with 0 errors**.
