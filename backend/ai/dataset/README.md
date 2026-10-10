# AniCare AI — Dataset Intelligence & Validation Framework

## Overview

The AniCare AI Dataset Intelligence framework defines a scientifically rigorous, veterinary-grade methodology for curating, validating, and partitioning animal health imagery prior to any machine learning model training. 

In veterinary medicine, computer vision errors can have severe economic and epidemiological consequences. An unverified image scraped from the internet can cause false negative predictions during transboundary disease outbreaks (e.g., Foot and Mouth Disease, Lumpy Skin Disease) or inappropriate antibiotic recommendations. AniCare AI solves this through strict clinical provenance, taxonomic validation, animal-level split isolation, and privacy guards.

---

## The 6-Stage Diagnostic Pipeline

AniCare AI rejects the monolithic "black box" disease classifier paradigm. Instead, inference is decomposed into 6 distinct stages that separate machine learning predictions from deterministic clinical and epidemiological rules:

| Stage | Name | Modality | Function & Purpose |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Species / Animal Detection** | **Machine Learning** | Confirms the animal presence and identifies biological species (Cattle, Buffalo, Goat, Sheep, Pig, Poultry, Dog) from background farm clutter. |
| **Stage 2** | **Image Quality Assessment** | **Deterministic Heuristics** | Detects file corruption, unsupported formats, sub-viable resolutions (<64×64), extreme aspect ratios, and computes SHA-256 and perceptual dHashes. |
| **Stage 3** | **Visual Condition Classification** | **Machine Learning** | Predicts probabilities for *visually assessable* lesions only (e.g., circumscribed dermal nodules, vesicular mucosal ulcers, circumscribed alopecia). Returns **"possible visual condition"**, never a laboratory diagnosis. |
| **Stage 4** | **Clinical & Contextual Risk Engine** | **Deterministic Rules** | Integrates user-reported clinical signs (fever, milk drop, recumbency), vaccination history, and anatomical localization against veterinary triage guidelines. |
| **Stage 5** | **Veterinary Tele-Review** | **Human-in-the-Loop** | Cases flagged with high contagion or severe mortality risk are routed to registered veterinary professionals with raw imagery and pre-filled clinical summaries. |
| **Stage 6** | **Epidemiological Cluster Intelligence** | **Spatio-Temporal Fusion** | Aggregates geographic clusters of AI visual detections, farmer symptom reports, and lab-verified field notifications to detect disease outbreaks early. |

---

## Controlled Veterinary Taxonomy

Diseases are categorized into four diagnostic classes to uphold veterinary integrity:

1. **Visually Assessable Conditions (`VISUAL_ASSESSABLE`)**:
   - Manifest with distinctive dermatological, ocular, or superficial anatomical signs.
   - *Examples*: Lumpy Skin Disease nodules, FMD vesicular erosions, Bovine Ringworm crusts, Contagious Ecthyma (Orf) scabs, Fowl Pox dry cutaneous nodules, Canine Demodectic Mange.
   - *Model Target*: These are the **only** conditions for which image-based visual classifiers are trained.

2. **Symptom-Driven Conditions (`SYMPTOM_DRIVEN`)**:
   - Require systemic, behavioral, or respiratory symptom inputs rather than static visual inspection.
   - *Examples*: Bovine Respiratory Disease Complex (tachypnea, thoracic crackles), Peste des Petits Ruminants (watery diarrhea, hyperthermia).
   - *Model Target*: Triaged via rule-based clinical symptom intake forms.

3. **Laboratory-Confirmation-Required Diseases (`LABORATORY_CONFIRMATION_REQUIRED`)**:
   - Clinically indistinguishable or hyper-acute conditions where definitive diagnosis legally requires laboratory confirmation.
   - *Examples*: Anthrax (*Bacillus anthracis* McFadyean capsule reaction), Brucellosis (serum Rose Bengal Plate Test), African Swine Fever (RT-PCR), Rabies (post-mortem brain DFA).
   - *Safety Guard*: AniCare AI raises an immediate emergency veterinary alert and **never** predicts a positive Anthrax or Rabies visual diagnosis from an image.

4. **Epidemiological Signals (`EPIDEMIOLOGICAL_SIGNAL`)**:
   - Herd-level mortality, sudden abortion storms, or regional spikes in unexplained lameness monitored by spatial cluster algorithms.

---

## Data Split Policy: Prevention of Same-Animal Leakage

In livestock datasets, capturing 10 photographs of a single cow from different angles and randomly assigning 7 to training and 3 to testing causes catastrophic data leakage:
- The convolutional network memorizes the unique coat pattern, ear tag, stall background, or horn curvature of the cow rather than the actual skin lesion pathology.
- Evaluation metrics yield artificially inflated test accuracies that collapse when deployed on new farms.

### Strict Group Partitioning
- **Animal-Level Grouping**: All images sharing the same `animal_id` (RFID tag, ear-tag, or patient identifier) are assigned strictly to a single partition (`train`, `validation`, OR `test`).
- **Standard Split Ratios**: 70% Train, 15% Validation, 15% Test.
- **Cryptographic & Perceptual De-duplication**: Exact SHA-256 matches and perceptual near-duplicates (Hamming distance $\le 5$ via dHash) occurring across split boundaries are flagged as `CRITICAL_LEAKAGE` by `DatasetManifestValidator`.

---

## Licensing, Provenance & Privacy Guards

- **Strict License Verification**: Only data sources with verified open licenses (`CC-BY-4.0`, `CC-BY-SA`, or formal Institutional Data Transfer Agreements) are marked `APPROVED`.
- **Public Scraping Quarantine**: Uncurated web-scraped images or anonymous Kaggle uploads without clinical records are categorized as `REJECTED_UNSUITABLE` due to high label corruption, lack of gold standard verification, and copyright risk.
- **PII Scrubbing**: Manifest records pass through a regex sanitizer that rejects mobile phone numbers (e.g. 10-digit Indian mobile formats) or citizen identity numbers in field notes to safeguard farmer and veterinarian privacy.
