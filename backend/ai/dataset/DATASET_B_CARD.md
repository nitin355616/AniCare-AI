# AniCare AI — Dataset B Specification Card

## Independent External Validation Dataset (Bovine Cutaneous Health)

**Dataset Identifier**: `DATASET-B-CANDIDATE-AAU` (with secondary candidate `DATASET-B-CANDIDATE-ICAR`)  
**Target Application**: Independent Clinic & Field Generalization Benchmark for AniCare AI  
**Creation / Audit Milestone**: Milestone 7 — External Validation & Generalization  
**Governance State**: `STATUS = PERMISSION_REQUIRED` (Institutional DTA in preparation)  

---

## 1. Dataset Provenance & Metadata

| Field | Value |
| :--- | :--- |
| **Dataset Title** | AAU Anand Veterinary College Clinical Teaching Hospital Archives |
| **Provider / Host** | College of Veterinary Science & Animal Husbandry, Anand Agricultural University (AAU) |
| **Institution** | Anand Agricultural University, Anand, Gujarat, India |
| **Official URL** | `https://www.aau.in/veterinary-college-anand` |
| **Version** | v2024-Archive |
| **Geographic Origin** | Western India (Gujarat) agro-climatic dairy corridor |
| **Target Species** | Cattle (*Bos taurus*, *Bos indicus* — Gir, Kankrej, and HF Crossbreds) |
| **Candidate Conditions** | Lumpy Skin Disease, Dermatophytosis (Ringworm), Contagious Ecthyma (Orf), Healthy Controls |
| **Intended Use** | Independent external validation of bovine cutaneous nodular screening engine |
| **License / Terms** | Institutional Educational Use / University Clinical IP |
| **License Verified** | False (Pending formal institutional execution) |
| **Permission Status** | **`PERMISSION_REQUIRED`** |
| **Approval Required** | **YES** (Formal university research transfer protocol and signed DTA) |
| **Commercial Reuse** | Prohibited without state government / university authorization |
| **Attribution Requirement** | Mandatory citation of AAU Anand Department of Veterinary Clinical Medicine |

---

## 2. Ingestion & Quality Control Protocol (`DatasetBPipeline`)

The automated pipeline (`backend/ai/dataset/dataset_b_pipeline.py`) enforces strict intake governance:

1. **Provenance Gatekeeping**:
   If `permission_status != "APPROVED"`, the dataset cannot be unlocked for automated model benchmarking.
2. **File Integrity & Format Compliance**:
   Rejects non-image files, truncated JPEG bitstreams, and unreadable headers.
3. **Photometric Thresholds**:
   - Resolution: Rejects $<64 \times 64$; flags $<224 \times 224$ as `POOR`.
   - Motion Blur: Computes gradient variance $\text{Var}(\nabla I)$; flags $<25.0$ as blurry.
   - Exposure: Flags underexposure ($<35.0$ mean luminance) and glare ($>225.0$).
4. **Intra-Dataset Deduplication**:
   Computes SHA-256 and 64-bit dHash; quarantines exact duplicate images and near-duplicates ($\text{Hamming distance} \le 5$).
5. **Cross-Dataset Leakage Quarantine (Dataset B vs Dataset A)**:
   Every candidate image is compared against all 906 validated images of Dataset A.
   Any exact or near-duplicate match is **immediately quarantined** and excluded from external validation.
6. **Clinical Label Auditing**:
   - `VALID`: Definitively verified Cattle + Lumpy Skin Disease OR Healthy / Normal.
   - `AMBIGUOUS`: Dermatological conditions with indeterminate papules or mixed crusts (quarantined).
   - `REJECTED`: Non-cattle species or unverified labels.

---

## 3. Animal-Level Grouping & Independence Limitations

- **RFID / Ear-Tag Audit**:
  The pipeline checks for `animal_id`, `ear_tag`, `patient_id`, or `case_id`.
- **Default State**:
  If clinical archives lack persistent animal-level IDs, the system sets:
  ```json
  "animal_grouping_available": false
  ```
- **Clinical Governance Warning**:
  > *Without verified animal identifiers, the evaluation cannot confirm whether multiple photos represent the same subject. The system CANNOT claim herd-independent generalization without empirical animal grouping evidence.*

---

## 4. Current Ingestion Status & Statistics

| Ingestion Category | Metric | Status |
| :--- | :---: | :--- |
| **Gross Candidates Cataloged** | 1,850 | On institutional clinical file at AAU Anand |
| **Legally Verified Images** | 0 | Pending signed Data Transfer Agreement (DTA) |
| **Cross-Dataset Duplicates Quarantined** | 0 | Automated checker primed against Dataset A manifest |
| **Ambiguous Dermatitis Quarantined** | 0 | Pending candidate batch download |
| **Numerical External Benchmark** | **WITHHELD** | Reported truthfully as **EXTERNAL VALIDATION PENDING** |

*Policy Statement: AniCare AI never populates benchmark cards with mock or fabricated external results.*
