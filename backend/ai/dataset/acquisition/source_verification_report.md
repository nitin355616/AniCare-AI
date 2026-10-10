# AniCare AI — External Dataset Source Verification Report

**Verification Date:** 2026-10-07  
**Auditor:** AniCare AI Scientific & Legal Provenance Validation Engine  
**Governance Standard:** Zero Web-Scraping / Strict Independent Verification Before Ingestion

---

## Executive Summary

Before any image downloading was initiated, all three candidate datasets listed in [`backend/ai/dataset/source_registry.json`](file:///d:/AniCare-AI/backend/ai/dataset/source_registry.json) were independently audited against their official repository hosts (Mendeley Data and Zenodo).

- **Dataset 1 (Mendeley Lumpy Skin Disease)**: **VERIFIED & APPROVED**. Independently resolved to official DOI `10.17632/w36hpf86j2.1`. Certified CC-BY-4.0 open license. Direct download endpoint verified with 1,024 ground truth images.
- **Dataset 2 (Zenodo Bovine Mastitis Candidate)**: **UNVERIFIED — MARKED `REVIEW_REQUIRED`**. Candidate URL `zenodo.org/record/bovine-mastitis-clinical` does not exist on Zenodo. Existing Zenodo mastitis assets are either conference papers lacking open image archives or dairy sheep thermal sets (`TIDS`). **Download strictly prohibited.**
- **Dataset 3 (Mendeley Avian Pathology Candidate)**: **UNVERIFIED — MARKED `REVIEW_REQUIRED`**. Candidate URL `data.mendeley.com/datasets/poultry-pathology-cases` does not exist on Mendeley Data. Existing public poultry assets on Mendeley are fecal microscopy images (`10.17632/8pnbzpt2k9.1`), not cutaneous fowl pox lesions. **Download strictly prohibited.**

---

## Detailed Audit Records

### 1. Mendeley Lumpy Skin Images Dataset

- **Exact Official URL**: `https://data.mendeley.com/datasets/w36hpf86j2/1`
- **DOI**: `10.17632/w36hpf86j2.1`
- **Dataset Owner / Organization**: Sachin Kumar & Sourabh Shastri, Department of Computer Science & IT, University of Jammu, India.
- **Exact Dataset Title**: `Lumpy Skin Images Dataset`
- **License**: `CC BY 4.0` (`Creative Commons Attribution 4.0 International`)
- **License URL**: `http://creativecommons.org/licenses/by/4.0`
- **Commercial / Research Reuse Permissions**: **Permitted**. CC-BY-4.0 explicitly authorizes sharing, copying, and redistributing the material in any medium or format, and adapting/transforming for any purpose, including commercial.
- **Citation Requirements**: Must cite authors and DOI:  
  *Kumar, Sachin; Shastri, Sourabh (2022), "Lumpy Skin Images Dataset", Mendeley Data, V1, doi: 10.17632/w36hpf86j2.1*
- **Actual Number of Images/Files**: 1,024 images across 2 subfolders:
  - `LUMPY SKIN`: 324 images
  - `NORMAL SKIN`: 700 images
- **Actual Class Names**: `LUMPY SKIN`, `NORMAL SKIN`
- **Species**: Cattle (*Bos taurus* / *Bos indicus*)
- **Labels Provided**: Yes, folder-level classification structure (`LUMPY SKIN/` and `NORMAL SKIN/`).
- **Images Downloadable**: **Yes**. Download verified via Mendeley Data Public API endpoint (`Lumpy Skin Images Dataset.zip`, 161,739,104 bytes, SHA-256: `8f683d7b70727d92427560bedb68ee0250e3b04165b2a570136bc4be61802331`).
- **Redistribution Permitted**: Yes, under CC-BY-4.0 attribution terms.
- **Restrictions**: Must provide attribution, include license link, and indicate if modifications were performed.
- **Dataset Version & Date**: Version 1, published August 19, 2022.
- **Verification Verdict**: **`APPROVED` — Eligible for Ingestion**.

---

### 2. Zenodo Bovine Mastitis Dataset (Candidate)

- **Candidate URL**: `https://zenodo.org/record/bovine-mastitis-clinical`
- **Audit Findings**: 
  - The URL `https://zenodo.org/record/bovine-mastitis-clinical` does not exist on Zenodo (HTTP 404 / 403).
  - A systematic search of Zenodo records identified related literature:
    1. *Early Disease Detection in Livestock Using Image Processing Techniques* (Meenu Antony & Navyamol K.T.): Conference paper discussing MobileNetV2 on cattle mastitis, but no open public image archive is attached for download.
    2. *TIDS: Thermal Imaging Dataset for Subclinical Mastitis in Dairy Sheep* (418 images): Involves dairy sheep and thermal infrared imaging, not bovine RGB clinical mastitis.
  - No independently verifiable, open-access CC-BY RGB bovine mastitis dataset exists at the candidate identifier.
- **Verification Verdict**: **`REVIEW_REQUIRED` (UNVERIFIED) — Acquisition Withheld**.
- **Action Taken**: Folder `backend/ai/dataset/raw/bovine_mastitis/` holds quarantine notice. Zero unverified files downloaded.

---

### 3. Mendeley Avian Pathology Dataset (Candidate)

- **Candidate URL**: `https://data.mendeley.com/datasets/poultry-pathology-cases`
- **Audit Findings**:
  - The URL `https://data.mendeley.com/datasets/poultry-pathology-cases` does not exist on Mendeley Data.
  - A systematic search of Mendeley Data poultry repositories identified:
    1. *Poultry Fecal Imagery Dataset* (DOI: `10.17632/8pnbzpt2k9.1`): 14,000+ fecal smear images for internal coccidiosis diagnostics, but not cutaneous comb/wattle fowl pox lesions.
  - No independently verifiable CC-BY-4.0 dataset with cutaneous fowl pox images was confirmed on Mendeley Data under this citation.
- **Verification Verdict**: **`REVIEW_REQUIRED` (UNVERIFIED) — Acquisition Withheld**.
- **Action Taken**: Folder `backend/ai/dataset/raw/avian_pathology/` holds quarantine notice. Zero unverified files downloaded.
