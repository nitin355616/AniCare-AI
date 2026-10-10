# AniCare AI — End-to-End Data Flow Specification

## 1. Lifecycle Data Flow

The platform guides information through an audited 10-stage lifecycle, ensuring complete traceability from initial village symptom detection to post-intervention surveillance.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer / Paravet
    participant Client as Offline PWA (IndexedDB)
    participant API as FastAPI Backend
    participant AI as ONNX Vision & Risk Engine
    participant Geo as Geospatial Engine
    actor Vet as Mobile Field Vet
    participant Lab as Diagnostic PCR Lab
    actor CVO as Chief Vet Officer

    Note over Farmer,Client: Stage 1: Detect
    Farmer->>Client: Log symptoms & upload lesion image (offline)
    Client->>Client: Cache locally with UUIDv4 idempotency key

    Note over Client,API: Connectivity Restored
    Client->>API: Batch sync payload (POST /api/sync/batch-upload)
    API->>API: Deduplicate and persist case record

    Note over API,AI: Stage 2: Assess
    API->>AI: Evaluate EfficientNet-B0 ONNX & clinical vitals
    AI-->>API: Return Multimodal Risk Index (0-100)

    Note over API,Geo: Stage 3: Map & Alert
    API->>Geo: Spatial query (5km radius DBSCAN clustering)
    Geo-->>API: Active hotspot detected (Spatial Risk Index 86.0)
    API->>API: Generate Priority P1 Alert & Response Case

    Note over API,Vet: Stage 5 & 6: Assign & Investigate
    API->>Vet: Dispatch alert to Mobile Unit #4
    Vet->>Farmer: On-site physical examination
    Vet->>API: Log confirmed clinical symptoms

    Note over Vet,Lab: Stage 7: Sample
    Vet->>Lab: Collect biopsy & EDTA blood (Sample SMP-2026-0802)
    Note over Lab: Cold-chain transit tracked

    Note over Lab,API: Stage 8: Verify
    Lab->>API: Submit PCR result: Capripoxvirus DNA Positive

    Note over API,CVO: Stage 9: Decide
    CVO->>API: Review dossier (AI + Field + PCR)
    CVO->>API: Authorize Directive AUTH-2026-001 (5km Ring Vaccination)

    Note over API,Vet: Stage 10: Follow-up & Monitor
    Vet->>API: Log herd recovery at Day 21 (Zero active cases)
    API->>API: Ingest case into Drift Monitoring (PSI 0.04 Stable)
```

## 2. Key Data Entities & Schemas

- **Animal Profile:** Identifies individual animals by Tag ID, species, breed, age, and owner contact.
- **Health Assessment:** Captures clinical signs, body temperature, mucosal condition, visual photo paths, and multimodal risk score.
- **Geospatial Hotspot:** Defines geographic cluster boundaries, center coordinates, radius, infected animal count, and Spatial Risk Index.
- **Response Alert:** Represents prioritized operational notifications (P1/P2/P3) linked to specific response cases.
- **Biological Sample:** Tracks chain of custody from specimen extraction to PCR laboratory validation.
- **Containment Authorization:** Documents regulatory decisions digitally signed by authorized veterinary officers.
