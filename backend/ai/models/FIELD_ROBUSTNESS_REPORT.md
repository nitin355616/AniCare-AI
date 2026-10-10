# AniCare AI — Field Robustness Evaluation & Failure Analysis Report

**Project**: AniCare AI — AI-Powered Animal Health & Disease Early-Warning System (SIH 2026)  
**Milestone**: Milestone 7 — Field Robustness & Environmental Failure Analysis  
**Model Architecture**: EfficientNet-B0 (`anicare_vision_bovine_v1.onnx`)  
**Operating Threshold**: $\tau = 0.50$ (**FROZEN**, selected strictly on validation data)  
**Evaluation Partition**: Dataset A Official Held-Out Test Set ($N=138$: 42 LSD, 96 Healthy)  

---

## 1. Field Robustness Taxonomy Framework

Real-world veterinary field triage occurs under adverse agricultural conditions. AniCare AI establishes a 12-category environmental and acquisition failure taxonomy to evaluate model vulnerability:

| Category Code | Description & Clinical Etiology | Primary Failure Mode |
| :--- | :--- | :--- |
| `EARLY_SUBTLE_PAPULES` | Pre-ulcerative stage; nodules $<10\text{ mm}$ lacking necrotic sit-fasts. | Texture blends into normal epidermal follicle grain. |
| `DISTANT_WHOLE_ANIMAL_FRAMING` | Capture distance $>3\text{ meters}$; entire animal silhouette in frame. | Lesions occupy $<4\%$ of pixels; downsampling attenuates nodules. |
| `SMALL_LESION_AREA` | Localized eruption confined to small flank/neck patch ($<5\%$ body surface). | Global average pooling activation diluted by extensive healthy skin. |
| `MUD_DEBRIS_OBSTRUCTION` | Heavy dried mud, dung splatters, or forage vegetation on coat. | Physical organic crust obscures epidermal lesion margins. |
| `POOR_LIGHTING` | Harsh barn structural shadows or severe backlight underexposure. | High-contrast shadow edges mimic or conceal nodular contours. |
| `OCCLUSION` | Fence posts, barn stanchions, or cohort animals blocking view. | Partial anatomical obstruction corrupts feature extraction. |
| `BACKGROUND_COMPLEXITY` | Straw bedding, textured earthen floor, or corrugated tin siding. | Complex textural frequencies trigger false-positive background activations. |
| `IMAGE_QUALITY` | Low sensor resolution ($<150\text{ px}$) or extreme JPEG block compression. | High-frequency lesion boundaries obliterated by compression. |
| `PARTIAL_BODY` | Extreme close-up of isolated body part (e.g. hock only) with no context. | Loss of macroscopic anatomical reference landmarks. |
| `MOTION_BLUR` | Animal movement during camera exposure causing motion smear. | Blurring degrades fine circular nodular edge gradients. |
| `NON_STANDARD_CAMERA` | Fish-eye distortion, heavy barrel aberration, or extreme white balance cast. | Optical deformation alters standard convolutional feature filters. |
| `UNKNOWN_FAILURE` | Specimen appears visually standard; failure occurs without clear physical defect. | Inherent deep neural network representation boundary variance. |

---

## 2. Multi-Label Annotation Semantics & Category Breakdown

> **Audit Notice**: Robustness categories are multi-label annotations; therefore category sample counts may exceed the total test-set size.

In real-world veterinary field conditions, acquisition challenges are not mutually exclusive: a distant standoff capture can simultaneously present a low lesion-to-background ratio (e.g. `ANI-LSD-0109` and `ANI-LSD-0151`), dried mud cakes can co-occur with barn bedding clutter (`ANI-LSD-0167`), and animal motion blur can combine with low sensor contrast (`ANI-LSD-0217`, `ANI-LSD-0593`).

### Empirical Multi-Label Distribution ($N=138$ Held-Out Test Set)
- **Unique Test Images Evaluated**: **138 / 138 (100%)**
- **Images with Exactly 1 Category Label**: **131** (94.9%)
- **Images with 2 Category Labels**: **5** (3.6%)
- **Images with 3 Category Labels**: **2** (1.4%)
- **Total Images with Multiple Robustness Labels**: **7** (5.1%)
- **Unique Test-Set False Negatives**: **Exactly 8 FNs** (No double-counting in test benchmark)
- **Category-Level FN Sum**: **14** (Reflects that individual challenging specimens span multiple co-occurring environmental categories)

### Category-Wise Performance Breakdown (Held-Out Test Partition)

In accordance with Section 9 of the Milestone 7 charter, **categories with sample size $n < 5$ report `"insufficient sample size"` rather than misleading percentages** (e.g., $1/1 = 100\%$ or $0/2 = 0\%$):

| Robustness Category | Sample Count ($n$) | Evaluation Status | Sensitivity (Recall) | Specificity | False Negatives (FN) | False Positives (FP) | Primary Vulnerability Finding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `EARLY_SUBTLE_PAPULES` | 2 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **2** | 0 | Flat pre-ulcerative papules near 0.50 boundary (`ANI-LSD-0027`, `ANI-LSD-0217`) |
| `DISTANT_WHOLE_ANIMAL_FRAMING` | 2 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **2** | 0 | Severe resolution loss from wide standoffs (`ANI-LSD-0109`, `ANI-LSD-0151`) |
| `SMALL_LESION_AREA` | 4 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **4** | 0 | Global pooling dilution by healthy coat (`ANI-LSD-0072`, `ANI-LSD-0109`, `ANI-LSD-0151`, `ANI-LSD-0179`) |
| `MUD_DEBRIS_OBSTRUCTION` | 1 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **1** | 0 | Physical mud crusting occludes lesion surface (`ANI-LSD-0167`) |
| `POOR_LIGHTING` | 2 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | 0 | 0 | Normal controls correctly classified despite lighting (`ANI-LSD-0058`, `ANI-LSD-0593`) |
| `OCCLUSION` | 0 | *no samples in partition* | — | — | 0 | 0 | Zero explicit physical occlusion cases in held-out test |
| `BACKGROUND_COMPLEXITY` | 1 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **1** | 0 | Mud + barn background overlap (`ANI-LSD-0167`) |
| `IMAGE_QUALITY` | 2 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **1** | 0 | Low sharpness/contrast degrades boundary gradients (`ANI-LSD-0217`, `ANI-LSD-0593`) |
| `PARTIAL_BODY` | 0 | *no samples in partition* | — | — | 0 | 0 | No extreme isolated-hock cases in test partition |
| `MOTION_BLUR` | 3 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **1** | 0 | Restless animal motion smears edge profiles (`ANI-LSD-0058`, `ANI-LSD-0217`, `ANI-LSD-0593`) |
| `NON_STANDARD_CAMERA` | 0 | *no samples in partition* | — | — | 0 | 0 | All test images acquired via mobile phone cameras |
| `UNKNOWN_FAILURE` | 1 | *insufficient sample size* | *withheld ($n<5$)* | *withheld ($n<5$)* | **1** | 0 | True unexplained failure without physical defect (`ANI-LSD-0013`) |
| `UNCLASSIFIED_STANDARD_CASE` | 128 | **Evaluated ($n \ge 5$)** | **100.0%** (34/34) | **97.87%** (92/94) | **0** | 2 | Standard presentations without adverse environmental degradation |

*Overall Held-Out Test Baseline*: $N=138$, Sensitivity = **$80.95\%$** (34/42), Specificity = **$97.92\%$** (94/96), Macro F1 = **$0.9106$**, Accuracy = **$92.75\%$**.

---

## 3. Comprehensive False-Negative Audit (Held-Out Test Set)

Every false negative on the frozen held-out test partition ($8$ cases) has been audited to determine its contributing physical failure factors:

| Sample ID | True Class | Model Probability ($p_{\text{LSD}}$) | Primary Failure Category | Observed Visual Characteristics | Possible Contributing Factor | Recommended Engineering & UX Mitigation |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **`ANI-LSD-0027`** | Lumpy Skin Disease | 0.4987 | `EARLY_SUBTLE_PAPULES` | Early flat papules; no necrosis or central sit-fast cratering. | Pre-eruptive stage has lower visual contrast; blends with dermal grain. | Multi-scale local patch zoom & pyrexia symptom score triage. |
| **`ANI-LSD-0109`** | Lumpy Skin Disease | 0.2121 | `DISTANT_WHOLE_ANIMAL_FRAMING` | Distant pasture shot ($>3\text{m}$); cow occupies wide frame. | Severe downsampling attenuation when resizing to $224 \times 224$. | Camera framing overlay in farmer UI; sliding-window tiling. |
| **`ANI-LSD-0151`** | Lumpy Skin Disease | 0.1280 | `DISTANT_WHOLE_ANIMAL_FRAMING` | Standoff capture; individual nodules $<3\%$ of pixel area. | Global average pooling aggregates majority healthy pasture background. | Multi-crop tiled inference; mandatory $<1.5\text{m}$ capture instruction. |
| **`ANI-LSD-0167`** | Lumpy Skin Disease | 0.3316 | `MUD_DEBRIS_OBSTRUCTION` | Dried organic mud cakes and soil crusting on lateral flank. | Physical opaque barrier covers cutaneous lesions. | UI prompt: *"Wipe skin with damp cloth before taking photo."* |
| **`ANI-LSD-0179`** | Lumpy Skin Disease | 0.4370 | `SMALL_LESION_AREA` | Localized cluster of 4 nodules; remainder of body unaffected. | Dilution of nodular feature activation by extensive clean coat. | Patch-level attention pooling; sliding window analysis. |
| **`ANI-LSD-0217`** | Lumpy Skin Disease | 0.4874 | `EARLY_SUBTLE_PAPULES` | Flat dermal elevations; near-boundary score ($0.487$). | Pre-ulcerative stage visual subtlety. | Secondary safety threshold tier (0.40) for veterinary re-examination. |
| **`ANI-LSD-0072`** | Lumpy Skin Disease | 0.4224 | `SMALL_LESION_AREA` | Sparse nodules on cervical neck; body clear. | Global average pooling spatial dilution. | High-resolution ($280 \times 280$) localized feature extraction. |
| **`ANI-LSD-0013`** | Lumpy Skin Disease | 0.2203 | `UNKNOWN_FAILURE` | Nodules visible; standard lighting; no mud or blur. | Inherent deep convolutional representation boundary variance. | Active learning queue for veterinary clinician re-annotation. |

---

## 4. Engineering & Field Deployment Mitigations

Based on empirical field failure modes, AniCare AI incorporates the following multi-tiered mitigations:

1. **Farmer Guided-Capture UI Overlay**:
   - Live framing bounding box prompts the farmer to approach within $1.0\text{ -- }1.5\text{ meters}$.
   - Real-time Laplacian blur detection blocks blurry images before inference.
   - Pre-capture checklist: *"Ensure coat is free of mud cakes and wet dung."*
2. **Multi-Scale Tiling (Secondary Mode)**:
   - For wide images where nodules occupy $<5\%$ of total pixels, the optional `TiledPreprocessor` runs a 5-patch decomposition, boosting localized lesion sensitivity.
3. **Multi-Modal Syndromic Safety Net**:
   - Because visual screening alone yields an $80.95\%$ sensitivity ceiling under field conditions, the `ClinicalRiskEngine` cross-references rectal temperature ($\ge 104^\circ\text{F}$), milk drop, and local epidemiological cluster alerts to escalate ambiguous cases to **High Clinical Risk** regardless of borderline vision scores.
