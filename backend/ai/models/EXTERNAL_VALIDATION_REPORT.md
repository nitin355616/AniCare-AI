# AniCare AI — External Baseline Validation & Domain-Shift Report

**Project**: AniCare AI — AI-Powered Animal Health & Disease Early-Warning Platform (SIH 2026)  
**Milestone**: Milestone 7 — External Validation & Generalization Assessment  
**Model Architecture**: EfficientNet-B0 (`anicare_vision_bovine_v1.onnx`, Opset 14, $224 \times 224$ input)  
**Operating Threshold**: $\tau = 0.50$ (**FROZEN**, selected strictly on validation data)  
**External Validation Status**: **PENDING LEGAL ACQUISITION**  

---

## 1. Official Statement on External Validation

> **External validation pending due to lack of a legally verified independent dataset.**

In adherence to scientific integrity for the Smart India Hackathon (SIH 2026), AniCare AI **does NOT fabricate artificial external datasets or simulate unverified validation numbers**. 

Independent candidate repositories (AAU Anand Clinical Teaching Hospital Archives and ICAR-DFMD National Bovine Viral Repository) require formal signed Data Transfer Agreements (DTAs) and animal owner privacy clearances. Public uncurated web-scrapes (e.g., Kaggle public dumps) were audited and formally **rejected** due to unverified provenance, copyright liabilities, and $>35\%$ label corruption.

The automated external validation harness (`backend/ai/evaluation/external_evaluation.py`) is fully implemented, unit-tested, and ready to ingest Dataset B immediately upon execution of institutional data sharing agreements.

---

## 2. Baseline Model Performance on Curated Dataset A

To evaluate future domain shift objectively, the frozen model's performance on Dataset A partitions must remain clearly separated and unmerged:

| Metric | Dataset A Validation ($N=135$) | Dataset A Held-Out Test ($N=138$) | Dataset B External ($N=\text{Pending}$) |
| :--- | :---: | :---: | :---: |
| **Partition Role** | Threshold Selection & Tuning | Final Untouched Test Diagnostic | Independent Clinic Generalization |
| **LSD Positives** | 40 | 42 | Pending DTA |
| **Healthy Controls**| 95 | 96 | Pending DTA |
| **Operating Threshold** | **0.50 (Frozen)** | **0.50 (Frozen)** | **0.50 (Frozen)** |
| **LSD Sensitivity (Recall)** | **92.50%** (37/40) | **80.95%** (34/42) | *Pending verified dataset* |
| **Healthy Specificity** | **94.74%** (90/95) | **97.92%** (94/96) | *Pending verified dataset* |
| **LSD Precision** | 88.10% (37/42) | 94.44% (34/36) | *Pending verified dataset* |
| **Macro F1 Score** | **0.9329** | **0.9106** | *Pending verified dataset* |
| **Overall Accuracy** | 94.07% | 92.75% | *Pending verified dataset* |
| **ROC-AUC** | 0.9855 | 0.9452 | *Pending verified dataset* |
| **False Negatives (FN)**| 3 | **8** | *Pending verified dataset* |
| **False Positives (FP)**| 5 | **2** | *Pending verified dataset* |
| **Average CPU Latency**| 5.82 ms | 5.86 ms | *Pending verified dataset* |

*Note: The 80.95% held-out test recall reflects real-world cutaneous nodular variability and is never obscured by the 92.50% validation metric.*

---

## 3. Formal Domain-Shift Analysis (Dataset A vs Candidate Dataset B)

A systematic qualitative audit was performed across 9 physical and environmental dimensions comparing Dataset A (Mendeley field outbreaks) with Candidate Dataset B (AAU Anand Veterinary College Teaching Hospital archives):

| Dimension | Dataset A (Mendeley LSD Outbreak) | Candidate Dataset B (AAU Anand Archives) | Domain-Shift Risk Assessment |
| :--- | :--- | :--- | :--- |
| **1. Image Resolution** | Mobile phone field cameras ($640 \times 480$ to $1280 \times 720$). | Clinical SLR cameras and examination bay cameras ($>1920 \times 1080$). | *Performance degradation may indicate distribution shift due to downsampling artifacts.* |
| **2. Camera & Sensor** | Varied consumer smartphones with heavy dynamic compression. | Standardized focal lenses with manual white balance calibration. | Sensor color temperature shifts may alter epidermal hue activations. |
| **3. Lighting Conditions** | Harsh tropical outdoor sun; extreme structural barn shadows. | Diffuse indoor examination lighting; minimal specular glare. | Shadow attenuation improves background contrast but shifts texture gradients. |
| **4. Background Complexity** | Earthen floors, corrugated iron sheets, dense herd crowding. | Clean clinical examination bays, restraint chutes, concrete. | Lower background clutter in hospital settings typically reduces false alarms. |
| **5. Animal Framing** | Wide whole-body pasture standoffs ($>3\text{m}$) and flank angles. | Guided macro-dermatology framing focused on suspicious lesions. | Macro framing prevents the severe spatial dilution seen in wide field shots. |
| **6. Disease Stage** | Predominantly acute, eruptive nodular stage with umbilication. | Includes early pre-ulcerative papules and convalescent cicatrices. | Early subtle lesions present the highest risk of false negatives. |
| **7. Geography & Breeds** | Pan-India zebu cattle (*Bos indicus*) and crossbred dairy cows. | Western India (Gujarat) agro-climatic dairy belt (Gir, Kankrej, crossbreds). | High genetic and coat color alignment between both cohorts. |
| **8. Institution** | Academic consortium aggregated across outbreak epicenters. | State Agricultural University Clinical Teaching Hospital. | Different institutional diagnostic corroboration protocols. |
| **9. Coat Cleanliness** | Heavy mud splatters and organic soil caked on pasture animals. | Cleaned coat surfaces prior to clinical physical examination. | Removal of organic soil crusts significantly lowers occlusion errors. |

### Cautious Scientific Synthesis
> *"Observed distribution differences between field outbreak photography and clinical teaching hospital archives indicate tangible potential for domain shift. Performance changes upon external validation must be rigorously attributed to these 9 acquisition factors rather than assumed to be random."*

---

## 4. Controlled Improvement Strategy (Post-Baseline Protocol)

In accordance with Section 12 of the Milestone 7 charter, **the current model was not retrained prior to recording this external baseline**.

Once verified external images from Dataset B are ingested, the following controlled improvement experiments will be evaluated in sequence against clear clinical hypotheses:

| Experiment ID | Hypothesis | Targeted Defect | Evaluation Partition |
| :--- | :--- | :--- | :--- |
| **EXP-M7-A** | Stronger contrast and illumination augmentations reduce shadow false negatives. | `POOR_LIGHTING` | Validation Set |
| **EXP-M7-B** | Multi-scale patch tiling ($5$-crop ensemble) improves nodule detection in wide standoffs. | `DISTANT_WHOLE_ANIMAL_FRAMING` | Validation Set |
| **EXP-M7-C** | Higher input resolution ($280 \times 280$) preserves high frequencies for subtle papules. | `EARLY_SUBTLE_PAPULES` | Validation Set |
| **EXP-M7-D** | Weighted Focal Loss ($\alpha=0.65, \gamma=2.0$) penalizes false negatives on sparse nodules. | `SMALL_LESION_AREA` | Validation Set |
| **EXP-M7-E** | Mud and soil debris segmentation filter alerts user to clean the coat before inference. | `MUD_DEBRIS_OBSTRUCTION` | Preprocessing Layer |

*Governance Mandate: Dataset C must remain strictly untouched and quarantined throughout all experimental tuning.*
