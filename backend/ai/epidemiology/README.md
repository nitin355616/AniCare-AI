# AniCare AI — Outbreak & Epidemiology Intelligence

## Architectural Vision

The AniCare AI Outbreak Intelligence module designs the data ingestion and spatio-temporal cluster surveillance engine to detect animal disease outbreaks days before traditional passive government reporting registers them.

Passive surveillance systems frequently experience delays of 7 to 21 days due to paper reporting chains. AniCare AI creates an active, multi-channel syndromic surveillance network.

---

## Multi-Source Data Fusion

The system is designed to fuse four distinct data streams:

```
+-----------------------------------------------------------------------------------+
|                           Multi-Source Ingestion Layer                            |
+---------------------+-------------------+-------------------+---------------------+
| 1. AI Visual Signals| 2. Farmer Reports | 3. Vet Diagnoses  | 4. Official DAHD    |
| - Lesion detections | - Symptom forms   | - Clinical exams  | - NADRS notifications|
| - High-confidence   | - Voice/USSD logs | - Rapid field kits| - INAPH ear-tag logs|
|   visual suspects   | - Milk drop notes | - Prescriptions   | - Lab PCR reports   |
+----------+----------+---------+---------+---------+---------+----------+----------+
           |                    |                   |                    |
           +--------------------+---------+---------+--------------------+
                                          |
                                          v
                   +-----------------------------------------------+
                   |      Spatio-Temporal Fusion & De-duplication  |
                   |      - Geographic boundary matching (GeoJSON) |
                   |      - Temporal window aggregation (3-14 days)|
                   |      - False-positive Bayesian filtering      |
                   +----------------------+------------------------+
                                          |
                                          v
                   +-----------------------------------------------+
                   |   Cluster Detection & Early Warning Trigger   |
                   |   - Spatial density clustering (DBSCAN)       |
                   |   - Anomaly score relative to historical base |
                   +----------------------+------------------------+
                                          |
                                          v
                   +-----------------------------------------------+
                   | Automated Multi-Tier Alert Dispatch           |
                   | - Red Alert: District Chief Veterinary Officer|
                   | - Orange Alert: Local Gram Panchayat Vets     |
                   | - Advisory: Livestock owners within 10km zone |
                   +-----------------------------------------------+
```

---

## 1. Event Structure Contract

Surveillance records follow the standardized `EpidemiologyEvent` schema:

- **`disease`**: Standardized disease identifier under controlled veterinary taxonomy.
- **`species`**: Target livestock species affected.
- **`location`**: Structured administrative hierarchy (`state`, `district`, `block_or_taluk`, `village`) with GPS latitude/longitude.
- **`date`**: ISO date of observation.
- **`affected_count`**, **`suspected_count`**, **`confirmed_count`**, **`mortality_count`**: Quantified epidemiological case counts.
- **`vaccination_status`**: Immunization state of affected cohort (`VACCINATED`, `UNVACCINATED`, `PARTIALLY_VACCINATED`, `UNKNOWN`).
- **`source`**: Stream origin (`AI_VISUAL_DETECTION`, `FARMER_SYMPTOM_REPORT`, `VETERINARY_CLINICAL_DIAGNOSIS`, `OFFICIAL_DAHD_NOTIFICATION`).
- **`verification_status`**: Lifecycle stage (`UNVERIFIED`, `FIELD_INVESTIGATION_PENDING`, `LAB_CONFIRMED`, `FALSE_POSITIVE`, `RESOLVED`).

---

## 2. Cluster Detection Principles

When fully deployed, the cluster detection engine utilizes:

1. **Spatial Radius Thresholds**:
   - For fast-spreading viral infections (FMD, African Swine Fever): 10 km ring containment radius.
   - For vector-borne diseases (Lumpy Skin Disease): 25 km vector surveillance buffer.

2. **Temporal Windowing**:
   - Rolling 7-day windows evaluated against 30-day baseline syndromic rates.
   - A cluster is flagged if $\ge 3$ distinct herd reports occur within a 5 km radius within 48 hours.

3. **Multi-Source Confidence Weighting**:
   - A lone farmer report is scored as low confidence.
   - A farmer report backed by an AI visual scan of mucosal vesicles elevates confidence to medium.
   - A field veterinarian's clinical confirmation elevates the event to high confidence, triggering administrative alerts.

---

## 3. Milestone 4A Boundary

> [!NOTE]
> In accordance with Milestone 4A requirements, **no external live APIs, scrapers, or third-party web services are connected yet**.
> This module establishes the rigorous data structures, mathematical consistency validators, and interface definitions required to integrate live data sources safely in future milestones.
