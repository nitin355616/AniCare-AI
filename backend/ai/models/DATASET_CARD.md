# AniCare AI — Dataset Card: Multi-Species Livestock Health Imagery Benchmark (MSL-HIB)

Following the framework proposed by Gebru et al. (*Datasheets for Datasets*, CACM 2021).

---

## 1. Dataset Summary

- **Dataset Name**: AniCare Multi-Species Livestock Health Imagery Benchmark (MSL-HIB)
- **Current Version**: 1.0.0-verified-ingestion (Milestone 4B Active)
- **Primary Custodians**: AniCare AI Research Group / Smart India Hackathon 2026
- **Release Status**: License-Verified Ingestion Complete for Approved Sources; Institutional & Quarantined Sources Tracked in Acquisition Registry.

---

## 2. Ingested Dataset Composition (Actual Verified Counts)

### 2.1 Primary Ingested Source
- **Source**: Mendeley Data — *Lumpy Skin Images Dataset* (Sachin Kumar & Sourabh Shastri, University of Jammu, India)
- **DOI**: `10.17632/w36hpf86j2.1`
- **Verified License**: `CC-BY-4.0` (Creative Commons Attribution 4.0 International)
- **Target Species**: Cattle (*Bos taurus* / *Bos indicus*)

### 2.2 Image Count Accounting (Strict Audit)
| Metric | Count | Description / Notes |
| :--- | :--- | :--- |
| **Source-Reported Count** | **1,024** | 324 claimed `LUMPY SKIN`, 700 claimed `NORMAL SKIN` in Mendeley metadata |
| **Actual Downloaded Count** | **1,024** | 100% matched across raw directories (`raw/lumpy_skin_disease/`) |
| **Corrupted / Unreadable Count** | **0** | Verified via `ImageQualityChecker`: all files decode as valid PNGs, 256×256 px |
| **Exact Duplicates Quarantined** | **5** | SHA-256 collision purge (including 2 cross-class duplicate anomalies in source data) |
| **Near Duplicates Quarantined** | **113** | Perceptual `dHash` Hamming distance $\le 5$ purged to protect holdout splits |
| **Total Quarantined** | **118** | Fully documented in `processed/quarantine_manifest.json` |
| **Final Validated Count** | **906** | High-integrity, deduplicated, taxonomically normalized samples |

### 2.3 Partitioning & Final Training Split
- **Train Split (70%)**: 633 images (189 Lumpy Skin Disease, 444 Healthy / Normal)
- **Validation Split (15%)**: 135 images (41 Lumpy Skin Disease, 94 Healthy / Normal)
- **Test Split (15%)**: 138 images (41 Lumpy Skin Disease, 97 Healthy / Normal)
- **Total Validated Split**: **906** images across 2 canonical classes (`Lumpy Skin Disease`, `Healthy / Normal`).

### 2.4 Status of Other Candidate Datasets
- **Zenodo Bovine Mastitis Candidate**:
  - *Source-Reported Count*: 780 (in draft registry)
  - *Actual Downloaded Count*: **0**
  - *Status*: **`REVIEW_REQUIRED` (Download Withheld)**. Candidate URL failed independent verification on Zenodo; downloading unverified sources is prohibited.
- **Mendeley Avian Pathology Candidate**:
  - *Source-Reported Count*: 640 (in draft registry)
  - *Actual Downloaded Count*: **0**
  - *Status*: **`REVIEW_REQUIRED` (Download Withheld)**. Candidate URL failed independent verification on Mendeley Data; downloading unverified sources is prohibited.

---

## 3. Geographic & Environmental Scope

- **Primary Geographic Origin**: India (Jammu & Kashmir agro-climatic dairy basin).
- **Subject Demographics**: Indigenous Zebu and mixed dairy cattle.
- **Environmental Context**: Field clinical captures, smallholder dairy sheds, variable illumination, direct sunlight and shaded stalls.
- **Lesion Morphology**: Variable stage circumscribed cutaneous nodules (2–5 cm diameter), ulcerated plaques, and unaffected dermal control surfaces.

---

## 4. Annotation & Provenance Methodology

- **Annotation Level**: Folder-level class consensus (`LUMPY SKIN` vs `NORMAL SKIN`) established by academic veterinary/computer science researchers.
- **Diagnostic Ground Truth**: Visual inspection correlated with epidemiological field presentations during the 2022 Indian Lumpy Skin Disease outbreak.
- **Canonical Mapping**: Mapped to AniCare Controlled Veterinary Taxonomy (`VISUAL_ASSESSABLE`, target species: `Cattle`, body region: `skin_cutaneous`).
- **Privacy & PII Protection**: Source data contains no farmer names, phone numbers, or residential addresses.

---

## 5. Critical Dataset Limitations

1. **Animal Grouping Limitation (`animal_grouping_available = false`)**:
   - The source publication did not record individual cow ear-tag or RFID identifiers.
   - Consequently, **animal-level grouping cannot be claimed** for this specific dataset.
   - To mitigate risk of the model memorizing coat patterns across splits, a strict perceptual near-duplicate quarantine (dHash $\le 5$) was executed prior to stratified partitioning.
2. **Binary Class Limitation**:
   - Currently covers `Lumpy Skin Disease` and `Healthy / Normal` bovine dermatological presentations.
   - Additional visual conditions (e.g., Bovine Ringworm, Contagious Ecthyma) await institutional data transfer execution.
3. **Resolution**:
   - Images preprocessed by original authors to 256×256 PNG. Suitable for standard $224\times 224$ CNN inputs without downsampling distortion.

---

## 6. Uses & Operational Boundaries

### 6.1 Intended Use
- Training and benchmarking visual lesion detection models for bovine cutaneous nodular eruptions.
- Educational screening and frontline risk triage.

### 6.2 Prohibited Use
- Sole basis for therapeutic interventions or regulatory quarantine enforcement without veterinary laboratory confirmation (Capripoxvirus PCR).

---

## 7. License & Attribution

- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`).
- **Citation**:
  > Kumar, Sachin; Shastri, Sourabh (2022), "Lumpy Skin Images Dataset", Mendeley Data, V1, doi: 10.17632/w36hpf86j2.1
